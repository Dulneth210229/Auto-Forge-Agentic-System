export function Card({ children, className = "" }) {
  return (
    <section className={`surface rounded-2xl border border-main shadow-soft ${className}`}>
      {children}
    </section>
  );
}

export function CardHeader({ title, subtitle, action, className = "" }) {
  return (
    <div className={`border-b border-main px-5 py-4 ${className}`}>
      <div className="flex items-start justify-between gap-4">
        <div>
          {title && <h2 className="text-base font-bold text-main">{title}</h2>}
          {subtitle && <p className="mt-1 text-sm text-muted">{subtitle}</p>}
        </div>
        {action}
      </div>
    </div>
  );
}

export function CardBody({ children, className = "" }) {
  return <div className={`p-5 ${className}`}>{children}</div>;
}

export default Card;