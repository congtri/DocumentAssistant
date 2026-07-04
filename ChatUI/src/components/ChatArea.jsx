import { useEffect, useRef } from 'react'
import Message from './Message'
import TypingIndicator from './TypingIndicator'
import './ChatArea.css'

export default function ChatArea({ messages, isLoading, status }) {
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isLoading])

  const showNoDocsWarning = !status.loading && status.connected && !status.indexed

  if (messages.length === 0 && !isLoading) {
    return (
      <main className="chat-area">
        <div className="welcome">
          {showNoDocsWarning ? (
            <>
              <div className="welcome-icon warning-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
                  <line x1="12" y1="9" x2="12" y2="13"/>
                  <line x1="12" y1="17" x2="12.01" y2="17"/>
                </svg>
              </div>
              <h2>No documents indexed yet</h2>
              <p>
                Upload your documents to get started. Click the
                <strong> paperclip button (📎) </strong>
                below to upload PDF, DOCX, or Markdown files.
              </p>
              <div className="welcome-hints">
                <div className="hint warning-hint">⚠️ RAG mode won't work until you upload documents</div>
                <div className="hint">You can still use Chat mode for direct AI conversation</div>
                <div className="hint">Uploaded files are automatically indexed for search</div>
              </div>
            </>
          ) : (
            <>
              <div className="welcome-icon">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
              </div>
              <h2>Ask your documents anything</h2>
              <p>
                Upload PDFs, DOCX, or Markdown files and ask questions.
                <br />
                Your AI assistant will find answers from your documents.
              </p>
              <div className="welcome-hints">
                <div className="hint">Upload documents using the paperclip button</div>
                <div className="hint">Switch between RAG and Chat modes</div>
                <div className="hint">Press Enter to send, Shift+Enter for new line</div>
              </div>
            </>
          )}
        </div>
      </main>
    )
  }

  return (
    <main className="chat-area">
      <div className="messages">
        {messages.map((msg, i) => (
          <Message key={i} message={msg} />
        ))}
        {isLoading && <TypingIndicator />}
        <div ref={endRef} />
      </div>
    </main>
  )
}
