import './TypingIndicator.css'

export default function TypingIndicator() {
  return (
    <div className="message message-assistant">
      <div className="message-header">
        <span className="message-role">Assistant</span>
      </div>
      <div className="typing-bubble">
        <span />
        <span />
        <span />
      </div>
    </div>
  )
}
