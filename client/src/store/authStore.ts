import { create } from 'zustand'

interface AuthState {
  isAuthenticated: boolean
  user: null | { id: string; name: string; email: string; role: string }
  login: (userData: { id: string; name: string; email: string; role: string }) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  isAuthenticated: false,
  user: null,
  login: (userData) => set({ isAuthenticated: true, user: userData }),
  logout: () => {
    // Clear all auth tokens consistently
    if (typeof window !== 'undefined') {
      localStorage.removeItem('token')
      localStorage.removeItem('auth_token')
      document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;'
    }
    set({ isAuthenticated: false, user: null })
    // Redirect to home page
    if (typeof window !== 'undefined') {
      window.location.href = '/'
    }
  },
}))
