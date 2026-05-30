import { ArrowRight, Loader } from 'lucide-react'
import type { AgentType } from '@/types'
import { getAgentConfig } from '@/lib/utils'
import { AgentIcon } from '../AgentIcon'

interface SubAgentCallCardProps {
  targetAgent: AgentType
  task: string
  isRunning?: boolean
}

export function SubAgentCallCard({ targetAgent, task, isRunning }: SubAgentCallCardProps) {
  const config = getAgentConfig(targetAgent)

  return (
    <div className="flex items-start gap-2 rounded-xl border border-amber-100 bg-amber-50/30 px-3 py-2">
      <div className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border ${config.borderColor} ${config.bgColor}`}>
        <AgentIcon type={targetAgent} size={12} className={config.color} />
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-1.5 mb-1">
          <span className="text-xs font-medium text-amber-700">
            调用子Agent
          </span>
          <ArrowRight size={10} className="text-amber-400" />
          <span className={`text-xs font-semibold ${config.color}`}>
            {config.name}
          </span>
          {isRunning && (
            <Loader size={10} className="animate-spin text-amber-500 ml-1" />
          )}
        </div>
        <div className="font-mono text-xs text-amber-800/70 bg-amber-100/40 rounded px-2 py-1.5 truncate" title={task}>
          {task}
        </div>
      </div>
    </div>
  )
}
