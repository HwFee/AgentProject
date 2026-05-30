import { useState, useMemo } from 'react'
import { Brain, ChevronDown, ChevronRight } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

interface ThinkingCardProps {
  content: string
  agentName?: string
}

const SUMMARY_MAX_CHARS = 80

function stripMarkdown(text: string): string {
  return text
    .replace(/```[\w]*\n?([\s\S]*?)```/g, (_, inner: string) => inner.trim())
    .replace(/`([^`]+)`/g, '$1')
    .replace(/\*{1,3}([^*]+)\*{1,3}/g, '$1')
    .replace(/^#{1,6}\s+/gm, '')
    .replace(/\[([^\]]+)\]\([^)]*\)/g, '$1')
    .replace(/^>\s?/gm, '')
    .trim()
}

function getSummary(text: string): string {
  const flat = stripMarkdown(text).replace(/\s+/g, ' ').trim()
  if (flat.length <= SUMMARY_MAX_CHARS) return flat
  const cut = flat.lastIndexOf(' ', SUMMARY_MAX_CHARS)
  const end = cut > 0 ? cut : SUMMARY_MAX_CHARS
  return `${flat.substring(0, end).trimEnd()}...`
}

export function ThinkingCard({ content, agentName = 'Agent' }: ThinkingCardProps) {
  const [expanded, setExpanded] = useState(false)

  const summary = useMemo(() => getSummary(content), [content])

  return (
    <div className="group/thinking">
      <button
        onClick={() => setExpanded(!expanded)}
        className="flex w-full items-center gap-1.5 rounded-xl px-1 py-1.5 text-left cursor-pointer hover:bg-gray-50 transition-colors"
        aria-expanded={expanded}
      >
        <div className="relative h-3.5 w-3.5 flex-shrink-0">
          <div
            className={`absolute inset-0 transition-opacity ${expanded ? 'opacity-0' : 'opacity-100 group-hover/thinking:opacity-0'}`}
          >
            <Brain size={14} className="text-gray-400" />
          </div>
          <div
            className={`absolute inset-0 flex items-center justify-center transition-opacity ${expanded ? 'opacity-100' : 'opacity-0 group-hover/thinking:opacity-100'}`}
          >
            {expanded ? (
              <ChevronDown size={14} className="text-gray-400" />
            ) : (
              <ChevronRight size={14} className="text-gray-400" />
            )}
          </div>
        </div>

        <span className="text-xs font-medium text-gray-500 flex-shrink-0">
          {agentName} 思考中
        </span>

        <div className="flex items-center gap-1 flex-1 min-w-0">
          {!expanded && summary ? (
            <span className="min-w-0 truncate text-xs text-gray-400 opacity-80" title={summary}>
              {summary}
            </span>
          ) : (
            <span className="min-w-0 flex-1" />
          )}
        </div>
      </button>

      {expanded && (
        <div className="relative ml-2 pl-3 pb-1 pt-0.5">
          <span
            aria-hidden="true"
            className="pointer-events-none absolute left-0 top-0 bottom-0 w-px bg-gray-200"
          />
          <div className="prose prose-xs max-w-none text-xs text-gray-600 max-h-80 overflow-y-auto">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  )
}
