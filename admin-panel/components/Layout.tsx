'use client';

import { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { logout, getCurrentUser } from '@/lib/api';
import { User, Settings, Users, FolderOpen, LogOut, Key, Network, ChevronRight, Activity, Image as ImageIcon } from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  const router = useRouter();
  const pathname = usePathname();
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUser();
  }, []);

  const loadUser = async () => {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
    } catch {
      router.push('/login');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await logout();
      router.push('/login');
    } catch (err) {
      console.error('Logout error:', err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-red-50 via-white to-red-50">
        <div className="text-center">
          <div className="relative w-16 h-16 mx-auto mb-4">
            <div className="absolute inset-0 border-4 border-red-200 rounded-full"></div>
            <div className="absolute inset-0 border-4 border-primary-600 rounded-full border-t-transparent animate-spin"></div>
          </div>
          <p className="text-gray-600 font-medium">Đang tải...</p>
        </div>
      </div>
    );
  }

  const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: Settings, desc: 'Tổng quan' },
    { href: '/dashboard/projects', label: 'Projects', icon: FolderOpen, desc: 'Quản lý dự án' },
    { href: '/dashboard/users', label: 'Users', icon: Users, desc: 'Quản lý người dùng' },
    { href: '/dashboard/elevenlabs', label: 'ElevenLabs', icon: Key, desc: 'API Keys' },
    { href: '/dashboard/gemini', label: 'Gemini', icon: ImageIcon, desc: 'Gemini Keys' },
    { href: '/dashboard/proxy', label: 'Proxy', icon: Network, desc: 'Proxy Keys' },
    { href: '/dashboard/activity', label: 'Activity', icon: Activity, desc: 'Lịch sử hoạt động' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-red-50">
      {/* Modern Header with Red Gradient */}
      <header className="bg-gradient-to-r from-primary-600 via-primary-500 to-red-500 shadow-elevated border-b border-red-600">
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            {/* Logo & Brand */}
            <div className="flex items-center space-x-4">
              <div className="relative w-12 h-12 bg-white rounded-xl shadow-md p-1">
                <Image 
                  src="/logo.jpg" 
                  alt="Logo" 
                  width={48} 
                  height={48}
                  className="rounded-lg object-contain"
                />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white tracking-tight">WorkFlow Admin</h1>
                <p className="text-red-100 text-xs font-medium">Management System</p>
              </div>
            </div>
            
            {/* User Info & Logout */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3 bg-white/10 backdrop-blur-sm px-4 py-2 rounded-xl border border-white/20">
                <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
                  <User className="w-4 h-4 text-primary-600" />
                </div>
                <div className="text-left">
                  <p className="text-sm font-semibold text-white">{user?.username}</p>
                  <span className="text-xs bg-white/20 text-white px-2 py-0.5 rounded-full uppercase tracking-wider font-bold">
                    {user?.role}
                  </span>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 bg-white/10 hover:bg-white/20 backdrop-blur-sm text-white px-4 py-2 rounded-xl transition-all duration-300 border border-white/20"
              >
                <LogOut className="w-4 h-4" />
                <span className="font-medium">Đăng xuất</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex max-w-7xl mx-auto">
        {/* Modern Sidebar */}
        <aside className="w-72 min-h-[calc(100vh-5rem)] p-6">
          <nav className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`group flex items-center justify-between px-5 py-4 rounded-2xl transition-all duration-300 ${
                    isActive
                      ? 'bg-gradient-to-r from-primary-500 to-red-500 text-white shadow-lg scale-[1.02]'
                      : 'bg-white hover:bg-red-50 text-gray-700 hover:text-primary-600 shadow-sm hover:shadow-md border border-gray-100'
                  }`}
                >
                  <div className="flex items-center space-x-4">
                    <div className={`p-2 rounded-xl ${
                      isActive 
                        ? 'bg-white/20' 
                        : 'bg-gray-100 group-hover:bg-primary-100'
                    }`}>
                      <Icon className={`w-5 h-5 ${
                        isActive ? 'text-white' : 'text-gray-600 group-hover:text-primary-600'
                      }`} />
                    </div>
                    <div>
                      <p className={`font-bold text-sm ${isActive ? 'text-white' : 'text-gray-900'}`}>
                        {item.label}
                      </p>
                      <p className={`text-xs ${isActive ? 'text-white/80' : 'text-gray-500'}`}>
                        {item.desc}
                      </p>
                    </div>
                  </div>
                  <ChevronRight className={`w-4 h-4 ${
                    isActive ? 'text-white' : 'text-gray-400 group-hover:text-primary-600'
                  } transition-transform group-hover:translate-x-1`} />
                </Link>
              );
            })}
          </nav>
        </aside>

        {/* Main Content with Enhanced Styling */}
        <main className="flex-1 p-8">
          <div className="max-w-6xl">
            {children}
          </div>
        </main>
      </div>
    </div>
  );
}






