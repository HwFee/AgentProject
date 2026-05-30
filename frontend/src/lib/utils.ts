import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
import type { AgentType, AgentConfig } from '@/types'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatDate(dateString: string): string {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

export function formatStatus(status: string): { label: string; color: string } {
  const map: Record<string, { label: string; color: string }> = {
    pending: { label: '等待中', color: 'bg-yellow-100 text-yellow-800' },
    planning: { label: '规划中', color: 'bg-blue-100 text-blue-800' },
    running: { label: '执行中', color: 'bg-indigo-100 text-indigo-800' },
    completed: { label: '已完成', color: 'bg-green-100 text-green-800' },
    failed: { label: '失败', color: 'bg-red-100 text-red-800' },
  }
  return map[status] || { label: status, color: 'bg-gray-100 text-gray-800' }
}

export const AGENT_CONFIG_MAP: Record<AgentType, AgentConfig> = {
  master: {
    type: 'master',
    name: '主Agent',
    icon: 'Bot',
    color: 'text-blue-600',
    borderColor: 'border-blue-400',
    bgColor: 'bg-blue-50',
  },
  researcher: {
    type: 'researcher',
    name: '研究员',
    icon: 'Search',
    color: 'text-green-600',
    borderColor: 'border-green-400',
    bgColor: 'bg-green-50',
  },
  analyst: {
    type: 'analyst',
    name: '分析师',
    icon: 'BarChart3',
    color: 'text-purple-600',
    borderColor: 'border-purple-400',
    bgColor: 'bg-purple-50',
  },
  writer: {
    type: 'writer',
    name: '撰写员',
    icon: 'FileText',
    color: 'text-orange-600',
    borderColor: 'border-orange-400',
    bgColor: 'bg-orange-50',
  },
  reviewer: {
    type: 'reviewer',
    name: '审核员',
    icon: 'Eye',
    color: 'text-pink-600',
    borderColor: 'border-pink-400',
    bgColor: 'bg-pink-50',
  },
}

export function getAgentConfig(type: AgentType): AgentConfig {
  return AGENT_CONFIG_MAP[type] || AGENT_CONFIG_MAP.master
}

export function getAgentTypeFromString(type: string): AgentType {
  const map: Record<string, AgentType> = {
    master: 'master',
    researcher: 'researcher',
    research: 'researcher',
    'research.collect': 'researcher',
    analyst: 'analyst',
    data: 'analyst',
    'data.analyze': 'analyst',
    writer: 'writer',
    write: 'writer',
    'writing.draft_report': 'writer',
    'writing.de_ai_polish': 'writer',
    reviewer: 'reviewer',
    review: 'reviewer',
    'review.quality_check': 'reviewer',
    'requirement.intake': 'master',
    'planning.outline': 'master',
    'export.report_files': 'writer',
  }
  return map[type] || 'master'
}
