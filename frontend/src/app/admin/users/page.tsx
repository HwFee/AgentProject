import { useState } from 'react'
import { useAdminUsers } from '@/api/queries'
import { useAdminUpdateUserRole, useAdminDeleteUser } from '@/api/mutations'
import { Card, CardContent } from '@/components/ui/card'
import { Pagination } from '@/components/ui/Pagination'
import { Skeleton } from '@/components/ui/skeleton'
import { Trash2 } from 'lucide-react'

export default function AdminUsersPage() {
  const [page, setPage] = useState(1)
  const [pageSize, setPageSize] = useState(10)
  const { data, isLoading } = useAdminUsers(page, pageSize)
  const updateRole = useAdminUpdateUserRole()
  const deleteUser = useAdminDeleteUser()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight">用户管理</h1>
        <p className="text-sm text-gray-500">管理系统用户</p>
      </div>

      <Card>
        <CardContent className="p-0">
          {isLoading ? (
            <div className="space-y-3 p-4">
              {[...Array(5)].map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}
            </div>
          ) : (
            <>
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b">
                    <th className="px-4 pb-3 pt-4 text-left font-medium text-gray-500">ID</th>
                    <th className="px-4 pb-3 pt-4 text-left font-medium text-gray-500">用户名</th>
                    <th className="px-4 pb-3 pt-4 text-left font-medium text-gray-500">邮箱</th>
                    <th className="px-4 pb-3 pt-4 text-left font-medium text-gray-500">角色</th>
                    <th className="px-4 pb-3 pt-4 text-left font-medium text-gray-500">注册时间</th>
                    <th className="px-4 pb-3 pt-4 text-left font-medium text-gray-500">操作</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {data?.items?.map((user) => (
                    <tr key={user.id} className="hover:bg-gray-50">
                      <td className="px-4 py-3">{user.id}</td>
                      <td className="px-4 py-3 font-medium">{user.username}</td>
                      <td className="px-4 py-3">{user.email}</td>
                      <td className="px-4 py-3">
                        <select
                          value={user.role}
                          onChange={(e) => updateRole.mutate({ userId: user.id, role: e.target.value })}
                          className="rounded border px-2 py-1 text-xs"
                        >
                          <option value="user">普通用户</option>
                          <option value="admin">管理员</option>
                        </select>
                      </td>
                      <td className="px-4 py-3 text-gray-500">{new Date(user.created_at).toLocaleString()}</td>
                      <td className="px-4 py-3">
                        <button onClick={() => deleteUser.mutate(user.id)}>
                          <Trash2 className="h-4 w-4 text-gray-400 hover:text-red-500" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
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
