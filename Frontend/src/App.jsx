import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  useLocation,
} from "react-router-dom";

import Login from "./pages/Login.jsx";
import InClassNotes from "./pages/InClassNotes.jsx";
import Revision from "./pages/Revision.jsx";
import Notebook from "./pages/Notebook.jsx";
import Register from "./pages/Register.jsx";
import Navbar from "./components/Navbar.jsx";
import { useAuth } from "./hooks/useAuth.jsx";

// Wraps internal pages + decides if navbar should show
function Layout({ children }) {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  const shouldShowNavbar = isAuthenticated && location.pathname !== "/";

  return (
    <>
      {shouldShowNavbar && <Navbar />}
      {children}
    </>
  );
}

// Block unauthenticated access
function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/" replace />;
}

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          {/* Public login page */}
          <Route path="/" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Auth-protected pages */}
          <Route
            path="/notes"
            element={
              <ProtectedRoute>
                <InClassNotes />
              </ProtectedRoute>
            }
          />

          <Route
            path="/learn"
            element={
              <ProtectedRoute>
                <Revision />
              </ProtectedRoute>
            }
          />

          <Route
            path="/notebook"
            element={
              <ProtectedRoute>
                <Notebook />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
