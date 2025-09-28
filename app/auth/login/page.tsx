'use client'

import React, { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { Eye, EyeOff, ArrowRight, Mail, Lock } from 'lucide-react'
import { useAuth } from '../../providers'
import { toast } from 'sonner'

const LoginPage = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [showPassword, setShowPassword] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  
  const { login } = useAuth()
  const router = useRouter()

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!formData.email || !formData.password) {
      toast.error('Please fill in all fields')
      return
    }

    setIsLoading(true)
    try {
      const success = await login(formData.email, formData.password)
      if (success) {
        router.push('/dashboard')
      }
    } catch (error) {
      console.error('Login error:', error)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center">
            <div className="h-12 w-12 polaris-gradient rounded-xl flex items-center justify-center mr-3">
              <span className="text-white font-bold text-lg">P</span>
            </div>
            <div className="text-left">
              <h1 className="text-2xl font-bold text-gray-900">Polaris</h1>
              <p className="text-sm text-gray-500">Business Assessment Platform</p>
            </div>
          </div>
        </div>

        {/* Login Form */}
        <div className="polaris-card">
          <div className="text-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Welcome Back</h2>
            <p className="text-gray-600">Sign in to your account to continue</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email Field */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  id="email"
                  name="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="polaris-input pl-10"
                  placeholder="Enter your email"
                  disabled={isLoading}
                />
              </div>
            </div>

            {/* Password Field */}
            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-1">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                <input
                  id="password"
                  name="password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="polaris-input pl-10 pr-10"
                  placeholder="Enter your password"
                  disabled={isLoading}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="h-5 w-5" /> : <Eye className="h-5 w-5" />}
                </button>
              </div>
            </div>

            {/* Forgot Password Link */}
            <div className="text-right">
              <Link
                href="/auth/forgot-password"
                className="text-sm text-polaris-blue hover:text-polaris-navy"
              >
                Forgot your password?
              </Link>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className={`w-full polaris-button-primary py-3 text-base font-semibold ${
                isLoading ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {isLoading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                  Signing In...
                </div>
              ) : (
                <div className="flex items-center justify-center">
                  Sign In
                  <ArrowRight className="ml-2 h-5 w-5" />
                </div>
              )}
            </button>
          </form>

          {/* Register Link */}
          <div className="mt-6 pt-6 border-t border-gray-200 text-center">
            <p className="text-gray-600">
              Don't have an account?{' '}
              <Link
                href="/auth/register"
                className="text-polaris-blue hover:text-polaris-navy font-medium"
              >
                Create one here
              </Link>
            </p>
          </div>
        </div>

        {/* Demo Accounts */}
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <h3 className="text-sm font-medium text-blue-900 mb-2">QA Test Accounts:</h3>
          <div className="text-xs text-blue-800 space-y-1">
            <div>Client: client.qa@polaris.example.com</div>
            <div>Provider: provider.qa@polaris.example.com</div>
            <div>Agency: agency.qa@polaris.example.com</div>
            <div>Navigator: navigator.qa@polaris.example.com</div>
            <div className="text-blue-600 font-medium mt-2">Password: Polaris#2025!</div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default LoginPage