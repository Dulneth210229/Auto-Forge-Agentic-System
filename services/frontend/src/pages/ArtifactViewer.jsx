import ArtifactList from "../components/shared/ArtifactList.jsx";
import { Card, CardBody, CardHeader } from "../components/ui/Card.jsx";
import { useProject } from "../context/useProject.js";

export default function ArtifactViewer() {
  const { artifactPaths } = useProject();

  return (
    <Card>
      <CardHeader
        title="Artifact Viewer"
        subtitle="Generated JSON, Markdown, reports, design packs, and code manifests."
      />
      <CardBody>
        <ArtifactList artifacts={artifactPaths} />
      </CardBody>
    </Card>
  );
}