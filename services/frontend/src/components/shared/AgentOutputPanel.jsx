import { useState } from "react";
import Tabs from "../ui/Tabs.jsx";
import JsonViewer from "../ui/JsonViewer.jsx";
import MarkdownViewer from "../ui/MarkdownViewer.jsx";

const outputTabs = [
  { id: "json", label: "JSON Output" },
  { id: "markdown", label: "Markdown Output" }
];

export default function AgentOutputPanel({ jsonData, markdownContent }) {
  const [activeTab, setActiveTab] = useState("json");

  return (
    <div className="rounded-2xl border border-main surface shadow-soft">
      <div className="px-5 pt-4">
        <Tabs tabs={outputTabs} activeTab={activeTab} onChange={setActiveTab} />
      </div>

      <div className="p-5">
        {activeTab === "json" ? (
          <JsonViewer data={jsonData} />
        ) : (
          <MarkdownViewer content={markdownContent} />
        )}
      </div>
    </div>
  );
}