'use client'

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react'
import { useRouter, usePathname } from 'next/navigation'
import { toast } from 'sonner'

// Types
interface User {
  id: string
  email: string
  name: string
  role: 'client' | 'provider' | 'agency' | 'navigator' | 'admin'
  status: string
  company_name?: string
  profile_image?: string
  created_at: string
}

interface AuthState {
  user: User | null
  token: string | null
  isLoading: boolean
  isAuthenticated: boolean
}

type AuthAction =
  | { type: 'LOGIN_START' }
  | { type: 'LOGIN_SUCCESS'; payload: { user: User; token: string } }
  | { type: 'LOGIN_FAILURE' }
  | { type: 'LOGOUT' }
  | { type: 'UPDATE_USER'; payload: User }
  | { type: 'SET_LOADING'; payload: boolean }

interface AuthContextType {
  state: AuthState
  login: (email: string, password: string) => Promise<boolean>
  logout: () => void
  register: (userData: RegisterData) => Promise<boolean>
  updateUser: (userData: Partial<User>) => void
  refreshToken: () => Promise<boolean>
}

interface RegisterData {
  email: string
  password: string
  name: string
  role: string
  phone?: string
  company_name?: string
  license_code?: string
}

// API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001/api'

// Auth reducer
function authReducer(state: AuthState, action: AuthAction): AuthState {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, isLoading: true }
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isLoading: false,
        isAuthenticated: true,
      }
    case 'LOGIN_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isLoading: false,
        isAuthenticated: false,
      }
    case 'LOGOUT':
      return {
        user: null,
        token: null,
        isLoading: false,
        isAuthenticated: false,
      }
    case 'UPDATE_USER':
      return {
        ...state,
        user: action.payload,
      }
    case 'SET_LOADING':
      return {
        ...state,
        isLoading: action.payload,
      }
    default:
      return state
  }
}

// Create context
const AuthContext = createContext<AuthContextType | null>(null)

// Custom hook to use auth
export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// API helper
class ApiClient {
  private baseURL: string
  private token: string | null = null

  constructor(baseURL: string) {
    this.baseURL = baseURL
  }

  setToken(token: string | null) {
    this.token = token
  }

  private async makeRequest(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseURL}${endpoint}`
    console.log('API Request URL:', url)
    const headers = {
      'Content-Type': 'application/json',
      ...(this.token && { Authorization: `Bearer ${this.token}` }),
      ...options.headers,
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      })

      console.log('API Response status:', response.status)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.message?.message || data.message || 'Request failed')
      }

      return data
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error)
      throw error
    }
  }

  // Public request method for other components
  async request(endpoint: string, options: RequestInit = {}) {
    return this.makeRequest(endpoint, options)
  }

  async login(email: string, password: string) {
    return this.makeRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
  }

  async register(userData: RegisterData) {
    return this.makeRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    })
  }

  async getMe() {
    return this.makeRequest('/auth/me')
  }

  async refreshToken() {
    return this.makeRequest('/auth/refresh', {
      method: 'POST',
    })
  }

  async logout() {
    return this.makeRequest('/auth/logout', {
      method: 'POST',
    })
  }
}

const apiClient = new ApiClient(API_BASE_URL)

// Auth Provider
function AuthProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(authReducer, {
    user: null,
    token: null,
    isLoading: true,
    isAuthenticated: false,
  })

  const router = useRouter()
  const pathname = usePathname()

  // Initialize auth state from localStorage (client-side only)
  useEffect(() => {
    const initAuth = async () => {
      try {
        // Ensure we're on the client side
        if (typeof window === 'undefined') {
          dispatch({ type: 'SET_LOADING', payload: false })
          return
        }

        const token = localStorage.getItem('polaris_token')
        const user = localStorage.getItem('polaris_user')

        if (token && user) {
          const parsedUser = JSON.parse(user)
          apiClient.setToken(token)
          
          // Verify token is still valid
          try {
            const response = await apiClient.getMe()
            dispatch({
              type: 'LOGIN_SUCCESS',
              payload: {
                user: response.data.user,
                token,
              },
            })
          } catch (error) {
            // Token invalid, clear storage
            localStorage.removeItem('polaris_token')
            localStorage.removeItem('polaris_user')
            dispatch({ type: 'LOGIN_FAILURE' })
          }
        } else {
          dispatch({ type: 'SET_LOADING', payload: false })
        }
      } catch (error) {
        console.error('Auth initialization failed:', error)
        dispatch({ type: 'LOGIN_FAILURE' })
      }
    }

    // Delay initialization to ensure client-side hydration is complete
    const timer = setTimeout(initAuth, 100)
    return () => clearTimeout(timer)
  }, [])

  // Redirect unauthenticated users from protected routes
  useEffect(() => {
    const publicRoutes = ['/', '/auth/login', '/auth/register', '/auth/forgot-password']
    const isPublicRoute = publicRoutes.some(route => pathname === route || pathname.startsWith('/auth/'))
    
    if (!state.isLoading && !state.isAuthenticated && !isPublicRoute) {
      router.push('/auth/login')
    }
  }, [state.isLoading, state.isAuthenticated, pathname, router])

  const login = async (email: string, password: string): Promise<boolean> => {
    try {
      dispatch({ type: 'LOGIN_START' })
      
      const response = await apiClient.login(email, password)
      
      // Handle FastAPI response structure (access_token)
      const token = response.access_token
      
      if (!token) {
        throw new Error('No access token received')
      }
      
      // Get user data with the token
      apiClient.setToken(token)
      const userResponse = await apiClient.getMe()
      const user = userResponse
      
      // Store in localStorage (client-side only)
      if (typeof window !== 'undefined') {
        localStorage.setItem('polaris_token', token)
        localStorage.setItem('polaris_user', JSON.stringify(user))
      }
      
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: { user, token },
      })
      
      toast.success('Welcome back!')
      return true
    } catch (error) {
      dispatch({ type: 'LOGIN_FAILURE' })
      toast.error(error instanceof Error ? error.message : 'Login failed')
      return false
    }
  }

  const register = async (userData: RegisterData): Promise<boolean> => {
    try {
      dispatch({ type: 'LOGIN_START' })
      
      const response = await apiClient.register(userData)
      const { user, token } = response.data
      
      // Store in localStorage (client-side only)
      if (typeof window !== 'undefined') {
        localStorage.setItem('polaris_token', token)
        localStorage.setItem('polaris_user', JSON.stringify(user))
      }
      
      apiClient.setToken(token)
      
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: { user, token },
      })
      
      toast.success('Account created successfully!')
      return true
    } catch (error) {
      dispatch({ type: 'LOGIN_FAILURE' })
      toast.error(error instanceof Error ? error.message : 'Registration failed')
      return false
    }
  }

  const logout = async () => {
    try {
      if (state.token) {
        await apiClient.logout()
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // Clear storage and state regardless of API call success (client-side only)
      if (typeof window !== 'undefined') {
        localStorage.removeItem('polaris_token')
        localStorage.removeItem('polaris_user')
      }
      apiClient.setToken(null)
      dispatch({ type: 'LOGOUT' })
      toast.success('Logged out successfully')
      router.push('/auth/login')
    }
  }

  const updateUser = (userData: Partial<User>) => {
    if (state.user && typeof window !== 'undefined') {
      const updatedUser = { ...state.user, ...userData }
      localStorage.setItem('polaris_user', JSON.stringify(updatedUser))
      dispatch({ type: 'UPDATE_USER', payload: updatedUser })
    }
  }

  const refreshToken = async (): Promise<boolean> => {
    try {
      const response = await apiClient.refreshToken()
      const { token } = response.data
      
      if (typeof window !== 'undefined') {
        localStorage.setItem('polaris_token', token)
      }
      apiClient.setToken(token)
      
      return true
    } catch (error) {
      console.error('Token refresh failed:', error)
      logout()
      return false
    }
  }

  const value: AuthContextType = {
    state,
    login,
    logout,
    register,
    updateUser,
    refreshToken,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

// Main Providers component
export function Providers({ children }: { children: ReactNode }) {
  return (
    <AuthProvider>
      {children}
    </AuthProvider>
  )
}

// Export API client for use in other components
export { apiClient }