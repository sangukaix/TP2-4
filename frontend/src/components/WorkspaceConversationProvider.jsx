import { useRef, useState } from 'react'
import { WorkspaceConversationContext } from './workspaceConversationContext'

// 기본 화면과 전체보기는 같은 대화와 진행 중 요청을 공유합니다.
export function WorkspaceConversationProvider({ children }) {
  const [messages, setMessages] = useState([])
  const [question, setQuestion] = useState('')
  const [useWebSearch, setUseWebSearch] = useState(false)
  const [appliedPatch, setAppliedPatch] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const requestPending = useRef(false)
  const beginRequest = () => {
    if (requestPending.current) return false
    requestPending.current = true
    return true
  }
  const endRequest = () => { requestPending.current = false }
  return <WorkspaceConversationContext.Provider value={{ messages, setMessages, question, setQuestion, useWebSearch, setUseWebSearch, appliedPatch, setAppliedPatch, loading, setLoading, error, setError, beginRequest, endRequest }}>{children}</WorkspaceConversationContext.Provider>
}
