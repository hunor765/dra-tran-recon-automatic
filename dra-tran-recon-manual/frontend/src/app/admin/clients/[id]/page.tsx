'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Settings, Users, Clock, Activity, Plus, AlertCircle, Play, Loader2 } from 'lucide-react'
import { api } from '@/lib/api/client'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { CardSkeleton, Skeleton } from '@/components/ui/LoadingSkeleton'
import { useToast, Toast } from '@/components/ui/Toast'

interface Client {
    id: number
    name: string
    slug: string
    logo_url: string | null
    is_active: boolean
    created_at: string
}

interface Connector {
    id: number
    type: string
    is_active: boolean
    created_at?: string
}

interface Job {
    id: number
    status: string
    last_run: string | null
    result_summary: string | null
}

export default function ClientDetailPage() {
    const params = useParams()
    const clientId = parseInt(params.id as string)
    
    const [client, setClient] = useState<Client | null>(null)
    const [connectors, setConnectors] = useState<Connector[]>([])
    const [jobs, setJobs] = useState<Job[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [runningJob, setRunningJob] = useState(false)
    const { toasts, dismiss, success, error: showError } = useToast()

    useEffect(() => {
        if (clientId) {
            fetchClientData()
        }
    }, [clientId])

    const fetchClientData = async () => {
        setError(null)
        try {
            // Fetch all data in parallel
            const [clientData, connectorsData, jobsData] = await Promise.all([
                api.getClient(clientId),
                api.getConnectors(clientId),
                api.getJobs({ client_id: clientId, limit: 5 })
            ])
            setClient(clientData)
            setConnectors(connectorsData)
            setJobs(jobsData)
        } catch (err: any) {
            console.error('Failed to fetch client data:', err)
            setError(err.message || 'Failed to fetch client data')
        } finally {
            setLoading(false)
        }
    }

    const handleRunJob = async () => {
        setRunningJob(true)
        setError(null)
        try {
            await api.runJob(clientId)
            success('Reconciliation job started successfully')
            // Refresh jobs list after starting
            await fetchClientData()
        } catch (err: any) {
            console.error('Failed to run job:', err)
            showError(err.message || 'Failed to run reconciliation job')
        } finally {
            setRunningJob(false)
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
                <Skeleton className="h-64 w-full" />
            </div>
        )
    }

    if (!client) {
        return (
            <div className="text-center py-12">
                <AlertCircle size={48} className="mx-auto text-red-400 mb-4" />
                <p className="text-gray-500">Client not found</p>
            </div>
        )
    }

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
            {/* Header */}
            <div className="mb-8">
                <Link href="/admin/clients" className="text-gray-500 hover:text-gray-900 flex items-center gap-1 mb-4">
                    <ArrowLeft size={16} />
                    Back to Clients
                </Link>
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold text-gray-900">{client.name}</h1>
                        <p className="text-gray-500 mt-1">{client.slug}</p>
                    </div>
                    <div className="flex gap-3">
                        <button
                            onClick={handleRunJob}
                            disabled={runningJob}
                            className="px-4 py-2 bg-revolt-red text-white rounded-lg font-medium hover:bg-red-700 transition flex items-center gap-2 disabled:opacity-50"
                        >
                            {runningJob ? <Loader2 size={18} className="animate-spin" /> : <Play size={18} />}
                            {runningJob ? 'Running...' : 'Run Now'}
                        </button>
                        <Link
                            href={`/admin/clients/${params.id}/connectors`}
                            className="px-4 py-2 bg-white border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition flex items-center gap-2"
                        >
                            <Settings size={18} />
                            Connectors
                        </Link>
                        <Link
                            href={`/admin/clients/${params.id}/users`}
                            className="px-4 py-2 bg-white border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition flex items-center gap-2"
                        >
                            <Users size={18} />
                            Users
                        </Link>
                    </div>
                </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                    <div className="flex items-center gap-3 mb-2">
                        <Settings className="text-blue-600" size={20} />
                        <span className="text-gray-500">Connectors</span>
                    </div>
                    <p className="text-2xl font-bold text-gray-900">{connectors.length}</p>
                </div>
                <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                    <div className="flex items-center gap-3 mb-2">
                        <Clock className="text-purple-600" size={20} />
                        <span className="text-gray-500">Total Jobs</span>
                    </div>
                    <p className="text-2xl font-bold text-gray-900">{jobs.length}</p>
                </div>
                <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                    <div className="flex items-center gap-3 mb-2">
                        <Activity className="text-green-600" size={20} />
                        <span className="text-gray-500">Status</span>
                    </div>
                    <p className="text-2xl font-bold text-gray-900">
                        {client.is_active ? 'Active' : 'Inactive'}
                    </p>
                </div>
            </div>

            {/* Connectors Section */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm mb-8">
                <div className="p-6 border-b border-gray-100 flex items-center justify-between">
                    <h2 className="text-lg font-bold text-gray-900">Connectors</h2>
                    <Link
                        href={`/admin/clients/${clientId}/connectors`}
                        className="text-revolt-red hover:text-red-700 font-medium text-sm flex items-center gap-1"
                    >
                        <Plus size={16} />
                        Add Connector
                    </Link>
                </div>
                <div className="divide-y divide-gray-100">
                    {connectors.map((connector) => (
                        <div key={connector.id} className="p-4 flex items-center justify-between hover:bg-gray-50">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-lg bg-gray-100 flex items-center justify-center">
                                    {connector.type === 'ga4' ? 'G' : connector.type === 'shopify' ? 'S' : 'W'}
                                </div>
                                <div>
                                    <p className="font-medium text-gray-900 capitalize">{connector.type}</p>
                                    <p className="text-sm text-gray-500">ID: {connector.id}</p>
                                </div>
                            </div>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${connector.is_active ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-700'}`}>
                                {connector.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </div>
                    ))}
                    {connectors.length === 0 && (
                        <div className="p-8 text-center text-gray-500">
                            No connectors configured. <Link href={`/admin/clients/${params.id}/connectors`} className="text-revolt-red hover:underline">Add one</Link>
                        </div>
                    )}
                </div>
            </div>

            {/* Recent Jobs Section */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
                <div className="p-6 border-b border-gray-100">
                    <h2 className="text-lg font-bold text-gray-900">Recent Jobs</h2>
                </div>
                <div className="divide-y divide-gray-100">
                    {jobs.map((job) => (
                        <div key={job.id} className="p-4 flex items-center justify-between hover:bg-gray-50">
                            <div>
                                <p className="font-medium text-gray-900">Job #{job.id}</p>
                                <p className="text-sm text-gray-500">{job.last_run ? new Date(job.last_run).toLocaleString() : 'Pending'}</p>
                            </div>
                            <StatusBadge status={job.status} />
                        </div>
                    ))}
                    {jobs.length === 0 && (
                        <div className="p-8 text-center text-gray-500">
                            No jobs yet. <button className="text-revolt-red hover:underline">Run first reconciliation</button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}


