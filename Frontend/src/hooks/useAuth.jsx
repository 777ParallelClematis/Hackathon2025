import { createContext, useContext, useState, useEffect, useRef } from "react";

const AuthContext = createContext();

// Inactivity timeout in ms (30 minutes)
const IDLE_TIMEOUT = 30 * 60 * 1000;

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [token, setToken] = useState(null);

  // Track last activity timestamp
  const lastActivity = useRef(Date.now());
  const inactivityTimer = useRef(null);

  // --------------------------------------------------
  // Restore token on page reload
  // --------------------------------------------------
  useEffect(() => {
    const stored = localStorage.getItem("token");
    if (stored) {
      setToken(stored);
      setIsAuthenticated(true);
      lastActivity.current = Date.now();
      startInactivityWatcher();
    }
  }, []);

  // --------------------------------------------------
  // Logout
  // --------------------------------------------------
  function logout() {
    localStorage.removeItem("token");
    setToken(null);
    setIsAuthenticated(false);
    stopInactivityWatcher();
  }

  // --------------------------------------------------
  // Login
  // --------------------------------------------------
  function login(jwtToken, userId) {
    localStorage.setItem("token", jwtToken);
    localStorage.setItem("student_id", userId);  // <-- ADD THIS
    setToken(jwtToken);
    setIsAuthenticated(true);
    lastActivity.current = Date.now();
    startInactivityWatcher();
  }
  

  // --------------------------------------------------
  // Inactivity watcher
  // --------------------------------------------------
  function startInactivityWatcher() {
    stopInactivityWatcher(); // ensure clean

    // Timer that checks once per minute
    inactivityTimer.current = setInterval(() => {
      const now = Date.now();
      if (now - lastActivity.current > IDLE_TIMEOUT) {
        console.warn("User logged out due to inactivity.");
        logout();
      }
    }, 60 * 1000);
  }

  function stopInactivityWatcher() {
    if (inactivityTimer.current) {
      clearInterval(inactivityTimer.current);
      inactivityTimer.current = null;
    }
  }

  // --------------------------------------------------
  // User activity listeners (reset idle timer)
  // --------------------------------------------------
  useEffect(() => {
    const resetTimer = () => {
      lastActivity.current = Date.now();
    };

    const events = ["mousemove", "keydown", "click", "scroll", "touchstart"];

    events.forEach((evt) => window.addEventListener(evt, resetTimer));

    return () => {
      events.forEach((evt) => window.removeEventListener(evt, resetTimer));
    };
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, token, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
