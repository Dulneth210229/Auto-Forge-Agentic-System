export default function FormSection({ title, description, children }) {
    return (
      <section className="form-section">
        <div className="form-section-header">
          <h2>{title}</h2>
          {description && <p>{description}</p>}
        </div>
  
        <div className="form-section-body">{children}</div>
      </section>
    );
  }