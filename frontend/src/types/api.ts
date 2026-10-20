export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface UserInfo {
  id: number
  email: string
  displayName: string
  role: string
}

export interface DatasetSource {
  id: number
  name: string
  dbType: string
}

export interface Dataset {
  id: number
  name: string
  description: string
  source: DatasetSource
}
