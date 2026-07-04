import { useMemo } from 'react'
import './Message.css'

function renderMarkdown(text) {
  if (!text) return ''

  // Strip <think>...</think> blocks (model reasoning)
  let cleaned = text.replace(/<think>[\s\S]*?<\/think>/g, '').trim()
  if (!cleaned) return ''

  let html = cleaned
    // Escape HTML
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')

  // Code blocks (```...```)
  html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => {
    return `<pre><code class="lang-${lang}">${code.trim()}</code></pre>`
  })

  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code>$1</code>')

  // Headers
  html = html.replace(/^#### (.+)$/gm, '<h4>$1</h4>')
  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>')
  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>')
  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>')

  // Bold and italic
  html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>')
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>')

  // Blockquotes
  html = html.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>')

  // Unordered lists
  html = html.replace(/^[-*] (.+)$/gm, '<li>$1</li>')
  html = html.replace(/((?:<li>.*<\/li>\n?)+)/g, '<ul>$1</ul>')

  // Ordered lists
  html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>')

  // Horizontal rules
  html = html.replace(/^---+$/gm, '<hr/>')

  // Links
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')

  // Line breaks: double newline = paragraph break, single = <br>
  html = html.replace(/\n\n/g, '</p><p>')
  html = html.replace(/\n/g, '<br/>')

  // Wrap in paragraph if not starting with block element
  if (!html.match(/^<(h[1-6]|pre|ul|ol|blockquote|hr)/)) {
    html = `<p>${html}</p>`
  }

  return html
}

export default function Message({ message }) {
  const { role, content, sources, error } = message
  const roleLabel = role === 'user' ? 'You' : role === 'system' ? 'System' : 'Assistant'

  const renderedHtml = useMemo(() => {
    if (role === 'user') return null
    return renderMarkdown(content)
  }, [content, role])

  return (
    <div className={`message message-${role} ${error ? 'message-error' : ''}`}>
      <div className="message-header">
        <span className="message-role">{roleLabel}</span>
      </div>
      <div className="message-content markdown-body">
        {role === 'user' ? (
          <p>{content}</p>
        ) : (
          <div dangerouslySetInnerHTML={{ __html: renderedHtml }} />
        )}
      </div>
      {sources && sources.length > 0 && (
        <div className="message-sources">
          <div className="sources-title">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
            </svg>
            Sources
          </div>
          {sources.map((s, i) => (
            <div key={i} className="source-item">
              <span className="source-name">{s.source}</span>
              {s.page != null && <span className="source-page">p.{s.page}</span>}
              {s.score != null && <span className="source-score">{(s.score * 100).toFixed(0)}%</span>}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
