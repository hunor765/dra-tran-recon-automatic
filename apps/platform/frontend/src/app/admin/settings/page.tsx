'use client'

import { Settings } from 'lucide-react'

export default function SettingsPage() {
    return (
        <div className="flex flex-col items-center justify-center py-24">
            <div className="w-16 h-16 rounded-2xl bg-gray-100 flex items-center justify-center mb-6">
                <Settings size={32} className="text-gray-500" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-3">Settings</h1>
            <p className="text-gray-500 text-center max-w-md mb-8">
                Platform configuration, notification preferences, and integration settings are coming in a future update.
            </p>
            <div className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium">
                Coming Soon
            </div>
        </div>
    )
}
