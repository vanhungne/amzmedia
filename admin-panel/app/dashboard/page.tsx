'use client';

import Layout from '@/components/Layout';
import SpaceLoader from '@/components/SpaceLoader';
import { getProjects, getUsers } from '@/lib/api';
import { useEffect, useState } from 'react';
import { FolderOpen, Users, Activity, Sparkles, TrendingUp } from 'lucide-react';

export default function DashboardPage() {
  const [stats, setStats] = useState({
    projects: 0,
    users: 0,
    loading: true,
  });

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const [projectsRes, usersRes] = await Promise.all([
        getProjects(),
        getUsers(),
      ]);
      setStats({
        projects: projectsRes.projects.length,
        users: usersRes.users.length,
        loading: false,
      });
    } catch (err) {
      console.error('Failed to load stats:', err);
      setStats((s) => ({ ...s, loading: false }));
    }
  };

  return (
    <Layout>
      <div>
        {/* Header with Space Theme */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 via-blue-600 to-pink-600 bg-clip-text text-transparent mb-2 flex items-center gap-3" style={{
            filter: 'drop-shadow(0 0 20px rgba(147, 51, 234, 0.3))'
          }}>
            <Sparkles className="w-10 h-10 text-purple-500 animate-pulse" />
            Dashboard Overview
          </h1>
          <p className="text-gray-700 font-medium">Tổng quan hệ thống và thống kê</p>
        </div>

        {stats.loading ? (
          <SpaceLoader message="Đang tải thống kê..." />
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Projects Card */}
            <div className="card-hover relative overflow-hidden group">
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <div className="absolute top-0 right-0 w-32 h-32 bg-purple-400 rounded-full blur-3xl"></div>
              </div>
              <div className="flex items-center justify-between relative z-10">
                <div>
                  <p className="text-sm font-bold text-gray-600 uppercase tracking-wide mb-2">Total Projects</p>
                  <p className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                    {stats.projects}
                  </p>
                  <div className="flex items-center gap-1 mt-2">
                    <TrendingUp className="w-4 h-4 text-green-500" />
                    <span className="text-xs text-green-600 font-semibold">Active</span>
                  </div>
                </div>
                <div className="p-4 rounded-2xl" style={{
                  background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%)',
                  boxShadow: '0 0 30px rgba(102, 126, 234, 0.3)'
                }}>
                  <FolderOpen className="w-12 h-12 text-purple-600" />
                </div>
              </div>
            </div>

            {/* Users Card */}
            <div className="card-hover relative overflow-hidden group">
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <div className="absolute top-0 right-0 w-32 h-32 bg-blue-400 rounded-full blur-3xl"></div>
              </div>
              <div className="flex items-center justify-between relative z-10">
                <div>
                  <p className="text-sm font-bold text-gray-600 uppercase tracking-wide mb-2">Total Users</p>
                  <p className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">
                    {stats.users}
                  </p>
                  <div className="flex items-center gap-1 mt-2">
                    <TrendingUp className="w-4 h-4 text-green-500" />
                    <span className="text-xs text-green-600 font-semibold">Growing</span>
                  </div>
                </div>
                <div className="p-4 rounded-2xl" style={{
                  background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.2) 0%, rgba(6, 182, 212, 0.2) 100%)',
                  boxShadow: '0 0 30px rgba(59, 130, 246, 0.3)'
                }}>
                  <Users className="w-12 h-12 text-blue-600" />
                </div>
              </div>
            </div>

            {/* System Status Card */}
            <div className="card-hover relative overflow-hidden group">
              <div className="absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                <div className="absolute top-0 right-0 w-32 h-32 bg-green-400 rounded-full blur-3xl"></div>
              </div>
              <div className="flex items-center justify-between relative z-10">
                <div>
                  <p className="text-sm font-bold text-gray-600 uppercase tracking-wide mb-2">System Status</p>
                  <p className="text-4xl font-bold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent flex items-center gap-2">
                    Online
                    <span className="inline-block w-3 h-3 bg-green-500 rounded-full animate-pulse"></span>
                  </p>
                  <div className="flex items-center gap-1 mt-2">
                    <span className="text-xs text-green-600 font-semibold">100% Uptime</span>
                  </div>
                </div>
                <div className="p-4 rounded-2xl" style={{
                  background: 'linear-gradient(135deg, rgba(34, 197, 94, 0.2) 0%, rgba(16, 185, 129, 0.2) 100%)',
                  boxShadow: '0 0 30px rgba(34, 197, 94, 0.3)'
                }}>
                  <Activity className="w-12 h-12 text-green-600" />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Welcome Message */}
        <div className="card mt-8 relative overflow-hidden">
          <div className="absolute inset-0 opacity-10">
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-gradient-to-r from-purple-400 to-pink-400 rounded-full blur-3xl animate-pulse"></div>
          </div>
          <div className="relative z-10 text-center py-8">
            <h2 className="text-2xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-3">
              Welcome to WorkFlow Admin Dashboard! 🚀
            </h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Quản lý toàn bộ hệ thống của bạn với giao diện hiện đại và tính năng mạnh mẽ. 
              Khám phá các công cụ quản lý Projects, Users, API Keys và nhiều hơn nữa.
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
}






