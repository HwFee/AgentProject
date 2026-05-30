import { AgentIcon } from '../AgentIcon'
import type { AgentType } from '@/types'
import { getAgentConfig } from '@/lib/utils'

interface AgentMessageProps {
  agentType: AgentType
  content: string
  timestamp?: string
}

function stripMarkdownFences(content: string): string {
  return content
    .replace(/^```markdown\s*\n?/i, '')
    .replace(/\n?```\s*$/i, '')
    .trim()
}

export function AgentMessage({ agentType, content, timestamp }: AgentMessageProps) {
  const config = getAgentConfig(agentType)
  const cleanContent = stripMarkdownFences(content)

  return (
    <div className="flex gap-3">
      <div className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full border ${config.borderColor} ${config.bgColor}`}>
        <AgentIcon type={agentType} size={14} className={config.color} />
      </div>
      <div className="flex-1">
        <div className="mb-1 flex items-center gap-2">
          <span className="text-xs font-semibold text-gray-700">{config.name}</span>
          {timestamp && (
            <span className="text-xs text-gray-400">
              {new Date(timestamp).toLocaleTimeString()}
            </span>
          )}
        </div>
        <div className="rounded-xl rounded-tl-sm bg-gray-50 px-4 py-2.5 text-sm text-gray-800 whitespace-pre-wrap">
          {cleanContent}
        </div>
      </div>
    </div>
  )
}
