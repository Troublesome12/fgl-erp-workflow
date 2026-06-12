import axios from "axios";

const TOKEN_KEY = "fgl_token";

export const apiClient = axios.create({
  baseURL: "/api",
  headers: { "Content-Type": "application/json" },
});

apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem("fgl_role");
      localStorage.removeItem("fgl_email");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  },
);

/**
 * Stores the authentication token, user role, and email in local storage.
 * @param token The JWT access token.
 * @param role The role of the authenticated user.
 * @param email The email of the authenticated user.
 */
export function setAuthToken(token: string, role: string, email: string): void {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem("fgl_role", role);
  localStorage.setItem("fgl_email", email);
}

/**
 * Clears all authentication-related data from local storage.
 */
export function clearAuth(): void {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem("fgl_role");
  localStorage.removeItem("fgl_email");
}

/**
 * Retrieves the stored user role from local storage.
 * @returns The user's role if found, otherwise null.
 */
export function getStoredRole(): string | null {
  return localStorage.getItem("fgl_role");
}

/**
 * Retrieves the stored user email from local storage.
 * @returns The user's email if found, otherwise null.
 */
export function getStoredEmail(): string | null {
  return localStorage.getItem("fgl_email");
}
