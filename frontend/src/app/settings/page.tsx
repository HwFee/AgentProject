import { useState } from 'react'
import { useUserProfile } from '@/api/queries'
import { useUpdateProfile, useUpdatePassword } from '@/api/mutations'
import { useAuthStore } from '@/stores/authStore'
import { Button } from '@/components/ui/button'
import { LogOut } from 'lucide-react'
import { Skeleton } from '@/components/ui/skeleton'

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<'profile' | 'password'>('profile')
  const { data: profile, isLoading } = useUserProfile()
  const { logout, user } = useAuthStore()
  const updateProfile = useUpdateProfile()
  const updatePassword = useUpdatePassword()

  const [username, setUsername] = useState('')
  const [email, setEmail] = useState('')

  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  const handleSaveProfile = async () => {
    await updateProfile.mutateAsync({
      username: username || profile?.username || '',
      email: email || profile?.email || '',
    })
  }

  const handleChangePassword = async () => {
    if (newPassword !== confirmPassword) {
      alert('两次输入的新密码不一致')
      return
    }
    await updatePassword.mutateAsync({
      old_password: oldPassword,
      new_password: newPassword,
      confirm_password: confirmPassword,
    })
    setOldPassword('')
    setNewPassword('')
    setConfirmPassword('')
  }

  if (isLoading) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-8 w-32" />
        <Skeleton className="h-10 w-full" />
        <Skeleton className="h-80 w-full" />
      </div>
    )
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <h1 className="text-2xl font-semibold tracking-tight">设置</h1>
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500">用户：{user?.username}</span>
          <button
            onClick={logout}
            className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-600 text-white transition-colors hover:bg-blue-700"
            title="退出登录"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <div className="flex gap-8">
          <button
            className={`border-b-2 px-1 pb-3 text-sm font-medium transition-colors ${
              activeTab === 'profile'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab('profile')}
          >
            个人信息
          </button>
          <button
            className={`border-b-2 px-1 pb-3 text-sm font-medium transition-colors ${
              activeTab === 'password'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700'
            }`}
            onClick={() => setActiveTab('password')}
          >
            修改密码
          </button>
        </div>
      </div>

      {/* Profile Tab */}
      {activeTab === 'profile' && (
        <div className="space-y-4">
          <div className="rounded-lg border border-gray-200 bg-white p-6 space-y-5">
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">用户名</label>
              <input
                type="text"
                className="w-full rounded-lg border border-gray-200 bg-gray-50 px-4 py-2.5 text-sm text-gray-900 outline-none"
                defaultValue={profile?.username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">邮箱</label>
              <input
                type="email"
                className="w-full rounded-lg border border-gray-200 bg-gray-50 px-4 py-2.5 text-sm text-gray-900 outline-none"
                defaultValue={profile?.email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">角色</label>
              <span className="inline-flex rounded-full bg-green-100 px-3 py-1 text-xs font-medium text-green-700">
                {profile?.role === 'admin' ? '管理员' : '普通用户'}
              </span>
            </div>
            <div>
              <label className="mb-2 block text-sm font-medium text-gray-700">注册时间</label>
              <input
                type="text"
                readOnly
                className="w-full rounded-lg border border-gray-200 bg-gray-50 px-4 py-2.5 text-sm text-gray-700 outline-none"
                value={profile?.created_at ? new Date(profile.created_at).toLocaleString('zh-CN') : '-'}
              />
            </div>
          </div>

          <div className="flex justify-end">
            <Button
              onClick={handleSaveProfile}
              disabled={updateProfile.isPending}
              className="h-10 bg-blue-600 px-6 text-sm font-medium hover:bg-blue-700"
            >
              保存信息
            </Button>
          </div>

          <button
            onClick={logout}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-red-500 py-3 text-sm font-medium text-white transition-colors hover:bg-red-600"
          >
            <LogOut className="h-4 w-4" />
            退出登录
          </button>
        </div>
      )}

      {/* Password Tab */}
      {activeTab === 'password' && (
        <div className="rounded-lg border border-gray-200 bg-white p-6 space-y-5">
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">当前密码</label>
            <input
              type="password"
              className="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm text-gray-900 outline-none"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              placeholder="请输入当前密码"
            />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">新密码</label>
            <input
              type="password"
              className="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm text-gray-900 outline-none"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="请输入新密码"
            />
          </div>
          <div>
            <label className="mb-2 block text-sm font-medium text-gray-700">确认新密码</label>
            <input
              type="password"
              className="w-full rounded-lg border border-gray-200 px-4 py-2.5 text-sm text-gray-900 outline-none"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="请再次输入新密码"
            />
          </div>
          <div className="flex justify-end">
            <Button
              onClick={handleChangePassword}
              disabled={updatePassword.isPending}
              className="h-10 bg-blue-600 px-6 text-sm font-medium hover:bg-blue-700"
            >
              修改密码
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
