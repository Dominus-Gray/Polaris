import type { Metadata } from 'next'
import Link from 'next/link'
import { 
  ArrowRight, 
  CheckCircle, 
  Target, 
  Users, 
  Award,
  Building,
  TrendingUp,
  Shield,
  Network,
  Map,
  Handshake,
  FileCheck
} from 'lucide-react'

export const metadata: Metadata = {
  title: 'Polaris - Procurement Readiness & Business Maturity Platform',
  description: 'Streamlining access to procurement opportunities through standardized small business maturity assurance and local ecosystem building.',
}

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      {/* ===== ENHANCED HEADER ===== */}
      <nav className="bg-white/95 backdrop-blur-md border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="h-10 w-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center mr-3">
                {/* North Star Logo */}
                <svg className="h-6 w-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 2l2.4 7.2h7.6l-6 4.8 2.4 7.2-6-4.8-6 4.8 2.4-7.2-6-4.8h7.6z"/>
                </svg>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Polaris</h1>
                <p className="text-xs text-gray-600">Procurement Readiness Platform</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                href="/auth/login"
                className="text-gray-700 hover:text-blue-600 font-medium transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/auth/register"
                className="bg-blue-600 text-white px-6 py-2 rounded-lg font-semibold hover:bg-blue-700 transition-colors shadow-sm"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* ===== ENHANCED HERO SECTION ===== */}
      <section className="relative py-20 lg:py-32 overflow-hidden">
        {/* Background Elements */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 via-purple-600/5 to-blue-800/5"></div>
        <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl"></div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="mb-8">
            <h1 className="text-4xl md:text-6xl lg:text-7xl font-bold text-gray-900 mb-6 leading-tight">
              <span className="block">Accelerate Your Path to</span>
              <span className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent block">
                Procurement Success
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl text-gray-600 mb-12 max-w-4xl mx-auto leading-relaxed">
              Transform your business into a competitive, procurement-ready organization through 
              expert-guided maturity development and strategic local partnerships.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
              <Link 
                href="/auth/register"
                className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 via-blue-700 to-blue-800 text-white font-bold text-lg rounded-xl shadow-lg hover:shadow-xl hover:-translate-y-0.5 transition-all duration-300"
              >
                Find Your Local Agency
                <ArrowRight className="ml-3 h-6 w-6" />
              </Link>
              
              <Link 
                href="/auth/login"
                className="inline-flex items-center px-8 py-4 bg-white/80 backdrop-blur-sm border-2 border-blue-200 text-blue-700 font-semibold text-lg rounded-xl hover:bg-blue-50 transition-all duration-300"
              >
                Agency Partner Login
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* ===== PROCUREMENT READINESS FEATURES ===== */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Procurement Readiness{' '}
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Made Simple
              </span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Expert-guided business transformation through proven assessment methodology, 
              strategic partnerships, and competitive advantage development.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {/* Enhanced Feature Cards with Icons */}
            <div className="bg-gradient-to-br from-white to-blue-50/50 rounded-2xl border border-blue-100 shadow-lg hover:shadow-xl transition-all duration-300 p-8 group">
              <div className="h-16 w-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Target className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Standardized Maturity Assessment</h3>
              <p className="text-gray-600 leading-relaxed mb-6">
                Comprehensive 10-area business evaluation framework designed to measure and improve 
                procurement readiness across all critical business dimensions.
              </p>
              <div className="flex items-center text-blue-600 font-semibold">
                <FileCheck className="h-4 w-4 mr-2" />
                <span>View Assessment Framework</span>
              </div>
            </div>

            <div className="bg-gradient-to-br from-white to-green-50/50 rounded-2xl border border-green-100 shadow-lg hover:shadow-xl transition-all duration-300 p-8 group">
              <div className="h-16 w-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Network className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Local Ecosystem Building</h3>
              <p className="text-gray-600 leading-relaxed mb-6">
                Connect with verified local agencies, service providers, and business support organizations 
                to build a stronger procurement-ready business community.
              </p>
              <div className="flex items-center text-green-600 font-semibold">
                <Map className="h-4 w-4 mr-2" />
                <span>Find Local Partners</span>
              </div>
            </div>

            <div className="bg-gradient-to-br from-white to-purple-50/50 rounded-2xl border border-purple-100 shadow-lg hover:shadow-xl transition-all duration-300 p-8 group">
              <div className="h-16 w-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform">
                <Award className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Competitive Advantage Development</h3>
              <p className="text-gray-600 leading-relaxed mb-6">
                Identify market positioning opportunities and develop strategic advantages 
                that differentiate your business in procurement competitions.
              </p>
              <div className="flex items-center text-purple-600 font-semibold">
                <TrendingUp className="h-4 w-4 mr-2" />
                <span>Build Competitive Edge</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== LOCAL ECOSYSTEM STATS ===== */}
      <section className="py-20 bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h3 className="text-3xl font-bold mb-12">Strengthening Local Business Ecosystems</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="group">
              <div className="text-4xl font-bold mb-2">850+</div>
              <div className="text-blue-200">Local Agencies</div>
              <div className="text-sm text-blue-300 mt-1">Nationwide Network</div>
            </div>
            <div className="group">
              <div className="text-4xl font-bold mb-2">15,000+</div>
              <div className="text-blue-200">Businesses Assessed</div>
              <div className="text-sm text-blue-300 mt-1">Procurement Ready</div>
            </div>
            <div className="group">
              <div className="text-4xl font-bold mb-2">2,400+</div>
              <div className="text-blue-200">Service Providers</div>
              <div className="text-sm text-blue-300 mt-1">Verified Experts</div>
            </div>
            <div className="group">
              <div className="text-4xl font-bold mb-2">$2.8M+</div>
              <div className="text-blue-200">Contracts Secured</div>
              <div className="text-sm text-blue-300 mt-1">Business Growth</div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== HOW IT WORKS - PROCUREMENT READINESS ===== */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Your Path to Procurement Readiness
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our proven methodology transforms small businesses into competitive, procurement-ready organizations 
              through systematic maturity assessment and targeted capability building.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="h-20 w-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <div className="h-12 w-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                  1
                </div>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Connect with Local Agency</h3>
              <p className="text-gray-600">
                Register and select your local procurement agency sponsor to gain access 
                to the standardized business maturity assessment framework.
              </p>
            </div>

            <div className="text-center">
              <div className="h-20 w-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <div className="h-12 w-12 bg-green-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                  2
                </div>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Complete Guided Assessment</h3>
              <p className="text-gray-600">
                Work through tier-based evaluations with expert support to identify 
                improvement opportunities and competitive advantage development areas.
              </p>
            </div>

            <div className="text-center">
              <div className="h-20 w-20 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <div className="h-12 w-12 bg-purple-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                  3
                </div>
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Achieve Procurement Readiness</h3>
              <p className="text-gray-600">
                Access strategic partnerships, verified capabilities, and ongoing support 
                to compete successfully in procurement opportunities.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ===== USER ACCOUNT TYPES SECTION ===== */}
      <section className="py-20 bg-gradient-to-br from-gray-50 to-blue-50/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-6">
              Choose Your{' '}
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Business Journey
              </span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Different pathways to procurement readiness based on your role in the business ecosystem.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Client Account */}
            <div className="bg-white rounded-2xl border-2 border-blue-100 shadow-lg hover:shadow-xl transition-all duration-300 p-8 group hover:border-blue-200">
              <div className="text-center mb-6">
                <div className="h-16 w-16 bg-gradient-to-br from-blue-500 to-blue-600 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                  <Building className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">Small Business Client</h3>
                <div className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                  Most Popular
                </div>
              </div>
              
              <div className="space-y-4 mb-8">
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Complete tier-based maturity assessments across 10 critical business areas</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Access local service providers for gap remediation and capability building</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Track progress toward procurement readiness certification</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">AI-powered guidance and competitive advantage development</span>
                </div>
              </div>
              
              <div className="border-t border-gray-100 pt-6">
                <p className="text-sm text-gray-600 mb-4">
                  Perfect for small businesses seeking procurement opportunities
                </p>
                <Link 
                  href="/auth/register"
                  className="w-full inline-flex items-center justify-center px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Get Agency Sponsorship
                </Link>
              </div>
            </div>

            {/* Provider Account */}
            <div className="bg-white rounded-2xl border-2 border-green-100 shadow-lg hover:shadow-xl transition-all duration-300 p-8 group hover:border-green-200">
              <div className="text-center mb-6">
                <div className="h-16 w-16 bg-gradient-to-br from-green-500 to-green-600 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                  <Users className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">Service Provider</h3>
                <div className="inline-flex items-center px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
                  Expert Network
                </div>
              </div>
              
              <div className="space-y-4 mb-8">
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Join verified network of procurement readiness specialists</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Receive matched client opportunities based on assessment gaps</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Manage client engagements and track service delivery</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Build reputation through verified client success stories</span>
                </div>
              </div>
              
              <div className="border-t border-gray-100 pt-6">
                <p className="text-sm text-gray-600 mb-4">
                  Ideal for consultants and business development experts
                </p>
                <Link 
                  href="/auth/register"
                  className="w-full inline-flex items-center justify-center px-6 py-3 bg-green-600 text-white font-semibold rounded-lg hover:bg-green-700 transition-colors"
                >
                  Apply to Provider Network
                </Link>
              </div>
            </div>

            {/* Agency Account */}
            <div className="bg-white rounded-2xl border-2 border-purple-100 shadow-lg hover:shadow-xl transition-all duration-300 p-8 group hover:border-purple-200">
              <div className="text-center mb-6">
                <div className="h-16 w-16 bg-gradient-to-br from-purple-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform">
                  <Network className="h-8 w-8 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">Local Agency</h3>
                <div className="inline-flex items-center px-3 py-1 bg-purple-100 text-purple-800 rounded-full text-sm font-medium">
                  Ecosystem Leader
                </div>
              </div>
              
              <div className="space-y-4 mb-8">
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Sponsor local small businesses through assessment programs</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Generate and distribute assessment access codes to clients</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Configure tier access levels and monitor client progress</span>
                </div>
                <div className="flex items-start">
                  <CheckCircle className="h-5 w-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-700">Build stronger local business ecosystems and partnerships</span>
                </div>
              </div>
              
              <div className="border-t border-gray-100 pt-6">
                <p className="text-sm text-gray-600 mb-4">
                  For economic development organizations and business incubators
                </p>
                <Link 
                  href="/auth/register"
                  className="w-full inline-flex items-center justify-center px-6 py-3 bg-purple-600 text-white font-semibold rounded-lg hover:bg-purple-700 transition-colors"
                >
                  Become Agency Partner
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== ENHANCED CTA SECTION ===== */}
      <section className="py-20 bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 text-white relative overflow-hidden">
        {/* Background Pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-64 h-64 border border-white/20 rounded-full"></div>
          <div className="absolute top-32 right-16 w-48 h-48 border border-white/20 rounded-full"></div>
          <div className="absolute bottom-16 left-32 w-32 h-32 border border-white/20 rounded-full"></div>
        </div>
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl md:text-6xl font-bold mb-6">
            Ready to Unlock Procurement Opportunities?
          </h2>
          <p className="text-xl text-blue-200 mb-12 max-w-3xl mx-auto">
            Partner with your local agency to access the standardized assessment framework 
            and begin your journey toward procurement readiness and competitive advantage.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-6 justify-center">
            <Link 
              href="/auth/register"
              className="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold text-lg rounded-xl shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-300"
            >
              <Handshake className="mr-3 h-6 w-6" />
              Find Your Local Agency Partner
              <ArrowRight className="ml-3 h-6 w-6" />
            </Link>
            
            <Link 
              href="/about"
              className="inline-flex items-center px-8 py-4 bg-white/10 backdrop-blur-sm border border-white/20 text-white font-semibold text-lg rounded-xl hover:bg-white/20 transition-all duration-300"
            >
              <Shield className="mr-3 h-6 w-6" />
              Learn About Our Platform
            </Link>
          </div>

          {/* Trust Indicators */}
          <div className="mt-16 pt-16 border-t border-white/20">
            <p className="text-blue-200 mb-8">Trusted by leading procurement agencies and business development organizations</p>
            <div className="flex flex-wrap justify-center items-center gap-8 opacity-60">
              <div className="flex items-center space-x-2">
                <Building className="h-6 w-6" />
                <span className="font-medium">SBA Partners</span>
              </div>
              <div className="flex items-center space-x-2">
                <Award className="h-6 w-6" />
                <span className="font-medium">APEX Accelerators</span>
              </div>
              <div className="flex items-center space-x-2">
                <Users className="h-6 w-6" />
                <span className="font-medium">Local EDCs</span>
              </div>
              <div className="flex items-center space-x-2">
                <Network className="h-6 w-6" />
                <span className="font-medium">Business Networks</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}