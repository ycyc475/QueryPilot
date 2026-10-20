import axios from 'axios'
import { ElMessage } from 'element-plus'
import { TOKEN_KEY } from '@/utils/constants'

const http = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY)
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    const msg: string = error.response?.data?.message ?? '请求失败'
    const isLoginRequest = error.config?.url?.includes('/auth/login')
    if (status === 401 && !isLoginRequest) {
      localStorage.removeItem(TOKEN_KEY)
      ElMessage.error(msg || '登录已过期，请重新登录')
      window.location.href = '/login'
    } else {
      ElMessage.error(msg)
    }
    return Promise.reject(error)
  },
)

export async function get<T>(url: string, params?: Record<string, unknown>): Promise<T> {
  return (await http.get(url, { params })) as unknown as T
}

export async function post<T>(url: string, data?: unknown): Promise<T> {
  return (await http.post(url, data)) as unknown as T
}

export default http
