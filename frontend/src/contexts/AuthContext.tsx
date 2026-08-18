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

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<authApi.UserOut | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem(TOKEN_KEY));

  const applyAuth = (resp: authApi.TokenResponse) => {
    localStorage.setItem(TOKEN_KEY, resp.access_token);
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
