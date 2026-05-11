import { Card, CardBody, CardHeader } from "../components/ui/Card.jsx";
import Badge from "../components/ui/Badge.jsx";

export default function TraceabilityDashboard() {
  return (
    <Card>
      <CardHeader
        title="Traceability Dashboard"
        subtitle="REQ → API → UI → CODE → TEST traceability view."
      />
      <CardBody>
        <div className="grid gap-4 md:grid-cols-4">
          <div className="rounded-2xl border border-main p-4">
            <Badge variant="info">REQ</Badge>
            <p className="mt-3 text-2xl font-extrabold text-main">0</p>
            <p className="text-sm text-muted">Requirements tracked</p>
          </div>

          <div className="rounded-2xl border border-main p-4">
            <Badge variant="info">API</Badge>
            <p className="mt-3 text-2xl font-extrabold text-main">0</p>
            <p className="text-sm text-muted">API links</p>
          </div>

          <div className="rounded-2xl border border-main p-4">
            <Badge variant="info">UI</Badge>
            <p className="mt-3 text-2xl font-extrabold text-main">0</p>
            <p className="text-sm text-muted">UI screen links</p>
          </div>

          <div className="rounded-2xl border border-main p-4">
            <Badge variant="info">TEST</Badge>
            <p className="mt-3 text-2xl font-extrabold text-main">0</p>
            <p className="text-sm text-muted">Test links</p>
          </div>
        </div>

        <p className="mt-5 text-sm leading-6 text-muted">
          This page is common for all agents. Later, once backend traceability output is ready,
          we will connect this dashboard to generated artifact metadata.
        </p>
      </CardBody>
    </Card>
  );
}