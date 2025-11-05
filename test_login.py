"""
Test script for Login Dialog
Run this to test the login functionality independently
"""

import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from login_dialog import LoginDialog

def main():
    app = QApplication(sys.argv)
    
    print("=" * 60)
    print("Testing WorkFlow Login Dialog")
    print("=" * 60)
    print("\nDefault credentials:")
    print("  Server: http://localhost:3000")
    print("  Username: admin")
    print("  Password: admin123")
    print("\nMake sure the admin panel is running!")
    print("  cd admin-panel")
    print("  npm run dev")
    print("=" * 60)
    print()
    
    dialog = LoginDialog()
    
    def on_success(api_client):
        print("\n✅ LOGIN SUCCESSFUL!")
        print(f"   User: {api_client.user_info}")
        print(f"   Token: {api_client.token[:30]}...")
        print(f"   Role: {api_client.user_info.get('role', 'unknown')}")
        
        # Test fetching projects
        print("\n📋 Testing project fetch...")
        projects = api_client.get_projects()
        if projects:
            print(f"   Found {len(projects)} projects:")
            for p in projects[:3]:  # Show first 3
                print(f"   - {p.get('channel_name', 'Unnamed')}")
        else:
            print("   No projects found or fetch failed")
        
        QMessageBox.information(
            None, "Login Test Success",
            f"✅ Successfully logged in as {api_client.user_info['username']}\n\n"
            f"Role: {api_client.user_info.get('role', 'unknown')}\n"
            f"Projects available: {len(projects) if projects else 0}"
        )
    
    def on_failure():
        print("\n❌ LOGIN FAILED OR CANCELLED")
        QMessageBox.warning(
            None, "Login Test Failed",
            "Login was cancelled or failed.\n\n"
            "Make sure:\n"
            "• Admin panel is running (npm run dev)\n"
            "• Server URL is correct\n"
            "• Credentials are correct"
        )
    
    dialog.login_successful.connect(on_success)
    
    result = dialog.exec()
    
    if result != LoginDialog.Accepted:
        on_failure()
    
    print("\nTest completed.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

