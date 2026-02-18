'use client'

import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

interface TrendData {
    date: string
    matchRate: number
}

interface TrendChartProps {
    data: TrendData[]
}

export function TrendChart({ data }: TrendChartProps) {
    return (
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm h-[350px]">
            <h3 className="text-lg font-bold text-gray-900 mb-4">Match Rate Trend (7 Days)</h3>
            <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data}>
                    <defs>
                        <linearGradient id="colorMatch" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="#dd3333" stopOpacity={0.1} />
                            <stop offset="95%" stopColor="#dd3333" stopOpacity={0} />
                        </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                    <XAxis
                        dataKey="date"
                        axisLine={false}
                        tickLine={false}
                        tick={{ fontSize: 12, fill: '#6b7280' }}
                        dy={10}
                    />
                    <YAxis
                        axisLine={false}
                        tickLine={false}
                        tick={{ fontSize: 12, fill: '#6b7280' }}
                        domain={[80, 100]}
                    />
                    <Tooltip
                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px rgba(0,0,0,0.1)' }}
                    />
                    <Area
                        type="monotone"
                        dataKey="matchRate"
                        stroke="#dd3333"
                        strokeWidth={2}
                        fillOpacity={1}
                        fill="url(#colorMatch)"
                    />
                </AreaChart>
            </ResponsiveContainer>
        </div>
    )
}
