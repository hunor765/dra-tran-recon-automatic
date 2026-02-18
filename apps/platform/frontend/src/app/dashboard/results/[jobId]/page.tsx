'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Download, FileText, TrendingUp, AlertTriangle, CheckCircle, FileSpreadsheet } from 'lucide-react'
import { api } from '@/lib/api/client'
import { HeroStat } from '@/components/dashboard/HeroStat'
import { TrendChart } from '@/components/dashboard/TrendChart'

export default function JobResultsPage() {
    const params = useParams()
    const jobId = params.jobId as string
    
    const [job, setJob] = useState<any>(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        if (jobId) {
            fetchJob()
        }
    }, [jobId])

    const fetchJob = async () => {
        try {
            const data = await api.getJob(Number(jobId))
            setJob(data)
        } catch (error) {
            console.error('Failed to fetch job:', error)
        } finally {
            setLoading(false)
        }
    }

    const exportResults = async (format: 'csv' | 'json' | 'excel') => {
        try {
            // Get the API URL from environment or use default
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
            
            // Get auth token from Supabase session
            const { createClient } = await import('@/lib/supabase/client')
            const supabase = createClient()
            const { data: { session } } = await supabase.auth.getSession()
            
            if (!session?.access_token) {
                alert('Please log in to export results')
                return
            }
            
            const endpoint = format === 'excel' 
                ? `${apiUrl}/api/v1/jobs/${jobId}/export/excel`
                : `${apiUrl}/api/v1/jobs/${jobId}/export?format=${format}`
            
            const response = await fetch(endpoint, {
                headers: {
                    'Authorization': `Bearer ${session.access_token}`
                }
            })
            
            if (!response.ok) {
                const error = await response.json()
                throw new Error(error.detail || 'Export failed')
            }
            
            // Get filename from Content-Disposition header
            const contentDisposition = response.headers.get('content-disposition')
            const filenameMatch = contentDisposition?.match(/filename="?([^"]+)"?/)
            const filename = filenameMatch?.[1] || `export.${format === 'excel' ? 'xlsx' : format}`
            
            // Download the file
            const blob = await response.blob()
            const url = window.URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.href = url
            link.download = filename
            document.body.appendChild(link)
            link.click()
            document.body.removeChild(link)
            window.URL.revokeObjectURL(url)
            
        } catch (error) {
            console.error('Export failed:', error)
            alert(`Export failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
        }
    }

    if (loading) {
        return <div className="min-h-screen bg-gray-50 p-8 text-center">Loading...</div>
    }

    if (!job) {
        return <div className="min-h-screen bg-gray-50 p-8 text-center">Job not found</div>
    }

    // Parse result_summary if it's a string
    let results = null
    try {
        results = job.result_summary ? JSON.parse(job.result_summary) : null
    } catch (e) {
        console.error('Failed to parse results:', e)
        results = null
    }

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="mb-8">
                    <Link href="/dashboard" className="text-gray-500 hover:text-gray-900 flex items-center gap-1 mb-4">
                        <ArrowLeft size={16} />
                        Back to Dashboard
                    </Link>
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-gray-900">Job Results #{job.id}</h1>
                            <p className="text-gray-500 mt-1">
                                {job.client_name} • {new Date(job.last_run).toLocaleString()}
                            </p>
                        </div>
                        <div className="flex gap-3">
                            <button
                                onClick={() => exportResults('csv')}
                                className="px-4 py-2 bg-white border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition flex items-center gap-2"
                            >
                                <Download size={18} />
                                Export CSV
                            </button>
                            <button
                                onClick={() => exportResults('json')}
                                className="px-4 py-2 bg-white border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition flex items-center gap-2"
                            >
                                <FileText size={18} />
                                Export JSON
                            </button>
                            <button
                                onClick={() => exportResults('excel')}
                                className="px-4 py-2 bg-white border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition flex items-center gap-2"
                            >
                                <FileSpreadsheet size={18} />
                                Export Excel
                            </button>
                        </div>
                    </div>
                </div>

                {/* Status Banner */}
                {job.status === 'completed' && results ? (
                    <>
                        {/* Hero Stats */}
                        <HeroStat
                            totalBackend={results.total_backend_value || 0}
                            totalGa4={results.total_ga4_value || 0}
                            matchRate={results.match_rate || 0}
                            missingOrders={results.missing_count || 0}
                        />

                        {/* Missing Orders */}
                        {results.missing_ids && results.missing_ids.length > 0 && (
                            <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden mt-6">
                                <div className="p-6 border-b border-gray-100">
                                    <h3 className="font-bold text-lg text-gray-900 flex items-center gap-2">
                                        <AlertTriangle className="text-revolt-red" size={20} />
                                        Missing Orders ({results.missing_ids.length})
                                    </h3>
                                </div>
                                <div className="p-6">
                                    <div className="bg-gray-50 p-4 rounded-lg font-mono text-sm max-h-64 overflow-y-auto">
                                        {results.missing_ids.map((id: string) => (
                                            <div key={id} className="py-1">{id}</div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}
                    </>
                ) : job.status === 'failed' ? (
                    <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
                        <AlertTriangle className="text-red-500 mx-auto mb-4" size={48} />
                        <h2 className="text-xl font-bold text-red-900 mb-2">Job Failed</h2>
                        <p className="text-red-700">{job.logs || 'An error occurred during reconciliation'}</p>
                    </div>
                ) : (
                    <div className="bg-blue-50 border border-blue-200 rounded-xl p-8 text-center">
                        <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                        <h2 className="text-xl font-bold text-blue-900">Job In Progress</h2>
                        <p className="text-blue-700">Please wait while we process your data...</p>
                    </div>
                )}
            </div>
        </div>
    )
}
