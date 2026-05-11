export default function PageHeader({ badge, title, description, outputs }) {
    return (
      <div className="page-header">
        <div>
          {badge && <span className="page-badge">{badge}</span>}
          <h1>{title}</h1>
          <p>{description}</p>
        </div>
  
        {outputs?.length > 0 && (
          <div className="output-mini-card">
            <span>Expected Outputs</span>
            <ul>
              {outputs.map((item) => (
                <li key={item}>{item}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    );
  }