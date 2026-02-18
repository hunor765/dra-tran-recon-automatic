import { createServerClient, type CookieOptions } from '@supabase/ssr'
import { NextResponse, type NextRequest } from 'next/server'

// Admin email patterns - should match your actual admin setup
const ADMIN_EMAIL_PATTERNS = [
    /@dra\.com$/i,           // DRA company emails
    /@datarevolt\.ro$/i,     // Data Revolt Romania
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
    const publicRoutes = ['/', '/login']
    if (publicRoutes.includes(pathname)) {
        return response
    }

    // Check if user is authenticated
    if (!user) {
        const loginUrl = new URL('/login', request.url)
        loginUrl.searchParams.set('redirect', pathname)
        return NextResponse.redirect(loginUrl)
    }

    // Check admin access
    const isAdmin = isAdminEmail(user.email) || user.user_metadata?.role === 'admin'
    
    // Admin routes require admin role
    if (pathname.startsWith('/admin') && !isAdmin) {
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
        '/((?!_next/static|_next/image|favicon.ico|.*\.(?:svg|png|jpg|jpeg|gif|webp)$).*)',
    ],
}
