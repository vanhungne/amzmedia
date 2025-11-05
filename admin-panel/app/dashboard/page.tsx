'use client';

import Layout from '@/components/Layout';
import { getProjects, getUsers } from '@/lib/api';
import { useEffect, useState } from 'react';
import { FolderOpen, Users, Activity } from 'lucide-react';

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
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

        {stats.loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Projects</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.projects}</p>
                </div>
                <FolderOpen className="w-12 h-12 text-primary-600" />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Users</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">{stats.users}</p>
                </div>
                <Users className="w-12 h-12 text-primary-600" />
              </div>
            </div>

            <div className="card">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">System Status</p>
                  <p className="text-3xl font-bold text-green-600 mt-2">Online</p>
                </div>
                <Activity className="w-12 h-12 text-green-600" />
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}






