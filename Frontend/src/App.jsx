import { BrowserRouter, Routes, Route } from "react-router-dom";
import Login from "./pages/Login.jsx";
import InClassNotes from "./pages/InClassNotes.jsx";
import Revision from "./pages/Revision.jsx";


export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/notes" element={<InClassNotes />} />
        <Route path="/learn" element={<Revision />} />
      </Routes>
    </BrowserRouter>
  );
}
