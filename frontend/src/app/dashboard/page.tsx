import { Link } from 'react-router-dom'
import { useReports, useReportStats } from '@/api/queries'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { Pagination } from '@/components/ui/Pagination'
import { Skeleton } from '@/components/ui/skeleton'
import { Plus, Eye, FileText, CheckCircle, Loader2, XCircle } from 'lucide-react'
import { useState } from 'react'

const modeLabels: Record<string, string> = {
  generate: '从零生成',
  template: '混合模式',
  reference: '参考型',
  edit: '迭代修改',
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

export default function DashboardPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(5)
  const { data: reportsData, isLoading: reportsLoading } = useReports(page, pageSize)
  const { data: stats, isLoading: statsLoading } = useReportStats()
  const reports = Array.isArray(reportsData?.items) ? reportsData.items : []
  const totalReports = typeof reportsData?.total === 'number' ? reportsData.total : 0

  const statCards = [
    { label: '总报告数', value: stats?.total ?? 0, icon: FileText, color: 'text-gray-900', bgColor: 'bg-blue-100', iconColor: 'text-blue-600' },
    { label: '已完成', value: stats?.completed ?? 0, icon: CheckCircle, color: 'text-green-500', bgColor: 'bg-green-100', iconColor: 'text-green-600' },
    { label: '生成中', value: stats?.running ?? 0, icon: Loader2, color: 'text-orange-500', bgColor: 'bg-orange-100', iconColor: 'text-orange-600' },
    { label: '失败', value: stats?.failed ?? 0, icon: XCircle, color: 'text-red-500', bgColor: 'bg-red-100', iconColor: 'text-red-600' },
  ]

  return (
    <div className="flex flex-1 flex-col gap-6">
      {/* Page title */}
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">仪表盘</h1>
      </div>

      {/* Stat cards */}
      <div className="grid gap-4 md:grid-cols-4">
        {statCards.map((card) => (
          <Card key={card.label}>
            <CardContent className="flex items-center justify-between p-6">
              <div>
                <p className="text-sm text-gray-500">{card.label}</p>
                <p className={`text-4xl font-bold ${card.color}`}>
                  {statsLoading ? '-' : card.value}
                </p>
              </div>
              <div className={`flex h-12 w-12 items-center justify-center rounded-full ${card.bgColor} ${card.iconColor}`}>
                <card.icon className="h-6 w-6" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Reports table - fills remaining height */}
      <div className="flex flex-1 flex-col">
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-lg font-semibold">最近 5 个报告</h2>
          <Link to="/reports/new">
            <Button className="bg-blue-600 hover:bg-blue-700">
              <Plus className="mr-2 h-4 w-4" />
              创建新报告
            </Button>
          </Link>
        </div>
        <Card className="flex flex-1 flex-col">
          <CardContent className="flex flex-1 flex-col p-0">
            {reportsLoading ? (
              <div className="space-y-3 p-4">
                {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-14 w-full" />)}
              </div>
            ) : (
              <>
                <div className="flex-1 overflow-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="px-6 pb-3 pt-4 text-left text-xs font-medium text-gray-500">标题</th>
                        <th className="px-6 pb-3 pt-4 text-left text-xs font-medium text-gray-500">状态</th>
                        <th className="px-6 pb-3 pt-4 text-left text-xs font-medium text-gray-500">创建时间</th>
                        <th className="px-6 pb-3 pt-4 text-left text-xs font-medium text-gray-500">模式</th>
                        <th className="px-6 pb-3 pt-4 pl-10 text-left text-xs font-medium text-gray-500">操作</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                      {reports.map((report, idx, arr) => (
                        <tr
                          key={report.id}
                          className={`hover:bg-gray-50/50 ${idx < arr.length - 1 ? 'border-b border-gray-100' : ''}`}
                        >
                          <td className="px-6 py-4 text-sm font-medium text-gray-900">{report.title}</td>
                          <td className="px-6 py-4"><StatusBadge status={report.status} /></td>
                          <td className="px-6 py-4 text-sm text-gray-500">{formatTime(report.created_at)}</td>
                          <td className="px-6 py-4 text-sm text-gray-500">{modeLabels[report.mode || ''] || report.mode || '-'}</td>
                          <td className="px-6 py-4 pl-10">
                            <div className="flex gap-2">
                              <Link to={`/reports/${report.id}`}>
                                <Button variant="outline" size="sm" className="h-8 gap-1 rounded-md border-gray-300 px-3 text-xs font-medium text-gray-700 hover:bg-gray-50">
                                  <Eye className="h-3.5 w-3.5" />
                                  查看
                                </Button>
                              </Link>
                            </div>
                          </td>
                        </tr>
                      ))}
                      {Array.from({ length: Math.max(0, 5 - reports.length) }).map((_, i) => (
                        <tr key={`empty-row-${i}`} className="h-[57px]">
                          <td className="px-6 py-4" colSpan={5}>&nbsp;</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                {reportsData && (
                  <Pagination
                    page={page}
                    pageSize={pageSize}
                    total={totalReports}
                    onPageChange={setPage}
                    onPageSizeChange={(s) => { setPageSize(s); setPage(1) }}
                  />
                )}
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
