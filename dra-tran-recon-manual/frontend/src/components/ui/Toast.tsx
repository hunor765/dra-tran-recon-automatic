'use client'

import { useEffect, useState } from 'react'
import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from 'lucide-react'

export type ToastType = 'success' | 'error' | 'warning' | 'info'

interface ToastProps {
    message: string
    type?: ToastType
    onDismiss: () => void
    duration?: number
}

const icons = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info,
}

const styles = {
    success: 'bg-green-50 border-green-200 text-green-800',
    error: 'bg-red-50 border-red-200 text-red-800',
    warning: 'bg-yellow-50 border-yellow-200 text-yellow-800',
    info: 'bg-blue-50 border-blue-200 text-blue-800',
}

export function Toast({ message, type = 'info', onDismiss, duration = 5000 }: ToastProps) {
    const [isVisible, setIsVisible] = useState(false)
    const Icon = icons[type]

    useEffect(() => {
        // Small delay for animation
        const showTimer = setTimeout(() => setIsVisible(true), 10)
        
        const hideTimer = setTimeout(() => {
            setIsVisible(false)
            setTimeout(onDismiss, 300) // Wait for animation
        }, duration)

        return () => {
            clearTimeout(showTimer)
            clearTimeout(hideTimer)
        }
    }, [duration, onDismiss])

    return (
        <div
            className={`fixed bottom-4 right-4 z-50 transform transition-all duration-300 ${
                isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'
            }`}
        >
            <div className={`flex items-center gap-3 px-4 py-3 rounded-xl border shadow-lg min-w-[300px] ${styles[type]}`}>
                <Icon size={20} />
                <span className="font-medium flex-1">{message}</span>
                <button 
                    onClick={() => {
                        setIsVisible(false)
                        setTimeout(onDismiss, 300)
                    }}
                    className="hover:opacity-70 transition"
                >
                    <X size={16} />
                </button>
            </div>
        </div>
    )
}

// Hook for managing toasts
export function useToast() {
    const [toasts, setToasts] = useState<Array<{ id: number; message: string; type: ToastType }>>([])

    const show = (message: string, type: ToastType = 'info') => {
        const id = Date.now()
        setToasts(prev => [...prev, { id, message, type }])
    }

    const dismiss = (id: number) => {
        setToasts(prev => prev.filter(t => t.id !== id))
    }

    return {
        toasts,
        show,
        dismiss,
        success: (msg: string) => show(msg, 'success'),
        error: (msg: string) => show(msg, 'error'),
        warning: (msg: string) => show(msg, 'warning'),
        info: (msg: string) => show(msg, 'info'),
    }
}
