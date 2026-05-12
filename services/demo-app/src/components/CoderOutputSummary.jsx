import { useEffect, useMemo, useState } from "react";
import { autoForgeApi } from "../api/autoForgeApi";
import CodeFolderTree from "./CodeFolderTree";

/**
 * Gets the full code version folder.
 *
 * Example:
 * output_dir = outputs/runs/RUN-0001/code/v7/generated_app
 * version folder = outputs/runs/RUN-0001/code/v7
 *
 * This is important because the user wants to download the whole v7 output,
 * not only the generated_app folder.
 */
function getCodeVersionFolder(data) {
  if (!data) return "";

  if (data.run_id && data.code_version) {
    return `outputs/runs/${data.run_id}/code/${data.code_version}`;
  }

  if (data.output_dir) {
    return data.output_dir.replace(/[/\\]generated_app$/, "");
  }

  return "";
}

export default function CoderOutputSummary({ data, onReadArtifact }) {
  const [treeData, setTreeData] = useState(null);
  const [treeError, setTreeError] = useState("");

  const versionFolderPath = useMemo(() => {
    return getCodeVersionFolder(data);
  }, [data]);

  const downloadUrl = versionFolderPath
    ? autoForgeApi.getFolderDownloadUrl(versionFolderPath)
    : "";

  useEffect(() => {
    async function loadFolderTree() {
      if (!versionFolderPath) return;

      try {
        setTreeError("");
        setTreeData(null);

        const result = await autoForgeApi.getArtifactTree(versionFolderPath);
        setTreeData(result);
      } catch (err) {
        setTreeError(err.message);
      }
    }

    loadFolderTree();
  }, [versionFolderPath]);

  if (!data) {
    return null;
  }

  const {
    status,
    run_id,
    code_version,
    source_srs_version,
    manifest_path,
    output_dir,
    generated_file_count,
    input_artifacts,
    validation_warnings,
  } = data;

  const readmePath = output_dir ? `${output_dir}/README.md` : "";

  return (
    <div className="coder-summary">
      <h3>Coder Agent Summary</h3>

      <div className="summary-grid">
        <div className="summary-card">
          <span>Status</span>
          <strong>{status || "Unknown"}</strong>
        </div>

        <div className="summary-card">
          <span>Run ID</span>
          <strong>{run_id || "-"}</strong>
        </div>

        <div className="summary-card">
          <span>Code Version</span>
          <strong>{code_version || "-"}</strong>
        </div>

        <div className="summary-card">
          <span>SRS Version</span>
          <strong>{source_srs_version || "-"}</strong>
        </div>

        <div className="summary-card">
          <span>Generated Files</span>
          <strong>{generated_file_count ?? 0}</strong>
        </div>
      </div>

      {output_dir && (
        <div className="path-box">
          <span>Generated App Folder</span>
          <code>{output_dir}</code>
        </div>
      )}

      {versionFolderPath && (
        <div className="path-box">
          <span>Whole Code Version Folder</span>
          <code>{versionFolderPath}</code>
        </div>
      )}

      {treeError && (
        <div className="warning-box">
          <h4>Folder Structure Could Not Be Loaded</h4>
          <p>{treeError}</p>
        </div>
      )}

      <CodeFolderTree
        treeData={treeData}
        versionFolderPath={versionFolderPath}
        downloadUrl={downloadUrl}
        onReadArtifact={onReadArtifact}
      />

      {manifest_path && (
        <button
          type="button"
          className="preview-button"
          onClick={() => onReadArtifact?.(manifest_path)}
        >
          Preview CodeManifest
        </button>
      )}

      {readmePath && (
        <button
          type="button"
          className="preview-button secondary"
          onClick={() => onReadArtifact?.(readmePath)}
        >
          Preview Generated README
        </button>
      )}

      {input_artifacts && (
        <div className="mini-section">
          <h4>Input Artifacts Used</h4>
          <pre>{JSON.stringify(input_artifacts, null, 2)}</pre>
        </div>
      )}

      {validation_warnings?.length > 0 && (
        <div className="warning-box">
          <h4>Validation Warnings</h4>
          <ul>
            {validation_warnings.map((warning, index) => (
              <li key={index}>{warning}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}