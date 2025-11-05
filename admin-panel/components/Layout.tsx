'use client';

import { useState, useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { logout, getCurrentUser } from '@/lib/api';
import { User, Settings, Users, FolderOpen, LogOut, Key, Network, ChevronRight, Activity, Image as ImageIcon } from 'lucide-react';
import SpaceBackground from './SpaceBackground';

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
    return null; // No loading screen, load silently
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
    <div className="min-h-screen relative">
      {/* Space Background with Stars */}
      <SpaceBackground />
      
      {/* Modern Header with Space Gradient */}
      <header className="relative z-10 shadow-elevated border-b border-white/20" style={{
        background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.95) 0%, rgba(118, 75, 162, 0.95) 50%, rgba(240, 147, 251, 0.95) 100%)',
        backdropFilter: 'blur(20px)',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2), 0 0 80px rgba(102, 126, 234, 0.3)'
      }}>
        <div className="max-w-7xl mx-auto px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            {/* Logo & Brand */}
            <div className="flex items-center space-x-4">
              <div className="relative w-12 h-12 bg-white rounded-xl p-1 animate-pulse" style={{
                boxShadow: '0 0 30px rgba(255, 255, 255, 0.5), 0 0 60px rgba(147, 197, 253, 0.3)'
              }}>
                <Image 
                  src="/logo.jpg" 
                  alt="Logo" 
                  width={48} 
                  height={48}
                  className="rounded-lg object-contain"
                />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-white tracking-tight" style={{
                  textShadow: '0 0 20px rgba(255, 255, 255, 0.5), 0 0 40px rgba(147, 197, 253, 0.3)'
                }}>
                  WorkFlow Admin
                </h1>
                <p className="text-white/90 text-xs font-medium flex items-center gap-2">
                  <span className="inline-block w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                  Management System
                </p>
              </div>
            </div>
            
            {/* User Info & Logout */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-3 px-4 py-2 rounded-xl border border-white/30 transition-all duration-300 hover:border-white/50" style={{
                background: 'rgba(255, 255, 255, 0.15)',
                backdropFilter: 'blur(10px)',
                boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)'
              }}>
                <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center animate-pulse" style={{
                  boxShadow: '0 0 20px rgba(255, 255, 255, 0.4)'
                }}>
                  <User className="w-4 h-4 text-purple-600" />
                </div>
                <div className="text-left">
                  <p className="text-sm font-semibold text-white">{user?.username}</p>
                  <span className="text-xs px-2 py-0.5 rounded-full uppercase tracking-wider font-bold" style={{
                    background: 'linear-gradient(135deg, rgba(255, 255, 255, 0.3), rgba(255, 255, 255, 0.1))',
                    color: 'white',
                    boxShadow: '0 0 10px rgba(255, 255, 255, 0.2)'
                  }}>
                    {user?.role}
                  </span>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 text-white px-4 py-2 rounded-xl transition-all duration-300 border border-white/30 hover:border-white/50 hover:scale-105"
                style={{
                  background: 'rgba(255, 255, 255, 0.15)',
                  backdropFilter: 'blur(10px)',
                  boxShadow: '0 4px 16px rgba(0, 0, 0, 0.1)'
                }}
              >
                <LogOut className="w-4 h-4" />
                <span className="font-medium">Đăng xuất</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="flex max-w-7xl mx-auto relative z-10">
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
                    isActive ? 'text-white shadow-lg scale-[1.02]' : 'text-gray-700 shadow-sm hover:shadow-md'
                  }`}
                  style={isActive ? {
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    boxShadow: '0 8px 32px rgba(102, 126, 234, 0.4), 0 0 40px rgba(118, 75, 162, 0.3)'
                  } : {
                    background: 'rgba(255, 255, 255, 0.9)',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(255, 255, 255, 0.5)'
                  }}
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






