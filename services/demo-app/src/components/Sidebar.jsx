import { NavLink } from "react-router-dom";

const navItems = [
  {
    path: "/",
    label: "Dashboard",
    description: "System overview",
    icon: "⌂",
  },
  {
    path: "/requirements",
    label: "Requirement Agent",
    description: "Generate and revise SRS",
    icon: "R",
  },
  {
    path: "/domain",
    label: "Domain Agent",
    description: "E-commerce rules pack",
    icon: "D",
  },
  {
    path: "/architecture",
    label: "Architect Agent",
    description: "SDS, API, database, diagrams",
    icon: "A",
  },
  {
    path: "/uiux",
    label: "UI/UX Agent",
    description: "Flows and wireframes",
    icon: "U",
  },
  {
    path: "/coder",
    label: "Coder Agent",
    description: "Generate runnable code",
    icon: "C",
  },
  {
    path: "/testing",
    label: "Testing / QA Agent",
    description: "Generate and run tests",
    icon: "Q",
  },
  {
    path: "/security",
    label: "Security Agent",
    description: "Scan generated code",
    icon: "S",
  },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand-block">
        <div className="brand-mark">AF</div>
        <div>
          <h1>AutoForge</h1>
          <p>Agentic SDLC Dashboard</p>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            end={item.path === "/"}
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            <span className="nav-icon">{item.icon}</span>
            <span>
              <strong>{item.label}</strong>
              <small>{item.description}</small>
            </span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <p>Pipeline</p>
        <strong>Requirements → Prototype → QA → Security</strong>
      </div>
    </aside>
  );
}