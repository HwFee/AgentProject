import { Link, useLocation } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import {
  LayoutDashboard,
  FileText,
  Plus,
  Settings,
} from 'lucide-react'
import { cn } from '@/lib/utils'

const navItems = [
  { path: '/dashboard', label: '仪表盘', icon: LayoutDashboard },
  { path: '/reports', label: '报告列表', icon: FileText },
  { path: '/reports/new', label: '创建报告', icon: Plus },
  { path: '/settings', label: '设置', icon: Settings },
]

export function Sidebar() {
  const location = useLocation()
  const { user } = useAuthStore()

  const activePath = navItems
    .filter((item) => location.pathname === item.path || location.pathname.startsWith(item.path + '/'))
    .sort((a, b) => b.path.length - a.path.length)[0]?.path

  const isActive = (path: string) => path === activePath

  const getInitial = (name: string) => name.charAt(0).toUpperCase()

  return (
    <aside className="fixed left-0 top-0 z-40 flex h-screen w-64 flex-col bg-slate-900">
      {/* Logo */}
      <div className="flex h-16 items-center px-6">
        <Link to="/" className="text-lg font-semibold tracking-tight text-white">
          Report Agent
        </Link>
      </div>

      {/* Nav */}
      <nav className="flex-1 space-y-1 px-3 py-4">
        {navItems.map((item) => (
          <Link
            key={item.path}
            to={item.path}
            className={cn(
              'flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition-colors',
              isActive(item.path)
                ? 'bg-blue-600 font-medium text-white'
                : 'text-gray-400 hover:bg-white/10 hover:text-white'
            )}
          >
            <item.icon className="h-4 w-4 shrink-0" />
            <span>{item.label}</span>
          </Link>
        ))}
      </nav>

      {/* User info */}
      {user && (
        <div className="mx-3 mb-4 rounded-lg bg-slate-800 p-3">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-600 text-sm font-medium text-white">
              {getInitial(user.username)}
            </div>
            <div className="min-w-0">
              <div className="text-sm font-medium text-white">{user.username}</div>
              <div className="truncate text-xs text-gray-400">{user.email}</div>
            </div>
          </div>
        </div>
      )}
    </aside>
  )
}
