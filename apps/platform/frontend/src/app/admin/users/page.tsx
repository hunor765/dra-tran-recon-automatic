'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Users, Mail, Shield, UserCheck, AlertCircle, Plus, Trash2, Search, RefreshCw } from 'lucide-react'
import { api } from '@/lib/api/client'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { useToast, Toast } from '@/components/ui/Toast'
import { TableSkeleton } from '@/components/ui/LoadingSkeleton'

interface User {
    id: string
    email: string
    role: string
    created_at: string
    last_sign_in_at: string | null
    user_metadata: {
        name?: string
    }
}

interface Client {
    id: number
    name: string
    slug: string
}

interface UserClientLink {
    id: number
    user_id: string
    client_id: number
    email: string
    role: string
    status: string
    client_name?: string
}

export default function AdminUsersPage() {
    const [users, setUsers] = useState<User[]>([])
    const [clients, setClients] = useState<Client[]>([])
    const [userClientLinks, setUserClientLinks] = useState<UserClientLink[]>([])
    const [loading, setLoading] = useState(true)
    const [searchQuery, setSearchQuery] = useState('')
    const [showInviteModal, setShowInviteModal] = useState(false)
    const { toasts, dismiss, success, error: showError } = useToast()

    useEffect(() => {
        fetchData()
    }, [])

    const fetchData = async () => {
        try {
            setLoading(true)
            // Fetch clients
            const clientsData = await api.getClients()
            setClients(clientsData)
            
            // Fetch user-client links from all clients
            const links: UserClientLink[] = []
            for (const client of clientsData) {
                try {
                    const clientUsers = await api.getClientUsers(client.id)
                    links.push(...clientUsers.map((u: UserClientLink) => ({ ...u, client_name: client.name })))
                } catch (e) {
                    // Skip clients we can't access
                }
            }
            setUserClientLinks(links)
        } catch (err: any) {
            console.error('Failed to fetch data:', err)
            showError(err.message || 'Failed to fetch data')
        } finally {
            setLoading(false)
        }
    }

    const removeUser = async (userId: number) => {
        if (!confirm('Are you sure you want to remove this user?')) return
        
        try {
            await api.removeUser(userId)
            await fetchData()
            success('User removed successfully')
        } catch (err: any) {
            console.error('Failed to remove user:', err)
            showError(err.message || 'Failed to remove user')
        }
    }

    const filteredLinks = userClientLinks.filter(link => 
        link.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
        link.client_name?.toLowerCase().includes(searchQuery.toLowerCase())
    )

    // Group by client
    const linksByClient = filteredLinks.reduce((acc, link) => {
        const clientName = link.client_name || 'Unknown'
        if (!acc[clientName]) acc[clientName] = []
        acc[clientName].push(link)
        return acc
    }, {} as Record<string, UserClientLink[]>)

    return (
        <div>
            <div className="mb-8">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                            <Users size={32} className="text-revolt-red" />
                            User Management
                        </h1>
                        <p className="text-gray-500 mt-2">
                            Manage user access across all clients
                        </p>
                    </div>
                    <div className="flex gap-3">
                        <button
                            onClick={fetchData}
                            className="px-4 py-2 border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition flex items-center gap-2"
                        >
                            <RefreshCw size={18} />
                            Refresh
                        </button>
                        <button
                            onClick={() => setShowInviteModal(true)}
                            className="bg-revolt-red text-white px-4 py-2 rounded-lg font-medium hover:bg-red-700 transition flex items-center gap-2"
                        >
                            <Plus size={18} />
                            Invite User
                        </button>
                    </div>
                </div>
            </div>

            {/* Search Bar */}
            <div className="mb-6">
                <div className="relative max-w-md">
                    <Search size={20} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Search users or clients..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-revolt-red focus:border-revolt-red outline-none"
                    />
                </div>
            </div>

            {/* Users by Client */}
            {loading ? (
                <TableSkeleton rows={8} columns={5} />
            ) : (
                <div className="space-y-8">
                    {Object.entries(linksByClient).map(([clientName, links]) => (
                        <div key={clientName} className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                            <div className="px-6 py-4 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
                                <h2 className="font-semibold text-gray-900 flex items-center gap-2">
                                    <Shield size={18} className="text-revolt-red" />
                                    {clientName}
                                </h2>
                                <span className="text-sm text-gray-500">
                                    {links.length} user{links.length !== 1 ? 's' : ''}
                                </span>
                            </div>
                            <table className="w-full">
                                <thead className="bg-gray-50 border-b border-gray-200">
                                    <tr>
                                        <th className="text-left px-6 py-3 text-sm font-semibold text-gray-600">User</th>
                                        <th className="text-left px-6 py-3 text-sm font-semibold text-gray-600">Role</th>
                                        <th className="text-left px-6 py-3 text-sm font-semibold text-gray-600">Status</th>
                                        <th className="text-left px-6 py-3 text-sm font-semibold text-gray-600">Added</th>
                                        <th className="text-right px-6 py-3 text-sm font-semibold text-gray-600">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-gray-100">
                                    {links.map((link) => (
                                        <tr key={link.id} className="hover:bg-gray-50 transition">
                                            <td className="px-6 py-4">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center">
                                                        <Mail size={14} className="text-gray-500" />
                                                    </div>
                                                    <span className="font-medium text-gray-900">{link.email}</span>
                                                </div>
                                            </td>
                                            <td className="px-6 py-4">
                                                <span className={`px-2 py-1 rounded-full text-xs font-medium capitalize ${
                                                    link.role === 'admin' 
                                                        ? 'bg-purple-50 text-purple-700' 
                                                        : 'bg-blue-50 text-blue-700'
                                                }`}>
                                                    {link.role}
                                                </span>
                                            </td>
                                            <td className="px-6 py-4">
                                                <StatusBadge status={link.status} />
                                            </td>
                                            <td className="px-6 py-4 text-gray-500 text-sm">
                                                {new Date(link.created_at).toLocaleDateString()}
                                            </td>
                                            <td className="px-6 py-4 text-right">
                                                <button
                                                    onClick={() => removeUser(link.id)}
                                                    className="p-2 text-gray-400 hover:text-red-600 transition"
                                                    title="Remove user"
                                                >
                                                    <Trash2 size={18} />
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                            {links.length === 0 && (
                                <div className="p-8 text-center text-gray-500">
                                    No users for this client.
                                </div>
                            )}
                        </div>
                    ))}
                    
                    {Object.keys(linksByClient).length === 0 && (
                        <div className="text-center py-12 bg-white rounded-xl border border-gray-200">
                            <Users size={48} className="mx-auto text-gray-300 mb-4" />
                            <h3 className="text-lg font-medium text-gray-900 mb-2">No Users Found</h3>
                            <p className="text-gray-500 mb-6">
                                {searchQuery ? 'No users match your search.' : 'No users have been invited yet.'}
                            </p>
                            <button
                                onClick={() => setShowInviteModal(true)}
                                className="bg-revolt-red text-white px-4 py-2 rounded-lg font-medium hover:bg-red-700 transition"
                            >
                                Invite Your First User
                            </button>
                        </div>
                    )}
                </div>
            )}

            {/* Global Invite Modal */}
            {showInviteModal && (
                <GlobalInviteModal
                    clients={clients}
                    onClose={() => setShowInviteModal(false)}
                    onInvited={fetchData}
                    onSuccess={() => success('Invitation sent successfully')}
                />
            )}

            {toasts.map(t => (
                <Toast key={t.id} message={t.message} type={t.type} onDismiss={() => dismiss(t.id)} />
            ))}
        </div>
    )
}

function GlobalInviteModal({ 
    clients, 
    onClose, 
    onInvited, 
    onSuccess 
}: { 
    clients: Client[]
    onClose: () => void
    onInvited: () => void
    onSuccess: () => void 
}) {
    const [email, setEmail] = useState('')
    const [role, setRole] = useState('viewer')
    const [selectedClient, setSelectedClient] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        if (!selectedClient) {
            setError('Please select a client')
            return
        }
        
        setLoading(true)
        setError(null)
        
        try {
            await api.inviteUser(parseInt(selectedClient), { email, role })
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
                <h2 className="text-xl font-bold text-gray-900 mb-1">Invite User</h2>
                <p className="text-gray-500 text-sm mb-4">
                    Send an invitation to access a client account
                </p>
                
                {error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm flex items-start gap-2">
                        <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
                        {error}
                    </div>
                )}
                
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Client <span className="text-red-500">*</span>
                        </label>
                        <select
                            value={selectedClient}
                            onChange={(e) => setSelectedClient(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-revolt-red focus:border-revolt-red outline-none"
                            required
                        >
                            <option value="">Select a client...</option>
                            {clients.map(client => (
                                <option key={client.id} value={client.id}>
                                    {client.name}
                                </option>
                            ))}
                        </select>
                    </div>
                    
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">
                            Email Address <span className="text-red-500">*</span>
                        </label>
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
                            <option value="viewer">Viewer (Read-only access)</option>
                            <option value="admin">Admin (Full access)</option>
                        </select>
                        <p className="text-xs text-gray-500 mt-1">
                            {role === 'viewer' 
                                ? 'Can view dashboards and reports only' 
                                : 'Can manage connectors, run jobs, and view all data'}
                        </p>
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
