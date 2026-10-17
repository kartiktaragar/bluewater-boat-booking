import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { api } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(Boolean(localStorage.getItem("bluewater_token")));

  useEffect(() => {
    if (!localStorage.getItem("bluewater_token")) {
      setLoading(false);
      return;
    }
    api("/auth/me")
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("bluewater_token");
        setUser(null);
      })
      .finally(() => setLoading(false));
  }, []);

  async function authenticate(endpoint, payload) {
    const result = await api(`/auth/${endpoint}`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    localStorage.setItem("bluewater_token", result.access_token);
    setUser(result.user);
    return result.user;
  }

  function logout() {
    localStorage.removeItem("bluewater_token");
    setUser(null);
  }

  const value = useMemo(
    () => ({
      user,
      loading,
      signup: (payload) => authenticate("signup", payload),
      login: (payload) => authenticate("login", payload),
      logout,
    }),
    [user, loading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used within AuthProvider");
  return value;
}
