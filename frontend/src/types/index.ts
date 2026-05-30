export interface User {
  id: number
  username: string
  email: string
  is_admin: boolean
}

export type ReportMode = 'generate' | 'template' | 'reference' | 'edit'

export interface Attachment {
  id: number
  filename: string
  file_type: string
  status: 'pending' | 'parsing' | 'parsed' | 'failed'
  parsed_length?: number
}

export interface AgentNodeStatus {
  node_id: string
  agent_type: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  started_at?: string
  completed_at?: string
  input_data?: Record<string, unknown>
  output_data?: {
    content?: string
    sources?: { link: string; title: string }[]
    [key: string]: unknown
  }
}

export interface ReportStatus {
  id: number
  status: string
  mode: ReportMode
  progress?: {
    current_step: string
    total_steps: number
    completed_steps: number
  }
  nodes: AgentNodeStatus[]
  attachments: Attachment[]
}

export interface ReportGenerateResponse {
  task_id: number
  status: string
  message: string
}

export interface ReportTask {
  id: number
  user_id: number
  title: string
  requirement: string
  status: 'pending' | 'planning' | 'running' | 'completed' | 'failed'
  mode?: ReportMode
  dag_plan?: Record<string, unknown>
  model_routing?: string
  final_report_md?: string
  pdf_path?: string
  docx_path?: string
  error_msg?: string
  created_at: string
  updated_at: string
}

export interface AgentNode {
  id: number
  task_id: number
  node_id: string
  agent_type: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  input_data?: Record<string, unknown>
  output_data?: Record<string, unknown>
  retry_count: number
  created_at: string
  updated_at: string
}

export interface ApiResponse<T> {
  status_code: number
  message: string
  data: T
}

export interface LoginRequest {
  username: string
  password: string
}

export interface RegisterRequest {
  username: string
  email: string
  password: string
}

export interface ReportGenerateRequest {
  title: string
  requirement: string
}

export type AgentType = 'master' | 'researcher' | 'analyst' | 'writer' | 'reviewer'

export interface AgentConfig {
  type: AgentType
  name: string
  icon: string // Lucide icon name
  color: string // Tailwind color class
  borderColor: string
  bgColor: string
}

export type MessageType =
  | 'user'
  | 'agent'
  | 'thinking'
  | 'tool_call'
  | 'subagent_call'
  | 'execution_pending'
  | 'result'
  | 'error'

export interface ChatMessage {
  id: string
  type: MessageType
  agentId?: string
  agentType?: AgentType
  content?: string
  toolName?: string
  toolParams?: Record<string, unknown>
  toolResult?: string
  targetAgent?: AgentType
  task?: string
  summary?: string
  details?: string
  status?: 'completed' | 'failed'
  timestamp: string
}

export interface AgentState {
  id: string
  type: AgentType
  name: string
  status: 'idle' | 'running' | 'completed' | 'failed'
  messages: ChatMessage[]
  nodeCount?: number
}

export interface ReportSession {
  id: number
  title: string
  status: string
  masterAgent: AgentState
  subAgents: AgentState[]
  currentView: 'master' | string
  reportMarkdown: string
  pdfUrl?: string
  docxUrl?: string
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ReportStats {
  total: number
  completed: number
  running: number
  failed: number
}

export interface UserProfile {
  id: number
  username: string
  email: string
  role: string
  created_at: string
}

export interface AdminStats {
  total_users: number
  total_reports: number
  today_reports: number
  running_tasks: number
  failed_tasks: number
  avg_duration: string
  pending_failures: number
  total_tokens: number
  trends: Record<string, number>
}

export interface AdminTask {
  id: number
  title: string
  username: string
  status: string
  mode: string
  created_at: string
  updated_at: string
  error_msg?: string
}
