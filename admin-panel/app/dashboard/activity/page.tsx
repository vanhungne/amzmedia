'use client';

import Layout from '@/components/Layout';
import { useState, useEffect } from 'react';
import { getUsers } from '@/lib/api';
import { Activity, Clock, User as UserIcon, Filter, RefreshCw, Eye } from 'lucide-react';

interface ActivityLog {
  id: number;
  user_id: number;
  username: string;
  action: string;
  category: string;
  details: string | null;
  status: string;
  ip_address: string;
  device_name: string;
  created_at: string;
}

interface User {
  id: number;
  username: string;
}

export default function ActivityPage() {
  const [logs, setLogs] = useState<ActivityLog[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedUser, setSelectedUser] = useState<string>('');
  const [selectedCategory, setSelectedCategory] = useState<string>('');
  const [selectedLog, setSelectedLog] = useState<ActivityLog | null>(null);
  const [total, setTotal] = useState(0);
  const [limit] = useState(50);
  const [offset, setOffset] = useState(0);

  useEffect(() => {
    loadUsers();
    loadLogs();
  }, [selectedUser, selectedCategory, offset]);

  const loadUsers = async () => {
    try {
      const res = await getUsers();
      setUsers(res.users);
    } catch (err) {
      console.error('Failed to load users:', err);
    }
  };

  const loadLogs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedUser) params.set('user_id', selectedUser);
      if (selectedCategory) params.set('category', selectedCategory);
      params.set('limit', limit.toString());
      params.set('offset', offset.toString());

      const res = await fetch(`/api/activity?${params.toString()}`, {
        credentials: 'include',
      });
      
      if (!res.ok) throw new Error('Failed to fetch logs');
      
      const data = await res.json();
      setLogs(data.logs);
      setTotal(data.pagination.total);
    } catch (err) {
      console.error('Failed to load activity logs:', err);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'auth': return 'bg-blue-100 text-blue-700';
      case 'project': return 'bg-purple-100 text-purple-700';
      case 'generation': return 'bg-green-100 text-green-700';
      case 'api': return 'bg-orange-100 text-orange-700';
      case 'system': return 'bg-gray-100 text-gray-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success': return 'bg-green-100 text-green-700';
      case 'failed': return 'bg-red-100 text-red-700';
      case 'error': return 'bg-red-100 text-red-700';
      default: return 'bg-gray-100 text-gray-700';
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString('vi-VN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <Layout>
      <div>
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-primary-600 to-red-600 bg-clip-text text-transparent mb-2">
              Activity History
            </h1>
            <p className="text-gray-600">Theo dõi hoạt động của người dùng</p>
          </div>
          <button onClick={loadLogs} className="btn btn-secondary">
            <RefreshCw className="w-5 h-5" />
            <span>Làm mới</span>
          </button>
        </div>

        {/* Filters */}
        <div className="card mb-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">
                <UserIcon className="w-4 h-4 inline mr-2" />
                Người dùng
              </label>
              <select
                className="input"
                value={selectedUser}
                onChange={(e) => {
                  setSelectedUser(e.target.value);
                  setOffset(0);
                }}
              >
                <option value="">Tất cả</option>
                {users.map((user) => (
                  <option key={user.id} value={user.id}>
                    {user.username}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">
                <Filter className="w-4 h-4 inline mr-2" />
                Danh mục
              </label>
              <select
                className="input"
                value={selectedCategory}
                onChange={(e) => {
                  setSelectedCategory(e.target.value);
                  setOffset(0);
                }}
              >
                <option value="">Tất cả</option>
                <option value="auth">Authentication</option>
                <option value="project">Project</option>
                <option value="generation">Generation</option>
                <option value="api">API</option>
                <option value="system">System</option>
              </select>
            </div>

            <div className="flex items-end">
              <div className="bg-gradient-to-r from-primary-50 to-red-50 p-4 rounded-xl border-2 border-primary-200 w-full">
                <p className="text-sm text-gray-600 mb-1">Tổng số logs</p>
                <p className="text-3xl font-bold text-primary-600">{total}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Activity Logs */}
        {loading ? (
          <div className="card text-center py-16">
            <div className="relative w-16 h-16 mx-auto mb-4">
              <div className="absolute inset-0 border-4 border-red-200 rounded-full"></div>
              <div className="absolute inset-0 border-4 border-primary-600 rounded-full border-t-transparent animate-spin"></div>
            </div>
            <p className="text-gray-600 font-medium">Đang tải...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="card text-center py-16">
            <Activity className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-600 font-medium text-lg">Chưa có hoạt động nào</p>
            <p className="text-gray-500 text-sm mt-2">Hoạt động sẽ hiển thị khi user sử dụng tool</p>
          </div>
        ) : (
          <>
            <div className="card overflow-hidden">
              <table className="table-modern">
                <thead>
                  <tr>
                    <th>Thời gian</th>
                    <th>User</th>
                    <th>Action</th>
                    <th>Category</th>
                    <th>Status</th>
                    <th>Device</th>
                    <th>IP</th>
                    <th>Chi tiết</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <tr key={log.id}>
                      <td>
                        <div className="flex items-center gap-2 text-xs">
                          <Clock className="w-4 h-4 text-gray-400" />
                          {formatDate(log.created_at)}
                        </div>
                      </td>
                      <td>
                        <span className="font-semibold text-gray-900">{log.username}</span>
                      </td>
                      <td>
                        <code className="text-xs bg-gray-100 px-2 py-1 rounded">{log.action}</code>
                      </td>
                      <td>
                        <span className={`badge ${getCategoryColor(log.category)}`}>
                          {log.category}
                        </span>
                      </td>
                      <td>
                        <span className={`badge ${getStatusColor(log.status)}`}>
                          {log.status}
                        </span>
                      </td>
                      <td className="text-xs text-gray-600">
                        {log.device_name || '-'}
                      </td>
                      <td className="text-xs text-gray-600">
                        {log.ip_address || '-'}
                      </td>
                      <td>
                        {log.details && (
                          <button
                            onClick={() => setSelectedLog(log)}
                            className="text-primary-600 hover:text-primary-700"
                            title="View Details"
                          >
                            <Eye className="w-4 h-4" />
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            <div className="flex justify-between items-center mt-6">
              <p className="text-sm text-gray-600">
                Hiển thị {offset + 1} - {Math.min(offset + limit, total)} của {total} logs
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => setOffset(Math.max(0, offset - limit))}
                  disabled={offset === 0}
                  className="btn btn-secondary"
                >
                  Trang trước
                </button>
                <button
                  onClick={() => setOffset(offset + limit)}
                  disabled={offset + limit >= total}
                  className="btn btn-secondary"
                >
                  Trang sau
                </button>
              </div>
            </div>
          </>
        )}

        {/* Details Modal */}
        {selectedLog && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[80vh] overflow-auto">
              <div className="sticky top-0 bg-gradient-to-r from-primary-600 to-red-600 p-6 text-white rounded-t-2xl">
                <div className="flex justify-between items-center">
                  <h2 className="text-2xl font-bold">Activity Details</h2>
                  <button 
                    onClick={() => setSelectedLog(null)}
                    className="text-white hover:bg-white/20 rounded-lg p-2 transition-colors"
                  >
                    ✕
                  </button>
                </div>
              </div>

              <div className="p-6 space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-sm text-gray-600 mb-1">User</p>
                    <p className="font-bold text-gray-900">{selectedLog.username}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Action</p>
                    <code className="text-sm bg-gray-100 px-3 py-1 rounded">{selectedLog.action}</code>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Category</p>
                    <span className={`badge ${getCategoryColor(selectedLog.category)}`}>
                      {selectedLog.category}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Status</p>
                    <span className={`badge ${getStatusColor(selectedLog.status)}`}>
                      {selectedLog.status}
                    </span>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">Device</p>
                    <p className="text-sm text-gray-900">{selectedLog.device_name || '-'}</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600 mb-1">IP Address</p>
                    <p className="text-sm text-gray-900">{selectedLog.ip_address || '-'}</p>
                  </div>
                  <div className="col-span-2">
                    <p className="text-sm text-gray-600 mb-1">Time</p>
                    <p className="text-sm text-gray-900">{formatDate(selectedLog.created_at)}</p>
                  </div>
                </div>

                {selectedLog.details && (
                  <div className="mt-6">
                    <p className="text-sm text-gray-600 mb-2 font-bold">Details (JSON):</p>
                    <pre className="bg-gray-100 p-4 rounded-xl text-xs overflow-auto max-h-96">
                      {JSON.stringify(JSON.parse(selectedLog.details), null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}



