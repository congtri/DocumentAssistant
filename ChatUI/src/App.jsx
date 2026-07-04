import { useState, useEffect } from 'react'
import Header from './components/Header'
import ChatArea from './components/ChatArea'
import InputBar from './components/InputBar'
import { checkHealth, sendQuery, sendChat, uploadFiles } from './api/client'

export default function App() {
  const [messages, setMessages] = useState([])
  const [status, setStatus] = useState({ connected: false, indexed: false, loading: true })
  const [ragMode, setRagMode] = useState(true)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    const check = async () => {
      const result = await checkHealth()
      setStatus(result)
    }
    check()
    const interval = setInterval(check, 30000)
    return () => clearInterval(interval)
  }, [])

  const handleSend = async (text) => {
    const userMsg = { role: 'user', content: text }
    setMessages((prev) => [...prev, userMsg])
    setIsLoading(true)

    try {
      const history = messages.map(({ role, content }) => ({ role, content }))
      let response

      if (ragMode) {
        response = await sendQuery(text, history)
        const assistantMsg = {
          role: 'assistant',
          content: response.answer,
          sources: response.sources,
        }
        setMessages((prev) => [...prev, assistantMsg])
      } else {
        response = await sendChat(text, history)
        const assistantMsg = { role: 'assistant', content: response.answer }
        setMessages((prev) => [...prev, assistantMsg])
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Error: ${err.message}`, error: true },
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleUpload = async (files) => {
    try {
      const result = await uploadFiles(files)
      const sysMsg = {
        role: 'system',
        content: `Uploaded and indexed ${result.chunks_indexed} chunks from ${result.filenames.join(', ')}`,
      }
      setMessages((prev) => [...prev, sysMsg])
      const healthResult = await checkHealth()
      setStatus(healthResult)
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'system', content: `Upload failed: ${err.message}`, error: true },
      ])
    }
  }

  const handleClear = () => setMessages([])

  return (
    <div className="app">
      <Header status={status} onClear={handleClear} />
      <ChatArea messages={messages} isLoading={isLoading} status={status} />
      <InputBar
        onSend={handleSend}
        onUpload={handleUpload}
        ragMode={ragMode}
        onToggleMode={() => setRagMode(!ragMode)}
        disabled={isLoading}
      />
    </div>
  )
}
