import { XCircle } from 'lucide-react'

interface ErrorCardProps {
  message: string
  agentName?: string
}

export function ErrorCard({ message, agentName }: ErrorCardProps) {
  return (
    <div className="rounded-lg border border-red-200 bg-red-50 px-3 py-2">
      <div className="flex items-center gap-2">
        <XCircle size={14} className="text-red-500" />
        <span className="text-xs font-medium text-red-700">
          {agentName ? `${agentName} 执行失败` : '执行失败'}
        </span>
      </div>
      <div className="mt-1 text-xs text-red-600">{message}</div>
    </div>
  )
}
