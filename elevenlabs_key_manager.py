"""
ElevenLabs Key Manager - Server-based key management
Replaces local voices.json file with centralized server management
"""

from typing import List, Optional, Dict
from tool_api_client import WorkFlowAPIClient


class ElevenLabsKeyManager:
    """
    Manages ElevenLabs API keys from server
    Features:
    - Load keys assigned to current user from server
    - Auto-rotation on key failure
    - Report key status back to server
    """
    
    def __init__(self, api_client: WorkFlowAPIClient):
        self.api_client = api_client
        self.keys: List[Dict] = []
        self.current_key_index = 0
        
    def load_keys_from_server(self) -> bool:
        """
        Load ElevenLabs keys from server
        Returns True if successful, False otherwise
        """
        if not self.api_client or not self.api_client.is_authenticated():
            print("⚠️ Not authenticated - cannot load ElevenLabs keys")
            return False
        
        try:
            keys = self.api_client.get_elevenlabs_keys()
            if keys:
                self.keys = keys
                self.current_key_index = 0
                print(f"✅ Loaded {len(keys)} ElevenLabs keys from server")
                return True
            else:
                print("⚠️ No ElevenLabs keys found on server")
                self.keys = []
                return False
        except Exception as e:
            print(f"❌ Error loading ElevenLabs keys: {e}")
            self.keys = []
            return False
    
    def get_current_key(self) -> Optional[str]:
        """
        Get current active API key
        Returns API key string or None if no keys available
        """
        if not self.keys:
            print("⚠️ No ElevenLabs keys available")
            return None
        
        if self.current_key_index >= len(self.keys):
            print("⚠️ All ElevenLabs keys exhausted")
            return None
        
        current = self.keys[self.current_key_index]
        return current.get('api_key')
    
    def report_key_success(self, credit_balance: Optional[int] = None):
        """Report successful key usage"""
        if not self.keys or self.current_key_index >= len(self.keys):
            return
        
        current = self.keys[self.current_key_index]
        self.api_client.report_elevenlabs_key_status(
            key_id=current['id'],
            status='active',
            credit_balance=credit_balance
        )
    
    def report_key_failure(self, error_message: str, is_out_of_credit: bool = False):
        """
        Report key failure and rotate to next key
        
        Args:
            error_message: Error message from ElevenLabs API
            is_out_of_credit: True if key failed due to insufficient credits
        """
        if not self.keys or self.current_key_index >= len(self.keys):
            return
        
        current = self.keys[self.current_key_index]
        status = 'out_of_credit' if is_out_of_credit else 'dead'
        
        print(f"❌ ElevenLabs key failed: {error_message}")
        print(f"🔄 Marking key as {status} and rotating to next key")
        
        # Report to server
        self.api_client.report_elevenlabs_key_status(
            key_id=current['id'],
            status=status,
            error_message=error_message
        )
        
        # Rotate to next key
        self.current_key_index += 1
        
        if self.current_key_index < len(self.keys):
            next_key = self.keys[self.current_key_index]
            print(f"✅ Rotated to next key: {next_key.get('name', 'Unnamed')}")
        else:
            print("⚠️ No more keys available")
    
    def get_all_keys(self) -> List[str]:
        """
        Get all available API keys as strings
        For compatibility with existing code
        """
        return [k['api_key'] for k in self.keys if k.get('api_key')]
    
    def has_keys(self) -> bool:
        """Check if any keys are available"""
        return len(self.keys) > 0 and self.current_key_index < len(self.keys)
    
    def get_keys_info(self) -> str:
        """Get human-readable info about available keys"""
        if not self.keys:
            return "No keys available"
        
        active_count = len([k for k in self.keys if k.get('status') == 'active'])
        return f"{active_count}/{len(self.keys)} keys available"


# Example Usage
if __name__ == "__main__":
    from tool_api_client import WorkFlowAPIClient
    
    # Initialize API client
    client = WorkFlowAPIClient("http://localhost:3000")
    
    if client.authenticate("admin", "admin123"):
        # Initialize key manager
        key_manager = ElevenLabsKeyManager(client)
        
        # Load keys from server
        if key_manager.load_keys_from_server():
            print(f"\n📊 Keys Status: {key_manager.get_keys_info()}")
            
            # Get current key
            current_key = key_manager.get_current_key()
            if current_key:
                print(f"\n🔑 Current Key: {current_key[:15]}...{current_key[-8:]}")
                
                # Simulate usage
                # key_manager.report_key_success(credit_balance=1000)
                
                # Simulate failure
                # key_manager.report_key_failure("Invalid API key", is_out_of_credit=False)


