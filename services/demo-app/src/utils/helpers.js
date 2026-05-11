/**
 * Converts multi-line textarea text into an array.
 * Empty lines are removed.
 */
export function linesToArray(value) {
    return value
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean);
  }
  
  /**
   * Extracts possible artifact paths from nested backend response objects.
   * This helps the frontend show generated file paths clearly.
   */
  export function extractArtifactPaths(data) {
    const paths = [];
  
    function walk(value) {
      if (!value) return;
  
      if (typeof value === "string") {
        const looksLikeArtifact =
          value.includes("outputs/") ||
          value.includes("outputs\\") ||
          value.endsWith(".json") ||
          value.endsWith(".md") ||
          value.endsWith(".yaml") ||
          value.endsWith(".yml") ||
          value.endsWith(".html") ||
          value.endsWith(".png") ||
          value.endsWith(".mmd");
  
        if (looksLikeArtifact) {
          paths.push(value);
        }
  
        return;
      }
  
      if (Array.isArray(value)) {
        value.forEach(walk);
        return;
      }
  
      if (typeof value === "object") {
        Object.values(value).forEach(walk);
      }
    }
  
    walk(data);
  
    return [...new Set(paths)];
  }
  
  /**
   * Creates a readable status label.
   */
  export function normalizeStatus(value) {
    if (!value) return "Not started";
    return String(value).replaceAll("_", " ");
  }