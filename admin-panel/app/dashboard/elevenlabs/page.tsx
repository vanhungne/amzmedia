'use client';

import Layout from '@/components/Layout';
import { useState, useEffect } from 'react';
import { getElevenLabsKeys, createElevenLabsKey, updateElevenLabsKey, deleteElevenLabsKey, getUsers, bulkImportElevenLabsKeys, bulkAssignElevenLabsKeys, checkElevenLabsKey, checkAllElevenLabsKeys, type ElevenLabsKey, type User } from '@/lib/api';
import { Plus, Edit, Trash2, X, Key, AlertCircle, CheckCircle, XCircle, Upload, Users, RefreshCw } from 'lucide-react';

export default function ElevenLabsPage() {
  const [keys, setKeys] = useState<ElevenLabsKey[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [showBulkImportModal, setShowBulkImportModal] = useState(false);
  const [showBulkAssignModal, setShowBulkAssignModal] = useState(false);
  const [editingKey, setEditingKey] = useState<ElevenLabsKey | null>(null);
  const [formData, setFormData] = useState({
    api_key: '',
    name: '',
    assigned_user_id: 0,
    status: 'active' as 'active' | 'dead' | 'out_of_credit',
    credit_balance: 0,
  });
  const [bulkImportData, setBulkImportData] = useState({
    keys_text: '',
    assigned_user_id: 0,
  });
  const [bulkAssignData, setBulkAssignData] = useState({
    user_id: 0,
    quantity: 1,
  });
  const [checkingKey, setCheckingKey] = useState<number | null>(null);
  const [checkingAll, setCheckingAll] = useState(false);
  const [showProgressModal, setShowProgressModal] = useState(false);
  const [progressData, setProgressData] = useState({
    total: 0,
    current: 0,
    currentKey: '',
    results: [] as any[],
    summary: null as any
  });

  useEffect(() => {
    loadKeys();
    loadUsers();
  }, []);

  const loadKeys = async () => {
    try {
      const res = await getElevenLabsKeys();
      setKeys(res.keys);
    } catch (err) {
      console.error('Failed to load ElevenLabs keys:', err);
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
      api_key: '',
      name: '',
      assigned_user_id: 0,
      status: 'active',
      credit_balance: 0,
    });
    setShowModal(true);
  };

  const handleEdit = (key: ElevenLabsKey) => {
    setEditingKey(key);
    setFormData({
      api_key: key.api_key,
      name: key.name || '',
      assigned_user_id: key.assigned_user_id || 0,
      status: key.status,
      credit_balance: key.credit_balance || 0,
    });
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const submitData = {
        ...formData,
        assigned_user_id: formData.assigned_user_id || null,
        credit_balance: formData.credit_balance || null,
      };

      if (editingKey) {
        await updateElevenLabsKey(editingKey.id, submitData);
      } else {
        await createElevenLabsKey(submitData);
      }
      setShowModal(false);
      loadKeys();
    } catch (err: any) {
      alert(err.message || 'Failed to save ElevenLabs key');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Bạn có chắc muốn xóa API key này?')) return;
    try {
      await deleteElevenLabsKey(id);
      loadKeys();
    } catch (err: any) {
      alert(err.message || 'Failed to delete ElevenLabs key');
    }
  };

  const handleBulkImport = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = await bulkImportElevenLabsKeys(
        bulkImportData.keys_text,
        bulkImportData.assigned_user_id || undefined
      );
      
      alert(
        `✅ Import thành công!\n\n` +
        `- Imported: ${result.imported_count}\n` +
        `- Duplicates: ${result.duplicate_count}\n` +
        `- Invalid: ${result.invalid_count}\n` +
        `- Skipped: ${result.skipped_count}`
      );
      
      setShowBulkImportModal(false);
      setBulkImportData({ keys_text: '', assigned_user_id: 0 });
      loadKeys();
    } catch (err: any) {
      alert(err.message || 'Failed to bulk import keys');
    }
  };

  const handleBulkAssign = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const result = await bulkAssignElevenLabsKeys(
        bulkAssignData.user_id,
        undefined,
        bulkAssignData.quantity
      );
      
      alert(`✅ Assigned ${result.assigned_count} keys to user successfully!`);
      setShowBulkAssignModal(false);
      setBulkAssignData({ user_id: 0, quantity: 1 });
      loadKeys();
    } catch (err: any) {
      alert(err.message || 'Failed to bulk assign keys');
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result as string;
      setBulkImportData({ ...bulkImportData, keys_text: text });
    };
    reader.readAsText(file);
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
      case 'out_of_credit':
        return (
          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <AlertCircle className="w-3 h-3 mr-1" />
            Out of Credit
          </span>
        );
      default:
        return status;
    }
  };

  const getKeyCountForUser = (userId: number) => {
    return keys.filter(k => k.assigned_user_id === userId && k.status === 'active').length;
  };

  const getUnassignedKeyCount = () => {
    return keys.filter(k => k.assigned_user_id === null && k.status === 'active').length;
  };

  const handleCheckKey = async (keyId: number) => {
    setCheckingKey(keyId);
    try {
      const result = await checkElevenLabsKey(keyId);
      if (result.success) {
        alert(
          `✅ Key đang hoạt động!\n\n` +
          `Status: ${result.status}\n` +
          `Credit Balance: ${result.credit_balance?.toLocaleString() || 'N/A'}\n` +
          `Tier: ${result.subscription_info?.tier || 'N/A'}\n` +
          (result.warning ? `\n⚠️ ${result.warning}` : '')
        );
      } else {
        alert(`❌ Key không hoạt động!\n\nError: ${result.error}`);
      }
      loadKeys(); // Reload to show updated data
    } catch (err: any) {
      alert(err.message || 'Failed to check key');
    } finally {
      setCheckingKey(null);
    }
  };

  const handleCheckAllKeys = async () => {
    if (!confirm('Bạn có chắc muốn check tất cả keys? Progress sẽ được hiển thị realtime.')) return;
    
    setCheckingAll(true);
    setShowProgressModal(true);
    setProgressData({
      total: 0,
      current: 0,
      currentKey: '',
      results: [],
      summary: null
    });

    try {
      const response = await fetch('/api/elevenlabs/check-all', {
        method: 'POST',
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to start checking');
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('No response stream');
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value);
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = JSON.parse(line.slice(6));

            if (data.type === 'start') {
              setProgressData(prev => ({ ...prev, total: data.total }));
            } else if (data.type === 'progress') {
              setProgressData(prev => ({
                ...prev,
                current: data.current,
                currentKey: data.keyName
              }));
            } else if (data.type === 'result') {
              setProgressData(prev => ({
                ...prev,
                results: [...prev.results, data]
              }));
            } else if (data.type === 'complete') {
              setProgressData(prev => ({
                ...prev,
                summary: data.summary
              }));
              loadKeys(); // Reload keys to show updated data
            } else if (data.type === 'error') {
              alert(`❌ Error: ${data.error}`);
            }
          }
        }
      }
    } catch (err: any) {
      alert(err.message || 'Failed to check all keys');
      setShowProgressModal(false);
    } finally {
      setCheckingAll(false);
    }
  };

  return (
    <Layout>
      <div>
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">ElevenLabs API Keys</h1>
            <p className="text-gray-600 mt-2">Quản lý API keys cho ElevenLabs voice generation</p>
          </div>
          <div className="flex space-x-3">
            <button 
              onClick={handleCheckAllKeys} 
              disabled={checkingAll}
              className="btn btn-secondary flex items-center space-x-2"
            >
              <RefreshCw className={`w-4 h-4 ${checkingAll ? 'animate-spin' : ''}`} />
              <span>{checkingAll ? 'Checking...' : 'Check All Keys'}</span>
            </button>
            <button onClick={() => setShowBulkImportModal(true)} className="btn btn-secondary flex items-center space-x-2">
              <Upload className="w-4 h-4" />
              <span>Import File TXT</span>
            </button>
            <button onClick={() => setShowBulkAssignModal(true)} className="btn btn-secondary flex items-center space-x-2">
              <Users className="w-4 h-4" />
              <span>Bulk Assign</span>
            </button>
            <button onClick={handleCreate} className="btn btn-primary flex items-center space-x-2">
              <Plus className="w-4 h-4" />
              <span>Thêm API Key</span>
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
            <Key className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">Chưa có API key nào. Thêm API key đầu tiên!</p>
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
                    API Key
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Assigned User
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Credits
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Last Used
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
                        {key.api_key.slice(0, 15)}...{key.api_key.slice(-8)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{key.assigned_username || 'Unassigned'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(key.status)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{key.credit_balance !== null ? key.credit_balance.toLocaleString() : '-'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {key.last_used ? new Date(key.last_used).toLocaleDateString() : 'Never'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => handleCheckKey(key.id)}
                        disabled={checkingKey === key.id}
                        className="text-blue-600 hover:text-blue-900 mr-4"
                        title="Check credit từ ElevenLabs server"
                      >
                        <RefreshCw className={`w-4 h-4 inline ${checkingKey === key.id ? 'animate-spin' : ''}`} />
                      </button>
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
                  {editingKey ? 'Chỉnh Sửa API Key' : 'Thêm API Key Mới'}
                </h2>
                <button onClick={() => setShowModal(false)} className="text-gray-400 hover:text-gray-600">
                  <X className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    API Key *
                  </label>
                  <input
                    type="text"
                    className="input font-mono"
                    value={formData.api_key}
                    onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                    placeholder="sk_..."
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">Format: sk_xxxxxxxxxxxxxxxxxxxx</p>
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
                    placeholder="My ElevenLabs Key"
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
                  <>
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
                        <option value="out_of_credit">Out of Credit</option>
                      </select>
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Credit Balance (Optional)
                      </label>
                      <input
                        type="number"
                        className="input"
                        value={formData.credit_balance}
                        onChange={(e) => setFormData({ ...formData, credit_balance: parseInt(e.target.value) || 0 })}
                        min={0}
                      />
                    </div>
                  </>
                )}

                <div className="flex justify-end space-x-3 pt-4">
                  <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary">
                    Hủy
                  </button>
                  <button type="submit" className="btn btn-primary">
                    {editingKey ? 'Cập Nhật' : 'Thêm API Key'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Bulk Import Modal */}
        {showBulkImportModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-center p-6 border-b">
                <h2 className="text-xl font-bold">Import API Keys từ File TXT</h2>
                <button onClick={() => setShowBulkImportModal(false)} className="text-gray-400 hover:text-gray-600">
                  <X className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={handleBulkImport} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Upload File TXT
                  </label>
                  <input
                    type="file"
                    accept=".txt"
                    onChange={handleFileUpload}
                    className="input"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    File format: một API key mỗi dòng (sk_xxx...)
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Hoặc Paste API Keys
                  </label>
                  <textarea
                    className="input font-mono text-sm"
                    rows={10}
                    value={bulkImportData.keys_text}
                    onChange={(e) => setBulkImportData({ ...bulkImportData, keys_text: e.target.value })}
                    placeholder="sk_xxx&#10;sk_yyy&#10;sk_zzz"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Mỗi dòng một API key. Lines bắt đầu bằng # hoặc // sẽ bị bỏ qua.
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Auto Assign to User (Optional)
                  </label>
                  <select
                    className="input"
                    value={bulkImportData.assigned_user_id}
                    onChange={(e) => setBulkImportData({ ...bulkImportData, assigned_user_id: parseInt(e.target.value) })}
                  >
                    <option value={0}>Unassigned (cấp phát sau)</option>
                    {users.map((user) => (
                      <option key={user.id} value={user.id}>
                        {user.username} ({user.role})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button type="button" onClick={() => setShowBulkImportModal(false)} className="btn btn-secondary">
                    Hủy
                  </button>
                  <button type="submit" className="btn btn-primary">
                    Import Keys
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
                <h2 className="text-xl font-bold">Bulk Assign Keys to User</h2>
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
                    Hệ thống sẽ tự động assign N keys chưa được cấp phát
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

        {/* Progress Modal for Check All */}
        {showProgressModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-3xl w-full mx-4 max-h-[90vh] overflow-hidden">
              <div className="flex justify-between items-center p-6 border-b bg-gradient-to-r from-blue-500 to-blue-600 text-white">
                <h2 className="text-xl font-bold flex items-center">
                  <RefreshCw className={`w-5 h-5 mr-2 ${checkingAll ? 'animate-spin' : ''}`} />
                  Checking All API Keys
                </h2>
                {!checkingAll && (
                  <button onClick={() => setShowProgressModal(false)} className="text-white hover:text-gray-200">
                    <X className="w-6 h-6" />
                  </button>
                )}
              </div>

              <div className="p-6">
                {/* Progress Bar */}
                <div className="mb-6">
                  <div className="flex justify-between text-sm text-gray-600 mb-2">
                    <span>Progress: {progressData.current} / {progressData.total}</span>
                    <span>{progressData.total > 0 ? Math.round((progressData.current / progressData.total) * 100) : 0}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-4 overflow-hidden">
                    <div 
                      className="bg-blue-600 h-4 rounded-full transition-all duration-300 ease-out flex items-center justify-end pr-2"
                      style={{ width: `${progressData.total > 0 ? (progressData.current / progressData.total) * 100 : 0}%` }}
                    >
                      {progressData.current > 0 && (
                        <span className="text-xs text-white font-medium">
                          {Math.round((progressData.current / progressData.total) * 100)}%
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                {/* Current Key Being Checked */}
                {checkingAll && progressData.currentKey && (
                  <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                    <div className="flex items-center text-blue-800">
                      <RefreshCw className="w-4 h-4 mr-2 animate-spin" />
                      <span className="font-medium">Đang check: {progressData.currentKey}</span>
                    </div>
                  </div>
                )}

                {/* Results List */}
                <div className="max-h-96 overflow-y-auto">
                  <h3 className="font-semibold text-gray-900 mb-3">Kết quả:</h3>
                  {progressData.results.length === 0 ? (
                    <p className="text-gray-500 text-center py-4">Chưa có kết quả...</p>
                  ) : (
                    <div className="space-y-2">
                      {progressData.results.map((result, index) => (
                        <div 
                          key={index} 
                          className={`p-3 rounded-lg border ${
                            result.success 
                              ? result.status === 'active' 
                                ? 'bg-green-50 border-green-200' 
                                : result.status === 'out_of_credit'
                                ? 'bg-yellow-50 border-yellow-200'
                                : 'bg-gray-50 border-gray-200'
                              : 'bg-red-50 border-red-200'
                          }`}
                        >
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center">
                                {result.success ? (
                                  result.status === 'active' ? (
                                    <CheckCircle className="w-4 h-4 text-green-600 mr-2" />
                                  ) : result.status === 'out_of_credit' ? (
                                    <AlertCircle className="w-4 h-4 text-yellow-600 mr-2" />
                                  ) : (
                                    <XCircle className="w-4 h-4 text-gray-600 mr-2" />
                                  )
                                ) : (
                                  <XCircle className="w-4 h-4 text-red-600 mr-2" />
                                )}
                                <span className="font-medium text-gray-900">
                                  {result.name || `Key #${result.id}`}
                                </span>
                              </div>
                              <div className="ml-6 mt-1 text-sm">
                                {result.success ? (
                                  <>
                                    <span className={`font-medium ${
                                      result.status === 'active' ? 'text-green-700' : 
                                      result.status === 'out_of_credit' ? 'text-yellow-700' : 
                                      'text-gray-700'
                                    }`}>
                                      {result.status.toUpperCase()}
                                    </span>
                                    {result.credit_balance !== undefined && (
                                      <span className="text-gray-600 ml-2">
                                        • {result.credit_balance.toLocaleString()} credits
                                      </span>
                                    )}
                                    {result.tier && (
                                      <span className="text-gray-600 ml-2">• {result.tier}</span>
                                    )}
                                    {result.warning && (
                                      <div className="text-yellow-600 mt-1">⚠️ {result.warning}</div>
                                    )}
                                  </>
                                ) : (
                                  <span className="text-red-600">❌ {result.error}</span>
                                )}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Summary */}
                {progressData.summary && (
                  <div className="mt-6 p-4 bg-gray-50 rounded-lg border border-gray-200">
                    <h3 className="font-semibold text-gray-900 mb-3">📊 Tổng Kết:</h3>
                    <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-gray-900">{progressData.summary.total}</div>
                        <div className="text-xs text-gray-600">Total</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-600">{progressData.summary.active}</div>
                        <div className="text-xs text-gray-600">Active</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-red-600">{progressData.summary.dead}</div>
                        <div className="text-xs text-gray-600">Dead</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-yellow-600">{progressData.summary.out_of_credit}</div>
                        <div className="text-xs text-gray-600">Out of Credit</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-orange-600">{progressData.summary.errors}</div>
                        <div className="text-xs text-gray-600">Errors</div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Close Button */}
                {!checkingAll && progressData.summary && (
                  <div className="mt-6 flex justify-end">
                    <button 
                      onClick={() => setShowProgressModal(false)} 
                      className="btn btn-primary"
                    >
                      Đóng
                    </button>
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

