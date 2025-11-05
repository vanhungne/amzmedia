"""
API Client for WorkFlow Admin Panel Integration
Allows Python tool to authenticate users and fetch projects from admin panel
"""

import requests
from typing import Optional, Dict, List
import json
import platform

def get_device_id() -> str:
    """
    Get unique device identifier (Windows MachineGuid)
    Fallback to hostname + MAC if registry not accessible
    """
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as k:
            v, _ = winreg.QueryValueEx(k, "MachineGuid")
        return str(v).strip()
    except Exception:
        # Fallback: hostname + MAC address
        import uuid
        return f"{platform.node()}-{uuid.getnode()}"

class WorkFlowAPIClient:
    """Client for WorkFlow Admin Panel API"""
    
    def __init__(self, base_url: str = "http://localhost:3000"):
        self.base_url = base_url.rstrip('/')
        self.token: Optional[str] = None
        self.user_info: Optional[Dict] = None
        self.device_id = get_device_id()  # Get device ID on init
    
    def authenticate(self, username: str, password: str) -> bool:
        """
        Authenticate user with admin panel
        Sends device_id for device lock verification
        Returns True if successful, False otherwise
        """
        try:
            device_name = platform.node()  # Get computer name
            
            response = requests.post(
                f"{self.base_url}/api/tool/auth",
                json={
                    "username": username, 
                    "password": password,
                    "device_id": self.device_id,
                    "device_name": device_name
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    self.token = data.get('token')
                    self.user_info = data.get('user')
                    print(f"✅ Authenticated as: {self.user_info['username']} ({self.user_info['role']})")
                    print(f"🔒 Device ID: {self.device_id[:16]}...")
                    
                    # Log login activity
                    self.log_activity(
                        action='login',
                        category='auth',
                        details={'device_id': self.device_id, 'device_name': device_name},
                        status='success'
                    )
                    
                    return True
            
            error_msg = response.json().get('error', 'Unknown error')
            print(f"❌ Authentication failed: {error_msg}")
            
            # Log failed login
            if self.token:  # If we had a previous token
                self.log_activity(
                    action='login_failed',
                    category='auth',
                    details={'error': error_msg},
                    status='failed'
                )
            
            return False
            
        except Exception as e:
            print(f"❌ API Error: {e}")
            return False
    
    def get_projects(self) -> Optional[List[Dict]]:
        """
        Fetch all projects from admin panel
        Returns list of projects or None if failed
        """
        if not self.token:
            print("❌ Not authenticated. Call authenticate() first.")
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/api/tool/projects",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    projects = data.get('projects', [])
                    print(f"✅ Loaded {len(projects)} projects from admin panel")
                    return projects
            
            print(f"❌ Failed to fetch projects: {response.json().get('error', 'Unknown error')}")
            return None
            
        except Exception as e:
            print(f"❌ API Error: {e}")
            return None
    
    def get_project_by_channel(self, channel_name: str) -> Optional[Dict]:
        """
        Get specific project by channel name
        """
        projects = self.get_projects()
        if not projects:
            return None
        
        for project in projects:
            if project['channel_name'].lower() == channel_name.lower():
                return project
        
        print(f"❌ Project not found: {channel_name}")
        return None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.token is not None
    
    def log_activity(self, action: str, category: str, details: Optional[Dict] = None, status: str = 'success') -> bool:
        """
        Log user activity to server
        
        Args:
            action: Activity action (e.g., 'login', 'generate_voice', 'create_project')
            category: Category ('auth', 'project', 'generation', 'api', 'system')
            details: Additional details (dict)
            status: 'success', 'failed', 'error'
        
        Returns:
            True if logged successfully, False otherwise
        """
        if not self.token:
            return False
        
        try:
            device_name = platform.node()
            
            response = requests.post(
                f"{self.base_url}/api/tool/activity",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "action": action,
                    "category": category,
                    "details": details,
                    "status": status,
                    "device_name": device_name
                },
                timeout=10
            )
            
            return response.status_code == 200
            
        except Exception as e:
            # Don't print errors for logging failures (to avoid spam)
            return False
    
    def create_project(self, project_data: Dict) -> Optional[Dict]:
        """
        Create new project on server
        
        Args:
            project_data: {
                "channel_name": str,
                "script_template": str,
                "num_prompts": int,
                "voice_id": str,
                "auto_workflow": bool
            }
        
        Returns:
            Created project dict or None if failed
        """
        if not self.token:
            print("❌ Not authenticated. Call authenticate() first.")
            return None
        
        try:
            response = requests.post(
                f"{self.base_url}/api/tool/projects",
                headers={"Authorization": f"Bearer {self.token}"},
                json=project_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Project created: {project_data['channel_name']}")
                    return data.get('project')
            
            print(f"❌ Failed to create project: {response.json().get('error', 'Unknown error')}")
            return None
            
        except Exception as e:
            print(f"❌ API Error: {e}")
            return None
    
    def update_project(self, project_id: str, project_data: Dict) -> bool:
        """
        Update existing project on server
        
        Args:
            project_id: Project UUID
            project_data: Fields to update
        
        Returns:
            True if successful, False otherwise
        """
        if not self.token:
            print("❌ Not authenticated. Call authenticate() first.")
            return False
        
        try:
            response = requests.put(
                f"{self.base_url}/api/tool/projects/{project_id}",
                headers={"Authorization": f"Bearer {self.token}"},
                json=project_data,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Project updated: {project_id}")
                    return True
            
            print(f"❌ Failed to update project: {response.json().get('error', 'Unknown error')}")
            return False
            
        except Exception as e:
            print(f"❌ API Error: {e}")
            return False
    
    def delete_project(self, project_id: str) -> bool:
        """
        Delete project from server
        
        Args:
            project_id: Project UUID
        
        Returns:
            True if successful, False otherwise
        """
        if not self.token:
            print("❌ Not authenticated. Call authenticate() first.")
            return False
        
        try:
            response = requests.delete(
                f"{self.base_url}/api/tool/projects/{project_id}",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Project deleted: {project_id}")
                    return True
            
            print(f"❌ Failed to delete project: {response.json().get('error', 'Unknown error')}")
            return False
            
        except Exception as e:
            print(f"❌ API Error: {e}")
            return False
    
    def get_elevenlabs_keys(self) -> Optional[List[Dict]]:
        """
        Fetch ElevenLabs API keys assigned to current user
        Returns list of active keys or None if failed
        """
        if not self.token:
            print("❌ Not authenticated. Call authenticate() first.")
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/api/tool/elevenlabs",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    keys = data.get('keys', [])
                    print(f"✅ Loaded {len(keys)} ElevenLabs keys from server")
                    
                    # Log activity
                    self.log_activity(
                        action='load_elevenlabs_keys',
                        category='api',
                        details={'keys_count': len(keys)},
                        status='success'
                    )
                    
                    return keys
            
            print(f"❌ Failed to fetch ElevenLabs keys: {response.json().get('error', 'Unknown error')}")
            return None
            
        except Exception as e:
            print(f"❌ API Error: {e}")
            return None
    
    def report_elevenlabs_key_status(self, key_id: int, status: str, error_message: str = None, credit_balance: int = None) -> bool:
        """
        Report ElevenLabs key status back to server
        
        Args:
            key_id: Database ID of the key
            status: 'active', 'dead', or 'out_of_credit'
            error_message: Error message if key failed
            credit_balance: Remaining credits if available
        
        Returns:
            True if successful, False otherwise
        """
        if not self.token:
            print("❌ Not authenticated. Call authenticate() first.")
            return False
        
        try:
            response = requests.post(
                f"{self.base_url}/api/tool/elevenlabs",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "key_id": key_id,
                    "status": status,
                    "error_message": error_message,
                    "credit_balance": credit_balance
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Reported key status: {status}")
                    return True
            
            print(f"❌ Failed to report key status: {response.json().get('error', 'Unknown error')}")
            return False
            
        except Exception as e:
            print(f"❌ API Error: {e}")
            return False
    
    def get_proxy_keys(self) -> Optional[List[Dict]]:
        """
        Fetch proxy keys assigned to current user
        Returns list of active proxy keys or None if failed
        """
        if not self.token:
            print("❌ Not authenticated. Call authenticate() first.")
            return None
        
        try:
            response = requests.get(
                f"{self.base_url}/api/tool/proxy",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    keys = data.get('keys', [])
                    print(f"✅ Loaded {len(keys)} proxy keys from server")
                    return keys
            
            print(f"❌ Failed to fetch proxy keys: {response.json().get('error', 'Unknown error')}")
            return None
            
        except Exception as e:
            print(f"❌ API Error: {e}")
            return None
    
    def report_proxy_status(self, key_id: int, status: str, error_message: str = None) -> bool:
        """
        Report proxy key status back to server
        
        Args:
            key_id: Database ID of the proxy key
            status: 'active' or 'dead'
            error_message: Error message if proxy failed
        
        Returns:
            True if successful, False otherwise
        """
        if not self.token:
            print("❌ Not authenticated. Call authenticate() first.")
            return False
        
        try:
            response = requests.post(
                f"{self.base_url}/api/tool/proxy",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "key_id": key_id,
                    "status": status,
                    "error_message": error_message
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print(f"✅ Reported proxy status: {status}")
                    return True
            
            print(f"❌ Failed to report proxy status: {response.json().get('error', 'Unknown error')}")
            return False
            
        except Exception as e:
            print(f"❌ API Error: {e}")
            return False
    
    def get_gemini_keys(self) -> List[Dict]:
        """
        Get Gemini API keys assigned to current user from server
        Returns list of active Gemini keys
        """
        if not self.token:
            print("❌ Not authenticated. Call authenticate() first.")
            return []
        
        try:
            response = requests.get(
                f"{self.base_url}/api/tool/gemini",
                headers={"Authorization": f"Bearer {self.token}"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    gemini_keys = data.get('keys', [])
                    print(f"✅ Loaded {len(gemini_keys)} Gemini API keys from server")
                    
                    # Log activity
                    self.log_activity(
                        action='load_gemini_keys',
                        category='api',
                        details={'key_count': len(gemini_keys)},
                        status='success'
                    )
                    
                    return gemini_keys
            
            print(f"❌ Failed to get Gemini keys: {response.json().get('error', 'Unknown error')}")
            return []
            
        except Exception as e:
            print(f"❌ API Error: {e}")
            return []
    
    def report_gemini_status(self, key_id: int, status: str, error_message: str = None) -> bool:
        """
        Report Gemini key status to server (auto-report dead/error keys)
        
        Args:
            key_id: Gemini key ID
            status: 'active' or 'dead'
            error_message: Optional error message
        
        Returns:
            True if reported successfully, False otherwise
        """
        if not self.token:
            return False
        
        try:
            response = requests.post(
                f"{self.base_url}/api/tool/gemini",
                headers={"Authorization": f"Bearer {self.token}"},
                json={
                    "key_id": key_id,
                    "status": status,
                    "error_message": error_message
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ Gemini key status reported: {status}")
                return True
            
            return False
            
        except Exception as e:
            print(f"❌ Error reporting Gemini key status: {e}")
            return False


# Example Usage
if __name__ == "__main__":
    # Initialize client
    client = WorkFlowAPIClient("http://localhost:3000")
    
    # Authenticate
    if client.authenticate("admin", "admin123"):
        # Get all projects
        projects = client.get_projects()
        
        if projects:
            print("\n📋 Available Projects:")
            for project in projects:
                print(f"\n  Channel: {project['channel_name']}")
                print(f"  Project ID: {project['project_id']}")
                print(f"  Num Prompts: {project['num_prompts']}")
                print(f"  Voice ID: {project['voice_id'] or 'Not set'}")
                print(f"  Auto Workflow: {'Yes' if project['auto_workflow'] else 'No'}")
                
                if project['script_template']:
                    print(f"  Script Template: {project['script_template'][:100]}...")
        
        # Get specific project
        project = client.get_project_by_channel("My Channel")
        if project:
            print(f"\n✅ Found project: {project['channel_name']}")






