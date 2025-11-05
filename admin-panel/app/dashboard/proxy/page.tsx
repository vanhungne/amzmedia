'use client';

import Layout from '@/components/Layout';
import { useState, useEffect } from 'react';
import { getProxyKeys, createProxyKey, updateProxyKey, deleteProxyKey, getUsers, type ProxyKey, type User } from '@/lib/api';
import { Plus, Edit, Trash2, X, Network, AlertCircle, CheckCircle, XCircle, Users } from 'lucide-react';

export default function ProxyPage() {
  const [keys, setKeys] = useState<ProxyKey[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showBulkAssignModal, setShowBulkAssignModal] = useState(false);
  const [editingKey, setEditingKey] = useState<ProxyKey | null>(null);
  const [formData, setFormData] = useState({
    proxy_key: '',
    name: '',
    assigned_user_id: 0,
    status: 'active' as 'active' | 'dead' | 'inactive',
  });
  const [bulkAssignData, setBulkAssignData] = useState({
    user_id: 0,
    quantity: 1,
  });

  useEffect(() => {
    loadKeys();
    loadUsers();
  }, []);

  const loadKeys = async () => {
    try {
      const res = await getProxyKeys();
      setKeys(res.keys);
    } catch (err) {
      console.error('Failed to load proxy keys:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadUsers = async () => {
    try {
      const res = await getUsers();
      setUsers(res.users);
    } catch (err) {
      console.error('Failed to load users:', err);
    }
  };

  const handleCreate = () => {
    setEditingKey(null);
    setFormData({
      proxy_key: '',
      name: '',
      assigned_user_id: 0,
      status: 'active',
    });
    setShowModal(true);
  };

  const handleEdit = (key: ProxyKey) => {
    setEditingKey(key);
    setFormData({
      proxy_key: key.proxy_key,
      name: key.name || '',
      assigned_user_id: key.assigned_user_id || 0,
      status: key.status,
    });
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        assigned_user_id: formData.assigned_user_id || undefined,
      };

      if (editingKey) {
        await updateProxyKey(editingKey.id, submitData);
      } else {
        await createProxyKey(submitData);
      }
      setShowModal(false);
      loadKeys();
    } catch (err: any) {
      alert(err.message || 'Failed to save proxy key');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Bạn có chắc muốn xóa proxy key này?')) return;
    try {
      await deleteProxyKey(id);
      loadKeys();
    } catch (err: any) {
      alert(err.message || 'Failed to delete proxy key');
    }
  };

  const handleBulkAssign = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!bulkAssignData.user_id) {
      alert('Vui lòng chọn user');
      return;
    }

    try {
      const unassignedKeys = keys.filter(k => k.assigned_user_id === null && k.status === 'active');
      const keysToAssign = unassignedKeys.slice(0, bulkAssignData.quantity);
      
      if (keysToAssign.length === 0) {
        alert('Không có proxy key nào khả dụng để assign');
        return;
      }

      let assignedCount = 0;
      for (const key of keysToAssign) {
        try {
          await updateProxyKey(key.id, { assigned_user_id: bulkAssignData.user_id });
          assignedCount++;
        } catch (err) {
          console.error(`Failed to assign key ${key.id}:`, err);
        }
      }

      alert(`✅ Đã giao ${assignedCount} proxy keys cho user thành công!`);
      setShowBulkAssignModal(false);
      setBulkAssignData({ user_id: 0, quantity: 1 });
      loadKeys();
    } catch (err: any) {
      alert(err.message || 'Failed to bulk assign keys');
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'active':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <CheckCircle className="w-3 h-3 mr-1" />
            Active
          </span>
        );
      case 'dead':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <XCircle className="w-3 h-3 mr-1" />
            Dead
          </span>
        );
      case 'inactive':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <AlertCircle className="w-3 h-3 mr-1" />
            Inactive
          </span>
        );
      default:
        return status;
    }
  };

  const getUnassignedKeyCount = () => {
    return keys.filter(k => k.assigned_user_id === null && k.status === 'active').length;
  };

  return (
    <Layout>
      <div>
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Proxy Keys</h1>
            <p className="text-gray-600 mt-2">Quản lý proxy keys cho server</p>
          </div>
          <div className="flex space-x-3">
            <button onClick={() => setShowBulkAssignModal(true)} className="btn btn-secondary flex items-center space-x-2">
              <Users className="w-4 h-4" />
              <span>Bulk Assign</span>
            </button>
            <button onClick={handleCreate} className="btn btn-primary flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>Thêm Proxy Key</span>
            </button>
          </div>
        </div>

        {/* Stats Summary */}
        {!loading && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
              <div className="text-sm text-gray-600">Total Keys</div>
              <div className="text-2xl font-bold text-gray-900">{keys.length}</div>
            </div>
            <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
              <div className="text-sm text-gray-600">Active Keys</div>
              <div className="text-2xl font-bold text-green-600">
                {keys.filter(k => k.status === 'active').length}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500">
              <div className="text-sm text-gray-600">Assigned Keys</div>
              <div className="text-2xl font-bold text-purple-600">
                {keys.filter(k => k.assigned_user_id !== null).length}
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4 border-l-4 border-orange-500">
              <div className="text-sm text-gray-600">Unassigned Keys</div>
              <div className="text-2xl font-bold text-orange-600">{getUnassignedKeyCount()}</div>
            </div>
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          </div>
        ) : keys.length === 0 ? (
          <div className="card text-center py-12">
            <Network className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Chưa có proxy key nào. Thêm proxy key đầu tiên!</p>
          </div>
        ) : (
          <div className="card overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Proxy Key
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Assigned User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Validated
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Error
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {keys.map((key) => (
                  <tr key={key.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{key.name || '-'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500 font-mono">
                        {key.proxy_key.length > 30 
                          ? `${key.proxy_key.slice(0, 15)}...${key.proxy_key.slice(-8)}`
                          : key.proxy_key}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{key.assigned_username || 'Unassigned'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(key.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {key.last_validated ? new Date(key.last_validated).toLocaleDateString() : 'Never'}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-500 max-w-xs truncate" title={key.last_error || ''}>
                        {key.last_error || '-'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleEdit(key)}
                        className="text-primary-600 hover:text-primary-900 mr-4"
                      >
                        <Edit className="w-4 h-4 inline" />
                      </button>
                      <button
                        onClick={() => handleDelete(key.id)}
                        className="text-red-600 hover:text-red-900"
                      >
                        <Trash2 className="w-4 h-4 inline" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-center p-6 border-b">
                <h2 className="text-xl font-bold">
                  {editingKey ? 'Chỉnh Sửa Proxy Key' : 'Thêm Proxy Key Mới'}
                </h2>
                <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">
                  <X className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Proxy Key *
                  </label>
                  <input
                    type="text"
                    className="input font-mono"
                    value={formData.proxy_key}
                    onChange={(e) => setFormData({ ...formData, proxy_key: e.target.value })}
                    placeholder="http://username:password@host:port hoặc socks5://..."
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">Format: http://user:pass@host:port hoặc socks5://user:pass@host:port</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Name (Optional)
                  </label>
                  <input
                    type="text"
                    className="input"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="My Proxy Key"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Assign to User
                  </label>
                  <select
                    className="input"
                    value={formData.assigned_user_id}
                    onChange={(e) => setFormData({ ...formData, assigned_user_id: parseInt(e.target.value) })}
                  >
                    <option value={0}>Unassigned</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.username} ({user.role})
                      </option>
                    ))}
                  </select>
                </div>

                {editingKey && (
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Status
                    </label>
                    <select
                      className="input"
                      value={formData.status}
                      onChange={(e) => setFormData({ ...formData, status: e.target.value as any })}
                    >
                      <option value="active">Active</option>
                      <option value="dead">Dead</option>
                      <option value="inactive">Inactive</option>
                    </select>
                  </div>
                )}

                <div className="flex justify-end space-x-3 pt-4">
                  <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary">
                    Hủy
                  </button>
                  <button type="submit" className="btn btn-primary">
                    {editingKey ? 'Cập Nhật' : 'Thêm Proxy Key'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Bulk Assign Modal */}
        {showBulkAssignModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
              <div className="flex justify-between items-center p-6 border-b">
                <h2 className="text-xl font-bold">Bulk Assign Proxy Keys to User</h2>
                <button onClick={() => setShowBulkAssignModal(false)} className="text-gray-400 hover:text-gray-600">
                  <X className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={handleBulkAssign} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select User *
                  </label>
                  <select
                    className="input"
                    value={bulkAssignData.user_id}
                    onChange={(e) => setBulkAssignData({ ...bulkAssignData, user_id: parseInt(e.target.value) })}
                    required
                  >
                    <option value={0}>-- Chọn User --</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.username} ({user.role})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Số Lượng Keys *
                  </label>
                  <input
                    type="number"
                    className="input"
                    value={bulkAssignData.quantity}
                    onChange={(e) => setBulkAssignData({ ...bulkAssignData, quantity: parseInt(e.target.value) || 1 })}
                    min={1}
                    max={100}
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Hệ thống sẽ tự động assign N proxy keys chưa được cấp phát
                  </p>
                </div>

                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-sm text-blue-800">
                    <strong>Note:</strong> Chỉ assign các keys có status = Active và chưa được assign cho user nào.
                  </p>
                  <p className="text-sm text-blue-800 mt-2">
                    <strong>Available:</strong> {getUnassignedKeyCount()} unassigned active keys
                  </p>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button type="button" onClick={() => setShowBulkAssignModal(false)} className="btn btn-secondary">
                    Hủy
                  </button>
                  <button type="submit" className="btn btn-primary">
                    Assign Keys
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






