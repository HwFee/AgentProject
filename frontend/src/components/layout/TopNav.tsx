import { useAuthStore } from '@/stores/authStore'
import { ChevronDown } from 'lucide-react'
import { useLocation } from 'react-router-dom'

const pageTitles: Record<string, string> = {
  '/dashboard': '仪表盘',
  '/reports': '报告列表',
  '/reports/new': '创建报告',
  '/settings': '设置',
}

export function TopNav() {
  const { user } = useAuthStore()
  const location = useLocation()

  const getInitial = (name: string) => name.charAt(0).toUpperCase()

  const title = pageTitles[location.pathname] || ''

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b bg-white/80 px-6 backdrop-blur-sm">
      <h1 className="text-xl font-semibold">{title}</h1>
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-4 text-sm text-gray-600">
          <div className="flex items-center gap-1.5">
            <span>队列</span>
            <span className="h-2 w-2 rounded-full bg-green-500" />
            <span className="text-gray-500">正常</span>
          </div>
          <div className="h-4 w-px bg-gray-200" />
          <div className="flex items-center gap-1.5">
            <span>后端</span>
            <span className="h-2 w-2 rounded-full bg-green-500" />
            <span className="text-gray-500">已连接</span>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-sm font-medium text-white">
            {user ? getInitial(user.username) : 'U'}
          </div>
          <div className="flex items-center gap-1 text-sm">
            <span className="font-medium">{user?.username || '访客'}</span>
            <ChevronDown className="h-4 w-4 text-gray-400" />
          </div>
        </div>
      </div>
    </header>
  )
}
