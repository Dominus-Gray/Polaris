import React from 'react'
import Link from 'next/link'
import { ArrowRight, CheckCircle, Star, Users, TrendingUp, Shield } from 'lucide-react'

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-8 w-8 polaris-gradient rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-sm">P</span>
                </div>
              </div>
              <div className="ml-3">
                <h1 className="text-xl font-bold text-gray-900">Polaris</h1>
                <p className="text-xs text-gray-500">Business Assessment Platform</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                href="/auth/login"
                className="text-gray-600 hover:text-gray-900 font-medium"
              >
                Sign In
              </Link>
              <Link
                href="/auth/register"
                className="polaris-button-primary inline-flex items-center"
              >
                Get Started
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative px-4 pt-16 pb-24 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-gray-900 mb-6">
              Unlock Your Business
              <span className="block text-transparent bg-clip-text polaris-gradient">
                Procurement Readiness
              </span>
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto mb-8">
              Complete tier-based assessments, access professional services, and get AI-powered guidance 
              to ensure your business meets compliance standards and competitive requirements.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/auth/register"
                className="polaris-button-primary inline-flex items-center px-8 py-4 text-lg font-semibold"
              >
                Start Free Assessment
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
              <Link
                href="#features"
                className="polaris-button-secondary inline-flex items-center px-8 py-4 text-lg font-semibold"
              >
                Learn More
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Everything You Need for Business Readiness
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Our comprehensive platform provides all the tools and resources you need to assess, 
              improve, and maintain your business compliance standards.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="polaris-card-hover text-center">
              <div className="w-12 h-12 polaris-gradient rounded-lg mx-auto mb-4 flex items-center justify-center">
                <CheckCircle className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Tier-Based Assessments
              </h3>
              <p className="text-gray-600">
                Complete comprehensive assessments across 10 business areas with progressive 
                tier levels to match your business complexity and requirements.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="polaris-card-hover text-center">
              <div className="w-12 h-12 polaris-gradient rounded-lg mx-auto mb-4 flex items-center justify-center">
                <Users className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Professional Services
              </h3>
              <p className="text-gray-600">
                Connect with qualified service providers for assessment help, compliance support, 
                and professional consulting services tailored to your needs.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="polaris-card-hover text-center">
              <div className="w-12 h-12 polaris-gradient rounded-lg mx-auto mb-4 flex items-center justify-center">
                <Star className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                AI-Powered Guidance
              </h3>
              <p className="text-gray-600">
                Get personalized recommendations, generate custom templates, and receive 
                intelligent coaching to accelerate your business readiness journey.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="polaris-card-hover text-center">
              <div className="w-12 h-12 polaris-gradient rounded-lg mx-auto mb-4 flex items-center justify-center">
                <TrendingUp className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Progress Tracking
              </h3>
              <p className="text-gray-600">
                Monitor your assessment progress, track compliance scores, and visualize 
                improvements across all business areas with detailed analytics.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="polaris-card-hover text-center">
              <div className="w-12 h-12 polaris-gradient rounded-lg mx-auto mb-4 flex items-center justify-center">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Knowledge Base
              </h3>
              <p className="text-gray-600">
                Access comprehensive resources, templates, guides, and best practices 
                for each business area to support your compliance efforts.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="polaris-card-hover text-center">
              <div className="w-12 h-12 polaris-gradient rounded-lg mx-auto mb-4 flex items-center justify-center">
                <Users className="h-6 w-6 text-white" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                Multi-Role Platform
              </h3>
              <p className="text-gray-600">
                Support for clients, service providers, agencies, and navigators with 
                role-specific dashboards and functionality tailored to each user type.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Business Areas Section */}
      <section className="py-24 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              10 Comprehensive Business Areas
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Our assessments cover all critical aspects of business operations to ensure 
              complete readiness and compliance.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {[
              'Business Formation & Registration',
              'Financial Operations & Management',
              'Legal & Contracting Compliance',
              'Quality Management & Standards',
              'Technology & Security Infrastructure',
              'Human Resources & Capacity',
              'Performance Tracking & Reporting',
              'Risk Management & Business Continuity',
              'Supply Chain Management & Vendor Relations',
              'Competitive Advantage & Market Position'
            ].map((area, index) => (
              <div key={index} className="flex items-center p-4 bg-white rounded-lg shadow-sm">
                <div className="w-8 h-8 polaris-gradient rounded-full flex items-center justify-center text-white font-semibold text-sm mr-4">
                  {index + 1}
                </div>
                <span className="font-medium text-gray-900">{area}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 polaris-gradient">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to Transform Your Business?
          </h2>
          <p className="text-xl text-blue-100 max-w-2xl mx-auto mb-8">
            Join thousands of businesses that have improved their procurement readiness 
            and competitive advantage with Polaris.
          </p>
          <Link
            href="/auth/register"
            className="inline-flex items-center px-8 py-4 bg-white text-polaris-blue font-semibold rounded-lg hover:bg-gray-50 transition-colors duration-200"
          >
            Start Your Assessment Today
            <ArrowRight className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <div className="h-8 w-8 polaris-gradient rounded-lg flex items-center justify-center mr-3">
                <span className="text-white font-bold text-sm">P</span>
              </div>
              <div>
                <h3 className="font-bold">Polaris</h3>
                <p className="text-sm text-gray-400">Business Assessment Platform</p>
              </div>
            </div>
            <div className="text-sm text-gray-400">
              © 2025 Polaris Platform. All rights reserved.
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}