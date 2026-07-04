import { useState, useRef } from 'react'
import './InputBar.css'

export default function InputBar({ onSend, onUpload, ragMode, onToggleMode, disabled }) {
  const [text, setText] = useState('')
  const textareaRef = useRef(null)
  const fileRef = useRef(null)

  const handleSubmit = () => {
    const trimmed = text.trim()
    if (!trimmed || disabled) return
    onSend(trimmed)
    setText('')
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  const handleInput = (e) => {
    setText(e.target.value)
    const el = e.target
    el.style.height = 'auto'
    el.style.height = Math.min(el.scrollHeight, 150) + 'px'
  }

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      onUpload(Array.from(e.target.files))
      e.target.value = ''
    }
  }

  return (
    <footer className="input-bar">
      <div className="input-container">
        <div className="composer">
          <button
            className="icon-btn"
            onClick={() => fileRef.current?.click()}
            title="Upload documents"
          >
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"/>
            </svg>
          </button>
          <input
            ref={fileRef}
            type="file"
            multiple
            accept=".pdf,.docx,.md"
            onChange={handleFileChange}
            hidden
          />
          <textarea
            ref={textareaRef}
            className="text-input"
            value={text}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question…"
            rows={1}
            disabled={disabled}
          />
          <div className="composer-actions">
            <button
              className={`mode-btn ${ragMode ? 'active' : ''}`}
              onClick={onToggleMode}
              title={ragMode ? 'RAG mode: answers from documents' : 'Chat mode: direct AI conversation'}
            >
              {ragMode ? 'RAG' : 'Chat'}
            </button>
            <button
              className="send-btn"
              onClick={handleSubmit}
              disabled={disabled || !text.trim()}
              title="Send message"
            >
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <line x1="22" y1="2" x2="11" y2="13"/>
                <polygon points="22 2 15 22 11 13 2 9 22 2"/>
              </svg>
            </button>
          </div>
        </div>
        <div className="input-footer">
          <span className="hint-text">
            {ragMode ? 'RAG mode — answers grounded in your documents' : 'Chat mode — direct conversation with AI'}
          </span>
        </div>
      </div>
    </footer>
  )
}
