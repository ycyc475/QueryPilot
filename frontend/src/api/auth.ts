import { get, post } from './http'
import type { ApiResponse, UserInfo } from '@/types/api'

export interface LoginResult {
  token: string
  user: UserInfo
}

export function login(email: string, password: string) {
  return post<ApiResponse<LoginResult>>('/auth/login', { email, password })
}

export function fetchMe() {
  return get<ApiResponse<UserInfo>>('/auth/me')
}
