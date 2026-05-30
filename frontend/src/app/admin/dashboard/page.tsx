import { useAdminStats, useAdminTokenTrend } from '@/api/queries'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Users,
  FileText,
  Calendar,
  Loader2,
  AlertCircle,
  TrendingUp,
  TrendingDown,
  Clock,
  AlertTriangle,
  Zap,
  ChevronRight,
} from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function AdminDashboardPage() {
  const { data: stats, isLoading } = useAdminStats()
  const { data: tokenTrend } = useAdminTokenTrend(7)

  const mainStats = [
    { label: '总用户数', value: stats?.total_users || 0, icon: Users, change: stats?.trends?.total_users || 0, changeLabel: '今日新增' },
    { label: '总报告数', value: stats?.total_reports || 0, icon: FileText, change: stats?.trends?.total_reports || 0, changeLabel: '本周' },
    { label: '今日生成数', value: stats?.today_reports || 0, icon: Calendar, change: stats?.trends?.today_reports || 0, changeLabel: '环比' },
    { label: '运行中任务数', value: stats?.running_tasks || 0, icon: Loader2, change: stats?.trends?.running_tasks || 0, changeLabel: '' },
    { label: '失败任务数', value: stats?.failed_tasks || 0, icon: AlertCircle, change: stats?.trends?.failed_tasks || 0, changeLabel: '待处理' },
  ]

  const subStats = [
    { label: '平均生成耗时', value: stats?.avg_duration || '0秒', icon: Clock, color: 'text-blue-500', bgColor: 'bg-blue-50' },
    { label: '待处理失败数', value: stats?.pending_failures || 0, icon: AlertTriangle, color: 'text-yellow-500', bgColor: 'bg-yellow-50' },
    { label: 'Token 使用量', value: stats?.total_tokens?.toLocaleString() || '0', icon: Zap, color: 'text-purple-500', bgColor: 'bg-purple-50' },
  ]

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">管理仪表盘</h1>
      </div>

      {/* Main Stats Row */}
      <div className="grid grid-cols-5 gap-4">
        {mainStats.map((stat) => (
          <div key={stat.label} className="rounded-lg border border-gray-200 bg-white p-4">
            <div className="flex items-center justify-between">
              <stat.icon className="h-5 w-5 text-gray-400" />
              {stat.change !== 0 && (
                <div className={`flex items-center gap-1 text-xs ${stat.change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {stat.change >= 0 ? <TrendingUp className="h-3 w-3" /> : <TrendingDown className="h-3 w-3" />}
                  {stat.change >= 0 ? '+' : ''}{stat.change}
                </div>
              )}
            </div>
            <p className="mt-2 text-2xl font-bold text-gray-900">{isLoading ? '-' : stat.value}</p>
            <p className="mt-0.5 text-xs text-gray-500">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* Sub Stats Row */}
      <div className="grid grid-cols-3 gap-4">
        {subStats.map((stat) => (
          <div key={stat.label} className="flex items-center gap-4 rounded-lg border border-gray-200 bg-white p-4">
            <div className={`flex h-10 w-10 items-center justify-center rounded-lg ${stat.bgColor}`}>
              <stat.icon className={`h-5 w-5 ${stat.color}`} />
            </div>
            <div>
              <p className="text-xs text-gray-500">{stat.label}</p>
              <p className="text-lg font-bold text-gray-900">{isLoading ? '-' : stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Charts and Tasks */}
      <div className="grid grid-cols-2 gap-6">
        {/* Token Trend Chart */}
        <div className="rounded-lg border border-gray-200 bg-white">
          <div className="border-b border-gray-100 px-4 py-3">
            <h3 className="text-sm font-semibold text-gray-900">Token 使用量趋势</h3>
          </div>
          <div className="p-4">
            {tokenTrend && tokenTrend.length > 0 ? (
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={tokenTrend}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                  <XAxis dataKey="date" tick={{ fontSize: 12, fill: '#9ca3af' }} axisLine={{ stroke: '#e5e7eb' }} />
                  <YAxis tick={{ fontSize: 12, fill: '#9ca3af' }} axisLine={{ stroke: '#e5e7eb' }} />
                  <Tooltip
                    contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb', fontSize: '12px' }}
                  />
                  <Line type="monotone" dataKey="tokens" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3, fill: '#3b82f6' }} />
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div className="flex h-[250px] items-center justify-center text-sm text-gray-400">
                暂无 Token 使用数据
              </div>
            )}
          </div>
        </div>

        {/* Recent Failed Tasks */}
        <div className="rounded-lg border border-gray-200 bg-white">
          <div className="flex items-center justify-between border-b border-gray-100 px-4 py-3">
            <h3 className="text-sm font-semibold text-gray-900">最近失败任务</h3>
            <a href="/admin/tasks" className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700">
              查看全部
              <ChevronRight className="h-3 w-3" />
            </a>
          </div>
          <div className="p-4">
            {isLoading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <Skeleton key={i} className="h-12 w-full" />
                ))}
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
                  <div>
                    <p className="text-sm font-medium text-gray-900">行业趋势分析报告</p>
                    <p className="text-xs text-gray-500">用户：hwfee · 2024-05-20 14:32:15</p>
                  </div>
                  <span className="cursor-pointer text-xs text-blue-600 hover:text-blue-700">查看详情</span>
                </div>
                <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
                  <div>
                    <p className="text-sm font-medium text-gray-900">竞品研究报告</p>
                    <p className="text-xs text-gray-500">用户：test001 · 2024-05-20 12:15:08</p>
                  </div>
                  <span className="cursor-pointer text-xs text-blue-600 hover:text-blue-700">查看详情</span>
                </div>
                <div className="flex items-center justify-between rounded-lg border border-gray-100 p-3">
                  <div>
                    <p className="text-sm font-medium text-gray-900">市场分析报告</p>
                    <p className="text-xs text-gray-500">用户：user123 · 2024-05-20 10:05:22</p>
                  </div>
                  <span className="cursor-pointer text-xs text-blue-600 hover:text-blue-700">查看详情</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
