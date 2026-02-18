'use client'

import { useEffect, useState, useCallback } from 'react'
import Link from 'next/link'
import { Plus, Search, MoreVertical, Edit, Trash2, AlertCircle, ChevronLeft, ChevronRight } from 'lucide-react'
import { api } from '@/lib/api/client'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { TableSkeleton, Skeleton } from '@/components/ui/LoadingSkeleton'
import { useToast, Toast } from '@/components/ui/Toast'

interface Client {
    id: number
    name: string
    slug: string
    logo_url: string | null
    is_active: boolean
    created_at: string
}

const ITEMS_PER_PAGE = 10

export default function ClientsPage() {
    const [clients, setClients] = useState<Client[]>([])
    const [loading, setLoading] = useState(true)
    const [search, setSearch] = useState('')
    const [showCreateModal, setShowCreateModal] = useState(false)
    const [currentPage, setCurrentPage] = useState(1)
    const { toasts, dismiss, success, error: showError } = useToast()
    const [fetchError, setFetchError] = useState<string | null>(null)

    const fetchClients = async () => {
        setFetchError(null)
        try {
            const data = await api.getClients()
            setClients(data)
        } catch (err: any) {
            console.error('Failed to fetch clients:', err)
            setFetchError(err.message || 'Failed to fetch clients')
        } finally {
            setLoading(false)
        }
    }

    const handleDelete = async (id: number) => {
        if (!confirm('Are you sure you want to delete this client? This action cannot be undone.')) return
        
        try {
            await api.deleteClient(id)
            setClients(prev => prev.filter(c => c.id !== id))
            success('Client deleted successfully')
        } catch (err: any) {
            console.error('Failed to delete client:', err)
            showError(err.message || 'Failed to delete client')
        }
    }

    const filteredClients = clients.filter(c => 
        c.name.toLowerCase().includes(search.toLowerCase()) ||
        c.slug.toLowerCase().includes(search.toLowerCase())
    )

    // Pagination
    const totalPages = Math.ceil(filteredClients.length / ITEMS_PER_PAGE)
    const paginatedClients = filteredClients.slice(
        (currentPage - 1) * ITEMS_PER_PAGE,
        currentPage * ITEMS_PER_PAGE
    )

    return (
        <div>
            <div className="flex items-center justify-between mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Clients</h1>
                <button
                    onClick={() => setShowCreateModal(true)}
                    className="bg-revolt-red text-white px-4 py-2 rounded-lg font-medium hover:bg-red-700 transition flex items-center gap-2"
                >
                    <Plus size={18} />
                    Add Client
                </button>
            </div>

            {/* Search */}
            <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm mb-6">
                <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                    <input
                        type="text"
                        placeholder="Search clients..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-10 pr-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-revolt-red focus:border-revolt-red outline-none"
                    />
                </div>
            </div>

            {/* Clients Table */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                            <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Client</th>
                            <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Slug</th>
                            <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Status</th>
                            <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Created</th>
                            <th className="text-right px-6 py-4 text-sm font-semibold text-gray-600">Actions</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {paginatedClients.map((client) => (
                            <tr key={client.id} className="hover:bg-gray-50 transition">
                                <td className="px-6 py-4">
                                    <Link href={`/admin/clients/${client.id}`} className="font-medium text-gray-900 hover:text-revolt-red transition">
                                        {client.name}
                                    </Link>
                                </td>
                                <td className="px-6 py-4 text-gray-500">{client.slug}</td>
                                <td className="px-6 py-4">
                                    <StatusBadge status={client.is_active ? 'active' : 'inactive'} />
                                </td>
                                <td className="px-6 py-4 text-gray-500">
                                    {new Date(client.created_at).toLocaleDateString()}
                                </td>
                                <td className="px-6 py-4 text-right">
                                    <div className="flex items-center justify-end gap-2">
                                        <Link
                                            href={`/admin/clients/${client.id}`}
                                            className="p-2 text-gray-400 hover:text-blue-600 transition"
                                        >
                                            <Edit size={16} />
                                        </Link>
                                        <button 
                                            onClick={() => handleDelete(client.id)}
                                            className="p-2 text-gray-400 hover:text-red-600 transition"
                                            title="Delete client"
                                        >
                                            <Trash2 size={16} />
                                        </button>
                                    </div>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {paginatedClients.length === 0 && (
                    <div className="p-8 text-center text-gray-500">
                        {search ? 'No clients match your search' : 'No clients yet. Create your first client!'}
                    </div>
                )}

                {/* Pagination */}
                {!loading && filteredClients.length > ITEMS_PER_PAGE && (
                    <div className="p-4 border-t border-gray-200 flex items-center justify-between">
                        <span className="text-sm text-gray-500">
                            Showing {((currentPage - 1) * ITEMS_PER_PAGE) + 1} - {Math.min(currentPage * ITEMS_PER_PAGE, filteredClients.length)} of {filteredClients.length}
                        </span>
                        <div className="flex gap-2">
                            <button
                                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                                disabled={currentPage === 1}
                                className="px-3 py-1 border border-gray-200 rounded-lg disabled:opacity-50 hover:bg-gray-50 transition"
                            >
                                <ChevronLeft size={16} />
                            </button>
                            <span className="px-3 py-1 text-sm text-gray-600">
                                Page {currentPage} of {totalPages}
                            </span>
                            <button
                                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                                disabled={currentPage === totalPages}
                                className="px-3 py-1 border border-gray-200 rounded-lg disabled:opacity-50 hover:bg-gray-50 transition"
                            >
                                <ChevronRight size={16} />
                            </button>
                        </div>
                    </div>
                )}
            </div>

            {/* Error Display */}
            {fetchError && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-red-700">
                    <AlertCircle size={20} />
                    <span>{fetchError}</span>
                    <button 
                        onClick={() => setFetchError(null)}
                        className="ml-auto text-sm font-medium hover:underline"
                    >
                        Dismiss
                    </button>
                </div>
            )}

            {toasts.map(t => (
                <Toast key={t.id} message={t.message} type={t.type} onDismiss={() => dismiss(t.id)} />
            ))}

            {/* Create Modal - simplified, expand later */}
            {showCreateModal && (
                <CreateClientModal 
                    onClose={() => setShowCreateModal(false)} 
                    onCreated={fetchClients}
                    onSuccess={() => success('Client created successfully')}
                />
            )}
        </div>
    )
}

function CreateClientModal({ onClose, onCreated, onSuccess }: { onClose: () => void; onCreated: () => void; onSuccess: () => void }) {
    const [name, setName] = useState('')
    const [slug, setSlug] = useState('')
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    // Auto-generate slug from name
    const handleNameChange = (value: string) => {
        setName(value)
        if (!slug) {
            setSlug(value.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, ''))
        }
    }

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError(null)
        
        try {
            await api.createClient({ name, slug })
            onCreated()
            onSuccess()
            onClose()
        } catch (err: any) {
            console.error('Failed to create client:', err)
            setError(err.message || 'Failed to create client')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-6 w-full max-w-md">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Create New Client</h2>
                {error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                        {error}
                    </div>
                )}
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Client Name</label>
                        <input
                            type="text"
                            value={name}
                            onChange={(e) => handleNameChange(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-revolt-red focus:border-revolt-red outline-none"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Slug</label>
                        <input
                            type="text"
                            value={slug}
                            onChange={(e) => setSlug(e.target.value)}
                            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-revolt-red focus:border-revolt-red outline-none"
                            required
                        />
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
                            {loading ? 'Creating...' : 'Create Client'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
