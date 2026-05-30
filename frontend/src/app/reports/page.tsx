import { Link } from 'react-router-dom'
import { useState, useRef, useEffect } from 'react'
import { useReports } from '@/api/queries'
import { useDeleteReport, useStopReport } from '@/api/mutations'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { Pagination } from '@/components/ui/Pagination'
import { Skeleton } from '@/components/ui/skeleton'
import { Plus, Search, Eye, Trash2, ChevronDown } from 'lucide-react'

const modeLabels: Record<string, string> = {
  generate: '从零生成',
  template: '深度模式',
  reference: '参考模式',
  edit: '分析模式',
}

function formatTime(dateString: string): string {
  const date = new Date(dateString)
  const y = date.getFullYear()
  const m = String(date.getMonth() + 1).padStart(2, '0')
  const d = String(date.getDate()).padStart(2, '0')
  const h = String(date.getHours()).padStart(2, '0')
  const min = String(date.getMinutes()).padStart(2, '0')
  return `${y}-${m}-${d} ${h}:${min}`
}

const statusOptions = [
  { value: '', label: '全部状态' },
  { value: 'running', label: '进行中' },
  { value: 'completed', label: '已完成' },
  { value: 'failed', label: '失败' },
  { value: 'cancelled', label: '已取消' },
]

function StatusSelect({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false)
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const current = statusOptions.find((o) => o.value === value) || statusOptions[0]

  return (
    <div className="relative" ref={ref}>
      <button
        onClick={() => setOpen(!open)}
        className="flex h-10 w-32 items-center justify-between rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-700 outline-none hover:border-gray-300"
      >
        {current.label}
        <ChevronDown className={`h-4 w-4 text-gray-400 transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      {open && (
        <div className="absolute left-0 top-full z-50 mt-1 w-full rounded-md border border-gray-200 bg-white py-1 shadow-lg">
          {statusOptions.map((option) => (
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

export default function ReportsPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const [search, setSearch] = useState('')
  const [status, setStatus] = useState('')
  const [searchInput, setSearchInput] = useState('')

  const { data, isLoading } = useReports(page, pageSize, search || undefined, status || undefined)
  const deleteMutation = useDeleteReport()
  const stopMutation = useStopReport()

  const handleSearch = () => setSearch(searchInput)

  return (
    <div className="flex flex-1 flex-col gap-6">
      {/* Page title */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">报告列表</h1>
      </div>

      {/* Search and filters */}
      <div className="flex items-center gap-3">
        <div className="flex flex-1 items-center rounded-md border border-gray-200 bg-white px-3 py-2">
          <Search className="mr-2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="搜索报告标题"
            className="flex-1 border-none bg-transparent text-sm outline-none"
            value={searchInput}
            onChange={(e) => setSearchInput(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
        </div>
        <StatusSelect
          value={status}
          onChange={(v) => { setStatus(v); setPage(1) }}
        />
        <Link to="/reports/new">
          <Button className="bg-blue-600 hover:bg-blue-700">
            <Plus className="mr-2 h-4 w-4" />
            创建报告
          </Button>
        </Link>
      </div>

      {/* Table */}
      <Card className="flex flex-1 flex-col">
        <CardContent className="flex flex-1 flex-col p-0">
          {isLoading ? (
            <div className="space-y-3 p-4">
              {[...Array(10)].map((_, i) => <Skeleton key={i} className="h-14 w-full" />)}
            </div>
          ) : (
            <>
              <div className="flex-1 overflow-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="px-6 pb-3 pt-4 text-left text-xs font-medium text-gray-500">标题</th>
                      <th className="px-6 pb-3 pt-4 text-left text-xs font-medium text-gray-500">生成模式</th>
                      <th className="px-6 pb-3 pt-4 text-left text-xs font-medium text-gray-500">状态</th>
                      <th className="px-6 pb-3 pt-4 text-left text-xs font-medium text-gray-500">创建时间</th>
                      <th className="px-6 pb-3 pt-4 text-left text-xs font-medium text-gray-500">更新时间</th>
                      <th className="px-6 pb-3 pt-4 pl-10 text-left text-xs font-medium text-gray-500">操作</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-100">
                    {data?.items?.map((report) => (
                      <tr key={report.id} className="hover:bg-gray-50/50">
                        <td className="px-6 py-4 text-sm font-medium text-gray-900">{report.title}</td>
                        <td className="px-6 py-4 text-sm text-gray-500">{modeLabels[report.mode || ''] || report.mode || '-'}</td>
                        <td className="px-6 py-4"><StatusBadge status={report.status} /></td>
                        <td className="px-6 py-4 text-sm text-gray-500">{formatTime(report.created_at)}</td>
                        <td className="px-6 py-4 text-sm text-gray-500">{formatTime(report.updated_at)}</td>
                        <td className="px-6 py-4 pl-10">
                          <div className="flex items-center gap-2">
                            <Link to={`/reports/${report.id}`}>
                              <Button variant="outline" size="sm" className="h-8 gap-1 rounded-md border-gray-300 px-3 text-xs font-medium text-gray-700 hover:bg-gray-50">
                                <Eye className="h-3.5 w-3.5" />
                                查看
                              </Button>
                            </Link>
                            {report.status === 'running' ? (
                              <>
                                <Button variant="outline" size="sm" className="h-8 gap-1 rounded-md border-red-200 px-3 text-xs font-medium text-red-600 hover:bg-red-50" onClick={() => stopMutation.mutate(report.id)}>
                                  停止
                                </Button>
                                <Button variant="outline" size="sm" className="h-8 w-8 rounded-md border-gray-300 p-0 text-gray-500 hover:bg-gray-50 hover:text-red-600" onClick={() => deleteMutation.mutate(report.id)}>
                                  <Trash2 className="h-3.5 w-3.5" />
                                </Button>
                              </>
                            ) : report.status === 'failed' ? (
                              <Button variant="outline" size="sm" className="h-8 gap-1 rounded-md border-red-200 px-3 text-xs font-medium text-red-600 hover:bg-red-50" onClick={() => deleteMutation.mutate(report.id)}>
                                <Trash2 className="h-3.5 w-3.5" />
                                删除
                              </Button>
                            ) : (
                              <Button
                                variant="outline"
                                size="sm"
                                className="h-8 w-8 rounded-md border-gray-300 p-0 text-gray-500 hover:bg-gray-50 hover:text-red-600"
                                onClick={() => deleteMutation.mutate(report.id)}
                              >
                                <Trash2 className="h-3.5 w-3.5" />
                              </Button>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
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
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
