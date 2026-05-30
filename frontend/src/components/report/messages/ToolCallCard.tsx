import { useState } from 'react'
import {
  Terminal, Search, FileText, Edit3, Globe, BarChart3,
  ChevronDown, ChevronRight, Loader
} from 'lucide-react'

interface ToolCallCardProps {
  toolName: string
  params: Record<string, unknown>
  agentName?: string
  isRunning?: boolean
}

// Tool icon mapping — learned from OpenChamber's toolPresentation.tsx
function getToolIcon(toolName: string) {
  const t = toolName.toLowerCase()
  if (t.includes('search') || t.includes('grep') || t.includes('find')) {
    return <Search size={14} className="text-gray-500" />
  }
  if (t.includes('read') || t.includes('view') || t.includes('file')) {
    return <FileText size={14} className="text-gray-500" />
  }
  if (t.includes('edit') || t.includes('write') || t.includes('patch')) {
    return <Edit3 size={14} className="text-gray-500" />
  }
  if (t.includes('web') || t.includes('fetch') || t.includes('curl')) {
    return <Globe size={14} className="text-gray-500" />
  }
  if (t.includes('analysis') || t.includes('data') || t.includes('compute')) {
    return <BarChart3 size={14} className="text-gray-500" />
  }
  return <Terminal size={14} className="text-gray-500" />
}

function getToolDescription(toolName: string, params: Record<string, unknown>): string {
  const t = toolName.toLowerCase()

  if (t.includes('web_search')) {
    return `搜索: "${params.query || '...'}"`
  }
  if (t.includes('arxiv')) {
    return `arXiv: "${params.query || '...'}"`
  }
  if (t.includes('file_read') || t.includes('read_file')) {
    return `读取: ${params.path || params.filename || '...'}`
  }
  if (t.includes('write') || t.includes('create')) {
    return `写入: ${params.path || params.filename || '...'}`
  }
  if (t.includes('edit') || t.includes('patch')) {
    return `编辑: ${params.path || params.filename || '...'}`
  }
  if (t.includes('bash') || t.includes('shell')) {
    const cmd = String(params.command || '').split('\n')[0]
    return cmd.substring(0, 60)
  }
  if (t.includes('analysis') || t.includes('data')) {
    return `分析: ${params.analysis_type || params.type || '...'}`
  }

  // Fallback: show first param
  const entries = Object.entries(params).slice(0, 2)
  const parts = entries.map(([_k, v]) => {
    const s = String(v).slice(0, 30)
    return s.length > 30 ? s + '...' : s
  })
  return parts.join(' · ') || toolName
}

export function ToolCallCard({ toolName, params, isRunning }: ToolCallCardProps) {
  const [expanded, setExpanded] = useState(false)
  const description = getToolDescription(toolName, params)
  const icon = getToolIcon(toolName)

  return (
    <div className="group/tool">
      {/* Compact tool row — learned from OpenChamber ToolPart */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-1.5 rounded-xl px-1 py-1.5 text-left cursor-pointer hover:bg-gray-50 transition-colors"
        aria-expanded={expanded}
      >
        <div className="relative h-3.5 w-3.5 flex-shrink-0">
          <div
            className={`absolute inset-0 transition-opacity ${expanded ? 'opacity-0' : 'opacity-100 group-hover/tool:opacity-0'}`}
          >
            {isRunning ? (
              <Loader size={14} className="animate-spin text-blue-500" />
            ) : (
              icon
            )}
          </div>
          <div
            className={`absolute inset-0 flex items-center justify-center transition-opacity ${expanded ? 'opacity-100' : 'opacity-0 group-hover/tool:opacity-100'}`}
          >
            {expanded ? (
              <ChevronDown size={14} className="text-gray-400" />
            ) : (
              <ChevronRight size={14} className="text-gray-400" />
            )}
          </div>
        </div>

        <span className="text-xs font-medium text-gray-600 flex-shrink-0">
          {toolName}
        </span>

        <div className="flex items-center gap-1 flex-1 min-w-0">
          <span className="min-w-0 truncate text-xs text-gray-400" title={description}>
            {description}
          </span>
        </div>
      </button>

      {/* Expanded content */}
      {expanded && (
        <div className="relative ml-2 pl-3 pb-2 pt-1">
          <span
            aria-hidden="true"
            className="pointer-events-none absolute left-0 top-0 bottom-0 w-px bg-gray-200"
          />
          <pre className="overflow-auto rounded-md bg-gray-100 p-2 text-xs text-gray-600 max-h-60">
            {JSON.stringify(params, null, 2)}
          </pre>
        </div>
      )}
    </div>
  )
}
