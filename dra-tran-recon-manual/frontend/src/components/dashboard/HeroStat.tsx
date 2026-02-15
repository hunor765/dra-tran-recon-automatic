import { ArrowUpRight, ArrowDownRight, AlertTriangle, CheckCircle2 } from 'lucide-react'

interface HeroStatProps {
    totalBackend: number
    totalGa4: number
    matchRate: number
    missingOrders: number
}

export function HeroStat({ totalBackend, totalGa4, matchRate, missingOrders }: HeroStatProps) {
    const discrepancy = totalBackend - totalGa4
    const isHealthy = matchRate >= 95

    return (
        <div className="relative overflow-hidden rounded-2xl bg-slate-900 text-white shadow-2xl p-8 mb-8 group">
            {/* Background Ambience */}
            <div className="absolute top-0 right-0 w-[300px] h-[300px] bg-revolt-red/20 rounded-full blur-[100px] translate-x-1/3 -translate-y-1/3" />
            <div className="absolute bottom-0 left-0 w-[200px] h-[200px] bg-blue-500/20 rounded-full blur-[80px] -translate-x-1/3 translate-y-1/3" />

            <div className="relative z-10 flex flex-col lg:flex-row justify-between items-start lg:items-center gap-8">
                <div>
                    <div className="flex items-center gap-3 mb-3">
                        <div className={`flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider ${isHealthy
                                ? 'bg-green-500/10 text-green-400 border border-green-500/20'
                                : 'bg-red-500/10 text-red-400 border border-red-500/20'
                            }`}>
                            {isHealthy ? <CheckCircle2 size={12} /> : <AlertTriangle size={12} />}
                            {isHealthy ? 'System Healthy' : 'Action Required'}
                        </div>
                        <span className="text-slate-400 text-sm">Last 30 Days</span>
                    </div>

                    <h2 className="text-4xl font-bold mb-2">
                        ${discrepancy.toLocaleString('en-US', { minimumFractionDigits: 2 })}
                    </h2>
                    <p className="text-slate-400">
                        Untracked revenue detected across <span className="text-white font-medium">{missingOrders} orders</span>.
                    </p>
                </div>

                <div className="flex bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-1">
                    <div className="px-8 py-4 border-r border-white/5 last:border-0 hover:bg-white/5 transition rounded-lg">
                        <p className="text-xs uppercase tracking-wider text-slate-400 mb-1">Match Rate</p>
                        <div className="flex items-baseline gap-2">
                            <span className={`text-2xl font-bold ${isHealthy ? 'text-white' : 'text-red-400'}`}>
                                {matchRate.toFixed(1)}%
                            </span>
                            <span className="text-xs text-slate-500">vs target 99%</span>
                        </div>
                    </div>

                    <div className="px-8 py-4 hover:bg-white/5 transition rounded-lg">
                        <p className="text-xs uppercase tracking-wider text-slate-400 mb-1">Discrepancy</p>
                        <div className="flex items-baseline gap-2">
                            <span className="text-2xl font-bold text-white">
                                {((100 - matchRate)).toFixed(1)}%
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
