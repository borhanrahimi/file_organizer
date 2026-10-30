// Talks to the Python backend over the local HTTP API (docs/decisions/002).
import { invoke } from "@tauri-apps/api/core";

export type OrganizerState = "running" | "stopped" | "error";

export interface Status {
  state: OrganizerState;
  message: string | null;
}

export interface Settings {
  watch_folder: string | null;
  destination_root: string | null;
  categories: Record<string, string[]>;
}

export type ActivityEvent =
  | { timestamp: string; type: "moved"; source: string; destination: string }
  | { timestamp: string; type: "error"; source: string; message: string };

interface Connection {
  port: number;
  token: string;
}

// The backend's own error format: {"error": {"code": ..., "message": ...}}.
export class ApiError extends Error {
  code: string;

  constructor(code: string, message: string) {
    super(message);
    this.code = code;
  }
}

let connection: Promise<Connection> | null = null;

function getConnection(): Promise<Connection> {
  if (connection === null) {
    connection = invoke<Connection>("backend_connection").catch((error) => {
      // Ask again next time; the error may be temporary.
      connection = null;
      throw new ApiError("backend_unavailable", String(error));
    });
  }
  return connection;
}

async function request<T>(method: string, path: string, body?: unknown): Promise<T> {
  const { port, token } = await getConnection();

  let response: Response;
  try {
    response = await fetch(`http://127.0.0.1:${port}${path}`, {
      method,
      headers: {
        Authorization: `Bearer ${token}`,
        ...(body === undefined ? {} : { "Content-Type": "application/json" }),
      },
      body: body === undefined ? undefined : JSON.stringify(body),
    });
  } catch {
    throw new ApiError("backend_unavailable", "Waiting for the organizer backend to start…");
  }

  const data = await response.json();
  if (!response.ok) {
    throw new ApiError(data.error?.code ?? "unknown", data.error?.message ?? response.statusText);
  }
  return data as T;
}

export const api = {
  status: () => request<Status>("GET", "/status"),
  start: () => request<Status>("POST", "/start"),
  stop: () => request<Status>("POST", "/stop"),
  settings: () => request<Settings>("GET", "/settings"),
  saveSettings: (watch_folder: string, destination_root: string) =>
    request<Settings>("PUT", "/settings", { watch_folder, destination_root }),
  activity: () => request<ActivityEvent[]>("GET", "/activity"),
};
