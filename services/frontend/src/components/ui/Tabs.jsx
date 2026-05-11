export default function Tabs({ tabs, activeTab, onChange }) {
  return (
    <div className="flex flex-wrap gap-2 border-b border-main">
      {tabs.map((tab) => {
        const isActive = tab.id === activeTab;

        return (
          <button
            key={tab.id}
            type="button"
            onClick={() => onChange(tab.id)}
            className={`rounded-t-xl px-4 py-2.5 text-sm font-semibold transition ${
              isActive
                ? "bg-indigo-50 text-indigo-700"
                : "text-muted hover:bg-slate-100 hover:text-main"
            }`}
          >
            {tab.label}
          </button>
        );
      })}
    </div>
  );
}