'use client';

import Layout from '@/components/Layout';
import SpaceLoader from '@/components/SpaceLoader';
import { useState, useEffect } from 'react';
import { getUsers, createUser, updateUser, deleteUser, type User } from '@/lib/api';
import { Plus, Edit, Trash2, X, CheckCircle, XCircle, Smartphone, RefreshCw, Users, Sparkles } from 'lucide-react';

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    role: 'user' as 'admin' | 'user',
    is_active: true,
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const res = await getUsers();
      setUsers(res.users);
    } catch (err) {
      console.error('Failed to load users:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingUser(null);
    setFormData({
      username: '',
      email: '',
      password: '',
      role: 'user',
      is_active: true,
    });
    setShowModal(true);
  };

  const handleEdit = (user: User) => {
    setEditingUser(user);
    setFormData({
      username: user.username,
      email: user.email || '',
      password: '',
      role: user.role,
      is_active: user.is_active,
    });
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingUser) {
        // Update - only send password if it's changed
        const updateData: any = {
          username: formData.username,
          email: formData.email || null,
          role: formData.role,
          is_active: formData.is_active,
        };
        if (formData.password) {
          updateData.password = formData.password;
        }
        await updateUser(editingUser.id, updateData);
      } else {
        // Create
        await createUser({
          username: formData.username,
          password: formData.password,
          email: formData.email || undefined,
          role: formData.role,
        });
      }
      setShowModal(false);
      loadUsers();
    } catch (err: any) {
      alert(err.message || 'Failed to save user');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Bạn có chắc muốn xóa user này?')) return;
    try {
      await deleteUser(id);
      loadUsers();
    } catch (err: any) {
      alert(err.message || 'Failed to delete user');
    }
  };

  const handleResetDevice = async (userId: number, username: string) => {
    if (!confirm(`Reset device lock cho user "${username}"?\n\nUser sẽ có thể đăng nhập từ máy mới.`)) return;
    try {
      const res = await fetch(`/api/users/${userId}/reset-device`, {
        method: 'POST',
        credentials: 'include',
      });
      
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Failed to reset device');
      }
      
      alert('✅ Device lock đã được reset thành công');
      loadUsers();
    } catch (err: any) {
      alert(err.message || 'Failed to reset device');
    }
  };

  return (
    <Layout>
      <div>
        {/* Header with Space Gradient */}
        <div className="flex justify-between items-center mb-8">
          <div className="relative">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 via-blue-600 to-pink-600 bg-clip-text text-transparent mb-2 flex items-center gap-3" style={{
              filter: 'drop-shadow(0 0 20px rgba(147, 51, 234, 0.3))'
            }}>
              <Sparkles className="w-10 h-10 text-purple-500 animate-pulse" />
              Users Management
            </h1>
            <p className="text-gray-700 font-medium">Quản lý người dùng và phân quyền</p>
          </div>
          <button onClick={handleCreate} className="btn btn-primary relative z-10">
            <Plus className="w-5 h-5 relative z-10" />
            <span className="relative z-10">Tạo User Mới</span>
          </button>
        </div>

        {loading ? (
          <SpaceLoader message="Đang tải danh sách users..." />
        ) : users.length === 0 ? (
          <div className="card text-center py-16 relative overflow-hidden">
            <div className="absolute inset-0 opacity-20">
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-purple-400 rounded-full blur-3xl animate-pulse"></div>
            </div>
            <Users className="w-16 h-16 mx-auto mb-4 relative z-10" style={{
              color: '#667eea',
              filter: 'drop-shadow(0 0 20px rgba(102, 126, 234, 0.5))'
            }} />
            <p className="text-gray-700 font-bold text-lg relative z-10">Chưa có user nào</p>
            <p className="text-gray-600 text-sm mt-2 relative z-10">Hãy tạo user đầu tiên</p>
          </div>
        ) : (
          <div className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="table-modern">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Username
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Email
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Role
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Device
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Assigned
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Active
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">                                     
                      Ready (&gt;800)
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ever Received
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Ever Used
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider sticky right-0 bg-gray-50 shadow-[-2px_0_4px_rgba(0,0,0,0.05)]">
                      Actions
                    </th>
                  </tr>
                </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {users.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50 group">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{user.username}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">{user.email || '-'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs font-medium rounded ${
                        user.role === 'admin' 
                          ? 'bg-purple-100 text-purple-800' 
                          : 'bg-blue-100 text-blue-800'
                      }`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {(user as any).device_name ? (
                        <div className="flex items-start space-x-2">
                          <Smartphone className="w-4 h-4 mt-0.5 text-green-600 flex-shrink-0" />
                          <div className="text-xs">
                            <div className="font-medium text-gray-900">{(user as any).device_name}</div>
                            <div className="text-gray-500 truncate max-w-[120px]" title={(user as any).device_id}>
                              {(user as any).device_id?.slice(0, 16)}...
                            </div>
                          </div>
                        </div>
                      ) : (
                        <span className="text-xs text-gray-400">Not set</span>
                      )}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-center">
                      <div className="text-sm font-semibold text-gray-900">
                        {user.current_assigned_keys || 0}
                      </div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-center">
                      <div className="text-sm font-semibold text-green-600">
                        {user.active_keys_count || 0}
                      </div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-center">
                      <div className="text-sm font-semibold text-blue-600">
                        {user.ready_keys_count || 0}
                      </div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-center">
                      <div className="text-sm text-gray-600">
                        {user.total_keys_received || 0}
                      </div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-center">
                      <div className="text-sm text-gray-600">
                        {user.total_keys_used || 0}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {user.is_active ? (
                        <span className="flex items-center text-green-600 text-sm">
                          <CheckCircle className="w-4 h-4 mr-1" />
                          Active
                        </span>
                      ) : (
                        <span className="flex items-center text-red-600 text-sm">
                          <XCircle className="w-4 h-4 mr-1" />
                          Inactive
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium sticky right-0 bg-white group-hover:bg-gray-50 shadow-[-2px_0_4px_rgba(0,0,0,0.05)]">
                      <button
                        onClick={() => handleEdit(user)}
                        className="text-primary-600 hover:text-primary-900 mr-4"
                        title="Edit User"
                      >
                        <Edit className="w-4 h-4 inline" />
                      </button>
                      {(user as any).device_name && (
                        <button
                          onClick={() => handleResetDevice(user.id, user.username)}
                          className="text-orange-600 hover:text-orange-900 mr-4"
                          title="Reset Device Lock"
                        >
                          <RefreshCw className="w-4 h-4 inline" />
                        </button>
                      )}
                      <button
                        onClick={() => handleDelete(user.id)}
                        className="text-red-600 hover:text-red-900"
                        title="Delete User"
                      >
                        <Trash2 className="w-4 h-4 inline" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Modal with Space Theme */}
        {showModal && (
          <div className="fixed inset-0 flex items-center justify-center z-50" style={{
            background: 'rgba(0, 0, 0, 0.7)',
            backdropFilter: 'blur(8px)'
          }}>
            <div className="rounded-2xl shadow-2xl max-w-lg w-full mx-4 border border-white/30" style={{
              background: 'rgba(255, 255, 255, 0.98)',
              backdropFilter: 'blur(20px)',
              boxShadow: '0 0 80px rgba(102, 126, 234, 0.5), 0 0 120px rgba(118, 75, 162, 0.3)'
            }}>
              <div className="flex justify-between items-center p-6 border-b border-purple-100" style={{
                background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)'
              }}>
                <h2 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  {editingUser ? 'Chỉnh Sửa User' : 'Tạo User Mới'}
                </h2>
                <button 
                  onClick={() => setShowModal(false)} 
                  className="text-gray-400 hover:text-purple-600 transition-all duration-300 hover:rotate-90 hover:scale-110"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Username *
                  </label>
                  <input
                    type="text"
                    className="input"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    className="input"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Password {editingUser ? '(để trống nếu không đổi)' : '*'}
                  </label>
                  <input
                    type="password"
                    className="input"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    required={!editingUser}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Role
                  </label>
                  <select
                    className="input"
                    value={formData.role}
                    onChange={(e) => setFormData({ ...formData, role: e.target.value as 'admin' | 'user' })}
                  >
                    <option value="user">User</option>
                    <option value="admin">Admin</option>
                  </select>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
                    Active (có thể đăng nhập)
                  </label>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary relative z-10">
                    <span className="relative z-10">Hủy</span>
                  </button>
                  <button type="submit" className="btn btn-primary relative">
                    <span className="relative z-10">{editingUser ? 'Cập Nhật' : 'Tạo User'}</span>
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
}






