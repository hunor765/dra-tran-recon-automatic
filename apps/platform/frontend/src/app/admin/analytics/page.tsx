'use client'

import { BarChart3 } from 'lucide-react'

export default function AnalyticsPage() {
    return (
        <div className="flex flex-col items-center justify-center py-24">
            <div className="w-16 h-16 rounded-2xl bg-orange-50 flex items-center justify-center mb-6">
                <BarChart3 size={32} className="text-orange-500" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-3">Analytics</h1>
            <p className="text-gray-500 text-center max-w-md mb-8">
                Detailed reconciliation analytics, trends, and insights are coming in a future update.
            </p>
            <div className="px-4 py-2 bg-orange-50 text-orange-700 rounded-lg text-sm font-medium">
                Coming Soon
            </div>
        </div>
    )
}
