import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/**
 * MarkdownPreview renders .md files like GitHub README pages.
 * It converts Markdown symbols such as #, -, *, tables, and code blocks
 * into readable formatted UI.
 */
export default function MarkdownPreview({ content }) {
  if (!content) {
    return null;
  }

  return (
    <div className="markdown-preview">
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{content}</ReactMarkdown>
    </div>
  );
}
