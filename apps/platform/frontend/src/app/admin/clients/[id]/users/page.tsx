'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Plus, Trash2, Mail, UserCheck, AlertCircle } from 'lucide-react'
import { api } from '@/lib/api/client'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { useToast, Toast } from '@/components/ui/Toast'
import { TableSkeleton } from '@/components/ui/LoadingSkeleton'

interface UserClient {
    id: number
    email: string
    role: string
    status: string
    created_at: string
}

export default function ClientUsersPage() {
    const params = useParams()
    const clientId = parseInt(params.id as string)
    
    const [users, setUsers] = useState<UserClient[]>([])
    const [showInviteModal, setShowInviteModal] = useState(false)
    const [loading, setLoading] = useState(true)
    const { toasts, dismiss, success, error: showError } = useToast()

    useEffect(() => {
        fetchUsers()
    }, [clientId])

    const fetchUsers = async () => {
        try {
            const data = await api.getClientUsers(clientId)
            setUsers(data)
        } catch (err: any) {
            console.error('Failed to fetch users:', err)
            showError(err.message || 'Failed to fetch users')
        } finally {
            setLoading(false)
        }
    }

    const removeUser = async (userId: number) => {
        if (!confirm('Are you sure you want to remove this user?')) return
        
        try {
            await api.removeUser(userId)
            await fetchUsers()
            success('User removed successfully')
        } catch (err: any) {
            console.error('Failed to remove user:', err)
            showError(err.message || 'Failed to remove user')
        }
    }

    return (
        <div>
            {loading ? (
                <TableSkeleton rows={5} columns={5} />
            ) : (
            <>
            <div className="mb-8">
                <Link href={`/admin/clients/${params.id}`} className="text-gray-500 hover:text-gray-900 flex items-center gap-1 mb-4">
                    <ArrowLeft size={16} />
                    Back to Client
                </Link>
                <div className="flex items-center justify-between">
                    <h1 className="text-3xl font-bold text-gray-900">Client Users</h1>
                    <button
                        onClick={() => setShowInviteModal(true)}
                        className="bg-revolt-red text-white px-4 py-2 rounded-lg font-medium hover:bg-red-700 transition flex items-center gap-2"
                    >
                        <Plus size={18} />
                        Invite User
                    </button>
                </div>
            </div>

            {/* Users Table */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                            <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Email</th>
                            <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Role</th>
                            <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Status</th>
                            <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Invited</th>
                            <th className="text-right px-6 py-4 text-sm font-semibold text-gray-600">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {users.map((user) => (
                            <tr key={user.id} className="hover:bg-gray-50 transition">
                                <td className="px-6 py-4 flex items-center gap-2">
                                    <Mail size={16} className="text-gray-400" />
                                    {user.email}
                                </td>
                                <td className="px-6 py-4">
                                    <span className="px-2 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-medium capitalize">
                                        {user.role}
                                    </span>
                                </td>
                                <td className="px-6 py-4">
                                    <StatusBadge status={user.status} />
                                </td>
                                <td className="px-6 py-4 text-gray-500">
                                    {new Date(user.created_at).toLocaleDateString()}
                                </td>
                                <td className="px-6 py-4 text-right">
                                    <button
                                        onClick={() => removeUser(user.id)}
                                        className="p-2 text-gray-400 hover:text-red-600 transition"
                                    >
                                        <Trash2 size={18} />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {users.length === 0 && (
                    <div className="p-8 text-center text-gray-500">
                        No users invited yet.
                    </div>
                )}
            </div>

            {/* Invite Modal */}
            {showInviteModal && (
                <InviteUserModal
                    clientId={clientId.toString()}
                    onClose={() => setShowInviteModal(false)}
                    onInvited={fetchUsers}
                    onSuccess={() => success('Invitation sent successfully')}
                />
            )}

            {toasts.map(t => (
                <Toast key={t.id} message={t.message} type={t.type} onDismiss={() => dismiss(t.id)} />
            ))}
            </>
            )}
        </div>
    )
}



function InviteUserModal({ clientId, onClose, onInvited, onSuccess }: { clientId: string; onClose: () => void; onInvited: () => void; onSuccess: () => void }) {
    const [email, setEmail] = useState('')
    const [role, setRole] = useState('viewer')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError(null)
        
        try {
            await api.inviteUser(parseInt(clientId), { email, role })
            onInvited()
            onSuccess()
            onClose()
        } catch (err: any) {
            console.error('Failed to invite user:', err)
            setError(err.message || 'Failed to send invitation')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-6 w-full max-w-md">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Invite User</h2>
                {error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                        {error}
                    </div>
                )}
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                        <input
                            type="email"
                            value={email}
                            onChange={(e) => setEmail(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-revolt-red focus:border-revolt-red outline-none"
                            placeholder="user@company.com"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Role</label>
                        <select
                            value={role}
                            onChange={(e) => setRole(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-revolt-red focus:border-revolt-red outline-none"
                        >
                            <option value="viewer">Viewer (Read-only)</option>
                            <option value="admin">Admin (Full access)</option>
                        </select>
                    </div>
                    <div className="flex gap-3 pt-4">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2 border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex-1 px-4 py-2 bg-revolt-red text-white rounded-lg font-medium hover:bg-red-700 transition disabled:opacity-50"
                        >
                            {loading ? 'Sending...' : 'Send Invite'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
