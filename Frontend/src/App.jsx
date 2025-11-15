import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  Outlet,
} from "react-router-dom";

import Login from "./pages/Login.jsx";
import InClassNotes from "./pages/InClassNotes.jsx";
import Revision from "./pages/Revision.jsx";
import Notebook from "./pages/Notebook.jsx";
import Register from "./pages/Register.jsx";
import Navbar from "./components/Navbar.jsx";
import { useAuth } from "./hooks/useAuth.jsx";
//import "./global.css";

// Layout ONLY for authenticated pages
function AuthedLayout() {
  return (
    <>
      <Navbar />
      <Outlet />
    </>
  );
}

// Protect internal pages
function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>

        {/* PUBLIC PAGES (no navbar) */}
        <Route path="/" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* AUTHENTICATED LAYOUT (navbar visible) */}
        <Route
          element={
            <ProtectedRoute>
              <AuthedLayout />
            </ProtectedRoute>
          }
        >
          <Route path="/notes" element={<InClassNotes />} />
          <Route path="/learn" element={<Revision />} />
          <Route path="/notebook" element={<Notebook />} />
        </Route>

      </Routes>
    </BrowserRouter>
  );
}
