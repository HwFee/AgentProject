import { Routes, Route, Navigate } from 'react-router-dom'
import { AppShell } from '@/components/layout/AppShell'
import { AuthGuard, AdminGuard, GuestGuard } from '@/components/layout/AuthGuard'
import LoginPage from '@/app/login/page'
import RegisterPage from '@/app/register/page'
import DashboardPage from '@/app/dashboard/page'
import ReportsPage from '@/app/reports/page'
import NewReportPage from '@/app/reports/new/page'
import ReportDetailPage from '@/app/reports/[id]/page'
import SettingsPage from '@/app/settings/page'
import AdminDashboardPage from '@/app/admin/dashboard/page'
import AdminTasksPage from '@/app/admin/tasks/page'
import AdminUsersPage from '@/app/admin/users/page'
import AdminAgentsPage from '@/app/admin/agents/page'

function App() {
  return (
    <Routes>
      <Route element={<GuestGuard><LoginPage /></GuestGuard>} path="/login" />
      <Route element={<GuestGuard><RegisterPage /></GuestGuard>} path="/register" />
      <Route element={<AuthGuard><AppShell /></AuthGuard>} path="/">
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route element={<DashboardPage />} path="dashboard" />
        <Route element={<ReportsPage />} path="reports" />
        <Route element={<NewReportPage />} path="reports/new" />
        <Route element={<ReportDetailPage />} path="reports/:id" />
        <Route element={<SettingsPage />} path="settings" />
      </Route>
      <Route element={<AdminGuard><AppShell /></AdminGuard>} path="/admin">
        <Route element={<AdminDashboardPage />} path="dashboard" />
        <Route element={<AdminTasksPage />} path="tasks" />
        <Route element={<AdminUsersPage />} path="users" />
        <Route element={<AdminAgentsPage />} path="agents" />
      </Route>
      <Route element={<Navigate to="/dashboard" />} path="*" />
    </Routes>
  )
}

export default App
