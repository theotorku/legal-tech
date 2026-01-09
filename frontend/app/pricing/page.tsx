'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { subscriptionAPI } from '@/lib/api-client';
import { SubscriptionPlanPublic, BillingCycle } from '@/lib/types';
import { useAuthStore } from '@/lib/store';
import { Check, Scale, ArrowLeft, Crown, Shield, Briefcase, Building2 } from 'lucide-react';

export default function PricingPage() {
  const router = useRouter();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);

  const [plans, setPlans] = useState<SubscriptionPlanPublic[]>([]);
  const [billingCycle, setBillingCycle] = useState<BillingCycle>('monthly');
  const [loading, setLoading] = useState(true);
  const [subscribing, setSubscribing] = useState<string | null>(null);

  useEffect(() => {
    loadPlans();
  }, []);

  const loadPlans = async () => {
    try {
      const data = await subscriptionAPI.getPlans();
      setPlans(data);
    } catch (error) {
      console.error('Failed to load plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (planName: string) => {
    if (!isAuthenticated) {
      router.push('/register');
      return;
    }

    setSubscribing(planName);
    try {
      await subscriptionAPI.subscribe({
        plan_name: planName,
        billing_cycle: billingCycle,
      });
      router.push('/dashboard?subscribed=true');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to subscribe');
    } finally {
      setSubscribing(null);
    }
  };

  const getPrice = (plan: SubscriptionPlanPublic) => {
    return billingCycle === 'monthly' ? plan.price_monthly : plan.price_annual / 12;
  };

  const getPlanIcon = (planName: string) => {
    switch (planName) {
      case 'starter': return <Shield className="w-6 h-6" />;
      case 'professional': return <Crown className="w-6 h-6" />;
      case 'business': return <Briefcase className="w-6 h-6" />;
      case 'enterprise': return <Building2 className="w-6 h-6" />;
      default: return <Scale className="w-6 h-6" />;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto"></div>
          <p className="mt-4 text-slate-400">Loading plans...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 py-12 px-4">
      {/* Navigation */}
      <div className="max-w-7xl mx-auto mb-8">
        <Link href="/" className="inline-flex items-center text-slate-400 hover:text-amber-400 transition-colors">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to home
        </Link>
      </div>

      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl mb-6 shadow-lg shadow-amber-500/20">
            <Scale className="w-8 h-8 text-slate-900" />
          </div>
          <h1 className="text-4xl md:text-5xl font-serif font-bold text-white mb-4">
            Select Your Counsel Plan
          </h1>
          <p className="text-xl text-slate-400 mb-8 max-w-2xl mx-auto">
            Choose the right plan for your practice. All plans include a 14-day free trial.
          </p>

          {/* Billing Toggle */}
          <div className="inline-flex items-center bg-slate-800 rounded-lg p-1.5 border border-slate-700">
            <button
              onClick={() => setBillingCycle('monthly')}
              className={`px-6 py-2.5 rounded-md font-medium transition ${
                billingCycle === 'monthly'
                  ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-slate-900'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingCycle('annual')}
              className={`px-6 py-2.5 rounded-md font-medium transition flex items-center ${
                billingCycle === 'annual'
                  ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-slate-900'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              Annual
              <span className="ml-2 text-xs bg-emerald-500/20 text-emerald-400 px-2 py-0.5 rounded font-semibold">
                Save 17%
              </span>
            </button>
          </div>
        </div>

        {/* Plans Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mb-16">
          {plans.map((plan) => (
            <div
              key={plan.id}
              className={`bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-8 border transition-all hover:scale-[1.02] ${
                plan.name === 'professional'
                  ? 'border-amber-500/50 ring-1 ring-amber-500/20 relative'
                  : 'border-slate-700/50 hover:border-amber-500/30'
              }`}
            >
              {plan.name === 'professional' && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <div className="bg-gradient-to-r from-amber-500 to-amber-600 text-slate-900 px-4 py-1 rounded-full text-sm font-bold shadow-lg shadow-amber-500/30">
                    Most Popular
                  </div>
                </div>
              )}

              <div className={`w-12 h-12 rounded-lg flex items-center justify-center mb-4 ${
                plan.name === 'professional'
                  ? 'bg-gradient-to-br from-amber-500 to-amber-600 text-slate-900'
                  : 'bg-slate-700 text-amber-400'
              }`}>
                {getPlanIcon(plan.name)}
              </div>

              <h3 className="text-2xl font-serif font-bold text-white mb-2">
                {plan.display_name}
              </h3>
              <p className="text-slate-400 mb-6 h-12 text-sm">{plan.description}</p>

              <div className="mb-6">
                <span className="text-4xl font-bold text-white">
                  ${getPrice(plan).toFixed(0)}
                </span>
                <span className="text-slate-400">/month</span>
                {billingCycle === 'annual' && (
                  <p className="text-sm text-emerald-400 mt-1">
                    Billed ${plan.price_annual}/year
                  </p>
                )}
              </div>

              <button
                onClick={() => handleSubscribe(plan.name)}
                disabled={subscribing === plan.name}
                className={`w-full py-3 px-4 rounded-lg font-semibold transition ${
                  plan.name === 'professional'
                    ? 'bg-gradient-to-r from-amber-500 to-amber-600 text-slate-900 hover:from-amber-400 hover:to-amber-500 shadow-lg shadow-amber-500/25'
                    : 'bg-slate-700 text-white hover:bg-slate-600 border border-slate-600'
                } disabled:opacity-50`}
              >
                {subscribing === plan.name ? 'Processing...' : 'Start Free Trial'}
              </button>

              <ul className="mt-8 space-y-3">
                <li className="flex items-start">
                  <Check className="w-5 h-5 text-amber-400 mr-3 flex-shrink-0 mt-0.5" />
                  <span className="text-slate-300 text-sm">
                    {plan.contracts_per_month === -1
                      ? 'Unlimited'
                      : plan.contracts_per_month}{' '}
                    contracts/month
                  </span>
                </li>
                {plan.features.map((feature, idx) => (
                  <li key={idx} className="flex items-start">
                    <Check className="w-5 h-5 text-amber-400 mr-3 flex-shrink-0 mt-0.5" />
                    <span className="text-slate-300 text-sm">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Trust badges */}
        <div className="text-center border-t border-slate-800 pt-12">
          <p className="text-slate-500 text-sm mb-4">Trusted by legal professionals worldwide</p>
          <div className="flex justify-center items-center gap-8 text-slate-600 text-xs">
            <span className="flex items-center gap-2">
              <Shield className="w-4 h-4" />
              SOC 2 Compliant
            </span>
            <span>•</span>
            <span>GDPR Ready</span>
            <span>•</span>
            <span>256-bit Encryption</span>
            <span>•</span>
            <span>ABA Endorsed</span>
          </div>
        </div>
      </div>
    </div>
  );
}

