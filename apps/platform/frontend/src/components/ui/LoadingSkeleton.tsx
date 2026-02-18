'use client'

interface SkeletonProps {
    className?: string
}

export function Skeleton({ className = '' }: SkeletonProps) {
    return (
        <div className={`animate-pulse bg-gray-200 rounded ${className}`} />
    )
}

export function CardSkeleton() {
    return (
        <div className="bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
            <div className="flex items-center justify-between">
                <div className="space-y-3">
                    <Skeleton className="h-4 w-24" />
                    <Skeleton className="h-8 w-16" />
                </div>
                <Skeleton className="w-12 h-12 rounded-xl" />
            </div>
        </div>
    )
}

export function TableRowSkeleton({ columns = 5 }: { columns?: number }) {
    return (
        <tr className="border-b border-gray-100">
            {Array.from({ length: columns }).map((_, i) => (
                <td key={i} className="px-6 py-4">
                    <Skeleton className="h-4 w-20" />
                </td>
            ))}
        </tr>
    )
}

export function TableSkeleton({ rows = 5, columns = 5 }: { rows?: number; columns?: number }) {
    return (
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            <table className="w-full">
                <tbody className="divide-y divide-gray-100">
                    {Array.from({ length: rows }).map((_, i) => (
                        <TableRowSkeleton key={i} columns={columns} />
                    ))}
                </tbody>
            </table>
        </div>
    )
}

export function PageSkeleton() {
    return (
        <div className="space-y-6">
            <Skeleton className="h-8 w-48" />
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <CardSkeleton />
                <CardSkeleton />
                <CardSkeleton />
                <CardSkeleton />
            </div>
            <Skeleton className="h-64 w-full" />
        </div>
    )
}
