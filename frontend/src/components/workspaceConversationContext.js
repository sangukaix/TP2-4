import { createContext, useContext } from 'react'

export const WorkspaceConversationContext = createContext(null)
export function useWorkspaceConversation() {
  return useContext(WorkspaceConversationContext)
}
