import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useAdminTasks } from '@/api/queries'
import { useAdminStopTask, useAdminDeleteTask } from '@/api/mutations'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { Pagination } from '@/components/ui/Pagination'
import { Skeleton } from '@/components/ui/skeleton'
import { Eye, Trash2, Square, ChevronDown, Filter } from 'lucide-react'

const modeLabels: Record<string, string> = {
  generate: '从零生成',
  template: '深度模式',
  reference: '参考模式',
  edit: '分析模式',
}

const statusOptions = [
  { value: '', label: '全部状态' },
  { value: 'running', label: '进行中' },
  { value: 'completed', label: '已完成' },
  { value: 'failed', label: '失败' },
]

const modeOptions = [
  { value: '', label: '全部模式' },
  { value: 'generate', label: '从零生成' },
  { value: 'template', label: '深度模式' },
  { value: 'reference', label: '参考模式' },
  { value: 'edit', label: '分析模式' },
]

function formatDateTime(dateString: string): string {
  const date = new Date(dateString)
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  const h = String(date.getHours()).padStart(2, '0')
  const min = String(date.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${d} ${h}:${min}`
}

function Select({
  value,
  onChange,
  options,
}: {
  value: string
  onChange: (v: string) => void
  options: { value: string; label: string }[]
}) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const current = options.find((o) => o.value === value) || options[0]

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="flex h-10 w-36 items-center justify-between rounded-lg border border-gray-200 bg-white px-3 text-sm text-gray-700 outline-none hover:border-gray-300"
      >
        {current.label}
        <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && (
        <div className="absolute left-0 top-full z-50 mt-1 w-full rounded-lg border border-gray-200 bg-white py-1 shadow-lg">
          {options.map((option) => (
            <button
              key={option.value}
              onClick={() => { onChange(option.value); setOpen(false) }}
              className={`flex w-full px-3 py-2 text-sm hover:bg-gray-50 ${option.value === value ? 'font-medium text-gray-900' : 'text-gray-600'}`}
            >
              {option.label}
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default function AdminTasksPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [filters, setFilters] = useState<Record<string, string>>({})
  const { data, isLoading } = useAdminTasks(page, pageSize, filters)
  const stopTask = useAdminStopTask()
  const deleteTask = useAdminDeleteTask()

  return (
    <div className="flex flex-1 flex-col gap-6">
      {/* Title */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">任务管理</h1>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3">
        <Select
          value={filters.status || ''}
          onChange={(v) => { setFilters({ ...filters, status: v }); setPage(1) }}
          options={statusOptions}
        />
        <Select
          value={filters.mode || ''}
          onChange={(v) => { setFilters({ ...filters, mode: v }); setPage(1) }}
          options={modeOptions}
        />
        <button
          className="flex h-10 items-center gap-1.5 rounded-lg bg-blue-600 px-4 text-sm font-medium text-white hover:bg-blue-700"
          onClick={() => setPage(1)}
        >
          <Filter className="h-4 w-4" />
          筛选
        </button>
      </div>

      {/* Table */}
      <div className="flex flex-1 flex-col rounded-lg border border-gray-200 bg-white">
        <div className="flex-1 overflow-auto">
          {isLoading ? (
            <div className="space-y-3 p-4">
              {[...Array(10)].map((_, i) => <Skeleton key={i} className="h-14 w-full" />)}
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="px-6 pb-3 pt-4 text-left text-xs font-medium text-gray-500">用户</th>
                  <th className="px-6 pb-3 pt-4 text-left text-xs font-medium text-gray-500">报告标题</th>
                  <th className="px-6 pb-3 pt-4 text-left text-xs font-medium text-gray-500">状态</th>
                  <th className="px-6 pb-3 pt-4 text-left text-xs font-medium text-gray-500">模式</th>
                  <th className="px-6 pb-3 pt-4 text-left text-xs font-medium text-gray-500">创建时间</th>
                  <th className="px-6 pb-3 pt-4 text-left text-xs font-medium text-gray-500">更新时间</th>
                  <th className="px-6 pb-3 pt-4 pl-10 text-left text-xs font-medium text-gray-500">操作</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {data?.items?.map((task) => (
                  <tr key={task.id} className="hover:bg-gray-50/50">
                    <td className="px-6 py-4 text-sm text-gray-700">{task.username}</td>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{task.title}</td>
                    <td className="px-6 py-4"><StatusBadge status={task.status} /></td>
                    <td className="px-6 py-4 text-sm text-gray-500">{modeLabels[task.mode || ''] || task.mode || '-'}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{formatDateTime(task.created_at)}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{formatDateTime(task.updated_at)}</td>
                    <td className="px-6 py-4 pl-10">
                      <div className="flex items-center gap-2">
                        <Link to={`/reports/${task.id}`}>
                          <button className="flex h-8 items-center gap-1 rounded-md border border-gray-300 px-3 text-xs font-medium text-gray-700 hover:bg-gray-50">
                            <Eye className="h-3.5 w-3.5" />
                            查看
                          </button>
                        </Link>
                        {task.status === 'running' && (
                          <button
                            onClick={() => stopTask.mutate(task.id)}
                            className="flex h-8 items-center gap-1 rounded-md border border-red-200 px-3 text-xs font-medium text-red-600 hover:bg-red-50"
                          >
                            <Square className="h-3.5 w-3.5" />
                            停止
                          </button>
                        )}
                        <button
                          onClick={() => deleteTask.mutate(task.id)}
                          className="flex h-8 w-8 items-center justify-center rounded-md border border-gray-300 text-gray-500 hover:bg-gray-50 hover:text-red-600"
                        >
                          <Trash2 className="h-3.5 w-3.5" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        {data && (
          <Pagination
            page={page}
            pageSize={pageSize}
            total={data.total}
            onPageChange={setPage}
            onPageSizeChange={(s) => { setPageSize(s); setPage(1) }}
          />
        )}
      </div>
    </div>
  )
}
