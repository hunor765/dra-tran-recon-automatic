'use client'

import { useEffect, useState } from 'react'
import { createClient } from '@/lib/supabase/client'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Alert, AlertDescription } from '@/components/ui/alert'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export default function DebugPage() {
    const [sessionInfo, setSessionInfo] = useState<any>(null)
    const [configCheck, setConfigCheck] = useState<any>(null)
    const [tokenValidation, setTokenValidation] = useState<any>(null)
    const [authCheck, setAuthCheck] = useState<any>(null)
    const [loading, setLoading] = useState({
        session: false,
        config: false,
        validate: false,
        auth: false
    })
    const [error, setError] = useState<string | null>(null)

    const checkSession = async () => {
        setLoading(prev => ({ ...prev, session: true }))
        setError(null)
        try {
            const supabase = createClient()
            const { data: { session }, error: sessionError } = await supabase.auth.getSession()
            
            if (sessionError) {
                setError(`Session error: ${sessionError.message}`)
                setSessionInfo(null)
            } else if (!session) {
                setError('No active session found. Please log in.')
                setSessionInfo(null)
            } else {
                setSessionInfo({
                    hasSession: true,
                    user: {
                        id: session.user.id,
                        email: session.user.email,
                    },
                    tokenPreview: session.access_token.substring(0, 30) + '...',
                    tokenLength: session.access_token.length,
                    expiresAt: new Date(session.expires_at! * 1000).toISOString(),
                })
            }
        } catch (e: any) {
            setError(`Error: ${e.message}`)
        }
        setLoading(prev => ({ ...prev, session: false }))
    }

    const checkBackendConfig = async () => {
        setLoading(prev => ({ ...prev, config: true }))
        try {
            const response = await fetch(`${API_URL}/api/v1/debug/config-check`)
            const data = await response.json()
            setConfigCheck(data)
        } catch (e: any) {
            setConfigCheck({ error: e.message })
        }
        setLoading(prev => ({ ...prev, config: false }))
    }

    const validateToken = async () => {
        setLoading(prev => ({ ...prev, validate: true }))
        try {
            const supabase = createClient()
            const { data: { session } } = await supabase.auth.getSession()
            
            if (!session) {
                setTokenValidation({ error: 'No session to validate' })
                return
            }

            const response = await fetch(`${API_URL}/api/v1/debug/validate-token`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ token: session.access_token })
            })
            const data = await response.json()
            setTokenValidation(data)
        } catch (e: any) {
            setTokenValidation({ error: e.message })
        }
        setLoading(prev => ({ ...prev, validate: false }))
    }

    const checkAuth = async () => {
        setLoading(prev => ({ ...prev, auth: true }))
        try {
            const supabase = createClient()
            const { data: { session } } = await supabase.auth.getSession()
            
            if (!session) {
                setAuthCheck({ error: 'No session' })
                return
            }

            const response = await fetch(`${API_URL}/api/v1/debug/auth-check`, {
                headers: {
                    'Authorization': `Bearer ${session.access_token}`
                }
            })
            const data = await response.json()
            setAuthCheck(data)
        } catch (e: any) {
            setAuthCheck({ error: e.message })
        }
        setLoading(prev => ({ ...prev, auth: false }))
    }

    useEffect(() => {
        checkSession()
        checkBackendConfig()
    }, [])

    return (
        <div className="container mx-auto py-8 px-4">
            <h1 className="text-3xl font-bold mb-8">Authentication Diagnostics</h1>
            
            {error && (
                <Alert variant="destructive" className="mb-6">
                    <AlertDescription>{error}</AlertDescription>
                </Alert>
            )}

            <div className="grid gap-6 md:grid-cols-2">
                {/* Session Check */}
                <Card>
                    <CardHeader>
                        <CardTitle>1. Frontend Session</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <Button 
                            onClick={checkSession} 
                            disabled={loading.session}
                            className="mb-4"
                        >
                            {loading.session ? 'Checking...' : 'Check Session'}
                        </Button>
                        {sessionInfo && (
                            <pre className="bg-slate-100 p-4 rounded text-sm overflow-auto">
                                {JSON.stringify(sessionInfo, null, 2)}
                            </pre>
                        )}
                    </CardContent>
                </Card>

                {/* Backend Config */}
                <Card>
                    <CardHeader>
                        <CardTitle>2. Backend Configuration</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <Button 
                            onClick={checkBackendConfig} 
                            disabled={loading.config}
                            className="mb-4"
                        >
                            {loading.config ? 'Checking...' : 'Check Config'}
                        </Button>
                        {configCheck && (
                            <pre className="bg-slate-100 p-4 rounded text-sm overflow-auto">
                                {JSON.stringify(configCheck, null, 2)}
                            </pre>
                        )}
                    </CardContent>
                </Card>

                {/* Token Validation */}
                <Card>
                    <CardHeader>
                        <CardTitle>3. Token Validation</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <Button 
                            onClick={validateToken} 
                            disabled={loading.validate || !sessionInfo}
                            className="mb-4"
                        >
                            {loading.validate ? 'Validating...' : 'Validate Token'}
                        </Button>
                        {!sessionInfo && (
                            <p className="text-sm text-slate-500 mb-2">
                                Login required first
                            </p>
                        )}
                        {tokenValidation && (
                            <pre className="bg-slate-100 p-4 rounded text-sm overflow-auto">
                                {JSON.stringify(tokenValidation, null, 2)}
                            </pre>
                        )}
                    </CardContent>
                </Card>

                {/* Full Auth Check */}
                <Card>
                    <CardHeader>
                        <CardTitle>4. Full Auth Check</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <Button 
                            onClick={checkAuth} 
                            disabled={loading.auth || !sessionInfo}
                            className="mb-4"
                        >
                            {loading.auth ? 'Checking...' : 'Test Auth Header'}
                        </Button>
                        {!sessionInfo && (
                            <p className="text-sm text-slate-500 mb-2">
                                Login required first
                            </p>
                        )}
                        {authCheck && (
                            <pre className="bg-slate-100 p-4 rounded text-sm overflow-auto">
                                {JSON.stringify(authCheck, null, 2)}
                            </pre>
                        )}
                    </CardContent>
                </Card>
            </div>

            <div className="mt-8 p-4 bg-blue-50 rounded-lg">
                <h2 className="font-semibold mb-2">Troubleshooting Steps:</h2>
                <ol className="list-decimal list-inside space-y-2 text-sm">
                    <li><strong>Check Session:</strong> Should show user email and token preview</li>
                    <li><strong>Check Config:</strong> Backend should show Supabase URL is configured</li>
                    <li><strong>Validate Token:</strong> Should show &quot;valid: true&quot; with user info</li>
                    <li><strong>Test Auth Header:</strong> Should show &quot;authenticated: true&quot;</li>
                </ol>
                
                <h3 className="font-semibold mt-4 mb-2">Common Issues:</h3>
                <ul className="list-disc list-inside space-y-1 text-sm">
                    <li><strong>JWT Secret mismatch:</strong> Get the correct JWT Secret from Supabase Dashboard → Project Settings → API</li>
                    <li><strong>Wrong Supabase project:</strong> Frontend and backend must use the same project URL and anon key</li>
                    <li><strong>Token expired:</strong> Try logging out and back in</li>
                    <li><strong>CORS issues:</strong> Check browser console for CORS errors</li>
                </ul>
            </div>
        </div>
    )
}
