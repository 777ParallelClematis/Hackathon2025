import { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(null);

  // On page reload, restore token
  useEffect(() => {
    const stored = localStorage.getItem("token");
    if (stored) {
      setToken(stored);
      setIsAuthenticated(true);
    }
  }, []);

  function login(jwtToken, userId) {
    localStorage.setItem("token", jwtToken);
    localStorage.setItem("_id", userId);   
    setToken(jwtToken);
    setIsAuthenticated(true);
  }
  

  function logout() {
    localStorage.removeItem("token");
    setToken(null);
    setIsAuthenticated(false);
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
