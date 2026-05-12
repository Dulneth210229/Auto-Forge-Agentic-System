function formatFileSize(size = 0) {
  if (size < 1024) return `${size} B`;
  if (size < 1024 * 1024) return `${(size / 1024).toFixed(1)} KB`;
  return `${(size / (1024 * 1024)).toFixed(1)} MB`;
}

function TreeNode({ node, level = 0, onReadArtifact }) {
  const isFolder = node.type === "folder";

  return (
    <div className="tree-node">
      <div
        className={isFolder ? "tree-row folder" : "tree-row file"}
        style={{ paddingLeft: `${level * 18 + 10}px` }}
      >
        <span className="tree-icon">{isFolder ? "📁" : "📄"}</span>

        <button
          type="button"
          className="tree-name"
          onClick={() => {
            if (!isFolder) {
              onReadArtifact?.(node.path);
            }
          }}
          title={node.path}
        >
          {node.name}
        </button>

        {!isFolder && (
          <span className="tree-size">{formatFileSize(node.size)}</span>
        )}
      </div>

      {isFolder &&
        node.children?.map((child) => (
          <TreeNode
            key={child.path}
            node={child}
            level={level + 1}
            onReadArtifact={onReadArtifact}
          />
        ))}
    </div>
  );
}

export default function CodeFolderTree({
  treeData,
  versionFolderPath,
  downloadUrl,
  onReadArtifact,
}) {
  if (!treeData) {
    return null;
  }

  return (
    <div className="code-folder-tree">
      <div className="folder-tree-header">
        <div>
          <h3>Generated Code Folder Structure</h3>
          <p>{versionFolderPath}</p>
        </div>

        {downloadUrl && (
          <a className="download-code-btn" href={downloadUrl}>
            Download This Code Version
          </a>
        )}
      </div>

      <div className="tree-root">
        <div className="tree-root-name">📦 {treeData.root_name}</div>

        {treeData.tree?.map((node) => (
          <TreeNode
            key={node.path}
            node={node}
            onReadArtifact={onReadArtifact}
          />
        ))}
      </div>
    </div>
  );
}