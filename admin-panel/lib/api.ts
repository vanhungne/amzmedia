const API_BASE = '/api';

export interface User {
  id: number;
  username: string;
  email: string | null;
  role: 'admin' | 'user';
  is_active: boolean;
  total_keys_received: number;
  total_keys_used: number;
  current_assigned_keys?: number;
  active_keys_count?: number;
  ready_keys_count?: number;
  device_id?: string | null;
  device_name?: string | null;
  device_locked_at?: string | null;
  created_at: string;
}

export interface Project {
  id: number;
  project_id: string;
  channel_name: string;
  script_template: string | null;
  num_prompts: number;
  voice_id: string | null;
  auto_workflow: boolean;
  video_output_folder: string | null;
  created_at: string;
  updated_at: string;
  created_by_username?: string;
}

export interface ElevenLabsKey {
  id: number;
  api_key: string;
  name: string | null;
  assigned_user_id: number | null;
  status: 'active' | 'dead' | 'out_of_credit';
  credit_balance: number | null;
  last_used: string | null;
  last_error: string | null;
  created_at: string;
  updated_at: string;
  assigned_username?: string;
  created_by_username?: string;
}

export interface ProxyKey {
  id: number;
  proxy_key: string;
  name: string | null;
  assigned_user_id: number | null;
  status: 'active' | 'dead' | 'inactive';
  last_validated: string | null;
  last_error: string | null;
  created_at: string;
  updated_at: string;
  assigned_username?: string;
  created_by_username?: string;
}

export interface GeminiKey {
  id: number;
  api_key: string;
  name: string | null;
  assigned_user_id: number | null;
  status: 'active' | 'dead';
  last_used: string | null;
  last_error: string | null;
  created_at: string;
  updated_at: string;
  assigned_username?: string;
  created_by_username?: string;
}

export interface OpenAIKey {
  id: number;
  api_key: string;
  name: string | null;
  assigned_user_id: number | null;
  status: 'active' | 'dead';
  last_used: string | null;
  last_error: string | null;
  created_at: string;
  updated_at: string;
  assigned_username?: string;
  created_by_username?: string;
}

// Auth API
export async function login(username: string, password: string) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error('Login failed');
  return res.json();
}

export async function logout() {
  const res = await fetch(`${API_BASE}/auth/logout`, {
    method: 'POST',
  });
  if (!res.ok) throw new Error('Logout failed');
  return res.json();
}

export async function getCurrentUser() {
  const res = await fetch(`${API_BASE}/auth/me`, {
    method: 'POST',
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Not authenticated');
  return res.json();
}

// Projects API
export async function getProjects(): Promise<{ projects: Project[] }> {
  const res = await fetch(`${API_BASE}/projects`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to fetch projects');
  return res.json();
}

export async function createProject(project: Partial<Project>): Promise<{ project: Project }> {
  const res = await fetch(`${API_BASE}/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(project),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to create project');
  }
  return res.json();
}

export async function updateProject(id: number, project: Partial<Project>): Promise<{ project: Project }> {
  const res = await fetch(`${API_BASE}/projects/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(project),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to update project');
  }
  return res.json();
}

export async function deleteProject(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/projects/${id}`, {
    method: 'DELETE',
    credentials: 'include',
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to delete project');
  }
}

// Users API
export async function getUsers(): Promise<{ users: User[] }> {
  const res = await fetch(`${API_BASE}/users`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to fetch users');
  return res.json();
}

export async function createUser(user: { username: string; password: string; email?: string; role?: 'admin' | 'user' }): Promise<User> {
  const res = await fetch(`${API_BASE}/users`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(user),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to create user');
  }
  return res.json();
}

export async function updateUser(id: number, user: Partial<User & { password?: string }>): Promise<{ user: User }> {
  const res = await fetch(`${API_BASE}/users/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(user),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to update user');
  }
  return res.json();
}

export async function deleteUser(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/users/${id}`, {
    method: 'DELETE',
    credentials: 'include',
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to delete user');
  }
}

// ElevenLabs Keys API
export async function getElevenLabsKeys(params?: {
  page?: number;
  limit?: number;
  status?: string;
  assigned_user_id?: number;
  search?: string;
}): Promise<{ 
  keys: ElevenLabsKey[]; 
  pagination: {
    total: number;
    page: number;
    limit: number;
    offset: number;
    hasMore: boolean;
    totalPages: number;
  };
  stats: {
    total: number;
    active: number;
    assigned: number;
    unassigned: number;
  };
}> {
  const queryParams = new URLSearchParams();
  if (params?.page) queryParams.set('page', params.page.toString());
  if (params?.limit) queryParams.set('limit', params.limit.toString());
  if (params?.status) queryParams.set('status', params.status);
  if (params?.assigned_user_id !== undefined) queryParams.set('assigned_user_id', params.assigned_user_id.toString());
  if (params?.search) queryParams.set('search', params.search);
  
  // CACHE BUSTING: Add timestamp to force fresh data
  queryParams.set('_t', Date.now().toString());
  
  const res = await fetch(`${API_BASE}/elevenlabs?${queryParams.toString()}`, {
    credentials: 'include',
    cache: 'no-store',
    headers: {
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache',
      'Expires': '0'
    }
  });
  if (!res.ok) throw new Error('Failed to fetch ElevenLabs keys');
  return res.json();
}

export async function createElevenLabsKey(key: { api_key: string; name?: string; assigned_user_id?: number }): Promise<{ key: ElevenLabsKey }> {
  const res = await fetch(`${API_BASE}/elevenlabs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(key),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to create ElevenLabs key');
  }
  return res.json();
}

export async function updateElevenLabsKey(id: number, key: Partial<ElevenLabsKey>): Promise<{ key: ElevenLabsKey }> {
  const res = await fetch(`${API_BASE}/elevenlabs/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(key),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to update ElevenLabs key');
  }
  return res.json();
}

export async function deleteElevenLabsKey(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/elevenlabs/${id}`, {
    method: 'DELETE',
    credentials: 'include',
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to delete ElevenLabs key');
  }
}

export async function bulkImportElevenLabsKeys(keys_text: string, assigned_user_id?: number): Promise<any> {
  const res = await fetch(`${API_BASE}/elevenlabs/bulk-import`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ keys_text, assigned_user_id }),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to bulk import keys');
  }
  return res.json();
}

export async function bulkAssignElevenLabsKeys(user_id: number, key_ids?: number[], quantity?: number): Promise<any> {
  const res = await fetch(`${API_BASE}/elevenlabs/bulk-assign`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ user_id, key_ids, quantity }),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to bulk assign keys');
  }
  return res.json();
}

// Check ElevenLabs Key Credit
export async function checkElevenLabsKey(id: number): Promise<any> {
  const res = await fetch(`${API_BASE}/elevenlabs/${id}/check`, {
    method: 'POST',
    credentials: 'include',
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to check ElevenLabs key');
  }
  return res.json();
}

export async function checkAllElevenLabsKeys(): Promise<any> {
  const res = await fetch(`${API_BASE}/elevenlabs/check-all`, {
    method: 'POST',
    credentials: 'include',
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to check all ElevenLabs keys');
  }
  return res.json();
}

// User Statistics API
export async function getUserStats(userId: number): Promise<any> {
  const res = await fetch(`${API_BASE}/users/${userId}/stats`, {
    credentials: 'include',
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to get user stats');
  }
  return res.json();
}

// Proxy Keys API
export async function getProxyKeys(): Promise<{ keys: ProxyKey[] }> {
  const res = await fetch(`${API_BASE}/proxy`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to fetch proxy keys');
  return res.json();
}

export async function createProxyKey(key: { proxy_key: string; name?: string; assigned_user_id?: number }): Promise<{ key: ProxyKey }> {
  const res = await fetch(`${API_BASE}/proxy`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(key),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to create proxy key');
  }
  return res.json();
}

export async function updateProxyKey(id: number, key: Partial<ProxyKey>): Promise<{ success: boolean }> {
  const res = await fetch(`${API_BASE}/proxy/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(key),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to update proxy key');
  }
  return res.json();
}

export async function deleteProxyKey(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/proxy/${id}`, {
    method: 'DELETE',
    credentials: 'include',
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to delete proxy key');
  }
}

// Gemini Keys API
export async function getGeminiKeys(): Promise<{ keys: GeminiKey[] }> {
  const res = await fetch(`${API_BASE}/gemini`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to fetch Gemini keys');
  return res.json();
}

export async function createGeminiKey(key: { api_key: string; name?: string; assigned_user_id?: number }): Promise<{ key: GeminiKey }> {
  const res = await fetch(`${API_BASE}/gemini`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(key),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to create Gemini key');
  }
  return res.json();
}

export async function updateGeminiKey(id: number, key: Partial<GeminiKey>): Promise<{ key: GeminiKey }> {
  const res = await fetch(`${API_BASE}/gemini/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(key),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to update Gemini key');
  }
  return res.json();
}

export async function deleteGeminiKey(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/gemini/${id}`, {
    method: 'DELETE',
    credentials: 'include',
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to delete Gemini key');
  }
}

// OpenAI Keys API
export async function getOpenAIKeys(): Promise<{ keys: OpenAIKey[] }> {
  const res = await fetch(`${API_BASE}/openai`, {
    credentials: 'include',
  });
  if (!res.ok) throw new Error('Failed to fetch OpenAI keys');
  return res.json();
}

export async function createOpenAIKey(key: { api_key: string; name?: string; assigned_user_id?: number }): Promise<{ key: OpenAIKey }> {
  const res = await fetch(`${API_BASE}/openai`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(key),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to create OpenAI key');
  }
  return res.json();
}

export async function updateOpenAIKey(id: number, key: Partial<OpenAIKey>): Promise<{ key: OpenAIKey }> {
  const res = await fetch(`${API_BASE}/openai/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify(key),
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to update OpenAI key');
  }
  return res.json();
}

export async function deleteOpenAIKey(id: number): Promise<void> {
  const res = await fetch(`${API_BASE}/openai/${id}`, {
    method: 'DELETE',
    credentials: 'include',
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.error || 'Failed to delete OpenAI key');
  }
}






