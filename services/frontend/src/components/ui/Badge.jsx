const styles = {
  default: "bg-slate-100 text-slate-700 border-slate-200",
  success: "bg-green-50 text-green-700 border-green-200",
  warning: "bg-amber-50 text-amber-700 border-amber-200",
  danger: "bg-red-50 text-red-700 border-red-200",
  info: "bg-indigo-50 text-indigo-700 border-indigo-200"
};

export default function Badge({ children, variant = "default", className = "" }) {
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-1 text-xs font-semibold ${
        styles[variant] || styles.default
      } ${className}`}
    >
      {children}
    </span>
  );
}