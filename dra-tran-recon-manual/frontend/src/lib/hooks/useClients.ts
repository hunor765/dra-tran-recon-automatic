'use client'

import { useState, useEffect, useCallback } from 'react'
import { api } from '../api/client'

interface Client {
    id: number
    name: string
    slug: string
    logo_url: string | null
    is_active: boolean
    created_at: string
}

export function useClients() {
    const [clients, setClients] = useState<Client[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    
    const fetchClients = useCallback(async () => {
        setLoading(true)
        setError(null)
        try {
            const data = await api.getClients()
            setClients(data)
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch clients')
        } finally {
            setLoading(false)
        }
    }, [])
    
    useEffect(() => {
        fetchClients()
    }, [fetchClients])
    
    const createClient = async (data: { name: string; slug: string }) => {
        const newClient = await api.createClient(data)
        setClients(prev => [...prev, newClient])
        return newClient
    }
    
    const deleteClient = async (id: number) => {
        await api.deleteClient(id)
        setClients(prev => prev.filter(c => c.id !== id))
    }
    
    return { clients, loading, error, refetch: fetchClients, createClient, deleteClient }
}

export function useClient(id: number | null) {
    const [client, setClient] = useState<Client | null>(null)
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    
    useEffect(() => {
        if (!id) {
            setLoading(false)
            return
        }
        
        api.getClient(id)
            .then(setClient)
            .catch(err => setError(err.message))
            .finally(() => setLoading(false))
    }, [id])
    
    return { client, loading, error }
}
