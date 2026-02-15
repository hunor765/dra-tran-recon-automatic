'use client'

export interface StatusBadgeProps {
    status: string
    size?: 'sm' | 'md'
}

const styles: Record<string, string> = {
    completed: 'bg-green-100 text-green-700',
    running: 'bg-blue-100 text-blue-700',
    pending: 'bg-yellow-100 text-yellow-700',
    failed: 'bg-red-100 text-red-700',
    active: 'bg-green-100 text-green-700',
    inactive: 'bg-gray-100 text-gray-700',
    invited: 'bg-yellow-100 text-yellow-700',
}

const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-3 py-1 text-xs',
}

export function StatusBadge({ status, size = 'sm' }: StatusBadgeProps) {
    return (
        <span 
            className={`rounded-full font-medium capitalize ${styles[status] || 'bg-gray-100 text-gray-700'} ${sizeClasses[size]}`}
        >
            {status}
        </span>
    )
}
