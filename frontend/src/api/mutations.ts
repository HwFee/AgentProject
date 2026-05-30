import { useMutation, useQueryClient } from '@tanstack/react-query'
import { apiClient } from './client'
import type { ApiResponse, ReportGenerateResponse, ReportMode, LoginRequest, RegisterRequest, User } from '@/types'

// --- Existing mutations (keep as-is) ---
export function useCreateReport() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (payload: {
      title: string
      requirement: string
      mode: ReportMode
      files: File[]
    }) => {
      const formData = new FormData()
      formData.append('title', payload.title)
      formData.append('requirement', payload.requirement)
      formData.append('mode', payload.mode)
      payload.files.forEach((file) => {
        formData.append('files', file)
      })
      const { data } = await apiClient.post<ApiResponse<ReportGenerateResponse>>(
        '/api/reports/generate',
        formData,
        { headers: { 'Content-Type': 'multipart/form-data' } }
      )
      return data.data
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
    },
  })
}

export function useDeleteReport() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/api/reports/${id}`)
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['reports'] })
    },
  })
}

export function useLogin() {
  return useMutation({
    mutationFn: async (payload: LoginRequest) => {
      const { data } = await apiClient.post<ApiResponse<{ user: User; access_token: string }>>('/api/user/login', payload)
      return data.data
    },
  })
}

export function useRegister() {
  return useMutation({
    mutationFn: async (payload: RegisterRequest) => {
      const { data } = await apiClient.post<ApiResponse<{ id: number; username: string }>>('/api/user/register', payload)
      return data.data
    },
  })
}

export function useStopReport() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (id: number) => {
      const { data } = await apiClient.post<ApiResponse<{ status: string }>>(`/api/reports/${id}/stop`)
      return data.data
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['reports', id] })
      queryClient.invalidateQueries({ queryKey: ['report-status', id] })
    },
  })
}

// --- NEW mutations ---
export function useUpdateProfile() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (data: { username: string; email: string }) => {
      const res = await apiClient.put('/api/user/profile', data)
      return res.data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['userProfile'] }),
  })
}

export function useUpdatePassword() {
  return useMutation({
    mutationFn: async (data: { old_password: string; new_password: string; confirm_password: string }) => {
      const res = await apiClient.put('/api/user/password', data)
      return res.data
    },
  })
}

export function useAdminStopTask() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (taskId: number) => {
      const res = await apiClient.post(`/api/admin/tasks/${taskId}/stop`)
      return res.data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['adminTasks'] }),
  })
}

export function useAdminDeleteTask() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (taskId: number) => {
      const res = await apiClient.delete(`/api/admin/tasks/${taskId}`)
      return res.data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['adminTasks'] }),
  })
}

export function useAdminUpdateUserRole() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ userId, role }: { userId: number; role: string }) => {
      const res = await apiClient.put(`/api/admin/users/${userId}/role?role=${role}`)
      return res.data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['adminUsers'] }),
  })
}

export function useAdminDeleteUser() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async (userId: number) => {
      const res = await apiClient.delete(`/api/admin/users/${userId}`)
      return res.data
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ['adminUsers'] }),
  })
}

export function useChatEdit() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ taskId, message, targetStepId, targetArtifactId }: {
      taskId: number
      message: string
      targetStepId?: string
      targetArtifactId?: number
    }) => {
      const { data } = await apiClient.post<ApiResponse<any>>(
        `/api/reports/${taskId}/chat`,
        { message, target_step_id: targetStepId, target_artifact_id: targetArtifactId }
      )
      return data.data
    },
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['reports', vars.taskId] })
      qc.invalidateQueries({ queryKey: ['report-status', vars.taskId] })
      qc.invalidateQueries({ queryKey: ['report-artifacts', vars.taskId] })
    },
  })
}

export function useRerunStep() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ taskId, stepId }: { taskId: number; stepId: string }) => {
      const { data } = await apiClient.post<ApiResponse<any>>(
        `/api/reports/${taskId}/rerun/${stepId}`
      )
      return data.data
    },
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['reports', vars.taskId] })
      qc.invalidateQueries({ queryKey: ['report-status', vars.taskId] })
      qc.invalidateQueries({ queryKey: ['report-artifacts', vars.taskId] })
    },
  })
}

export function useRestoreVersion() {
  const qc = useQueryClient()
  return useMutation({
    mutationFn: async ({ taskId, artifactId, versionId }: {
      taskId: number
      artifactId: number
      versionId: number
    }) => {
      const { data } = await apiClient.post<ApiResponse<any>>(
        `/api/reports/${taskId}/artifacts/${artifactId}/restore`,
        { version_id: versionId }
      )
      return data.data
    },
    onSuccess: (_, vars) => {
      qc.invalidateQueries({ queryKey: ['report-artifacts', vars.taskId] })
      qc.invalidateQueries({ queryKey: ['artifact-versions', vars.taskId, vars.artifactId] })
      qc.invalidateQueries({ queryKey: ['reports', vars.taskId] })
    },
  })
}
