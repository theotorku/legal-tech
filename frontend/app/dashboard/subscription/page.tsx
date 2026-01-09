'use client';

import { useEffect, useState } from 'react';
import { subscriptionAPI } from '@/lib/api-client';
import { useSubscriptionStore } from '@/lib/store';
import { SubscriptionPlanPublic } from '@/lib/types';
import {
  CreditCard,
  Calendar,
  TrendingUp,
  AlertCircle,
  CheckCircle,
  ArrowUpCircle,
  Scale,
  Clock,
} from 'lucide-react';

export default function SubscriptionPage() {
  const { subscription, usage, setSubscription } = useSubscriptionStore();
  const [plans, setPlans] = useState<SubscriptionPlanPublic[]>([]);
  const [loading, setLoading] = useState(true);
  const [upgrading, setUpgrading] = useState(false);
  const [canceling, setCanceling] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const plansData = await subscriptionAPI.getPlans();
      setPlans(plansData);
    } catch (error) {
      console.error('Failed to load plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async (planName: string) => {
    if (!confirm(`Upgrade to ${planName} plan?`)) return;

    setUpgrading(true);
    try {
      const response = await subscriptionAPI.upgrade(planName);
      setSubscription(response.subscription);
      alert(response.message);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to upgrade');
    } finally {
      setUpgrading(false);
    }
  };

  const handleCancel = async () => {
    if (!confirm('Are you sure you want to cancel your subscription? Access will continue until the end of your billing period.')) {
      return;
    }

    setCanceling(true);
    try {
      const response = await subscriptionAPI.cancel();
      setSubscription(response.subscription);
      alert(response.message);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to cancel subscription');
    } finally {
      setCanceling(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500"></div>
      </div>
    );
  }

  const currentPlan = subscription?.plan;
  const isTrialActive = subscription?.status === 'trial';
  const isCanceled = subscription?.status === 'canceled';

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-serif font-bold text-slate-900 mb-2">Subscription Management</h1>
        <p className="text-slate-600">Manage your plan, billing, and usage</p>
      </div>

      {/* Current Subscription */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8">
        <div className="flex items-center mb-6">
          <Scale className="w-5 h-5 text-amber-600 mr-2" />
          <h2 className="text-xl font-serif font-bold text-slate-900">Current Subscription</h2>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Plan Info */}
          <div className="p-5 bg-slate-50 rounded-xl border border-slate-100">
            <div className="flex items-center mb-4">
              <div className="w-10 h-10 bg-amber-100 rounded-lg flex items-center justify-center mr-3">
                <CreditCard className="w-5 h-5 text-amber-600" />
              </div>
              <div>
                <p className="text-sm text-slate-500">Current Plan</p>
                <p className="text-xl font-serif font-bold text-slate-900 capitalize">
                  {currentPlan?.display_name}
                </p>
              </div>
            </div>

            <div className="space-y-3 mt-4">
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-emerald-500 mr-2" />
                <span className="text-slate-700">
                  {currentPlan?.contracts_per_month === -1
                    ? 'Unlimited'
                    : currentPlan?.contracts_per_month}{' '}
                  contracts/month
                </span>
              </div>
              <div className="flex items-center">
                <CheckCircle className="w-5 h-5 text-emerald-500 mr-2" />
                <span className="text-slate-700">
                  {currentPlan?.rate_limit_per_minute} requests/minute
                </span>
              </div>
            </div>
          </div>

          {/* Billing Info */}
          <div className="p-5 bg-slate-50 rounded-xl border border-slate-100">
            <div className="flex items-center mb-4">
              <div className="w-10 h-10 bg-slate-200 rounded-lg flex items-center justify-center mr-3">
                <Calendar className="w-5 h-5 text-slate-600" />
              </div>
              <div>
                <p className="text-sm text-slate-500">Billing Cycle</p>
                <p className="text-xl font-serif font-bold text-slate-900 capitalize">
                  {subscription?.billing_cycle}
                </p>
              </div>
            </div>

            <div className="space-y-3 text-sm mt-4">
              <div className="flex justify-between">
                <span className="text-slate-500">Status:</span>
                <span className={`font-semibold capitalize px-2 py-0.5 rounded-full text-xs ${
                  isTrialActive ? 'bg-amber-100 text-amber-700' :
                  isCanceled ? 'bg-red-100 text-red-700' : 'bg-emerald-100 text-emerald-700'
                }`}>
                  {subscription?.status}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Period Start:</span>
                <span className="text-slate-900 font-medium">
                  {new Date(subscription?.current_period_start!).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Period End:</span>
                <span className="text-slate-900 font-medium">
                  {new Date(subscription?.current_period_end!).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Trial Banner */}
        {isTrialActive && (
          <div className="mt-6 p-5 bg-gradient-to-r from-amber-50 to-amber-100/50 border border-amber-200 rounded-xl flex items-center">
            <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mr-4">
              <Clock className="w-6 h-6 text-amber-600" />
            </div>
            <div>
              <p className="text-amber-900 font-semibold">
                Free Trial Active
              </p>
              <p className="text-sm text-amber-700">
                Trial ends on {new Date(subscription?.trial_end!).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })} • No payment required
              </p>
            </div>
          </div>
        )}

        {/* Canceled Banner */}
        {isCanceled && (
          <div className="mt-6 p-5 bg-red-50 border border-red-200 rounded-xl flex items-center">
            <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center mr-4">
              <AlertCircle className="w-6 h-6 text-red-600" />
            </div>
            <div>
              <p className="text-red-900 font-semibold">
                Subscription Canceled
              </p>
              <p className="text-sm text-red-700">
                Access continues until {new Date(subscription?.current_period_end!).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Usage Stats */}
      {usage && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8">
          <div className="flex items-center mb-6">
            <TrendingUp className="w-5 h-5 text-emerald-600 mr-2" />
            <h2 className="text-xl font-serif font-bold text-slate-900">Current Usage</h2>
          </div>

          <div className="space-y-4">
            <div className="p-5 bg-slate-50 rounded-xl border border-slate-100">
              <div className="flex justify-between mb-3">
                <span className="text-slate-700 font-medium">Contracts Analyzed</span>
                <span className="font-bold text-slate-900">
                  {usage.contracts_analyzed} / {usage.contracts_limit === -1 ? '∞' : usage.contracts_limit}
                </span>
              </div>
              <div className="w-full bg-slate-200 rounded-full h-3">
                <div
                  className={`h-3 rounded-full transition-all ${
                    usage.percentage_used > 80 ? 'bg-gradient-to-r from-red-500 to-red-600' :
                    usage.percentage_used > 50 ? 'bg-gradient-to-r from-amber-500 to-amber-600' : 'bg-gradient-to-r from-emerald-500 to-emerald-600'
                  }`}
                  style={{ width: `${Math.min(usage.percentage_used, 100)}%` }}
                />
              </div>
              <p className="text-sm text-slate-500 mt-2">
                {usage.percentage_used.toFixed(1)}% of monthly limit used
              </p>
            </div>

            {usage.overage_contracts > 0 && (
              <div className="p-4 bg-amber-50 border border-amber-200 rounded-xl flex items-center">
                <AlertCircle className="w-5 h-5 text-amber-600 mr-3" />
                <span className="text-amber-900">
                  {usage.overage_contracts} overage contracts (additional charges may apply)
                </span>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Available Plans */}
      {!isCanceled && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 mb-8">
          <div className="flex items-center mb-6">
            <ArrowUpCircle className="w-5 h-5 text-amber-600 mr-2" />
            <h2 className="text-xl font-serif font-bold text-slate-900">Upgrade Your Plan</h2>
          </div>

          <div className="grid md:grid-cols-2 gap-6">
            {plans
              .filter((plan) => plan.name !== currentPlan?.name)
              .map((plan) => (
                <div
                  key={plan.id}
                  className="p-6 border-2 border-slate-200 rounded-xl hover:border-amber-400 hover:bg-amber-50/30 transition-all"
                >
                  <h3 className="text-lg font-serif font-bold text-slate-900 mb-2">
                    {plan.display_name}
                  </h3>
                  <p className="text-3xl font-serif font-bold text-slate-900 mb-4">
                    ${plan.price_monthly}
                    <span className="text-base font-normal text-slate-500">/month</span>
                  </p>
                  <ul className="space-y-2 mb-6">
                    <li className="flex items-center text-sm text-slate-700">
                      <CheckCircle className="w-4 h-4 text-amber-500 mr-2" />
                      {plan.contracts_per_month === -1 ? 'Unlimited' : plan.contracts_per_month} contracts/month
                    </li>
                    {plan.features.slice(0, 3).map((feature, idx) => (
                      <li key={idx} className="flex items-center text-sm text-slate-700">
                        <CheckCircle className="w-4 h-4 text-amber-500 mr-2" />
                        {feature}
                      </li>
                    ))}
                  </ul>
                  <button
                    onClick={() => handleUpgrade(plan.name)}
                    disabled={upgrading}
                    className="w-full bg-gradient-to-r from-amber-500 to-amber-600 text-slate-900 py-3 px-4 rounded-lg font-semibold hover:from-amber-400 hover:to-amber-500 transition-all disabled:opacity-50 shadow-lg shadow-amber-500/20"
                  >
                    {upgrading ? 'Processing...' : 'Upgrade Now'}
                  </button>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Cancel Subscription */}
      {!isCanceled && (
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
          <h2 className="text-xl font-serif font-bold text-slate-900 mb-4">Cancel Subscription</h2>
          <p className="text-slate-600 mb-4">
            Your access will continue until the end of your current billing period. You can resubscribe at any time.
          </p>
          <button
            onClick={handleCancel}
            disabled={canceling}
            className="bg-slate-100 text-red-600 border border-slate-200 py-2.5 px-6 rounded-lg font-medium hover:bg-red-50 hover:border-red-200 transition disabled:opacity-50"
          >
            {canceling ? 'Canceling...' : 'Cancel Subscription'}
          </button>
        </div>
      )}
    </div>
  );
}

