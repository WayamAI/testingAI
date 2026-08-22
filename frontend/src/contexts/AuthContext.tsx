import { createContext, useContext, useState, type ReactNode } from "react";
import { TOKEN_KEY } from "../services/api/client";
import * as authApi from "../services/api/auth";

interface AuthState {
  user: authApi.UserOut | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  demoLogin: () => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export const USER_KEY = "wayam_user";

/**
 * Reads the persisted session (token + user) from localStorage. A stored
 * token is only trusted if its paired user object is present and parses
 * cleanly — otherwise both keys are cleared and the session is treated as
 * logged out, rather than leaving the app authenticated with `user: null`.
 */
function readStoredSession(): { token: string | null; user: authApi.UserOut | null } {
  const token = localStorage.getItem(TOKEN_KEY);
  const rawUser = localStorage.getItem(USER_KEY);
  if (!token || !rawUser) {
    if (token || rawUser) {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    }
    return { token: null, user: null };
  }
  try {
    return { token, user: JSON.parse(rawUser) as authApi.UserOut };
  } catch {
    // Corrupted stored user — treat as logged out rather than crashing.
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_KEY);
    return { token: null, user: null };
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<authApi.UserOut | null>(() => readStoredSession().user);
  const [token, setToken] = useState<string | null>(() => readStoredSession().token);

  const applyAuth = (resp: authApi.TokenResponse) => {
    localStorage.setItem(TOKEN_KEY, resp.access_token);
    localStorage.setItem(USER_KEY, JSON.stringify(resp.user));
    setToken(resp.access_token);
    setUser(resp.user);
  };

  const value: AuthState = {
    user,
    token,
    login: async (email, password) => applyAuth(await authApi.login(email, password)),
    demoLogin: async () => applyAuth(await authApi.demoLogin()),
    logout: () => {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      setToken(null);
      setUser(null);
    },
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
