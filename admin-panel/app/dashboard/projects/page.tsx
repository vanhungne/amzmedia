'use client';

import Layout from '@/components/Layout';
import SpaceLoader from '@/components/SpaceLoader';
import { useState, useEffect } from 'react';
import { getProjects, createProject, updateProject, deleteProject, getCurrentUser, type Project, type User } from '@/lib/api';
import { Plus, Edit, Trash2, X, Sparkles, FolderOpen } from 'lucide-react';

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<User | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [editingProject, setEditingProject] = useState<Project | null>(null);
  const [formData, setFormData] = useState({
    channel_name: '',
    script_template: '',
    num_prompts: 12,
    voice_id: '',
    auto_workflow: true,
    video_output_folder: '',
  });

  useEffect(() => {
    loadUser();
    loadProjects();
  }, []);

  const loadUser = async () => {
    try {
      const userData = await getCurrentUser();
      setUser(userData);
    } catch (err) {
      console.error('Failed to load user:', err);
    }
  };

  const loadProjects = async () => {
    try {
      const res = await getProjects();
      setProjects(res.projects);
    } catch (err) {
      console.error('Failed to load projects:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = () => {
    setEditingProject(null);
    setFormData({
      channel_name: '',
      script_template: '',
      num_prompts: 12,
      voice_id: '',
      auto_workflow: true,
      video_output_folder: '',
    });
    setShowModal(true);
  };

  const handleEdit = (project: Project) => {
    setEditingProject(project);
    setFormData({
      channel_name: project.channel_name,
      script_template: project.script_template || '',
      num_prompts: project.num_prompts,
      voice_id: project.voice_id || '',
      auto_workflow: project.auto_workflow,
      video_output_folder: project.video_output_folder || '',
    });
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      if (editingProject) {
        await updateProject(editingProject.id, formData);
      } else {
        await createProject(formData);
      }
      setShowModal(false);
      loadProjects();
    } catch (err: any) {
      alert(err.message || 'Failed to save project');
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Bạn có chắc muốn xóa project này?')) return;
    try {
      await deleteProject(id);
      loadProjects();
    } catch (err: any) {
      alert(err.message || 'Failed to delete project');
    }
  };

  return (
    <Layout>
      <div>
        <div className="flex justify-between items-center mb-8">
          <div className="relative">
            <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 via-blue-600 to-pink-600 bg-clip-text text-transparent mb-2 flex items-center gap-3" style={{
              filter: 'drop-shadow(0 0 20px rgba(147, 51, 234, 0.3))'
            }}>
              <Sparkles className="w-10 h-10 text-purple-500 animate-pulse" />
              Projects Management
            </h1>
            <p className="text-gray-700 font-medium">Quản lý các dự án và cấu hình</p>
          </div>
          {user?.role !== 'manager' && (
            <button onClick={handleCreate} className="btn btn-primary relative z-10">
              <Plus className="w-5 h-5 relative z-10" />
              <span className="relative z-10">Tạo Project Mới</span>
            </button>
          )}
        </div>

        {loading ? (
          <SpaceLoader message="Đang tải danh sách projects..." />
        ) : projects.length === 0 ? (
          <div className="card text-center py-16 relative overflow-hidden">
            <div className="absolute inset-0 opacity-20">
              <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-purple-400 rounded-full blur-3xl animate-pulse"></div>
            </div>
            <FolderOpen className="w-16 h-16 mx-auto mb-4 relative z-10" style={{
              color: '#667eea',
              filter: 'drop-shadow(0 0 20px rgba(102, 126, 234, 0.5))'
            }} />
            <p className="text-gray-700 font-bold text-lg relative z-10">Chưa có project nào</p>
            <p className="text-gray-600 text-sm mt-2 relative z-10">Hãy tạo project đầu tiên!</p>
          </div>
        ) : (
          <div className="card overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Channel Name
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Project ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Voice ID
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Created By
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {projects.map((project) => (
                  <tr key={project.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{project.channel_name}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500 font-mono">{project.project_id.slice(0, 8)}...</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">{project.voice_id || '-'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">{project.created_by_username || '-'}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      {user?.role !== 'manager' && (
                        <>
                          <button
                            onClick={() => handleEdit(project)}
                            className="text-primary-600 hover:text-primary-900 mr-4"
                          >
                            <Edit className="w-4 h-4 inline" />
                          </button>
                          <button
                            onClick={() => handleDelete(project.id)}
                            className="text-red-600 hover:text-red-900"
                          >
                            <Trash2 className="w-4 h-4 inline" />
                          </button>
                        </>
                      )}
                      {user?.role === 'manager' && (
                        <span className="text-gray-400 text-xs">Chỉ xem</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Modal with Space Theme */}
        {showModal && (
          <div className="fixed inset-0 flex items-center justify-center z-50" style={{
            background: 'rgba(0, 0, 0, 0.7)',
            backdropFilter: 'blur(8px)'
          }}>
            <div className="rounded-2xl shadow-2xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto border border-white/30" style={{
              background: 'rgba(255, 255, 255, 0.98)',
              backdropFilter: 'blur(20px)',
              boxShadow: '0 0 80px rgba(102, 126, 234, 0.5), 0 0 120px rgba(118, 75, 162, 0.3)'
            }}>
              <div className="flex justify-between items-center p-6 border-b border-purple-100" style={{
                background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)'
              }}>
                <h2 className="text-xl font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
                  {editingProject ? 'Chỉnh Sửa Project' : 'Tạo Project Mới'}
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
                    Channel Name *
                  </label>
                  <input
                    type="text"
                    className="input"
                    value={formData.channel_name}
                    onChange={(e) => setFormData({ ...formData, channel_name: e.target.value })}
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Script Template (System Prompt cho Groq)
                  </label>
                  <textarea
                    className="input"
                    rows={8}
                    value={formData.script_template}
                    onChange={(e) => setFormData({ ...formData, script_template: e.target.value })}
                    placeholder="GPT này chuyên xử lý các kịch bản dài..."
                  />
                </div>

                {/* Số Prompts - Hidden, auto random 12-24 in Python app */}

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Voice ID (ElevenLabs)
                  </label>
                  <input
                    type="text"
                    className="input"
                    value={formData.voice_id}
                    onChange={(e) => setFormData({ ...formData, voice_id: e.target.value })}
                    placeholder="uju3wxzG5OhpWcoi3SMy"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Video Output Folder
                  </label>
                  <input
                    type="text"
                    className="input"
                    value={formData.video_output_folder}
                    onChange={(e) => setFormData({ ...formData, video_output_folder: e.target.value })}
                    placeholder="D:\Videos\Output"
                  />
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="auto_workflow"
                    checked={formData.auto_workflow}
                    onChange={(e) => setFormData({ ...formData, auto_workflow: e.target.checked })}
                    className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <label htmlFor="auto_workflow" className="ml-2 text-sm text-gray-700">
                    Auto Workflow (tự động chạy voice + image)
                  </label>
                </div>

                <div className="flex justify-end space-x-3 pt-4">
                  <button type="button" onClick={() => setShowModal(false)} className="btn btn-secondary relative z-10">
                    <span className="relative z-10">Hủy</span>
                  </button>
                  <button type="submit" className="btn btn-primary relative">
                    <span className="relative z-10">{editingProject ? 'Cập Nhật' : 'Tạo Project'}</span>
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






