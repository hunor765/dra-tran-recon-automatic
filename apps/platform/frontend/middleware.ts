import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

// Admin email patterns - should match your actual admin setup
const ADMIN_EMAIL_PATTERNS = [
    /@dra\.com$/i,           // DRA company emails
    /@datarevolt\.ro$/i,     // Data Revolt Romania
    /@datarevolt\.agency$/i, // Data Revolt Agency
    /@revolt\.agency$/i,     // Revolt Agency
]

// Check if email is admin based on patterns
function isAdminEmail(email: string | undefined): boolean {
    if (!email) return false
    return ADMIN_EMAIL_PATTERNS.some(pattern => pattern.test(email))
}

export async function middleware(request: NextRequest) {
    let response = NextResponse.next({
        request: {
            headers: request.headers,
        },
    })

    const supabase = createServerClient(
        process.env.NEXT_PUBLIC_SUPABASE_URL!,
        process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
        {
            cookies: {
                get(name: string) {
                    return request.cookies.get(name)?.value
                },
                set(name: string, value: string, options: CookieOptions) {
                    request.cookies.set({ name, value, ...options })
                    response = NextResponse.next({ request: { headers: request.headers } })
                    response.cookies.set({ name, value, ...options })
                },
                remove(name: string, options: CookieOptions) {
                    request.cookies.set({ name, value: '', ...options })
                    response = NextResponse.next({ request: { headers: request.headers } })
                    response.cookies.set({ name, value: '', ...options })
                },
            },
        }
    )

    const { data: { user } } = await supabase.auth.getUser()
    const pathname = request.nextUrl.pathname

    // Public routes that don't require auth
    const publicRoutes = ['/', '/login', '/admin/login']
    if (publicRoutes.includes(pathname)) {
        // If user is already logged in, redirect to appropriate dashboard
        if (user) {
            const isAdmin = isAdminEmail(user.email) || user.app_metadata?.role === 'admin' || user.user_metadata?.role === 'admin'
            
            // If admin hits /login, redirect to /admin
            if (isAdmin && pathname === '/login') {
                return NextResponse.redirect(new URL('/admin', request.url))
            }
            
            // If client hits /admin/login, redirect to /dashboard
            if (!isAdmin && pathname === '/admin/login') {
                return NextResponse.redirect(new URL('/dashboard', request.url))
            }
            
            // If already logged in and hits their respective login page, go to dashboard
            if ((isAdmin && pathname === '/admin/login') || (!isAdmin && pathname === '/login')) {
                return NextResponse.redirect(new URL(isAdmin ? '/admin' : '/dashboard', request.url))
            }
        }
        return response
    }

    // Check if user is authenticated
    if (!user) {
        // Determine which login page to redirect to based on the path they're trying to access
        const isAdminPath = pathname.startsWith('/admin')
        const loginUrl = new URL(isAdminPath ? '/admin/login' : '/login', request.url)
        loginUrl.searchParams.set('redirect', pathname)
        return NextResponse.redirect(loginUrl)
    }

    // Check admin access
    const isAdmin = isAdminEmail(user.email) || user.app_metadata?.role === 'admin' || user.user_metadata?.role === 'admin'
    
    // Admin routes require admin role
    if (pathname.startsWith('/admin') && pathname !== '/admin/login' && !isAdmin) {
        console.warn(`Non-admin user ${user.email} attempted to access ${pathname}`)
        return NextResponse.redirect(new URL('/dashboard', request.url))
    }

    // Client dashboard requires user_client mapping
    // This will be checked by the backend API
    // We just ensure they're logged in here

    return response
}

export const config = {
    matcher: [
        '/admin/:path*',
        '/dashboard/:path*',
        '/login',
        '/',
        '/((?!_next/static|_next/image|favicon.ico|.*\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
    ],
}
