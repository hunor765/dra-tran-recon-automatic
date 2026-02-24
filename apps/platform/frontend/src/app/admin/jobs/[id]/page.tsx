'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Clock, AlertCircle, RefreshCw, Loader2 } from 'lucide-react'
import { api } from '@/lib/api/client'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { CardSkeleton, Skeleton } from '@/components/ui/LoadingSkeleton'

interface JobDetail {
    id: number
    client_id: number
    client_name?: string | null
    status: string
    started_at: string | null
    completed_at: string | null
    last_run: string | null
    created_at?: string
    result_summary: any
    logs: string | null
    days: number
    start_date: string | null
    end_date: string | null
    retry_count: number
    max_retries: number
    can_retry?: boolean
}

export default function JobDetailPage() {
    const params = useParams()
    const jobId = parseInt(params.id as string)

    const [job, setJob] = useState<JobDetail | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        if (jobId) {
            fetchJob()
        }
    }, [jobId])

    const fetchJob = async () => {
        setError(null)
        try {
            const data = await api.getJob(jobId)
            setJob(data)
        } catch (err: any) {
            console.error('Failed to fetch job:', err)
            setError(err.message || 'Failed to fetch job details')
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="space-y-6">
                <Skeleton className="h-8 w-64" />
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    <CardSkeleton />
                    <CardSkeleton />
                    <CardSkeleton />
                </div>
            </div>
        )
    }

    if (error || !job) {
        return (
            <div className="text-center py-12">
                <AlertCircle size={48} className="mx-auto text-red-400 mb-4" />
                <p className="text-gray-500">{error || 'Job not found'}</p>
                <Link href="/admin/jobs" className="text-revolt-red hover:underline mt-4 inline-block">
                    Back to Jobs
                </Link>
            </div>
        )
    }

    return (
        <div>
            {/* Header */}
            <div className="mb-8">
                <Link href="/admin/jobs" className="text-gray-500 hover:text-gray-900 flex items-center gap-1 mb-4">
                    <ArrowLeft size={16} />
                    Back to Jobs
                </Link>
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">Job #{job.id}</h1>
                        <p className="text-gray-500 mt-1">Client: {job.client_name}</p>
                    </div>
                    <StatusBadge status={job.status} />
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                    <div className="flex items-center gap-3 mb-2">
                        <Clock className="text-blue-600" size={20} />
                        <span className="text-gray-500">Created</span>
                    </div>
                    <p className="text-lg font-semibold text-gray-900">
                        {job.created_at ? new Date(job.created_at).toLocaleString() : 'N/A'}
                    </p>
                </div>
                <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                    <div className="flex items-center gap-3 mb-2">
                        <Clock className="text-purple-600" size={20} />
                        <span className="text-gray-500">Started</span>
                    </div>
                    <p className="text-lg font-semibold text-gray-900">
                        {job.started_at ? new Date(job.started_at).toLocaleString() : 'Pending'}
                    </p>
                </div>
                <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                    <div className="flex items-center gap-3 mb-2">
                        <Clock className="text-green-600" size={20} />
                        <span className="text-gray-500">Completed</span>
                    </div>
                    <p className="text-lg font-semibold text-gray-900">
                        {job.completed_at ? new Date(job.completed_at).toLocaleString() : 'N/A'}
                    </p>
                </div>
            </div>

            {/* Result Summary */}
            {job.result_summary && (
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm mb-8">
                    <div className="p-6 border-b border-gray-100">
                        <h2 className="text-lg font-bold text-gray-900">Results</h2>
                    </div>
                    <div className="p-6">
                        <pre className="bg-gray-50 p-4 rounded-lg text-sm text-gray-800 overflow-auto">
                            {JSON.stringify(job.result_summary, null, 2)}
                        </pre>
                    </div>
                </div>
            )}

            {/* Logs */}
            {job.logs && (
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm mb-8">
                    <div className="p-6 border-b border-gray-100">
                        <h2 className="text-lg font-bold text-gray-900">Logs</h2>
                    </div>
                    <div className="p-6">
                        <pre className="bg-gray-50 p-4 rounded-lg text-sm text-gray-800 overflow-auto whitespace-pre-wrap">
                            {job.logs}
                        </pre>
                    </div>
                </div>
            )}

            {/* Retry Info */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
                <div className="p-6 border-b border-gray-100">
                    <h2 className="text-lg font-bold text-gray-900">Configuration</h2>
                </div>
                <div className="p-6 grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div>
                        <p className="text-sm text-gray-500">Days</p>
                        <p className="font-semibold text-gray-900">{job.days}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">Date Range</p>
                        <p className="font-semibold text-gray-900">
                            {job.start_date && job.end_date
                                ? `${job.start_date} → ${job.end_date}`
                                : `Last ${job.days} days`}
                        </p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">Retry Count</p>
                        <p className="font-semibold text-gray-900">{job.retry_count} / {job.max_retries}</p>
                    </div>
                    <div>
                        <p className="text-sm text-gray-500">Can Retry</p>
                        <p className="font-semibold text-gray-900">{job.can_retry ? 'Yes' : 'No'}</p>
                    </div>
                </div>
            </div>
        </div>
    )
}
