'use client'

import { useState, useEffect, useCallback } from 'react'
import { api } from '../api/client'

interface Job {
    id: number
    client_id: number
    client_name?: string | null
    status: string
    last_run: string | null
    result_summary: string | null
}

export function useJobs(params?: { client_id?: number; status?: string; limit?: number }) {
    const [jobs, setJobs] = useState<Job[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    
    const fetchJobs = useCallback(async () => {
        setLoading(true)
        setError(null)
        try {
            const data = await api.getJobs(params)
            setJobs(data)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch jobs')
        } finally {
            setLoading(false)
        }
    }, [params?.client_id, params?.status, params?.limit])
    
    useEffect(() => {
        fetchJobs()
    }, [fetchJobs])
    
    const runJob = async (clientId: number) => {
        const newJob = await api.runJob(clientId)
        setJobs(prev => [newJob, ...prev])
        return newJob
    }
    
    return { jobs, loading, error, refetch: fetchJobs, runJob }
}

export function useJob(id: number | null) {
    const [job, setJob] = useState<Job | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    
    useEffect(() => {
        if (!id) {
            setLoading(false)
            return
        }
        
        api.getJob(id)
            .then(setJob)
            .catch(err => setError(err.message))
            .finally(() => setLoading(false))
    }, [id])
    
    return { job, loading, error }
}
