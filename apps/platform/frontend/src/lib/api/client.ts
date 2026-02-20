import { createClient } from '@/lib/supabase/client'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Debug: Log the actual API URL being used
if (typeof window !== 'undefined') {
    console.log('[API Client] NEXT_PUBLIC_API_URL:', process.env.NEXT_PUBLIC_API_URL)
    console.log('[API Client] API_URL used:', API_URL)
}

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
    client_id: number
    type: string
    config_json?: string
    is_active: boolean
    created_at?: string
}

interface JobResult {
    match_rate: number
    total_backend_value: number
    total_ga4_value: number
    missing_count: number
    missing_ids: string[]
    ga4_records: number
    backend_records: number
}

interface Job {
    id: number
    client_id: number
    client_name?: string | null
    status: 'pending' | 'running' | 'completed' | 'failed' | 'retrying'
    last_run: string | null
    result_summary: JobResult | null
    logs: string | null
    days: number
    start_date: string | null
    end_date: string | null
    retry_count: number
    max_retries: number
    can_retry?: boolean
}

class DraApiClient {
    private baseUrl: string
    
    constructor() {
        // Remove trailing slash to avoid double slashes in URLs
        this.baseUrl = API_URL.replace(/\/$/, '')
    }
    
    private async getValidToken(): Promise<string | null> {
        const supabase = createClient()
        
        // First try to get existing session
        const { data: { session }, error: sessionError } = await supabase.auth.getSession()
        
        if (sessionError) {
            console.error('[API Client] Error getting session:', sessionError)
        }
        
        if (session?.access_token) {
            console.log('[API Client] Got token from session:', session.access_token.substring(0, 20) + '...')
            return session.access_token
        }
        
        // If no session, try to refresh
        console.log('[API Client] No session found, attempting refresh...')
        const { data: { session: refreshedSession }, error: refreshError } = await supabase.auth.refreshSession()
        
        if (refreshError) {
            console.error('[API Client] Error refreshing session:', refreshError)
            return null
        }
        
        if (refreshedSession?.access_token) {
            console.log('[API Client] Got token from refresh:', refreshedSession.access_token.substring(0, 20) + '...')
            return refreshedSession.access_token
        }
        
        console.error('[API Client] No token available - user may not be logged in')
        return null
    }
    
    private async fetch(path: string, options: RequestInit = {}) {
        const url = `${this.baseUrl}${path}`
        
        // Debug: Log the actual URL being fetched
        if (typeof window !== 'undefined') {
            console.log('[API Client] Fetching URL:', url)
        }
        
        // Get valid token (with refresh if needed)
        const token = await this.getValidToken()
        
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            ...options.headers as Record<string, string>,
        }
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`
            console.log('[API Client] Authorization header set')
        } else {
            console.warn('[API Client] No token available - request will be unauthorized')
        }
        
        const response = await fetch(url, {
            ...options,
            headers,
        })
        
        if (!response.ok) {
            const errorText = await response.text()
            console.error(`[API Client] HTTP ${response.status} error:`, errorText)
            
            // If unauthorized, try to refresh token once and retry
            if (response.status === 401 && token) {
                console.log('[API Client] Got 401, attempting token refresh and retry...')
                const supabase = createClient()
                const { data: { session: newSession } } = await supabase.auth.refreshSession()
                
                if (newSession?.access_token) {
                    headers['Authorization'] = `Bearer ${newSession.access_token}`
                    const retryResponse = await fetch(url, {
                        ...options,
                        headers,
                    })
                    
                    if (retryResponse.ok) {
                        return retryResponse.json()
                    }
                }
            }
            
            throw new Error(errorText || `HTTP ${response.status}`)
        }
        
        return response.json()
    }
    
    // Clients
    async getClients(): Promise<Client[]> {
        return this.fetch('/api/v1/clients/')
    }
    
    async getClient(id: number): Promise<Client> {
        return this.fetch(`/api/v1/clients/${id}`)
    }
    
    async createClient(data: { name: string; slug: string }): Promise<Client> {
        return this.fetch('/api/v1/clients/', {
            method: 'POST',
            body: JSON.stringify(data)
        })
    }
    
    async updateClient(id: number, data: { name: string; slug: string }): Promise<Client> {
        return this.fetch(`/api/v1/clients/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        })
    }
    
    async deleteClient(id: number): Promise<void> {
        return this.fetch(`/api/v1/clients/${id}`, { method: 'DELETE' })
    }
    
    // Connectors
    async getConnectors(clientId: number): Promise<Connector[]> {
        return this.fetch(`/api/v1/clients/${clientId}/connectors`)
    }
    
    async getConnector(id: number): Promise<Connector> {
        return this.fetch(`/api/v1/connectors/${id}`)
    }
    
    async createConnector(clientId: number, data: { type: string; config: Record<string, any> }): Promise<Connector> {
        return this.fetch(`/api/v1/clients/${clientId}/connectors`, {
            method: 'POST',
            body: JSON.stringify(data)
        })
    }
    
    async updateConnector(id: number, data: { type?: string; config?: Record<string, any> }): Promise<Connector> {
        return this.fetch(`/api/v1/connectors/${id}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        })
    }
    
    async deleteConnector(id: number): Promise<void> {
        return this.fetch(`/api/v1/connectors/${id}`, { method: 'DELETE' })
    }
    
    async testConnector(id: number): Promise<{ success: boolean; message: string }> {
        return this.fetch(`/api/v1/connectors/${id}/test`, { method: 'POST' })
    }
    
    // Jobs
    async getJobs(params?: { client_id?: number; status?: string; limit?: number }): Promise<Job[]> {
        const queryParams = new URLSearchParams()
        if (params?.client_id) queryParams.append('client_id', String(params.client_id))
        if (params?.status) queryParams.append('status', params.status)
        if (params?.limit) queryParams.append('limit', String(params.limit))
        
        return this.fetch(`/api/v1/jobs?${queryParams}`)
    }
    
    async getJob(id: number): Promise<Job> {
        return this.fetch(`/api/v1/jobs/${id}`)
    }
    
    async runJob(clientId: number, config?: { days?: number; start_date?: string; end_date?: string; max_retries?: number }): Promise<Job> {
        return this.fetch(`/api/v1/jobs/run/${clientId}`, { 
            method: 'POST',
            body: config ? JSON.stringify(config) : undefined
        })
    }

    async retryJob(jobId: number): Promise<Job> {
        return this.fetch(`/api/v1/jobs/${jobId}/retry`, { method: 'POST' })
    }
    
    // Admin
    async getAdminStats(): Promise<{
        total_clients: number
        active_clients: number
        total_jobs: number
        jobs_by_status: Record<string, number>
        recent_jobs: Job[]
    }> {
        return this.fetch('/api/v1/admin/stats')
    }
    
    async getAdminJobs(params?: { client_id?: number; status?: string }): Promise<Job[]> {
        const queryParams = new URLSearchParams()
        if (params?.client_id) queryParams.append('client_id', String(params.client_id))
        if (params?.status) queryParams.append('status', params.status)
        
        return this.fetch(`/api/v1/admin/jobs?${queryParams}`)
    }

    // Users
    async getClientUsers(clientId: number): Promise<{ id: number; email: string; role: string; status: string; created_at: string }[]> {
        return this.fetch(`/api/v1/clients/${clientId}/users`)
    }

    async inviteUser(clientId: number, data: { email: string; role: string }): Promise<{ success: boolean }> {
        return this.fetch(`/api/v1/clients/${clientId}/invite`, {
            method: 'POST',
            body: JSON.stringify(data)
        })
    }

    async removeUser(userId: number): Promise<void> {
        return this.fetch(`/api/v1/users/${userId}`, { method: 'DELETE' })
    }
}

export const api = new DraApiClient()
