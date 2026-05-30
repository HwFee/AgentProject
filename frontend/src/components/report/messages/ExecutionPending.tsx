import { Loader } from 'lucide-react'

interface ExecutionPendingProps {
  agentName: string
}

export function ExecutionPending({ agentName }: ExecutionPendingProps) {
  return (
    <div className="flex items-center gap-2 rounded-xl border border-blue-100 bg-blue-50/50 px-3 py-2">
      <Loader size={14} className="animate-spin text-blue-500" />
      <span className="text-xs text-blue-700 font-medium">{agentName} 执行中...</span>
    </div>
  )
}
