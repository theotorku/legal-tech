import Link from 'next/link';
import { Scale, Gavel, Shield, BookOpen, ArrowRight, Award, Lock, FileCheck } from 'lucide-react';

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900">
      {/* Navigation */}
      <nav className="bg-slate-900/95 backdrop-blur-sm border-b border-amber-900/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            <div className="flex items-center">
              <div className="flex items-center justify-center w-12 h-12 bg-gradient-to-br from-amber-500 to-amber-600 rounded-lg mr-3 shadow-lg shadow-amber-500/20">
                <Scale className="w-7 h-7 text-slate-900" />
              </div>
              <div>
                <span className="text-xl font-serif font-bold text-white tracking-wide">LegalMind</span>
                <span className="block text-[10px] text-amber-500 uppercase tracking-[0.2em] font-medium">Contract Intelligence</span>
              </div>
            </div>
            <div className="flex items-center space-x-6">
              <Link
                href="/pricing"
                className="text-slate-300 hover:text-amber-400 px-3 py-2 text-sm font-medium transition-colors"
              >
                Pricing
              </Link>
              <Link
                href="/login"
                className="text-slate-300 hover:text-amber-400 px-3 py-2 text-sm font-medium transition-colors"
              >
                Sign In
              </Link>
              <Link
                href="/register"
                className="bg-gradient-to-r from-amber-500 to-amber-600 text-slate-900 px-5 py-2.5 rounded font-semibold hover:from-amber-400 hover:to-amber-500 transition-all shadow-lg shadow-amber-500/25"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="relative overflow-hidden">
        {/* Decorative elements */}
        <div className="absolute top-20 left-10 w-72 h-72 bg-amber-500/10 rounded-full blur-3xl"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-amber-600/5 rounded-full blur-3xl"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 relative">
          <div className="text-center">
            {/* Badge */}
            <div className="inline-flex items-center bg-amber-500/10 border border-amber-500/20 rounded-full px-4 py-2 mb-8">
              <Award className="w-4 h-4 text-amber-400 mr-2" />
              <span className="text-amber-400 text-sm font-medium">Trusted by 500+ Law Firms</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-serif font-bold text-white mb-6 leading-tight">
              Legal Contract Analysis
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-amber-600 mt-2">
                Powered by AI
              </span>
            </h1>
            <p className="text-xl text-slate-400 mb-10 max-w-3xl mx-auto leading-relaxed">
              Transform your legal practice with AI-driven contract intelligence.
              Identify risks, ensure compliance, and extract key clauses with
              <span className="text-amber-400 font-semibold"> unprecedented accuracy</span>.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Link
                href="/register"
                className="bg-gradient-to-r from-amber-500 to-amber-600 text-slate-900 px-8 py-4 rounded font-bold text-lg hover:from-amber-400 hover:to-amber-500 transition-all shadow-xl shadow-amber-500/30 inline-flex items-center justify-center"
              >
                Begin Free Trial
                <ArrowRight className="w-5 h-5 ml-2" />
              </Link>
              <Link
                href="/pricing"
                className="bg-slate-800 text-white px-8 py-4 rounded font-semibold text-lg border border-slate-700 hover:bg-slate-700 hover:border-slate-600 transition-all"
              >
                View Plans
              </Link>
            </div>
            <p className="text-sm text-slate-500 mt-6">
              <Lock className="w-4 h-4 inline mr-1" />
              14-day trial • No credit card required • SOC 2 Compliant
            </p>
          </div>
        </div>
      </div>

      {/* Features */}
      <div className="bg-slate-800/50 border-y border-slate-700/50 py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-sm font-semibold text-amber-400 uppercase tracking-wider mb-3">
              Why Legal Professionals Choose Us
            </h2>
            <p className="text-3xl md:text-4xl font-serif font-bold text-white">
              Built for the Modern Law Practice
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-8 border border-slate-700/50 hover:border-amber-500/30 transition-all group">
              <div className="w-14 h-14 bg-gradient-to-br from-amber-500 to-amber-600 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-lg shadow-amber-500/20">
                <Gavel className="w-7 h-7 text-slate-900" />
              </div>
              <h3 className="text-xl font-serif font-bold text-white mb-3">Judicial Precision</h3>
              <p className="text-slate-400 leading-relaxed">
                AI trained on millions of legal documents ensures analysis meets the highest
                standards of legal accuracy and compliance.
              </p>
            </div>
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-8 border border-slate-700/50 hover:border-amber-500/30 transition-all group">
              <div className="w-14 h-14 bg-gradient-to-br from-amber-500 to-amber-600 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-lg shadow-amber-500/20">
                <Shield className="w-7 h-7 text-slate-900" />
              </div>
              <h3 className="text-xl font-serif font-bold text-white mb-3">Risk Identification</h3>
              <p className="text-slate-400 leading-relaxed">
                Automatically detect unfavorable terms, hidden liabilities, and compliance
                gaps before they become costly legal issues.
              </p>
            </div>
            <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-xl p-8 border border-slate-700/50 hover:border-amber-500/30 transition-all group">
              <div className="w-14 h-14 bg-gradient-to-br from-amber-500 to-amber-600 rounded-lg flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-lg shadow-amber-500/20">
                <BookOpen className="w-7 h-7 text-slate-900" />
              </div>
              <h3 className="text-xl font-serif font-bold text-white mb-3">Clause Library</h3>
              <p className="text-slate-400 leading-relaxed">
                Extract and categorize key clauses instantly. Build your knowledge base
                with every contract analyzed.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Social Proof / Stats */}
      <div className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-8 text-center">
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
              <FileCheck className="w-8 h-8 text-amber-400 mx-auto mb-3" />
              <p className="text-4xl font-serif font-bold text-white mb-1">50,000+</p>
              <p className="text-slate-400 text-sm">Contracts Analyzed</p>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
              <Scale className="w-8 h-8 text-amber-400 mx-auto mb-3" />
              <p className="text-4xl font-serif font-bold text-white mb-1">500+</p>
              <p className="text-slate-400 text-sm">Law Firms Trust Us</p>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
              <Shield className="w-8 h-8 text-amber-400 mx-auto mb-3" />
              <p className="text-4xl font-serif font-bold text-white mb-1">99.7%</p>
              <p className="text-slate-400 text-sm">Accuracy Rate</p>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700/50">
              <Award className="w-8 h-8 text-amber-400 mx-auto mb-3" />
              <p className="text-4xl font-serif font-bold text-white mb-1">90%</p>
              <p className="text-slate-400 text-sm">Time Saved</p>
            </div>
          </div>
        </div>
      </div>

      {/* Testimonial */}
      <div className="py-20 bg-slate-800/30">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="mb-6">
            <div className="inline-flex gap-1">
              {[...Array(5)].map((_, i) => (
                <svg key={i} className="w-6 h-6 text-amber-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              ))}
            </div>
          </div>
          <blockquote className="text-2xl md:text-3xl font-serif text-white italic leading-relaxed mb-8">
            "LegalMind has revolutionized how we handle contract review. What used to take
            hours now takes minutes, with even greater accuracy than before."
          </blockquote>
          <div>
            <p className="text-white font-semibold">Sarah Mitchell, J.D.</p>
            <p className="text-slate-400 text-sm">Partner, Mitchell & Associates LLP</p>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-24">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-gradient-to-br from-amber-500 to-amber-600 rounded-2xl p-12 text-center relative overflow-hidden">
            {/* Decorative scales */}
            <div className="absolute top-4 right-4 opacity-10">
              <Scale className="w-32 h-32" />
            </div>
            <h2 className="text-3xl md:text-4xl font-serif font-bold text-slate-900 mb-4">
              Elevate Your Legal Practice
            </h2>
            <p className="text-lg text-slate-800 mb-8 max-w-2xl mx-auto">
              Join the leading law firms already using AI-powered contract intelligence.
              Start your 14-day trial today.
            </p>
            <Link
              href="/register"
              className="bg-slate-900 text-amber-400 px-8 py-4 rounded font-bold text-lg hover:bg-slate-800 transition-all inline-flex items-center shadow-xl"
            >
              Begin Your Free Trial
              <ArrowRight className="w-5 h-5 ml-2" />
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-slate-950 border-t border-slate-800 py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-12">
            <div>
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 bg-gradient-to-br from-amber-500 to-amber-600 rounded-lg flex items-center justify-center mr-3">
                  <Scale className="w-5 h-5 text-slate-900" />
                </div>
                <div>
                  <span className="font-serif font-bold text-white">LegalMind</span>
                </div>
              </div>
              <p className="text-slate-500 text-sm leading-relaxed">
                AI-powered contract analysis for the modern legal practice.
                Trusted by leading law firms worldwide.
              </p>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-4 uppercase text-sm tracking-wider">Product</h3>
              <ul className="space-y-3 text-sm text-slate-400">
                <li><Link href="/pricing" className="hover:text-amber-400 transition-colors">Pricing</Link></li>
                <li><Link href="/register" className="hover:text-amber-400 transition-colors">Sign Up</Link></li>
                <li><a href="#" className="hover:text-amber-400 transition-colors">Features</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-4 uppercase text-sm tracking-wider">Company</h3>
              <ul className="space-y-3 text-sm text-slate-400">
                <li><a href="#" className="hover:text-amber-400 transition-colors">About Us</a></li>
                <li><a href="#" className="hover:text-amber-400 transition-colors">Contact</a></li>
                <li><a href="#" className="hover:text-amber-400 transition-colors">Careers</a></li>
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-white mb-4 uppercase text-sm tracking-wider">Legal</h3>
              <ul className="space-y-3 text-sm text-slate-400">
                <li><a href="#" className="hover:text-amber-400 transition-colors">Privacy Policy</a></li>
                <li><a href="#" className="hover:text-amber-400 transition-colors">Terms of Service</a></li>
                <li><a href="#" className="hover:text-amber-400 transition-colors">Security</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-slate-800 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
            <p className="text-slate-500 text-sm">
              &copy; 2026 LegalMind. All rights reserved.
            </p>
            <div className="flex items-center gap-4 mt-4 md:mt-0">
              <span className="text-slate-600 text-xs">SOC 2 Compliant</span>
              <span className="text-slate-700">•</span>
              <span className="text-slate-600 text-xs">GDPR Ready</span>
              <span className="text-slate-700">•</span>
              <span className="text-slate-600 text-xs">ABA Endorsed</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
