import { get, post } from './http'
import type { ApiResponse, Conversation, QueryRunResult } from '@/types/api'

export function createConversation(datasetId: number) {
  return post<ApiResponse<Conversation>>('/conversations', { datasetId })
}

export function getConversation(id: number) {
  return get<ApiResponse<Conversation>>(`/conversations/${id}`)
}

export function ask(id: number, content: string) {
  return post<ApiResponse<QueryRunResult>>(`/conversations/${id}/messages`, { content })
}
