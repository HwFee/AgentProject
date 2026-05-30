import { useQuery } from '@tanstack/react-query'
import { apiClient } from './client'
import type {
  ApiResponse,
  AdminStats,
  AdminTask,
  PaginatedResponse,
  ReportStats,
  ReportStatus,
  ReportTask,
  UserProfile,
} from '@/types'

// Keep existing but modified for pagination
export function useReports(
  page: number = 1,
  pageSize: number = 10,
  search?: string,
  status?: string
) {
  return useQuery({
    queryKey: ['reports', page, pageSize, search, status],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
      })
      if (search) params.append('search', search)
      if (status) params.append('status', status)
      const { data } = await apiClient.get<ApiResponse<PaginatedResponse<ReportTask>>>(
        `/api/reports?${params}`
      )
      return data.data
    },
    refetchInterval: 5000,
  })
}

// Keep existing
export function useReport(id: number | string | undefined) {
  return useQuery({
    queryKey: ['reports', id],
    queryFn: async () => {
      const { data } = await apiClient.get<ApiResponse<ReportTask>>(`/api/reports/${id}`)
      return data.data
    },
    enabled: !!id,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status === 'completed' || status === 'failed' ? false : 3000
    },
  })
}

// Keep existing
export function useReportStatus(taskId: number | string | undefined) {
  return useQuery({
    queryKey: ['report-status', taskId],
    queryFn: async () => {
      const { data } = await apiClient.get<ApiResponse<ReportStatus>>(
        `/api/reports/${taskId}/status`
      )
      return data.data
    },
    enabled: !!taskId,
    refetchInterval: (query) => {
      const status = query.state.data?.status
      return status === 'completed' || status === 'failed' ? false : 3000
    },
  })
}

// NEW hooks
export function useReportStats() {
  return useQuery({
    queryKey: ['reportStats'],
    queryFn: async () => {
      const { data } = await apiClient.get<ApiResponse<ReportStats>>('/api/reports/stats')
      return data.data
    },
  })
}

export function useUserProfile() {
  return useQuery({
    queryKey: ['userProfile'],
    queryFn: async () => {
      const { data } = await apiClient.get<ApiResponse<UserProfile>>('/api/user/profile')
      return data.data
    },
  })
}

export function useAdminStats() {
  return useQuery({
    queryKey: ['adminStats'],
    queryFn: async () => {
      const { data } = await apiClient.get<ApiResponse<AdminStats>>('/api/admin/stats')
      return data.data
    },
  })
}

export function useAdminTokenTrend(days: number = 7) {
  return useQuery({
    queryKey: ['adminTokenTrend', days],
    queryFn: async () => {
      const { data } = await apiClient.get<ApiResponse<{ data: Array<{ date: string; tokens: number }> }>>(
        `/api/admin/token-trend?days=${days}`
      )
      return data.data.data
    },
  })
}

export function useAdminTasks(
  page: number = 1,
  pageSize: number = 10,
  filters?: Record<string, string>
) {
  return useQuery({
    queryKey: ['adminTasks', page, pageSize, filters],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: String(page),
        page_size: String(pageSize),
      })
      if (filters) {
        Object.entries(filters).forEach(([k, v]) => {
          if (v) params.append(k, v)
        })
      }
      const { data } = await apiClient.get<ApiResponse<PaginatedResponse<AdminTask>>>(
        `/api/admin/tasks?${params}`
      )
      return data.data
    },
  })
}

export function useAdminUsers(page: number = 1, pageSize: number = 10) {
  return useQuery({
    queryKey: ['adminUsers', page, pageSize],
    queryFn: async () => {
      const { data } = await apiClient.get<
        ApiResponse<
          PaginatedResponse<{
            id: number
            username: string
            email: string
            role: string
            created_at: string
          }>
        >
      >(`/api/admin/users?page=${page}&page_size=${pageSize}`)
      return data.data
    },
  })
}

export function useReportArtifacts(taskId: number | string | undefined) {
  return useQuery({
    queryKey: ['report-artifacts', taskId],
    queryFn: async () => {
      const { data } = await apiClient.get<ApiResponse<any[]>>(
        `/api/reports/${taskId}/artifacts`
      )
      return data.data
    },
    enabled: !!taskId,
    refetchInterval: 3000,
  })
}

export function useArtifactVersions(taskId: number | string | undefined, artifactId: number | undefined) {
  return useQuery({
    queryKey: ['artifact-versions', taskId, artifactId],
    queryFn: async () => {
      const { data } = await apiClient.get<ApiResponse<any[]>>(
        `/api/reports/${taskId}/artifacts/${artifactId}/versions`
      )
      return data.data
    },
    enabled: !!taskId && !!artifactId,
  })
}

export function useToolEvents(taskId: number | string | undefined, stepId?: string) {
  return useQuery({
    queryKey: ['tool-events', taskId, stepId || 'all'],
    queryFn: async () => {
      const params = stepId ? `?step_id=${stepId}` : ''
      const { data } = await apiClient.get<ApiResponse<any[]>>(
        `/api/reports/${taskId}/tool-events${params}`
      )
      return data.data
    },
    enabled: !!taskId,
    refetchInterval: 3000,
  })
}
