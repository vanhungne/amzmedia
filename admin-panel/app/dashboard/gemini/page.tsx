'use client';

import { useEffect, useState } from 'react';
import Layout from '@/components/Layout';
import { getGeminiKeys, createGeminiKey, updateGeminiKey, deleteGeminiKey, getUsers } from '@/lib/api';
import type { GeminiKey, User } from '@/lib/api';
import { Plus, Trash2, Edit2, RefreshCw, Key } from 'lucide-react';

export default function GeminiKeysPage() {
  const [keys, setKeys] = useState<GeminiKey[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showForm, setShowForm] = useState(false);
  const [editingKey, setEditingKey] = useState<GeminiKey | null>(null);
  const [formData, setFormData] = useState({
    api_key: '',
    name: '',
    assigned_user_id: 0,
    status: 'active' as 'active' | 'dead',
  });

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      setLoading(true);
      const [keysData, usersData] = await Promise.all([
        getGeminiKeys(),
        getUsers(),
      ]);
      setKeys(keysData.keys);
      setUsers(usersData.users);
      setError(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleAdd() {
    setEditingKey(null);
    setFormData({
      api_key: '',
      name: '',
      assigned_user_id: 0,
      status: 'active',
    });
    setShowForm(true);
  }

  function handleEdit(key: GeminiKey) {
    setEditingKey(key);
    setFormData({
      api_key: key.api_key,
      name: key.name || '',
      assigned_user_id: key.assigned_user_id || 0,
      status: key.status,
    });
    setShowForm(true);
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      if (editingKey) {
        await updateGeminiKey(editingKey.id, {
          name: formData.name || undefined,
          assigned_user_id: formData.assigned_user_id || undefined,
          status: formData.status,
        });
      } else {
        await createGeminiKey({
          api_key: formData.api_key,
          name: formData.name || undefined,
          assigned_user_id: formData.assigned_user_id || undefined,
        });
      }
      setShowForm(false);
      await loadData();
    } catch (err: any) {
      alert(err.message);
    }
  }

  async function handleDelete(id: number) {
    if (!confirm('Xóa Gemini API key này?')) return;
    try {
      await deleteGeminiKey(id);
      await loadData();
    } catch (err: any) {
      alert(err.message);
    }
  }

  const activeKeys = keys.filter(k => k.status === 'active').length;
  const deadKeys = keys.filter(k => k.status === 'dead').length;

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Gemini API Keys</h1>
          <p className="text-gray-600">Quản lý Gemini API keys cho việc tạo ảnh</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Tổng Keys</p>
                <p className="text-2xl font-bold text-gray-900">{keys.length}</p>
              </div>
              <Key className="w-10 h-10 text-blue-500 opacity-80" />
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Active</p>
                <p className="text-2xl font-bold text-green-600">{activeKeys}</p>
              </div>
              <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center">
                <span className="text-green-600 font-bold">✓</span>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">Dead</p>
                <p className="text-2xl font-bold text-red-600">{deadKeys}</p>
              </div>
              <div className="w-10 h-10 bg-red-100 rounded-full flex items-center justify-center">
                <span className="text-red-600 font-bold">✗</span>
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-between items-center mb-4">
          <button
            onClick={handleAdd}
            className="btn-primary flex items-center gap-2"
          >
            <Plus className="w-4 h-4" />
            Thêm Gemini Key
          </button>
          <button
            onClick={loadData}
            className="btn-secondary flex items-center gap-2"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {/* Form Modal */}
        {showForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h2 className="text-xl font-bold mb-4">
                {editingKey ? 'Chỉnh sửa Key' : 'Thêm Gemini Key mới'}
              </h2>
              <form onSubmit={handleSubmit}>
                {!editingKey && (
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      API Key *
                    </label>
                    <input
                      type="text"
                      value={formData.api_key}
                      onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                      className="input"
                      required
                      placeholder="AIzaSy..."
                    />
                  </div>
                )}
                
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Tên (optional)
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="input"
                    placeholder="VD: Gemini Key #1"
                  />
                </div>

                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Assign User
                  </label>
                  <select
                    value={formData.assigned_user_id}
                    onChange={(e) => setFormData({ ...formData, assigned_user_id: parseInt(e.target.value) })}
                    className="input"
                  >
                    <option value={0}>-- Không gán --</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.username}
                      </option>
                    ))}
                  </select>
                </div>

                {editingKey && (
                  <div className="mb-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Status
                    </label>
                    <select
                      value={formData.status}
                      onChange={(e) => setFormData({ ...formData, status: e.target.value as 'active' | 'dead' })}
                      className="input"
                    >
                      <option value="active">Active</option>
                      <option value="dead">Dead</option>
                    </select>
                  </div>
                )}

                <div className="flex gap-3">
                  <button type="submit" className="btn-primary flex-1">
                    {editingKey ? 'Cập nhật' : 'Tạo'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowForm(false)}
                    className="btn-secondary flex-1"
                  >
                    Hủy
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-4">
            {error}
          </div>
        )}

        {/* Keys Table */}
        {loading ? (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-sm overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    API Key
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Tên
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    User
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Used
                  </th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {keys.map((key) => (
                  <tr key={key.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                      {key.api_key.substring(0, 15)}...{key.api_key.substring(key.api_key.length - 6)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {key.name || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {key.assigned_username || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center">
                      <span
                        className={`badge ${
                          key.status === 'active'
                            ? 'badge-success'
                            : 'badge-danger'
                        }`}
                      >
                        {key.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {key.last_used ? new Date(key.last_used).toLocaleString('vi-VN') : 'Chưa sử dụng'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-center text-sm font-medium">
                      <button
                        onClick={() => handleEdit(key)}
                        className="text-blue-600 hover:text-blue-900 mr-3"
                        title="Chỉnh sửa"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button
                        onClick={() => handleDelete(key.id)}
                        className="text-red-600 hover:text-red-900"
                        title="Xóa"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {keys.length === 0 && !loading && (
          <div className="text-center py-12 bg-white rounded-lg shadow-sm">
            <Key className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">Chưa có Gemini API keys nào.</p>
            <button onClick={handleAdd} className="btn-primary mt-4 inline-flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Thêm key đầu tiên
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
}

