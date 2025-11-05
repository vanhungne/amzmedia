'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { login } from '@/lib/api';
import { Lock, User, ArrowRight, AlertCircle, Sparkles } from 'lucide-react';
import SpaceBackground from '@/components/SpaceBackground';

export default function LoginPage() {
  const router = useRouter();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(username, password);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Invalid credentials');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Space Background */}
      <SpaceBackground />

      {/* Login Card */}
      <div className="relative z-10 w-full max-w-md mx-4">
        <div className="rounded-3xl shadow-2xl p-10 border border-white/30" style={{
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(20px)',
          boxShadow: '0 0 80px rgba(102, 126, 234, 0.5), 0 0 120px rgba(118, 75, 162, 0.3)'
        }}>
          {/* Logo & Brand */}
          <div className="text-center mb-8">
            <div className="flex justify-center mb-6 relative">
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-28 h-28 bg-gradient-to-br from-purple-400 to-pink-400 rounded-full blur-2xl opacity-60 animate-pulse"></div>
              </div>
              <div className="relative w-20 h-20 rounded-2xl shadow-xl p-2 animate-pulse" style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                boxShadow: '0 0 40px rgba(102, 126, 234, 0.6), 0 0 80px rgba(118, 75, 162, 0.4)'
              }}>
                <Image 
                  src="/logo.jpg" 
                  alt="Logo" 
                  width={80} 
                  height={80}
                  className="rounded-xl object-contain"
                />
              </div>
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 via-blue-600 to-pink-600 bg-clip-text text-transparent mb-2 flex items-center justify-center gap-2" style={{
              filter: 'drop-shadow(0 0 20px rgba(147, 51, 234, 0.3))'
            }}>
              <Sparkles className="w-8 h-8 text-purple-500 animate-pulse" />
              WorkFlow Admin
            </h1>
            <p className="text-gray-700 font-bold">Hệ thống quản lý tập trung</p>
          </div>

          {/* Login Form */}
          <form onSubmit={handleSubmit} className="space-y-6">
            {error && (
              <div className="px-4 py-3 rounded-xl flex items-start gap-3 border border-red-300" style={{
                background: 'linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.1) 100%)',
                backdropFilter: 'blur(10px)'
              }}>
                <AlertCircle className="w-5 h-5 mt-0.5 flex-shrink-0 text-red-600" />
                <span className="text-sm font-bold text-red-700">{error}</span>
              </div>
            )}

            <div>
              <label htmlFor="username" className="block text-sm font-bold text-gray-700 mb-2">
                Tên đăng nhập
              </label>
              <div className="relative">
                <div className="absolute left-4 top-1/2 transform -translate-y-1/2">
                  <User className="w-5 h-5 text-gray-400" />
                </div>
                <input
                  id="username"
                  type="text"
                  className="input pl-12"
                  placeholder="Nhập tên đăng nhập"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  required
                  autoFocus
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-bold text-gray-700 mb-2">
                Mật khẩu
              </label>
              <div className="relative">
                <div className="absolute left-4 top-1/2 transform -translate-y-1/2">
                  <Lock className="w-5 h-5 text-gray-400" />
                </div>
                <input
                  id="password"
                  type="password"
                  className="input pl-12"
                  placeholder="Nhập mật khẩu"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary w-full text-lg py-4 group relative"
            >
              {loading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin relative z-10"></div>
                  <span className="relative z-10">Đang đăng nhập...</span>
                </>
              ) : (
                <>
                  <span className="relative z-10">Đăng nhập</span>
                  <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform relative z-10" />
                </>
              )}
            </button>
          </form>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-purple-100 text-center">
            <p className="text-sm text-gray-600 font-medium">
              © 2025 WorkFlow Admin. All rights reserved.
            </p>
          </div>
        </div>

        {/* Security Badge */}
        <div className="mt-6 flex justify-center">
          <div className="px-6 py-3 rounded-full border border-white/30" style={{
            background: 'rgba(255, 255, 255, 0.2)',
            backdropFilter: 'blur(10px)',
            boxShadow: '0 4px 16px rgba(102, 126, 234, 0.2)'
          }}>
            <p className="text-white text-sm font-bold flex items-center gap-2" style={{
              textShadow: '0 0 10px rgba(0, 0, 0, 0.3)'
            }}>
              <Lock className="w-4 h-4" />
              Bảo mật với SSL/TLS Encryption
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}






