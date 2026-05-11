import { Navigate, Route, Routes } from "react-router-dom";
import AppShell from "./layouts/AppShell.jsx";
import ProjectsHome from "./pages/ProjectsHome.jsx";
import NewProjectWizard from "./pages/NewProjectWizard.jsx";
import PipelineDashboard from "./pages/PipelineDashboard.jsx";
import ArtifactViewer from "./pages/ArtifactViewer.jsx";
import TraceabilityDashboard from "./pages/TraceabilityDashboard.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<AppShell />}>
        <Route index element={<Navigate to="/projects" replace />} />
        <Route path="/projects" element={<ProjectsHome />} />
        <Route path="/projects/new" element={<NewProjectWizard />} />
        <Route path="/pipeline/:stageId?" element={<PipelineDashboard />} />
        <Route path="/artifacts" element={<ArtifactViewer />} />
        <Route path="/traceability" element={<TraceabilityDashboard />} />
      </Route>
    </Routes>
  );
}