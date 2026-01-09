'use client';

import { useEffect, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import Link from 'next/link';
import { subscriptionAPI } from '@/lib/api-client';
import { useSubscriptionStore } from '@/lib/store';
import { SubscriptionWithPlan, CurrentUsage } from '@/lib/types';
import {
  FileText,
  TrendingUp,
  Clock,
  AlertCircle,
  CheckCircle,
  ArrowRight,
  Scale,
  Gavel,
  BookOpen,
} from 'lucide-react';

export default function DashboardPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { subscription, usage, setSubscription, setUsage } = useSubscriptionStore();

  const [loading, setLoading] = useState(true);
  const [showSuccess, setShowSuccess] = useState(false);

  useEffect(() => {
    if (searchParams.get('subscribed') === 'true') {
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 5000);
    }
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const [subData, usageData] = await Promise.all([
        subscriptionAPI.getMySubscription(),
        subscriptionAPI.getUsage(),
      ]);
      setSubscription(subData);
      setUsage(usageData);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-amber-500 mx-auto"></div>
          <p className="mt-4 text-slate-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const isTrialActive = subscription?.status === 'trial';
  const usagePercentage = usage?.percentage_used || 0;
  const isNearLimit = usagePercentage > 80;

  return (
    <div className="max-w-7xl mx-auto">
      {/* Success Message */}
      {showSuccess && (
        <div className="mb-6 p-4 bg-emerald-50 border border-emerald-200 rounded-xl flex items-center shadow-sm">
          <div className="w-10 h-10 bg-emerald-100 rounded-full flex items-center justify-center mr-4">
            <CheckCircle className="w-5 h-5 text-emerald-600" />
          </div>
          <div>
            <p className="text-emerald-900 font-semibold">Welcome to LegalMind!</p>
            <p className="text-emerald-700 text-sm">Your 14-day free trial has started. Begin analyzing contracts today.</p>
          </div>
        </div>
      )}

      {/* Trial Banner */}
      {isTrialActive && subscription && (
        <div className="mb-6 p-5 bg-gradient-to-r from-amber-50 to-amber-100/50 border border-amber-200 rounded-xl flex items-center justify-between shadow-sm">
          <div className="flex items-center">
            <div className="w-12 h-12 bg-amber-100 rounded-xl flex items-center justify-center mr-4">
              <Clock className="w-6 h-6 text-amber-600" />
            </div>
            <div>
              <p className="text-slate-900 font-semibold">Free Trial Active</p>
              <p className="text-sm text-slate-600">
                Your trial period ends on <span className="font-medium">{new Date(subscription.trial_end!).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</span>
              </p>
            </div>
          </div>
          <Link
            href="/dashboard/subscription"
            className="px-5 py-2.5 bg-gradient-to-r from-amber-500 to-amber-600 text-slate-900 rounded-lg font-semibold hover:from-amber-400 hover:to-amber-500 transition shadow-lg shadow-amber-500/20"
          >
            View Plans
          </Link>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        {/* Contracts Analyzed */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-slate-500 font-medium text-sm uppercase tracking-wide">Contracts Analyzed</h3>
            <div className="w-10 h-10 bg-slate-100 rounded-lg flex items-center justify-center">
              <FileText className="w-5 h-5 text-slate-600" />
            </div>
          </div>
          <p className="text-4xl font-serif font-bold text-slate-900">
            {usage?.contracts_analyzed || 0}
          </p>
          <p className="text-sm text-slate-500 mt-2">
            of {usage?.contracts_limit === -1 ? 'unlimited' : usage?.contracts_limit} this month
          </p>
        </div>

        {/* Usage Percentage */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-slate-500 font-medium text-sm uppercase tracking-wide">Monthly Usage</h3>
            <div className="w-10 h-10 bg-emerald-50 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-emerald-600" />
            </div>
          </div>
          <p className="text-4xl font-serif font-bold text-slate-900">
            {usagePercentage.toFixed(0)}%
          </p>
          <div className="mt-3 w-full bg-slate-100 rounded-full h-2.5">
            <div
              className={`h-2.5 rounded-full transition-all ${
                isNearLimit ? 'bg-gradient-to-r from-red-500 to-red-600' : 'bg-gradient-to-r from-emerald-500 to-emerald-600'
              }`}
              style={{ width: `${Math.min(usagePercentage, 100)}%` }}
            />
          </div>
        </div>

        {/* Current Plan */}
        <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 hover:shadow-md transition-shadow">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-slate-500 font-medium text-sm uppercase tracking-wide">Current Plan</h3>
            <div className="w-10 h-10 bg-amber-50 rounded-lg flex items-center justify-center">
              <Scale className="w-5 h-5 text-amber-600" />
            </div>
          </div>
          <p className="text-3xl font-serif font-bold text-slate-900 capitalize">
            {subscription?.plan.display_name || 'No Plan'}
          </p>
          <Link
            href="/dashboard/subscription"
            className="text-sm text-amber-600 hover:text-amber-700 mt-2 inline-flex items-center font-medium"
          >
            Manage subscription <ArrowRight className="w-4 h-4 ml-1" />
          </Link>
        </div>
      </div>

      {/* Usage Warning */}
      {isNearLimit && (
        <div className="mb-6 p-5 bg-red-50 border border-red-200 rounded-xl flex items-center shadow-sm">
          <div className="w-12 h-12 bg-red-100 rounded-xl flex items-center justify-center mr-4">
            <AlertCircle className="w-6 h-6 text-red-600" />
          </div>
          <div className="flex-1">
            <p className="text-red-900 font-semibold">Approaching Usage Limit</p>
            <p className="text-sm text-red-700">
              You've used {usagePercentage.toFixed(0)}% of your monthly contract limit. Upgrade your plan to continue uninterrupted service.
            </p>
          </div>
          <Link
            href="/dashboard/subscription"
            className="px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition ml-4"
          >
            Upgrade Now
          </Link>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <h2 className="text-xl font-serif font-bold text-slate-900 mb-6">Quick Actions</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <Link
            href="/dashboard/analyze"
            className="p-6 border-2 border-slate-200 rounded-xl hover:border-amber-400 hover:bg-amber-50/50 transition-all group"
          >
            <div className="w-14 h-14 bg-gradient-to-br from-amber-500 to-amber-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-105 transition-transform shadow-lg shadow-amber-500/20">
              <Gavel className="w-7 h-7 text-slate-900" />
            </div>
            <h3 className="text-lg font-serif font-semibold text-slate-900 mb-2">
              Analyze New Contract
            </h3>
            <p className="text-slate-600 text-sm">
              Upload and analyze a contract document with our AI-powered legal intelligence
            </p>
          </Link>

          <Link
            href="/dashboard/subscription"
            className="p-6 border-2 border-slate-200 rounded-xl hover:border-emerald-400 hover:bg-emerald-50/50 transition-all group"
          >
            <div className="w-14 h-14 bg-gradient-to-br from-emerald-500 to-emerald-600 rounded-xl flex items-center justify-center mb-4 group-hover:scale-105 transition-transform shadow-lg shadow-emerald-500/20">
              <TrendingUp className="w-7 h-7 text-white" />
            </div>
            <h3 className="text-lg font-serif font-semibold text-slate-900 mb-2">
              Upgrade Your Plan
            </h3>
            <p className="text-slate-600 text-sm">
              Unlock more contracts and advanced features for your legal practice
            </p>
          </Link>
        </div>
      </div>

      {/* Recent Activity Placeholder */}
      <div className="mt-6 bg-white rounded-xl shadow-sm border border-slate-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-serif font-bold text-slate-900">Recent Activity</h2>
          <BookOpen className="w-5 h-5 text-slate-400" />
        </div>
        <div className="text-center py-8">
          <div className="w-16 h-16 bg-slate-100 rounded-xl flex items-center justify-center mx-auto mb-4">
            <FileText className="w-8 h-8 text-slate-400" />
          </div>
          <p className="text-slate-500">No contracts analyzed yet</p>
          <p className="text-sm text-slate-400 mt-1">Upload your first contract to get started</p>
          <Link
            href="/dashboard/analyze"
            className="inline-flex items-center mt-4 text-amber-600 hover:text-amber-700 font-medium text-sm"
          >
            Analyze a contract <ArrowRight className="w-4 h-4 ml-1" />
          </Link>
        </div>
      </div>
    </div>
  );
}

