import { AgentIcon } from './AgentIcon'
import type { AgentState, ReportTask } from '@/types'
import { getAgentConfig, formatDate } from '@/lib/utils'
import { CheckCircle, Loader, Clock } from 'lucide-react'

interface ProjectSidebarProps {
  title: string
  report?: ReportTask
  masterAgent: AgentState
  subAgents: AgentState[]
  currentView: 'master' | string
  onViewChange: (view: 'master' | string) => void
}

function StatusDot({ status }: { status: string }) {
  switch (status) {
    case 'completed':
      return <CheckCircle size={12} className="text-green-500" />
    case 'running':
      return <Loader size={12} className="animate-spin text-blue-500" />
    case 'failed':
      return <CheckCircle size={12} className="text-red-500" />
    default:
      return <Clock size={12} className="text-gray-300" />
  }
}

function AgentNavItem({
  agent,
  isActive,
  onClick,
}: {
  agent: AgentState
  isActive: boolean
  onClick: () => void
}) {
  const config = getAgentConfig(agent.type)

  return (
    <button
      onClick={onClick}
      className={`flex w-full items-center gap-2 rounded-md px-2 py-1.5 text-left text-xs transition-colors ${
        isActive
          ? 'bg-blue-50 text-blue-700'
          : 'text-gray-600 hover:bg-gray-50'
      }`}
    >
      <div className={`w-1 h-4 rounded-full ${isActive ? 'bg-blue-400' : config.borderColor.replace('border', 'bg')}`} />
      <AgentIcon type={agent.type} size={12} className={isActive ? 'text-blue-600' : config.color} />
      <span className="flex-1 truncate">{config.name}</span>
      {agent.nodeCount && agent.nodeCount > 1 ? (
        <span className="flex-shrink-0 text-[10px] px-1.5 py-0 rounded-full bg-gray-100 text-gray-500">
          {agent.nodeCount}
        </span>
      ) : null}
      <StatusDot status={agent.status} />
    </button>
  )
}

export function ProjectSidebar({
  title,
  report,
  masterAgent,
  subAgents,
  currentView,
  onViewChange,
}: ProjectSidebarProps) {
  return (
    <div className="flex h-full flex-col border-r border-gray-200 bg-gray-50/50">
      <div className="border-b border-gray-200 p-3">
        <div className="rounded-md bg-blue-50 px-3 py-2 text-sm font-medium text-blue-800 border-l-2 border-blue-400">
          {title}
        </div>
      </div>

      {/* Report Info */}
      {report && (
        <div className="border-b border-gray-200 p-3">
          <div className="mb-2 text-xs font-medium text-gray-400">报告信息</div>
          <div className="space-y-1.5 text-xs">
            <div className="flex justify-between">
              <span className="text-gray-500">状态</span>
              <span className={`rounded px-1.5 py-0.5 text-[10px] font-medium ${
                report.status === 'completed' ? 'bg-green-100 text-green-700' :
                report.status === 'running' || report.status === 'planning' ? 'bg-blue-100 text-blue-700' :
                report.status === 'failed' ? 'bg-red-100 text-red-700' :
                'bg-yellow-100 text-yellow-700'
              }`}>
                {report.status === 'completed' ? '已完成' :
                 report.status === 'running' ? '进行中' :
                 report.status === 'planning' ? '规划中' :
                 report.status === 'failed' ? '失败' : '等待中'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">创建时间</span>
              <span className="text-gray-700">{formatDate(report.created_at)}</span>
            </div>
            {report.updated_at !== report.created_at && (
              <div className="flex justify-between">
                <span className="text-gray-500">更新时间</span>
                <span className="text-gray-700">{formatDate(report.updated_at)}</span>
              </div>
            )}
            <div className="flex justify-between">
              <span className="text-gray-500">生成模式</span>
              <span className="text-gray-700">
                {report.mode === 'generate' ? '从零生成' :
                 report.mode === 'template' ? '基于模板' :
                 report.mode === 'reference' ? '参考资料' :
                 report.mode === 'edit' ? '自由修改' : report.mode || '参考型'}
              </span>
            </div>
          </div>
        </div>
      )}

      <div className="flex-1 overflow-y-auto p-2">
        <div className="mb-1 px-2 text-xs font-medium text-gray-400">Agent 列表</div>

        <AgentNavItem
          agent={masterAgent}
          isActive={currentView === 'master'}
          onClick={() => onViewChange('master')}
        />

        {subAgents.map((agent) => (
          <div key={agent.id} className="ml-2 mt-0.5">
            <AgentNavItem
              agent={agent}
              isActive={currentView === agent.id}
              onClick={() => onViewChange(agent.id)}
            />
          </div>
        ))}
      </div>
    </div>
  )
}
