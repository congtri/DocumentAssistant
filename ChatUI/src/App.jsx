import { useState, useEffect, useRef } from 'react'
import Header from './components/Header'
import ChatArea from './components/ChatArea'
import InputBar from './components/InputBar'
import { checkHealth, sendQuery, sendChat, uploadFiles, getProcessingStatus, getModels, switchModel } from './api/client'

export default function App() {
  const [messages, setMessages] = useState([])
  const [status, setStatus] = useState({ connected: false, indexed: false, loading: true })
  const [ragMode, setRagMode] = useState(true)
  const [isLoading, setIsLoading] = useState(false)
  const [processing, setProcessing] = useState({ active: false, status: '', progress: 0 })
  const [models, setModels] = useState([])
  const [currentModel, setCurrentModel] = useState('')
  const pollRef = useRef(null)

  useEffect(() => {
    const check = async () => {
      const result = await checkHealth()
      setStatus(result)
    }
    check()
    const interval = setInterval(check, 30000)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    getModels().then((data) => {
      setModels(data.models || [])
      setCurrentModel(data.current || '')
    }).catch(() => {})
  }, [])

  const pollProcessing = () => {
    if (pollRef.current) return
    pollRef.current = setInterval(async () => {
      const state = await getProcessingStatus()
      setProcessing(state)
      if (!state.active) {
        clearInterval(pollRef.current)
        pollRef.current = null
      }
    }, 1000)
  }

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
    setProcessing({ active: true, status: 'Uploading...', progress: 5 })
    pollProcessing()
    try {
      const result = await uploadFiles(files)
      setProcessing({ active: false, status: '', progress: 0 })
      const sysMsg = {
        role: 'system',
        content: `Uploaded and indexed ${result.chunks_indexed} chunks from ${result.filenames.join(', ')}`,
      }
      setMessages((prev) => [...prev, sysMsg])
      const healthResult = await checkHealth()
      setStatus(healthResult)
    } catch (err) {
      setProcessing({ active: false, status: '', progress: 0 })
      setMessages((prev) => [
        ...prev,
        { role: 'system', content: `Upload failed: ${err.message}`, error: true },
      ])
    }
  }

  const handleModelSwitch = async (modelPath) => {
    try {
      const result = await switchModel(modelPath)
      setCurrentModel(modelPath)
      setMessages((prev) => [
        ...prev,
        { role: 'system', content: result.message },
      ])
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'system', content: `Model switch failed: ${err.message}`, error: true },
      ])
    }
  }

  const handleClear = () => setMessages([])

  return (
    <div className="app">
      <Header
        status={status}
        onClear={handleClear}
        models={models}
        currentModel={currentModel}
        onModelSwitch={handleModelSwitch}
      />
      {processing.active && (
        <div className="processing-banner">
          <div className="processing-text">{processing.status}</div>
          <div className="processing-bar">
            <div className="processing-fill" style={{ width: `${processing.progress}%` }} />
          </div>
        </div>
      )}
      <ChatArea messages={messages} isLoading={isLoading} status={status} />
      <InputBar
        onSend={handleSend}
        onUpload={handleUpload}
        ragMode={ragMode}
        onToggleMode={() => setRagMode(!ragMode)}
        disabled={isLoading || processing.active}
      />
    </div>
  )
}
