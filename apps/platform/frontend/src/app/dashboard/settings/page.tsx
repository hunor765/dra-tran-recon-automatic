'use client'

import { useState } from 'react'
import { AlertCircle, CheckCircle, Bell, Shield, User } from 'lucide-react'

export default function SettingsPage() {
    const [error, setError] = useState<string | null>(null)
    const [message, setMessage] = useState<string | null>(null)

    return (
        <div>
            <h1 className="text-2xl font-bold text-gray-900 mb-6">Settings</h1>
            
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

            {message && (
                <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-xl flex items-center gap-3 text-green-700">
                    <CheckCircle size={20} />
                    <span>{message}</span>
                    <button 
                        onClick={() => setMessage(null)}
                        className="ml-auto text-sm font-medium hover:underline"
                    >
                        Dismiss
                    </button>
                </div>
            )}

            <div className="space-y-6">
                {/* Profile Section */}
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                            <User className="text-blue-600" size={20} />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-gray-900">Profile</h2>
                            <p className="text-sm text-gray-500">Manage your account information</p>
                        </div>
                    </div>
                    <p className="text-gray-500 text-sm">Profile settings coming soon...</p>
                </div>

                {/* Notifications Section */}
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                            <Bell className="text-yellow-600" size={20} />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-gray-900">Notifications</h2>
                            <p className="text-sm text-gray-500">Configure alert preferences</p>
                        </div>
                    </div>
                    <p className="text-gray-500 text-sm">Notification settings coming soon...</p>
                </div>

                {/* Security Section */}
                <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                            <Shield className="text-green-600" size={20} />
                        </div>
                        <div>
                            <h2 className="text-lg font-bold text-gray-900">Security</h2>
                            <p className="text-sm text-gray-500">Password and authentication</p>
                        </div>
                    </div>
                    <p className="text-gray-500 text-sm">Security settings coming soon...</p>
                </div>
            </div>
        </div>
    )
}
