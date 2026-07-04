import './Header.css'

export default function Header({ status, onClear, models, currentModel, onModelSwitch }) {
  const getStatusText = () => {
    if (status.loading) return 'Connecting…'
    if (!status.connected) return 'Offline'
    return status.indexed ? 'Ready' : 'Ready · no docs'
  }

  const getStatusClass = () => {
    if (status.loading) return 'status-badge'
    if (!status.connected) return 'status-badge bad'
    return 'status-badge ok'
  }

  return (
    <header className="header">
      <div className="header-left">
        <a
          className="llama-btn"
          href="http://127.0.0.1:8081"
          target="_blank"
          rel="noopener noreferrer"
          title="Open Llama.cpp Web UI"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
            <line x1="8" y1="21" x2="16" y2="21"/>
            <line x1="12" y1="17" x2="12" y2="21"/>
          </svg>
          <span>Llama.cpp</span>
        </a>
        <svg className="header-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
          <polyline points="14 2 14 8 20 8"/>
          <line x1="16" y1="13" x2="8" y2="13"/>
          <line x1="16" y1="17" x2="8" y2="17"/>
        </svg>
        <h1 className="header-title">DocumentAssistant</h1>
      </div>
      <div className="header-right">
        {models && models.length > 0 && (
          <select
            className="model-select"
            value={currentModel}
            onChange={(e) => onModelSwitch(e.target.value)}
            title="Select model"
          >
            {models.map((m) => (
              <option key={m.path} value={m.path}>
                {m.name} ({m.size_mb} MB)
              </option>
            ))}
          </select>
        )}
        <button className="clear-btn" onClick={onClear} title="Clear conversation">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="3 6 5 6 21 6"/>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
          </svg>
        </button>
        <span className={getStatusClass()}>{getStatusText()}</span>
      </div>
    </header>
  )
}
