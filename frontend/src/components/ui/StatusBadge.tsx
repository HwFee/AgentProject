import { Badge } from './badge'

const statusMap: Record<string, { label: string; className: string }> = {
  completed: { label: 'completed', className: 'bg-green-100 text-green-700 hover:bg-green-100' },
  running: { label: 'running', className: 'bg-orange-100 text-orange-700 hover:bg-orange-100' },
  planning: { label: 'planning', className: 'bg-blue-100 text-blue-700 hover:bg-blue-100' },
  pending: { label: 'pending', className: 'bg-yellow-100 text-yellow-700 hover:bg-yellow-100' },
  failed: { label: 'failed', className: 'bg-red-100 text-red-700 hover:bg-red-100' },
  cancelled: { label: 'cancelled', className: 'bg-gray-100 text-gray-700 hover:bg-gray-100' },
}

export function StatusBadge({ status }: { status: string }) {
  const config = statusMap[status] || statusMap.pending
  return <Badge className={config.className}>{config.label}</Badge>
}
