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

export interface Message {
  id: number
  role: string
  content: string
  createdAt: string | null
}

export interface Conversation {
  id: number
  datasetId: number
  messages: Message[]
  createdAt: string | null
}

export interface ColumnInfo {
  name: string
  type: string
}

export interface ChartSpec {
  type: string
  x_field?: string
  y_field?: string
}

export interface QueryRunResult {
  runId: number
  sql: string
  columns: ColumnInfo[]
  rows: unknown[][]
  rowCount: number
  chart: ChartSpec
  summary: string
  durationMs: number
}
