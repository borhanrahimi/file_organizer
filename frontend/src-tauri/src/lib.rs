// The app owns the Python backend process (see docs/decisions/002).
// It starts the backend with a free port and a random token, hands both to
// the window, and asks the backend to shut down when the app quits.

use std::io::{Read, Write};
use std::net::{TcpListener, TcpStream};
use std::process::{Child, Command};
use std::sync::Mutex;
use std::time::{Duration, Instant};

use serde::Serialize;
use tauri::{Manager, RunEvent};

const SHUTDOWN_WAIT: Duration = Duration::from_secs(5);

struct Backend {
    port: u16,
    token: String,
    child: Mutex<Option<Child>>,
    start_error: Option<String>,
}

#[derive(Serialize)]
struct BackendConnection {
    port: u16,
    token: String,
}

// Development runs the backend with the local Python, where the package is
// installed with `pip install -e ./backend`. ORGANIZER_PYTHON overrides it.
fn python_command() -> String {
    std::env::var("ORGANIZER_PYTHON").unwrap_or_else(|_| {
        if cfg!(windows) { "python" } else { "python3" }.to_string()
    })
}

fn free_port() -> std::io::Result<u16> {
    let listener = TcpListener::bind("127.0.0.1:0")?;
    Ok(listener.local_addr()?.port())
}

fn start_backend(app: &tauri::App) -> Backend {
    let token = uuid::Uuid::new_v4().simple().to_string();
    let mut backend = Backend {
        port: 0,
        token: token.clone(),
        child: Mutex::new(None),
        start_error: None,
    };

    let settings = match app.path().app_data_dir() {
        Ok(folder) => folder.join("settings.yaml"),
        Err(error) => {
            backend.start_error = Some(format!("Could not find the app data folder: {error}"));
            return backend;
        }
    };

    backend.port = match free_port() {
        Ok(port) => port,
        Err(error) => {
            backend.start_error = Some(format!("Could not find a free port: {error}"));
            return backend;
        }
    };

    let python = python_command();
    let result = Command::new(&python)
        .args(["-m", "organizer.server", "--port"])
        .arg(backend.port.to_string())
        .arg("--settings")
        .arg(settings)
        .arg("--parent-pid")
        .arg(std::process::id().to_string())
        .env("ORGANIZER_TOKEN", &token)
        .spawn();

    match result {
        Ok(child) => backend.child = Mutex::new(Some(child)),
        Err(error) => {
            backend.start_error = Some(format!("Could not run '{python}': {error}"))
        }
    }
    backend
}

#[tauri::command]
fn backend_connection(backend: tauri::State<Backend>) -> Result<BackendConnection, String> {
    if let Some(error) = &backend.start_error {
        return Err(error.clone());
    }

    let mut child = backend.child.lock().unwrap();
    if let Some(process) = child.as_mut() {
        if let Ok(Some(status)) = process.try_wait() {
            return Err(format!(
                "The organizer backend exited ({status}). Is the Python package installed?"
            ));
        }
    }

    Ok(BackendConnection {
        port: backend.port,
        token: backend.token.clone(),
    })
}

// A plain HTTP request so quitting needs no extra libraries.
fn request_shutdown(port: u16, token: &str) -> std::io::Result<()> {
    let mut stream = TcpStream::connect(("127.0.0.1", port))?;
    stream.set_read_timeout(Some(SHUTDOWN_WAIT))?;
    write!(
        stream,
        "POST /shutdown HTTP/1.1\r\nHost: 127.0.0.1\r\nAuthorization: Bearer {token}\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
    )?;
    let mut response = Vec::new();
    stream.read_to_end(&mut response)?;
    Ok(())
}

fn stop_backend(backend: &Backend) {
    let Some(mut child) = backend.child.lock().unwrap().take() else {
        return;
    };

    if let Err(error) = request_shutdown(backend.port, &backend.token) {
        eprintln!("Could not ask the backend to shut down: {error}");
    }

    let deadline = Instant::now() + SHUTDOWN_WAIT;
    while Instant::now() < deadline {
        if let Ok(Some(_)) = child.try_wait() {
            return;
        }
        std::thread::sleep(Duration::from_millis(100));
    }

    // No backend process may be left running after the app quits.
    eprintln!("The backend did not exit in time; ending it.");
    let _ = child.kill();
    let _ = child.wait();
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_dialog::init())
        .setup(|app| {
            let backend = start_backend(app);
            app.manage(backend);
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![backend_connection])
        .build(tauri::generate_context!())
        .expect("error while building tauri application")
        .run(|app, event| {
            if let RunEvent::Exit = event {
                stop_backend(&app.state::<Backend>());
            }
        });
}

#[cfg(test)]
mod tests {
    use super::*;

    fn wait_for_server(port: u16) {
        let deadline = Instant::now() + Duration::from_secs(10);
        while TcpStream::connect(("127.0.0.1", port)).is_err() {
            assert!(Instant::now() < deadline, "backend did not start");
            std::thread::sleep(Duration::from_millis(100));
        }
    }

    // Needs the Python package installed: pip install -e ./backend
    #[test]
    fn stop_backend_shuts_down_the_python_server() {
        let folder = std::env::temp_dir().join(format!("organizer-test-{}", std::process::id()));
        let port = free_port().unwrap();
        let token = "test-token".to_string();
        let child = Command::new(python_command())
            .args(["-m", "organizer.server", "--port", &port.to_string()])
            .arg("--settings")
            .arg(folder.join("settings.yaml"))
            .arg("--lock-file")
            .arg(folder.join("organizer.lock"))
            .env("ORGANIZER_TOKEN", &token)
            .spawn()
            .unwrap();
        wait_for_server(port);

        let backend = Backend {
            port,
            token,
            child: Mutex::new(Some(child)),
            start_error: None,
        };
        let started = Instant::now();
        stop_backend(&backend);

        // Exiting well before the deadline means /shutdown worked, not the kill.
        assert!(started.elapsed() < SHUTDOWN_WAIT);
        assert!(backend.child.lock().unwrap().is_none());
        assert!(TcpStream::connect(("127.0.0.1", port)).is_err());
        let _ = std::fs::remove_dir_all(folder);
    }

    #[test]
    fn stop_backend_kills_a_backend_that_does_not_answer() {
        let child = Command::new("sleep").arg("60").spawn().unwrap();
        let backend = Backend {
            port: free_port().unwrap(),
            token: "unused".to_string(),
            child: Mutex::new(Some(child)),
            start_error: None,
        };

        stop_backend(&backend);

        assert!(backend.child.lock().unwrap().is_none());
    }
}
