export default function Textarea({ label, error, className = "", ...props }) {
  return (
    <label className="block">
      {label && <span className="mb-1.5 block text-sm font-semibold text-main">{label}</span>}
      <textarea
        className={`min-h-[120px] w-full resize-y rounded-xl border border-main surface px-3 py-2.5 text-sm text-main outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100 ${className}`}
        {...props}
      />
      {error && <span className="mt-1 block text-xs font-medium text-red-600">{error}</span>}
    </label>
  );
}