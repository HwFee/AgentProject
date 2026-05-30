import { Outlet } from 'react-router-dom'
import { Sidebar } from './Sidebar'

export function AppShell() {
  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      <Sidebar />
      <div className="ml-64 flex flex-1 flex-col h-full overflow-hidden">
        <main className="flex flex-1 flex-col p-6 h-full overflow-hidden">
          <Outlet />
        </main>
      </div>
    </div>
  )
}
