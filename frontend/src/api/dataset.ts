import { get } from './http'
import type { ApiResponse, Dataset } from '@/types/api'

export function listDatasets() {
  return get<ApiResponse<Dataset[]>>('/datasets')
}
