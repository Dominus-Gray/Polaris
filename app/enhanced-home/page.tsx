import React from 'react'
import Link from 'next/link'
import { 
  ArrowRight, 
  CheckCircle, 
  Star, 
  Zap, 
  Shield, 
  TrendingUp,
  BarChart3,
  Users,
  Target,
  Sparkles,
  Globe,
  Award
} from 'lucide-react'

const EnhancedHomePage = () => {
  return (
    <div className="min-h-screen">
      {/* ===== ENHANCED HERO SECTION ===== */}
      <section className="polaris-hero-section">
        <div className="polaris-container-premium text-center text-white relative z-10">
          <div className="polaris-fade-in-up">
            <div className="inline-flex items-center px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full text-sm font-medium text-white/90 mb-8 polaris-glow">
              <Sparkles className="w-4 h-4 mr-2" />
              Trusted by 10,000+ businesses worldwide
            </div>
            
            <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-blue-500 bg-clip-text text-transparent">
                Unlock Your
              </span>
              <br />
              <span className="text-white">Business Potential</span>
            </h1>
            
            <p className="text-xl md:text-2xl text-blue-100 mb-12 max-w-3xl mx-auto leading-relaxed">
              Complete tier-based assessments, access professional services, and get AI-powered guidance 
              to ensure your business meets compliance standards and competitive requirements.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-6 justify-center items-center">
              <Link href="/auth/register" className="polaris-button-hero group">
                Start Free Assessment
                <ArrowRight className="ml-3 h-6 w-6 group-hover:translate-x-1 transition-transform" />
              </Link>
              
              <Link href="/auth/login" className="polaris-button-glass">
                Sign In to Continue
              </Link>
            </div>
          </div>
          
          {/* Floating Elements */}
          <div className="absolute top-1/4 left-1/4 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl polaris-float"></div>
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl polaris-float" style={{animationDelay: '1s'}}></div>
        </div>
      </section>

      {/* ===== ENHANCED FEATURES SECTION ===== */}
      <section className="polaris-section-premium">
        <div className="polaris-container-premium">
          <div className="text-center mb-16 polaris-fade-in-up">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
              Everything You Need for{' '}
              <span className="bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Business Excellence
              </span>
            </h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our comprehensive platform provides all the tools and resources you need to assess, 
              improve, and maintain your business compliance standards.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-16">
            {/* Enhanced Feature Cards */}
            <div className="polaris-card-premium polaris-hover-lift-premium group">
              <div className="h-16 w-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <Target className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Tier-Based Assessments</h3>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Comprehensive 10-area business evaluation with tier-based progression and detailed gap analysis.
              </p>
              <div className="flex items-center text-blue-600 font-semibold group-hover:text-purple-600 transition-colors">
                <span>Learn More</span>
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>

            <div className="polaris-card-premium polaris-hover-lift-premium group">
              <div className="h-16 w-16 bg-gradient-to-br from-green-500 to-blue-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <Users className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">Professional Services</h3>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Connect with qualified service providers and get expert help for your business improvement needs.
              </p>
              <div className="flex items-center text-green-600 font-semibold group-hover:text-blue-600 transition-colors">
                <span>Find Providers</span>
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>

            <div className="polaris-card-premium polaris-hover-lift-premium group">
              <div className="h-16 w-16 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                <Zap className="h-8 w-8 text-white" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-4">AI-Powered Guidance</h3>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Get intelligent recommendations and personalized guidance powered by advanced AI technology.
              </p>
              <div className="flex items-center text-purple-600 font-semibold group-hover:text-pink-600 transition-colors">
                <span>Try AI Assistant</span>
                <ArrowRight className="ml-2 h-4 w-4 group-hover:translate-x-1 transition-transform" />
              </div>
            </div>
          </div>

          {/* Enhanced Stats Section */}
          <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-700 rounded-3xl p-12 text-white text-center polaris-scale-in">
            <h3 className="text-3xl font-bold mb-8">Trusted by Industry Leaders</h3>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <div className="polaris-bounce-in-premium">
                <div className="text-4xl font-bold mb-2">10,000+</div>
                <div className="text-blue-200">Businesses Assessed</div>
              </div>
              <div className="polaris-bounce-in-premium" style={{animationDelay: '0.1s'}}>
                <div className="text-4xl font-bold mb-2">95%</div>
                <div className="text-blue-200">Success Rate</div>
              </div>
              <div className="polaris-bounce-in-premium" style={{animationDelay: '0.2s'}}>
                <div className="text-4xl font-bold mb-2">500+</div>
                <div className="text-blue-200">Expert Providers</div>
              </div>
              <div className="polaris-bounce-in-premium" style={{animationDelay: '0.3s'}}>
                <div className="text-4xl font-bold mb-2">24/7</div>
                <div className="text-blue-200">AI Support</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ===== ENHANCED CTA SECTION ===== */}
      <section className="py-20 bg-gradient-to-br from-gray-900 to-blue-900 text-white">
        <div className="polaris-container-premium text-center">
          <div className="polaris-fade-in-up">
            <h2 className="text-4xl md:text-6xl font-bold mb-6">
              Ready to Transform Your Business?
            </h2>
            <p className="text-xl text-blue-200 mb-12 max-w-2xl mx-auto">
              Join thousands of successful businesses that have improved their compliance and competitive advantage with Polaris.
            </p>
            
            <div className="flex flex-col sm:flex-row gap-6 justify-center">
              <Link href="/auth/register" className="polaris-button-hero">
                <Award className="mr-3 h-6 w-6" />
                Start Your Journey Today
                <ArrowRight className="ml-3 h-6 w-6" />
              </Link>
              
              <Link href="/demo" className="polaris-button-glass">
                <Globe className="mr-3 h-6 w-6" />
                Watch Demo
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Floating Action Button */}
      <button className="polaris-button-floating polaris-pulse-premium">
        <Zap className="h-8 w-8" />
      </button>
    </div>
  )
}

export default EnhancedHomePage