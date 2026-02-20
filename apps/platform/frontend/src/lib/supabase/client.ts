import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
    return createBrowserClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
            cookies: {
                get(name: string) {
                    if (typeof document === 'undefined') return undefined
                    const cookie = document.cookie
                        .split('; ')
                        .find((row) => row.startsWith(`${name}=`))
                    return cookie ? cookie.split('=')[1] : undefined
                },
                set(name: string, value: string, options: { path?: string; maxAge?: number; domain?: string; secure?: boolean }) {
                    if (typeof document === 'undefined') return
                    let cookieString = `${name}=${value}`
                    if (options.path) cookieString += `; path=${options.path}`
                    if (options.maxAge) cookieString += `; max-age=${options.maxAge}`
                    if (options.domain) cookieString += `; domain=${options.domain}`
                    if (options.secure) cookieString += `; secure`
                    document.cookie = cookieString
                },
                remove(name: string, options: { path?: string }) {
                    if (typeof document === 'undefined') return
                    document.cookie = `${name}=; path=${options.path || '/'}; max-age=0`
                },
            },
        }
    )
}
