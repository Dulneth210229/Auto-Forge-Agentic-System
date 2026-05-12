import { createBrowserRouter, RouterProvider } from "react-router-dom";
import DashboardLayout from "./layout/DashboardLayout";

import DashboardPage from "./pages/DashboardPage";
import RequirementAgentPage from "./pages/RequirementAgentPage";
import DomainAgentPage from "./pages/DomainAgentPage";
import ArchitectAgentPage from "./pages/ArchitectAgentPage";
import UIUXAgentPage from "./pages/UIUXAgentPage";
import CoderAgentPage from "./pages/CoderAgentPage";
import TestingAgentPage from "./pages/TestingAgentPage";
import SecurityAgentPage from "./pages/SecurityAgentPage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <DashboardLayout />,
    children: [
      {
        index: true,
        element: <DashboardPage />,
      },
      {
        path: "requirements",
        element: <RequirementAgentPage />,
      },
      {
        path: "domain",
        element: <DomainAgentPage />,
      },
      {
        path: "architecture",
        element: <ArchitectAgentPage />,
      },
      {
        path: "uiux",
        element: <UIUXAgentPage />,
      },
      {
        path: "coder",
        element: <CoderAgentPage />,
      },
      {
        path: "testing",
        element: <TestingAgentPage />,
      },
      {
        path: "security",
        element: <SecurityAgentPage />,
      },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}