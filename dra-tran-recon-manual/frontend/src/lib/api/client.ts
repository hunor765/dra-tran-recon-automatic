import { createClient } from '@/lib/supabase/client'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

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

interface Job {
    id: number
    client_id: number
    client_name?: string | null
    status: string
    last_run: string | null
    result_summary: string | null
}

class DraApiClient {
    private baseUrl: string
    
    constructor() {
        this.baseUrl = API_URL
    }
    
    private async fetch(path: string, options: RequestInit = {}) {
        const url = `${this.baseUrl}${path}`
        
        // Get auth token from Supabase
        const supabase = createClient()
        const { data: { session } } = await supabase.auth.getSession()
        const token = session?.access_token
        
        const headers: Record<string, string> = {
            'Content-Type': 'application/json',
            ...options.headers as Record<string, string>,
        }
        
        if (token) {
            headers['Authorization'] = `Bearer ${token}`
        }
        
        const response = await fetch(url, {
            ...options,
            headers,
        })
        
        if (!response.ok) {
            const error = await response.text()
            throw new Error(error || `HTTP ${response.status}`)
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
    
    async runJob(clientId: number): Promise<Job> {
        return this.fetch(`/api/v1/jobs/run/${clientId}`, { method: 'POST' })
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
