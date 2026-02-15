'use client'

import { useEffect, useState } from 'react'
import Link from 'next/link'
import { Clock, Filter, RefreshCw, Play, AlertCircle, Loader2, ChevronLeft, ChevronRight } from 'lucide-react'
import { api } from '@/lib/api/client'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { TableSkeleton } from '@/components/ui/LoadingSkeleton'
import { useToast, Toast } from '@/components/ui/Toast'

interface Job {
    id: number
    client_id: number
    client_name?: string | null
    status: string
    last_run: string | null
    result_summary: string | null
}

const ITEMS_PER_PAGE = 10

export default function JobsPage() {
    const [jobs, setJobs] = useState<Job[]>([])
    const [loading, setLoading] = useState(true)
    const [filter, setFilter] = useState({ status: '', client_id: '' })
    const [error, setError] = useState<string | null>(null)
    const [clients, setClients] = useState<{id: number, name: string}[]>([])
    const [runningForClient, setRunningForClient] = useState<number | null>(null)
    const [currentPage, setCurrentPage] = useState(1)
    const { toasts, dismiss, success, error: showError } = useToast()

    useEffect(() => {
        fetchJobs()
        fetchClients()
    }, [filter])

    const fetchClients = async () => {
        try {
            const data = await api.getClients()
            setClients(data.map(c => ({ id: c.id, name: c.name })))
        } catch (err) {
            console.error('Failed to fetch clients:', err)
        }
    }

    const fetchJobs = async () => {
        setLoading(true)
        setError(null)
        try {
            const data = await api.getAdminJobs({ 
                status: filter.status || undefined, 
                client_id: filter.client_id ? parseInt(filter.client_id) : undefined 
            })
            setJobs(data)
        } catch (err: any) {
            console.error('Failed to fetch jobs:', err)
            setError(err.message || 'Failed to fetch jobs')
        } finally {
            setLoading(false)
        }
    }

    const handleRunJob = async (clientId: number) => {
        setRunningForClient(clientId)
        setError(null)
        try {
            await api.runJob(clientId)
            success('Job started successfully')
            // Refresh jobs list
            await fetchJobs()
        } catch (err: any) {
            console.error('Failed to run job:', err)
            showError(err.message || 'Failed to run job')
        } finally {
            setRunningForClient(null)
        }
    }

    // Pagination
    const filteredJobs = jobs
    const totalPages = Math.ceil(filteredJobs.length / ITEMS_PER_PAGE)
    const paginatedJobs = filteredJobs.slice(
        (currentPage - 1) * ITEMS_PER_PAGE,
        currentPage * ITEMS_PER_PAGE
    )

    return (
        <div>
            {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3 text-red-700">
                    <AlertCircle size={20} />
                    <span>{error}</span>
                    <button 
                        onClick={() => setError(null)}
                        className="ml-auto text-sm font-medium hover:underline"
                    >
                        Dismiss
                    </button>
                </div>
            )}

            <div className="flex items-center justify-between mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Jobs</h1>
                <button
                    onClick={fetchJobs}
                    className="px-4 py-2 bg-white border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition flex items-center gap-2"
                >
                    <RefreshCw size={18} />
                    Refresh
                </button>
            </div>

            {/* Filters */}
            <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm mb-6 flex gap-4 items-center">
                <select
                    value={filter.status}
                    onChange={(e) => setFilter({ ...filter, status: e.target.value })}
                    className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-revolt-red focus:border-revolt-red outline-none"
                >
                    <option value="">All Statuses</option>
                    <option value="completed">Completed</option>
                    <option value="running">Running</option>
                    <option value="pending">Pending</option>
                    <option value="failed">Failed</option>
                </select>

                <div className="h-6 w-px bg-gray-200"></div>

                <span className="text-sm text-gray-500">Run for client:</span>
                <select
                    value={runningForClient || ''}
                    onChange={(e) => {
                        const clientId = parseInt(e.target.value)
                        if (clientId) handleRunJob(clientId)
                    }}
                    disabled={runningForClient !== null}
                    className="px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-revolt-red focus:border-revolt-red outline-none"
                >
                    <option value="">Select client...</option>
                    {clients.map(client => (
                        <option key={client.id} value={client.id}>{client.name}</option>
                    ))}
                </select>
                {runningForClient && <Loader2 size={18} className="animate-spin text-revolt-red" />}
            </div>

            {/* Jobs Table */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                {loading ? (
                    <TableSkeleton rows={5} columns={5} />
                ) : (
                    <>
                        <table className="w-full">
                            <thead className="bg-gray-50 border-b border-gray-200">
                                <tr>
                                    <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Job ID</th>
                                    <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Client</th>
                                    <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Status</th>
                                    <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Last Run</th>
                                    <th className="text-right px-6 py-4 text-sm font-semibold text-gray-600">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100">
                                {paginatedJobs.map((job) => (
                                    <tr key={job.id} className="hover:bg-gray-50 transition">
                                        <td className="px-6 py-4 font-medium text-gray-900">#{job.id}</td>
                                        <td className="px-6 py-4 text-gray-700">{job.client_name || '-'}</td>
                                        <td className="px-6 py-4">
                                            <StatusBadge status={job.status} />
                                        </td>
                                        <td className="px-6 py-4 text-gray-500">
                                            {job.last_run ? new Date(job.last_run).toLocaleString() : 'Pending'}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <Link
                                                href={`/admin/jobs/${job.id}`}
                                                className="text-revolt-red hover:text-red-700 font-medium text-sm"
                                            >
                                                View
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                        {filteredJobs.length === 0 && (
                            <div className="p-8 text-center text-gray-500">No jobs found</div>
                        )}

                        {/* Pagination */}
                        {filteredJobs.length > ITEMS_PER_PAGE && (
                            <div className="p-4 border-t border-gray-200 flex items-center justify-between">
                                <span className="text-sm text-gray-500">
                                    Showing {((currentPage - 1) * ITEMS_PER_PAGE) + 1} - {Math.min(currentPage * ITEMS_PER_PAGE, filteredJobs.length)} of {filteredJobs.length}
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
                    </>
                )}
            </div>
        </div>
    )
}


