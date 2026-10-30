import { useCallback, useEffect, useState } from "react";
import { open } from "@tauri-apps/plugin-dialog";
import { revealItemInDir } from "@tauri-apps/plugin-opener";
import { ActivityEvent, api, ApiError, Settings, Status } from "./api";
import "./App.css";

const POLL_INTERVAL_MS = 2000;

const STATE_LABELS = {
  running: "Running",
  stopped: "Stopped",
  error: "Needs attention",
};

function fileName(path: string) {
  return path.split(/[\\/]/).pop() ?? path;
}

function lastTwoParts(path: string) {
  return path.split(/[\\/]/).slice(-2).join("/");
}

function formatTime(timestamp: string) {
  return new Date(timestamp).toLocaleTimeString();
}

function errorText(error: unknown) {
  return error instanceof Error ? error.message : String(error);
}

function App() {
  const [status, setStatus] = useState<Status | null>(null);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [actionError, setActionError] = useState<string | null>(null);
  const [settings, setSettings] = useState<Settings | null>(null);
  const [watchFolder, setWatchFolder] = useState("");
  const [destination, setDestination] = useState("");
  const [activity, setActivity] = useState<ActivityEvent[]>([]);
  const [busy, setBusy] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const [newStatus, newActivity] = await Promise.all([api.status(), api.activity()]);
      setStatus(newStatus);
      setActivity(newActivity);
      setConnectionError(null);
    } catch (error) {
      setConnectionError(errorText(error));
    }
  }, []);

  // Poll status and activity every 2 seconds while the window is visible.
  useEffect(() => {
    refresh();
    const timer = window.setInterval(() => {
      if (document.visibilityState === "visible") {
        refresh();
      }
    }, POLL_INTERVAL_MS);
    return () => window.clearInterval(timer);
  }, [refresh]);

  // Load settings once the backend answers.
  useEffect(() => {
    if (status === null || settings !== null) {
      return;
    }
    api
      .settings()
      .then((loaded) => {
        setSettings(loaded);
        setWatchFolder(loaded.watch_folder ?? "");
        setDestination(loaded.destination_root ?? "");
      })
      .catch((error) => setActionError(errorText(error)));
  }, [status, settings]);

  async function run(action: () => Promise<void>) {
    setBusy(true);
    setActionError(null);
    try {
      await action();
    } catch (error) {
      setActionError(error instanceof ApiError ? error.message : errorText(error));
    } finally {
      setBusy(false);
    }
  }

  async function chooseFolder(setter: (path: string) => void) {
    const chosen = await open({ directory: true, multiple: false });
    if (typeof chosen === "string") {
      setter(chosen);
    }
  }

  const running = status?.state === "running";
  const savedWatch = settings?.watch_folder ?? "";
  const savedDestination = settings?.destination_root ?? "";
  const settingsChanged = watchFolder !== savedWatch || destination !== savedDestination;
  const settingsComplete = savedWatch !== "" && savedDestination !== "";

  if (status === null) {
    return (
      <main className="app">
        <h1>File Organizer</h1>
        <section className="card">
          <p>{connectionError ?? "Connecting to the organizer…"}</p>
        </section>
      </main>
    );
  }

  return (
    <main className="app">
      <header className="header">
        <h1>File Organizer</h1>
        <span className={`pill pill-${status.state}`}>{STATE_LABELS[status.state]}</span>
      </header>

      {connectionError && <p className="banner banner-error">{connectionError}</p>}
      {actionError && <p className="banner banner-error">{actionError}</p>}

      <section className="card">
        <h2>Status</h2>
        {status.message && <p className="status-message">{status.message}</p>}
        <p className="hint">
          {running
            ? "New files in the source folder are being sorted into the destination."
            : "Start sorts files already in the source folder, including subfolders, and keeps watching for new ones."}
        </p>
        <div className="row">
          {running ? (
            <button
              disabled={busy}
              onClick={() => run(async () => setStatus(await api.stop()))}
            >
              Stop
            </button>
          ) : (
            <button
              className="primary"
              disabled={busy || !settingsComplete || settingsChanged}
              onClick={() => run(async () => setStatus(await api.start()))}
            >
              Start
            </button>
          )}
          {savedDestination && (
            <button onClick={() => run(() => revealItemInDir(savedDestination))}>
              Show destination
            </button>
          )}
        </div>
        <p className="hint">Closing this window stops the organizer.</p>
      </section>

      <section className="card">
        <h2>Folders</h2>
        <FolderField
          label="Source folder"
          value={watchFolder}
          disabled={running || busy}
          onChoose={() => chooseFolder(setWatchFolder)}
        />
        <FolderField
          label="Destination folder"
          value={destination}
          disabled={running || busy}
          onChoose={() => chooseFolder(setDestination)}
        />
        <div className="row">
          <button
            className="primary"
            disabled={running || busy || !settingsChanged || !watchFolder || !destination}
            onClick={() =>
              run(async () => {
                const saved = await api.saveSettings(watchFolder, destination);
                setSettings(saved);
                setWatchFolder(saved.watch_folder ?? "");
                setDestination(saved.destination_root ?? "");
                setStatus(await api.status());
              })
            }
          >
            Save folders
          </button>
          {settingsChanged && settings && (
            <button
              disabled={busy}
              onClick={() => {
                setWatchFolder(savedWatch);
                setDestination(savedDestination);
              }}
            >
              Undo changes
            </button>
          )}
        </div>
        {running && <p className="hint">Stop the organizer to change folders.</p>}

        {settings && (
          <>
            <h3>Categories</h3>
            <ul className="categories">
              {Object.entries(settings.categories).map(([category, extensions]) => (
                <li key={category}>
                  <strong>{category}</strong> <span>{extensions.join(" ")}</span>
                </li>
              ))}
              <li>
                <strong>Others</strong> <span>everything else</span>
              </li>
            </ul>
          </>
        )}
      </section>

      <section className="card">
        <h2>Recent activity</h2>
        {activity.length === 0 ? (
          <p className="hint">No files moved yet.</p>
        ) : (
          <ul className="activity">
            {activity.map((event, index) => (
              <li key={`${event.timestamp}-${index}`} className={`event-${event.type}`}>
                <time>{formatTime(event.timestamp)}</time>
                {event.type === "moved" ? (
                  <span title={`${event.source} → ${event.destination}`}>
                    {fileName(event.source)} → {lastTwoParts(event.destination)}
                  </span>
                ) : (
                  <span title={event.source}>
                    {fileName(event.source)}: {event.message}
                  </span>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}

interface FolderFieldProps {
  label: string;
  value: string;
  disabled: boolean;
  onChoose: () => void;
}

function FolderField({ label, value, disabled, onChoose }: FolderFieldProps) {
  return (
    <div className="folder-field">
      <span className="folder-label">{label}</span>
      <span className="folder-path" title={value}>
        {value || "Not chosen"}
      </span>
      <button disabled={disabled} onClick={onChoose}>
        Choose…
      </button>
    </div>
  );
}

export default App;
