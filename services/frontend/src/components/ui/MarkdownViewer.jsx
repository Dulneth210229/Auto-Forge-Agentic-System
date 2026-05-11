import ReactMarkdown from "react-markdown";

export default function MarkdownViewer({ content, emptyMessage = "No Markdown output yet." }) {
  if (!content) {
    return (
      <div className="rounded-xl border border-dashed border-main p-6 text-center text-sm text-muted">
        {emptyMessage}
      </div>
    );
  }

  return (
    <article className="prose prose-slate max-w-none rounded-xl border border-main surface p-5">
      <ReactMarkdown>{content}</ReactMarkdown>
    </article>
  );
}