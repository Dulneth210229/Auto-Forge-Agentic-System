import { useMemo, useState } from "react";
import { DEFAULT_RUN_ID } from "../constants/samplePayloads.js";
import { ProjectContext } from "./ProjectContextValue.js";

export function ProjectProvider({ children }) {
  const [runId, setRunId] = useState(DEFAULT_RUN_ID);
  const [activeStageId, setActiveStageId] = useState("requirements");
  const [artifactPaths, setArtifactPaths] = useState([]);
  const [latestOutputs, setLatestOutputs] = useState({});

  function registerArtifacts(paths = []) {
    const validPaths = paths.filter(Boolean);

    setArtifactPaths((current) => {
      const merged = [...current, ...validPaths];
      return Array.from(new Set(merged));
    });
  }

  function saveStageOutput(stageId, output) {
    setLatestOutputs((current) => ({
      ...current,
      [stageId]: output
    }));

    const paths = [
      output?.json_path,
      output?.markdown_path,
      output?.report_path,
      output?.openapi_path,
      output?.sds_path,
      output?.designpack_path,
      output?.code_manifest_path
    ];

    registerArtifacts(paths);
  }

  const value = useMemo(
    () => ({
      runId,
      setRunId,
      activeStageId,
      setActiveStageId,
      artifactPaths,
      registerArtifacts,
      latestOutputs,
      saveStageOutput
    }),
    [runId, activeStageId, artifactPaths, latestOutputs]
  );

  return <ProjectContext.Provider value={value}>{children}</ProjectContext.Provider>;
}