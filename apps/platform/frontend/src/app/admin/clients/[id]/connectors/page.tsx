'use client'

import { useEffect, useState } from 'react'
import { useParams } from 'next/navigation'
import Link from 'next/link'
import { ArrowLeft, Plus, TestTube, Trash2, Edit, CheckCircle, XCircle, AlertCircle, Loader2 } from 'lucide-react'
import { api } from '@/lib/api/client'
import { useToast, Toast } from '@/components/ui/Toast'
import { Skeleton } from '@/components/ui/LoadingSkeleton'

interface Connector {
    id: number
    type: string
    is_active: boolean
    created_at?: string
}

export default function ConnectorsPage() {
    const params = useParams()
    const clientId = parseInt(params.id as string)
    
    const [connectors, setConnectors] = useState<Connector[]>([])
    const [showCreateModal, setShowCreateModal] = useState(false)
    const [testingId, setTestingId] = useState<number | null>(null)
    const [loading, setLoading] = useState(true)
    const { toasts, dismiss, success, error: showError } = useToast()

    useEffect(() => {
        fetchConnectors()
    }, [clientId])

    const fetchConnectors = async () => {
        try {
            const data = await api.getConnectors(clientId)
            setConnectors(data)
        } catch (err: any) {
            console.error('Failed to fetch connectors:', err)
            showError(err.message || 'Failed to fetch connectors')
        } finally {
            setLoading(false)
        }
    }

    const testConnector = async (connectorId: number) => {
        setTestingId(connectorId)
        try {
            const result = await api.testConnector(connectorId)
            success(result.message)
        } catch (err: any) {
            showError(err.message || 'Test failed')
        } finally {
            setTestingId(null)
        }
    }

    const deleteConnector = async (connectorId: number) => {
        if (!confirm('Are you sure you want to delete this connector?')) return
        
        try {
            await api.deleteConnector(connectorId)
            await fetchConnectors()
            success('Connector deleted successfully')
        } catch (err: any) {
            console.error('Failed to delete connector:', err)
            showError(err.message || 'Failed to delete connector')
        }
    }

    return (
        <div>
            {loading ? (
                <div className="space-y-4">
                    <Skeleton className="h-8 w-64" />
                    <Skeleton className="h-24 w-full" />
                    <Skeleton className="h-24 w-full" />
                </div>
            ) : (
            <>
            <div className="mb-8">
                <Link href={`/admin/clients/${params.id}`} className="text-gray-500 hover:text-gray-900 flex items-center gap-1 mb-4">
                    <ArrowLeft size={16} />
                    Back to Client
                </Link>
                <div className="flex items-center justify-between">
                    <h1 className="text-3xl font-bold text-gray-900">Connectors</h1>
                    <button
                        onClick={() => setShowCreateModal(true)}
                        className="bg-revolt-red text-white px-4 py-2 rounded-lg font-medium hover:bg-red-700 transition flex items-center gap-2"
                    >
                        <Plus size={18} />
                        Add Connector
                    </button>
                </div>
            </div>

            {/* Connectors List */}
            <div className="space-y-4">
                {connectors.map((connector) => (
                    <div key={connector.id} className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-xl bg-gray-100 flex items-center justify-center text-xl font-bold text-gray-700">
                                    {connector.type === 'ga4' ? 'G4' : connector.type === 'shopify' ? 'Sh' : 'WC'}
                                </div>
                                <div>
                                    <h3 className="font-bold text-gray-900 capitalize">{connector.type}</h3>
                                    <p className="text-sm text-gray-500">ID: {connector.id}</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-2">
                                <button
                                    onClick={() => testConnector(connector.id)}
                                    disabled={testingId === connector.id}
                                    className="px-3 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg transition flex items-center gap-1"
                                >
                                    <TestTube size={16} />
                                    {testingId === connector.id ? 'Testing...' : 'Test'}
                                </button>
                                <button className="p-2 text-gray-400 hover:text-blue-600 transition">
                                    <Edit size={18} />
                                </button>
                                <button
                                    onClick={() => deleteConnector(connector.id)}
                                    className="p-2 text-gray-400 hover:text-red-600 transition"
                                >
                                    <Trash2 size={18} />
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
                
                {connectors.length === 0 && (
                    <div className="bg-white p-12 rounded-xl border border-gray-200 text-center">
                        <p className="text-gray-500 mb-4">No connectors configured yet</p>
                        <button
                            onClick={() => setShowCreateModal(true)}
                            className="text-revolt-red hover:underline font-medium"
                        >
                            Add your first connector
                        </button>
                    </div>
                )}
            </div>

            {/* Create Modal */}
            {showCreateModal && (
                <CreateConnectorModal
                    clientId={params.id as string}
                    onClose={() => setShowCreateModal(false)}
                    onCreated={fetchConnectors}
                    onSuccess={() => success('Connector created successfully')}
                />
            )}

            {toasts.map(t => (
                <Toast key={t.id} message={t.message} type={t.type} onDismiss={() => dismiss(t.id)} />
            ))}
            </>
            )}
        </div>
    )
}

function CreateConnectorModal({ clientId, onClose, onCreated, onSuccess }: { clientId: string; onClose: () => void; onCreated: () => void; onSuccess: () => void }) {
    const [type, setType] = useState<'ga4' | 'shopify' | 'woocommerce'>('ga4')
    const [config, setConfig] = useState<Record<string, string>>({})
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState<string | null>(null)

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError(null)
        
        try {
            await api.createConnector(parseInt(clientId), { type, config })
            onCreated()
            onSuccess()
            onClose()
        } catch (err: any) {
            console.error('Failed to create connector:', err)
            setError(err.message || 'Failed to create connector')
        } finally {
            setLoading(false)
        }
    }

    const renderConfigFields = () => {
        switch (type) {
            case 'ga4':
                return (
                    <>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Property ID</label>
                            <input
                                type="text"
                                placeholder="123456789"
                                value={config.property_id || ''}
                                onChange={(e) => setConfig({ ...config, property_id: e.target.value })}
                                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-revolt-red focus:border-revolt-red outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Service Account JSON</label>
                            <textarea
                                placeholder="Paste your Google Service Account JSON here..."
                                value={config.credentials_json || ''}
                                onChange={(e) => setConfig({ ...config, credentials_json: e.target.value })}
                                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-revolt-red focus:border-revolt-red outline-none h-32 font-mono text-xs"
                            />
                        </div>
                    </>
                )
            case 'shopify':
                return (
                    <>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Shop URL</label>
                            <input
                                type="text"
                                placeholder="my-store.myshopify.com"
                                value={config.shop_url || ''}
                                onChange={(e) => setConfig({ ...config, shop_url: e.target.value })}
                                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-revolt-red focus:border-revolt-red outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Access Token</label>
                            <input
                                type="password"
                                placeholder="shpat_xxxxxxxxxxxxxxxx"
                                value={config.access_token || ''}
                                onChange={(e) => setConfig({ ...config, access_token: e.target.value })}
                                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-revolt-red focus:border-revolt-red outline-none"
                            />
                        </div>
                    </>
                )
            case 'woocommerce':
                return (
                    <>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Store URL</label>
                            <input
                                type="text"
                                placeholder="https://my-store.com"
                                value={config.url || ''}
                                onChange={(e) => setConfig({ ...config, url: e.target.value })}
                                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-revolt-red focus:border-revolt-red outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Consumer Key</label>
                            <input
                                type="text"
                                value={config.consumer_key || ''}
                                onChange={(e) => setConfig({ ...config, consumer_key: e.target.value })}
                                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-revolt-red focus:border-revolt-red outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Consumer Secret</label>
                            <input
                                type="password"
                                value={config.consumer_secret || ''}
                                onChange={(e) => setConfig({ ...config, consumer_secret: e.target.value })}
                                className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-revolt-red focus:border-revolt-red outline-none"
                            />
                        </div>
                    </>
                )
        }
    }

    return (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
            <div className="bg-white rounded-xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
                <h2 className="text-xl font-bold text-gray-900 mb-4">Add Connector</h2>
                {error && (
                    <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
                        {error}
                    </div>
                )}
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                        <select
                            value={type}
                            onChange={(e) => setType(e.target.value as any)}
                            className="w-full px-4 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-revolt-red focus:border-revolt-red outline-none"
                        >
                            <option value="ga4">Google Analytics 4</option>
                            <option value="shopify">Shopify</option>
                            <option value="woocommerce">WooCommerce</option>
                        </select>
                    </div>
                    
                    <div className="border-t border-gray-100 pt-4">
                        <h3 className="text-sm font-medium text-gray-500 mb-3">Configuration</h3>
                        {renderConfigFields()}
                    </div>
                    
                    <div className="flex gap-3 pt-4">
                        <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 px-4 py-2 border border-gray-200 rounded-lg font-medium hover:bg-gray-50 transition"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            className="flex-1 px-4 py-2 bg-revolt-red text-white rounded-lg font-medium hover:bg-red-700 transition disabled:opacity-50"
                        >
                            {loading ? 'Creating...' : 'Create Connector'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    )
}
