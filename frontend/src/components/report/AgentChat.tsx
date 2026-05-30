import { useRef, useEffect } from 'react'
import type { AgentState } from '@/types'
import { AgentIcon } from './AgentIcon'
import { ChatInput } from './ChatInput'
import { UserMessage } from './messages/UserMessage'
import { AgentMessage } from './messages/AgentMessage'
import { ThinkingCard } from './messages/ThinkingCard'
import { ToolCallCard } from './messages/ToolCallCard'
import { SubAgentCallCard } from './messages/SubAgentCallCard'
import { ExecutionPending } from './messages/ExecutionPending'
import { ResultCard } from './messages/ResultCard'
import { ErrorCard } from './messages/ErrorCard'
import { getAgentConfig } from '@/lib/utils'

interface AgentChatProps {
  agent: AgentState
  onSendMessage: (message: string) => void
  onStop?: () => void
  isRunning?: boolean
}

export function AgentChat({ agent, onSendMessage, onStop, isRunning }: AgentChatProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const config = getAgentConfig(agent.type)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [agent.messages])

  return (
    <div className="flex h-full flex-col bg-white">
      {/* Header */}
      <div className="flex items-center gap-2 border-b border-gray-100 px-4 py-3">
        <div className={`flex h-8 w-8 items-center justify-center rounded-full border ${config.borderColor} ${config.bgColor}`}>
          <AgentIcon type={agent.type} size={14} className={config.color} />
        </div>
        <div>
          <span className="text-sm font-semibold text-gray-800">{config.name}</span>
          {agent.type === 'master' && (
            <span className="ml-2 text-xs text-gray-400">协调者</span>
          )}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
        {agent.messages.map((msg) => {
          switch (msg.type) {
            case 'user':
              return <UserMessage key={msg.id} content={msg.content || ''} timestamp={msg.timestamp} />
            case 'agent':
              return (
                <AgentMessage
                  key={msg.id}
                  agentType={msg.agentType || agent.type}
                  content={msg.content || ''}
                  timestamp={msg.timestamp}
                />
              )
            case 'thinking':
              return (
                <ThinkingCard
                  key={msg.id}
                  content={msg.content || ''}
                  agentName={config.name}
                />
              )
            case 'tool_call':
              return (
                <ToolCallCard
                  key={msg.id}
                  toolName={msg.toolName || 'unknown'}
                  params={msg.toolParams || {}}
                  agentName={config.name}
                />
              )
            case 'subagent_call':
              return (
                <SubAgentCallCard
                  key={msg.id}
                  targetAgent={msg.targetAgent || 'researcher'}
                  task={msg.task || ''}
                />
              )
            case 'execution_pending':
              return <ExecutionPending key={msg.id} agentName={config.name} />
            case 'result':
              return (
                <ResultCard
                  key={msg.id}
                  fromAgent={msg.agentType || 'researcher'}
                  summary={msg.summary || ''}
                  details={msg.details}
                  status={msg.status}
                />
              )
            case 'error':
              return <ErrorCard key={msg.id} message={msg.content || ''} agentName={config.name} />
            default:
              return null
          }
        })}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-100 px-4 py-3">
        <ChatInput
          onSend={onSendMessage}
          onStop={onStop}
          isRunning={isRunning}
          disabled={isRunning}
        />
      </div>
    </div>
  )
}
