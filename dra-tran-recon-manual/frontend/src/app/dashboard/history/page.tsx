'use client'

import { useEffect, useState } from 'react'
import { Clock, AlertCircle } from 'lucide-react'
import { api } from '@/lib/api/client'

interface Job {
    id: number
    client_id: number
    client_name?: string | null
    status: string
    last_run: string | null
    result_summary: string | null
}

export default function HistoryPage() {
    const [jobs, setJobs] = useState<Job[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetchJobs()
    }, [])

    const fetchJobs = async () => {
        setError(null)
        try {
            const data = await api.getJobs({ limit: 50 })
            setJobs(data)
        } catch (err: any) {
            console.error('Failed to fetch jobs:', err)
            setError(err.message || 'Failed to fetch jobs')
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="w-8 h-8 border-4 border-revolt-red border-t-transparent rounded-full animate-spin"></div>
            </div>
        )
    }

    return (
        <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-6">Reconciliation History</h1>
            
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

            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
                <table className="w-full">
                    <thead className="bg-gray-50 border-b border-gray-200">
                        <tr>
                            <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Job ID</th>
                            <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Status</th>
                            <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Date</th>
                            <th className="text-left px-6 py-4 text-sm font-semibold text-gray-600">Results</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-100">
                        {jobs.map((job) => (
                            <tr key={job.id} className="hover:bg-gray-50 transition">
                                <td className="px-6 py-4 font-medium text-gray-900">#{job.id}</td>
                                <td className="px-6 py-4">
                                    <StatusBadge status={job.status} />
                                </td>
                                <td className="px-6 py-4 text-gray-500">
                                    {job.last_run ? new Date(job.last_run).toLocaleString() : 'Pending'}
                                </td>
                                <td className="px-6 py-4">
                                    {job.result_summary ? (
                                        <span className="text-green-600 font-medium">Available</span>
                                    ) : (
                                        <span className="text-gray-400">-</span>
                                    )}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
                {jobs.length === 0 && (
                    <div className="p-8 text-center text-gray-500">
                        <Clock size={48} className="mx-auto mb-4 text-gray-300" />
                        <p>No reconciliation jobs yet.</p>
                    </div>
                )}
            </div>
        </div>
    )
}

function StatusBadge({ status }: { status: string }) {
    const styles: Record<string, string> = {
        completed: 'bg-green-100 text-green-700',
        running: 'bg-blue-100 text-blue-700',
        pending: 'bg-yellow-100 text-yellow-700',
        failed: 'bg-red-100 text-red-700',
    }
    
    return (
        <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[status] || 'bg-gray-100 text-gray-700'}`}>
            {status}
        </span>
    )
}
