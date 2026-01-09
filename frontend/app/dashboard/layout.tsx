'use client';

import { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import { useAuthStore, useUIStore } from '@/lib/store';
import {
  LayoutDashboard,
  FileText,
  CreditCard,
  Settings,
  LogOut,
  Menu,
  X,
  Key,
  Scale,
  Gavel,
} from 'lucide-react';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const pathname = usePathname();
  const { isAuthenticated, user, logout } = useAuthStore();
  const { sidebarOpen, toggleSidebar } = useUIStore();

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  const handleLogout = () => {
    logout();
    router.push('/login');
  };

  if (!isAuthenticated) {
    return null;
  }

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
    { name: 'Analyze Contract', href: '/dashboard/analyze', icon: FileText },
    { name: 'Subscription', href: '/dashboard/subscription', icon: CreditCard },
    { name: 'API Keys', href: '/dashboard/api-keys', icon: Key },
    { name: 'Settings', href: '/dashboard/settings', icon: Settings },
  ];

  return (
    <div className="min-h-screen bg-slate-100">
      {/* Mobile sidebar backdrop */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-slate-900/75 backdrop-blur-sm z-20 lg:hidden"
          onClick={toggleSidebar}
        />
      )}

      {/* Sidebar */}
      <div
        className={`fixed inset-y-0 left-0 z-30 w-72 bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 shadow-2xl transform transition-transform duration-300 ease-in-out ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } lg:translate-x-0`}
      >
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center justify-between h-20 px-6 border-b border-slate-700/50">
            <Link href="/" className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-br from-amber-500 to-amber-600 rounded-lg flex items-center justify-center mr-3 shadow-lg shadow-amber-500/20">
                <Scale className="w-5 h-5 text-slate-900" />
              </div>
              <div>
                <span className="text-lg font-serif font-bold text-white">LegalMind</span>
                <span className="block text-[9px] text-amber-500 uppercase tracking-[0.15em]">Dashboard</span>
              </div>
            </Link>
            <button onClick={toggleSidebar} className="lg:hidden text-slate-400 hover:text-white">
              <X className="w-6 h-6" />
            </button>
          </div>

          {/* User Info */}
          <div className="px-6 py-5 border-b border-slate-700/50">
            <div className="flex items-center">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-amber-500/20 to-amber-600/20 border border-amber-500/30 flex items-center justify-center">
                <span className="text-amber-400 font-serif font-bold">
                  {user?.full_name?.charAt(0) || 'U'}
                </span>
              </div>
              <div className="ml-3">
                <p className="text-sm font-medium text-white">{user?.full_name}</p>
                <p className="text-xs text-slate-500">{user?.email}</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-1 overflow-y-auto">
            <p className="px-4 text-xs font-semibold text-slate-500 uppercase tracking-wider mb-4">
              Main Menu
            </p>
            {navigation.map((item) => {
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.name}
                  href={item.href}
                  className={`flex items-center px-4 py-3 rounded-lg transition-all group ${
                    isActive
                      ? 'bg-gradient-to-r from-amber-500/10 to-transparent text-amber-400 border-l-2 border-amber-500'
                      : 'text-slate-400 hover:text-white hover:bg-slate-800/50'
                  }`}
                >
                  <item.icon className={`w-5 h-5 mr-3 ${isActive ? 'text-amber-400' : 'text-slate-500 group-hover:text-amber-400'}`} />
                  <span className="font-medium">{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* Pro tip */}
          <div className="mx-4 mb-4 p-4 rounded-xl bg-slate-800/50 border border-slate-700/50">
            <div className="flex items-center mb-2">
              <Gavel className="w-4 h-4 text-amber-400 mr-2" />
              <span className="text-xs font-semibold text-amber-400">Pro Tip</span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Upload contracts in PDF format for the most accurate analysis results.
            </p>
          </div>

          {/* Logout */}
          <div className="p-4 border-t border-slate-700/50">
            <button
              onClick={handleLogout}
              className="flex items-center w-full px-4 py-3 text-slate-400 rounded-lg hover:bg-red-500/10 hover:text-red-400 transition-all"
            >
              <LogOut className="w-5 h-5 mr-3" />
              Sign Out
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="lg:pl-72">
        {/* Top Bar */}
        <div className="sticky top-0 z-10 flex items-center justify-between h-16 px-6 bg-white/80 backdrop-blur-lg border-b border-slate-200">
          <div className="flex items-center">
            <button
              onClick={toggleSidebar}
              className="mr-4 text-slate-600 hover:text-slate-900 lg:hidden"
            >
              <Menu className="w-6 h-6" />
            </button>
            <div>
              <h2 className="text-lg font-serif font-semibold text-slate-900">
                Welcome back, {user?.full_name?.split(' ')[0]}
              </h2>
              <p className="text-xs text-slate-500">Ready to review contracts</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden sm:flex items-center text-xs text-slate-500 bg-slate-100 px-3 py-1.5 rounded-full">
              <div className="w-2 h-2 bg-emerald-500 rounded-full mr-2 animate-pulse"></div>
              System Online
            </div>
          </div>
        </div>

        {/* Page Content */}
        <main className="p-6 bg-slate-100 min-h-[calc(100vh-4rem)]">{children}</main>
      </div>
    </div>
  );
}

