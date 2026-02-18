'use client'

import { useEffect, useState } from 'react'
import { Briefcase, Clock, CheckCircle, AlertCircle, TrendingUp, Activity } from 'lucide-react'
import { api } from '@/lib/api/client'
import { StatusBadge } from '@/components/ui/StatusBadge'
import { CardSkeleton, TableSkeleton } from '@/components/ui/LoadingSkeleton'

interface JobResult {
    match_rate: number
    total_backend_value: number
    total_ga4_value: number
    missing_count: number
    missing_ids: string[]
    ga4_records: number
    backend_records: number
}

interface AdminStats {
    total_clients: number
    active_clients: number
    total_jobs: number
    jobs_by_status: Record<string, number>
    recent_jobs: Array<{
        id: number
        client_id: number
        client_name?: string | null
        status: string
        last_run: string | null
        result_summary: JobResult | null
    }>
}

export default function AdminDashboard() {
    const [stats, setStats] = useState<AdminStats | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetchStats()
    }, [])

    const fetchStats = async () => {
        setError(null)
        try {
            const data = await api.getAdminStats()
            setStats(data)
        } catch (err: any) {
            console.error('Failed to fetch stats:', err)
            setError(err.message || 'Failed to fetch stats')
        } finally {
            setLoading(false)
        }
    }

    if (loading) {
        return (
            <div className="space-y-8">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <CardSkeleton />
                    <CardSkeleton />
                    <CardSkeleton />
                    <CardSkeleton />
                </div>
                <TableSkeleton rows={5} columns={4} />
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
            <h1 className="text-3xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>
            
            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatCard
                    title="Total Clients"
                    value={stats?.total_clients || 0}
                    icon={Briefcase}
                    color="blue"
                />
                <StatCard
                    title="Active Clients"
                    value={stats?.active_clients || 0}
                    icon={CheckCircle}
                    color="green"
                />
                <StatCard
                    title="Total Jobs"
                    value={stats?.total_jobs || 0}
                    icon={Clock}
                    color="purple"
                />
                <StatCard
                    title="Success Rate"
                    value="94%"
                    icon={TrendingUp}
                    color="orange"
                />
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm">
                <div className="p-6 border-b border-gray-100">
                    <h2 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                        <Activity size={20} className="text-revolt-red" />
                        Recent Activity
                    </h2>
                </div>
                <div className="divide-y divide-gray-100">
                    {stats?.recent_jobs?.map((job) => (
                        <div key={job.id} className="p-4 hover:bg-gray-50 transition">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="font-medium text-gray-900">{job.client_name}</p>
                                    <p className="text-sm text-gray-500">
                                        Job #{job.id} • {job.last_run ? new Date(job.last_run).toLocaleString() : 'Pending'}
                                    </p>
                                </div>
                                <StatusBadge status={job.status} size="md" />
                            </div>
                        </div>
                    )) || (
                        <div className="p-8 text-center text-gray-500">No recent activity</div>
                    )}
                </div>
            </div>
        </div>
    )
}

function StatCard({ title, value, icon: Icon, color }: { title: string; value: number | string; icon: any; color: string }) {
    const colors: Record<string, string> = {
        blue: 'bg-blue-50 text-blue-600',
        green: 'bg-green-50 text-green-600',
        purple: 'bg-purple-50 text-purple-600',
        orange: 'bg-orange-50 text-orange-600',
    }
    
    return (
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-sm font-medium text-gray-500">{title}</p>
                    <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
                </div>
                <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${colors[color]}`}>
                    <Icon size={24} />
                </div>
            </div>
        </div>
    )
}
