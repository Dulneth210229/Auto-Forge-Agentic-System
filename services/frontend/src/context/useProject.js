import { useContext } from "react";
import { ProjectContext } from "./ProjectContextValue.js";

export function useProject() {
  const context = useContext(ProjectContext);

  if (!context) {
    throw new Error("useProject must be used inside ProjectProvider");
  }

  return context;
}