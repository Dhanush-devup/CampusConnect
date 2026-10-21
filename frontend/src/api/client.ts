/**
 * Centralized API Client with JWT Bearer Token Handling and Automatic Error Parsing.
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export class ApiError extends Error {
  status: number;
  data: any;

  constructor(status: number, message: string, data?: any) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.data = data;
  }
}

export async function apiRequest<T = any>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem("campus_connect_token");
  const headers = new Headers(options.headers || {});

  // Do not set Content-Type for FormData; browser sets boundary automatically
  if (!(options.body instanceof FormData) && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const url = endpoint.startsWith("http") ? endpoint : `${API_BASE_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    // Session expired or invalid
    localStorage.removeItem("campus_connect_token");
    localStorage.removeItem("campus_connect_user");
    window.dispatchEvent(new Event("auth:logout"));
  }

  if (!response.ok) {
    let errorDetail = "An unexpected error occurred.";
    let errorData = null;
    try {
      errorData = await response.json();
      if (typeof errorData.detail === "string") {
        errorDetail = errorData.detail;
      } else if (Array.isArray(errorData.detail)) {
        // Pydantic validation error list
        errorDetail = errorData.detail
          .map((err: any) => `${err.loc ? err.loc.slice(1).join(".") + ": " : ""}${err.msg}`)
          .join(" | ");
      }
    } catch {
      errorDetail = response.statusText || errorDetail;
    }
    throw new ApiError(response.status, errorDetail, errorData);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

/**
 * Downloads a binary file (e.g., student resume PDF) with Bearer token authentication.
 */
export async function downloadFile(endpoint: string, filename: string): Promise<void> {
  const token = localStorage.getItem("campus_connect_token");
  const headers: HeadersInit = {};
  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const url = endpoint.startsWith("http") ? endpoint : `${API_BASE_URL}${endpoint}`;
  const response = await fetch(url, { headers });

  if (!response.ok) {
    let msg = "Failed to download file.";
    try {
      const err = await response.json();
      msg = err.detail || msg;
    } catch {}
    throw new ApiError(response.status, msg);
  }

  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = downloadUrl;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  window.URL.revokeObjectURL(downloadUrl);
}
