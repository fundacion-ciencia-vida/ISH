import type {
  BootstrapData,
  ContentBundle,
  DraftHistoryItem,
  LocalAuthStatus,
  MediaItem,
  PublishedHistoryItem,
  WorkspaceStatus,
} from "./types";

const parameters = new URLSearchParams(window.location.search);
const parameter = parameters.get("setup") ?? parameters.get("session");
if (parameter) {
  window.sessionStorage.setItem("ish-editor-setup", parameter);
  window.history.replaceState({}, "", window.location.pathname);
}

const legacySetup = window.sessionStorage.getItem("ish-editor-session") ?? "";
if (legacySetup && !window.sessionStorage.getItem("ish-editor-setup")) {
  window.sessionStorage.setItem("ish-editor-setup", legacySetup);
}
window.sessionStorage.removeItem("ish-editor-session");
const setupToken = window.sessionStorage.getItem("ish-editor-setup") ?? "";

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const headers = new Headers(init.headers);
  if (init.body && !(init.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  const response = await fetch(path, { ...init, headers, credentials: "same-origin" });
  if (!response.ok) {
    let message = `Error ${response.status}`;
    try {
      const payload = (await response.json()) as { detail?: string };
      message = payload.detail || message;
    } catch {
      message = response.statusText || message;
    }
    if (response.status === 401 && !path.startsWith("/api/auth/")) {
      window.dispatchEvent(new Event("ish-auth-expired"));
    }
    throw new Error(message);
  }
  return (await response.json()) as T;
}

export const api = {
  authStatus: () => request<LocalAuthStatus>("/api/auth/status", { headers: setupToken ? { "X-ISH-Setup": setupToken } : {} }),
  setupLocalAuth: async (username: string, password: string) => {
    const result = await request<{ authenticated: boolean }>("/api/auth/setup", {
      method: "POST",
      headers: setupToken ? { "X-ISH-Setup": setupToken } : {},
      body: JSON.stringify({ username, password }),
    });
    window.sessionStorage.removeItem("ish-editor-setup");
    return result;
  },
  loginLocal: (username: string, password: string) =>
    request<{ authenticated: boolean }>("/api/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    }),
  changeLocalPassword: (currentPassword: string, newPassword: string) =>
    request<{ authenticated: boolean }>("/api/auth/password", {
      method: "POST",
      body: JSON.stringify({ current_password: currentPassword, new_password: newPassword }),
    }),
  logoutLocal: () => request<{ authenticated: boolean }>("/api/auth/logout", { method: "POST" }),
  bootstrap: () => request<BootstrapData>("/api/bootstrap"),
  content: () =>
    request<{ bundle: ContentBundle; saved_at: string; base_commit: string; workspace: WorkspaceStatus }>(
      "/api/content",
    ),
  saveDraft: (bundle: ContentBundle, snapshot = false) =>
    request<{ saved_at: string; base_commit: string }>("/api/draft", {
      method: "PUT",
      body: JSON.stringify({ bundle, snapshot }),
    }),
  preview: (bundle: ContentBundle) =>
    request<{ pages: Record<string, string>; output: string }>("/api/preview", {
      method: "POST",
      body: JSON.stringify({ bundle, snapshot: false }),
    }),
  saveToken: (token: string) =>
    request<{ configured: boolean; persistent: boolean }>("/api/token", {
      method: "POST",
      body: JSON.stringify({ token }),
    }),
  clone: (destination: string) =>
    request<WorkspaceStatus>("/api/clone", {
      method: "POST",
      body: JSON.stringify({ destination }),
    }),
  sync: () => request<{ head: string; updated: boolean }>("/api/git/sync", { method: "POST" }),
  publish: (bundle: ContentBundle, message: string) =>
    request<{ published: boolean; message: string; commit: string }>("/api/publish", {
      method: "POST",
      body: JSON.stringify({ bundle, message }),
    }),
  media: () => request<MediaItem[]>("/api/media"),
  uploadMedia: async (file: File, kind: "image" | "document") => {
    const body = new FormData();
    body.append("file", file);
    return request<MediaItem>(`/api/media?kind=${kind}`, { method: "POST", body });
  },
  deleteMedia: (path: string) =>
    request<{ deleted: boolean }>(`/api/media/${path.split("/").map(encodeURIComponent).join("/")}`, {
      method: "DELETE",
    }),
  restoreMedia: (path: string) =>
    request<{ restored: boolean }>("/api/media/restore", {
      method: "POST",
      body: JSON.stringify({ identifier: path }),
    }),
  draftHistory: () => request<DraftHistoryItem[]>("/api/drafts/history"),
  restoreDraft: (identifier: string) =>
    request<{ bundle: ContentBundle }>("/api/drafts/restore", {
      method: "POST",
      body: JSON.stringify({ identifier }),
    }),
  publishedHistory: () => request<PublishedHistoryItem[]>("/api/history"),
  restorePublished: (identifier: string) =>
    request<{ bundle: ContentBundle }>("/api/history/restore", {
      method: "POST",
      body: JSON.stringify({ identifier }),
    }),
};
