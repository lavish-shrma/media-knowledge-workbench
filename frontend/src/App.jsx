import { Route, Routes } from "react-router-dom";
import WorkspacePage from "./pages/WorkspacePage";

export default function App() {
  void [Route, Routes, WorkspacePage];

  return (
    <Routes>
      <Route path="/" element={<WorkspacePage />} />
    </Routes>
  );
}
