import { Bot, Search, BarChart3, FileText, Eye } from 'lucide-react'
import type { AgentType } from '@/types'
import { getAgentConfig } from '@/lib/utils'

const ICON_MAP = {
  Bot,
  Search,
  BarChart3,
  FileText,
  Eye,
}

interface AgentIconProps {
  type: AgentType
  size?: number
  className?: string
}

export function AgentIcon({ type, size = 16, className }: AgentIconProps) {
  const config = getAgentConfig(type)
  const IconComponent = ICON_MAP[config.icon as keyof typeof ICON_MAP]

  if (!IconComponent) {
    return <Bot size={size} className={className} />
  }

  return <IconComponent size={size} className={className} />
}
