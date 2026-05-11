import { SendHorizonal } from "lucide-react";
import Button from "../ui/Button.jsx";
import Textarea from "../ui/Textarea.jsx";
import Input from "../ui/Input.jsx";

export default function ChatRevisionBox({
  currentVersion,
  newVersion,
  changeRequest,
  onCurrentVersionChange,
  onNewVersionChange,
  onChangeRequestChange,
  onSubmit,
  loading = false
}) {
  return (
    <div className="rounded-2xl border border-main surface p-5 shadow-soft">
      <h3 className="text-base font-bold text-main">Revision Chat</h3>
      <p className="mt-1 text-sm text-muted">
        Ask the agent to revise the current artifact. The old version will be preserved.
      </p>

      <div className="mt-4 grid gap-4 md:grid-cols-2">
        <Input
          label="Current Version"
          value={currentVersion}
          onChange={(event) => onCurrentVersionChange(event.target.value)}
          placeholder="v1"
        />
        <Input
          label="New Version"
          value={newVersion}
          onChange={(event) => onNewVersionChange(event.target.value)}
          placeholder="v2"
        />
      </div>

      <div className="mt-4">
        <Textarea
          label="Change Request"
          value={changeRequest}
          onChange={(event) => onChangeRequestChange(event.target.value)}
          placeholder="Example: Add product search by name, category, and price range."
        />
      </div>

      <div className="mt-4 flex justify-end">
        <Button onClick={onSubmit} disabled={loading}>
          <SendHorizonal className="h-4 w-4" />
          {loading ? "Revising..." : "Submit Revision"}
        </Button>
      </div>
    </div>
  );
}