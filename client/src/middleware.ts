import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('auth_token')?.value
  const { pathname } = request.nextUrl
  
  // Define protected route prefixes and required roles
  const protectedRoutes: { [key: string]: string[] } = {
    '/producer': ['PRODUCER', 'ADMIN'],
    '/authority': ['VERIFICATION_AUTHORITY', 'ADMIN'],
    '/lab': ['LAB', 'ADMIN'],
    '/distributor': ['DISTRIBUTOR', 'ADMIN'],
    '/admin': ['ADMIN'],
  }

  const isAuthRoute = pathname.startsWith('/login') || pathname.startsWith('/register')

  // Not authenticated
  if (!token) {
    if (isAuthRoute) return NextResponse.next()
    
    // Check if trying to access a protected route
    for (const route of Object.keys(protectedRoutes)) {
      if (pathname.startsWith(route)) {
        return NextResponse.redirect(new URL('/', request.url))
      }
    }
    
    return NextResponse.next()
  }

  // Authenticated user trying to access auth pages (redirect to their dashboard)
  if (token && isAuthRoute) {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const role = payload.role
      let dashboardUrl = '/unauthorized'
      
      switch (role) {
        case 'ADMIN': dashboardUrl = '/admin/dashboard'; break
        case 'PRODUCER': dashboardUrl = '/producer/dashboard'; break
        case 'VERIFICATION_AUTHORITY': dashboardUrl = '/authority/dashboard'; break
        case 'LAB': dashboardUrl = '/lab/dashboard'; break
        case 'DISTRIBUTOR': dashboardUrl = '/distributor/dashboard'; break
      }
      return NextResponse.redirect(new URL(dashboardUrl, request.url))
    } catch (e) {
      // Invalid token format
      const response = NextResponse.redirect(new URL('/', request.url))
      response.cookies.delete('auth_token')
      return response
    }
  }

  // Check RBAC for protected routes
  for (const [route, allowedRoles] of Object.entries(protectedRoutes)) {
    if (pathname.startsWith(route)) {
      try {
        const payload = JSON.parse(atob(token.split('.')[1]))
        const userRole = payload.role
        if (!allowedRoles.includes(userRole)) {
          return NextResponse.redirect(new URL('/unauthorized', request.url))
        }
      } catch (e) {
        const response = NextResponse.redirect(new URL('/', request.url))
        response.cookies.delete('auth_token')
        return response
      }
    }
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
}
