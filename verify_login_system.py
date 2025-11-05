"""
Verification Script for Login System
Checks all components are properly integrated
"""

import sys
import os
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"  [OK] {description}: {filepath}")
        return True
    else:
        print(f"  [MISSING] {description} NOT FOUND: {filepath}")
        return False

def check_imports():
    """Check if all required modules can be imported"""
    print("\n[Imports] Checking Imports...")
    
    all_ok = True
    
    # Check tool_api_client
    try:
        from tool_api_client import WorkFlowAPIClient
        print("  [OK] tool_api_client.py imported successfully")
    except Exception as e:
        print(f"  [ERROR] Failed to import tool_api_client: {e}")
        all_ok = False
    
    # Check login_dialog
    try:
        from login_dialog import LoginDialog
        print("  [OK] login_dialog.py imported successfully")
    except Exception as e:
        print(f"  [ERROR] Failed to import login_dialog: {e}")
        all_ok = False
    
    # Check PySide6
    try:
        from PySide6.QtWidgets import QApplication, QDialog
        print("  [OK] PySide6 imported successfully")
    except Exception as e:
        print(f"  [ERROR] Failed to import PySide6: {e}")
        all_ok = False
    
    # Check requests
    try:
        import requests
        print("  [OK] requests module imported successfully")
    except Exception as e:
        print(f"  [ERROR] Failed to import requests: {e}")
        all_ok = False
    
    return all_ok

def check_genvideopro_integration():
    """Check if GenVideoPro.py has the login integration"""
    print("\n[Integration] Checking GenVideoPro.py Integration...")
    
    filepath = Path(__file__).parent / "GenVideoPro.py"
    if not filepath.exists():
        print("  [ERROR] GenVideoPro.py not found!")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    checks = [
        ("from login_dialog import LoginDialog", "LoginDialog import"),
        ("self.current_user = None", "current_user attribute"),
        ("self.user_role = None", "user_role attribute"),
        ("def update_ui_permissions", "update_ui_permissions method"),
        ("def on_logout", "on_logout method"),
        ("self.lbl_user_info", "user info label"),
        ("self.btn_logout", "logout button"),
        ("self.btn_new_project", "new project button reference"),
        ("self.btn_edit_project", "edit project button reference"),
        ("self.btn_delete_project", "delete project button reference"),
        ("LOGIN_DIALOG_AVAILABLE", "LOGIN_DIALOG_AVAILABLE flag"),
        ("login_dialog = LoginDialog()", "LoginDialog instantiation in main"),
    ]
    
    all_ok = True
    for search_str, description in checks:
        if search_str in content:
            print(f"  [OK] {description} found")
        else:
            print(f"  [MISSING] {description} NOT FOUND")
            all_ok = False
    
    return all_ok

def check_admin_panel_connection():
    """Check if admin panel is accessible"""
    print("\n[Admin Panel] Checking Admin Panel Connection...")
    
    try:
        import requests
        response = requests.get("https://amz.io.vn", timeout=5)
        if response.status_code == 200:
            print("  [OK] Admin Panel is running at https://amz.io.vn")
            return True
        else:
            print(f"  [WARNING] Admin Panel responded with status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("  [ERROR] Cannot connect to Admin Panel at https://amz.io.vn")
        print("     Please check your internet connection")
        return False
    except Exception as e:
        print(f"  [ERROR] Error checking Admin Panel: {e}")
        return False

def check_api_endpoints():
    """Check if API endpoints are accessible"""
    print("\n[API] Checking API Endpoints...")
    
    try:
        import requests
        
        # Check auth endpoint
        response = requests.post(
            "https://amz.io.vn/api/tool/auth",
            json={"username": "test", "password": "test"},
            timeout=5
        )
        if response.status_code in [200, 401]:
            print("  [OK] Auth endpoint (/api/tool/auth) is accessible")
        else:
            print(f"  [WARNING] Auth endpoint returned status {response.status_code}")
        
        # Check projects endpoint (will fail without auth, but should be accessible)
        response = requests.get(
            "https://amz.io.vn/api/tool/projects",
            timeout=5
        )
        if response.status_code in [200, 401]:
            print("  [OK] Projects endpoint (/api/tool/projects) is accessible")
        else:
            print(f"  [WARNING] Projects endpoint returned status {response.status_code}")
        
        return True
    except Exception as e:
        print(f"  [ERROR] Error checking API endpoints: {e}")
        return False

def main():
    print("=" * 70)
    print("WorkFlow Login System Verification")
    print("=" * 70)
    
    # Check files
    print("\n[Files] Checking Files...")
    files_ok = True
    files_ok &= check_file_exists("login_dialog.py", "Login Dialog")
    files_ok &= check_file_exists("tool_api_client.py", "API Client")
    files_ok &= check_file_exists("GenVideoPro.py", "Main Application")
    files_ok &= check_file_exists("test_login.py", "Test Script")
    files_ok &= check_file_exists("LOGIN_GUIDE.md", "User Guide")
    files_ok &= check_file_exists("LOGIN_SYSTEM_SUMMARY.md", "System Summary")
    
    # Check imports
    imports_ok = check_imports()
    
    # Check GenVideoPro integration
    integration_ok = check_genvideopro_integration()
    
    # Check admin panel
    admin_panel_ok = check_admin_panel_connection()
    
    # Check API endpoints
    api_ok = check_api_endpoints() if admin_panel_ok else False
    
    # Summary
    print("\n" + "=" * 70)
    print("VERIFICATION SUMMARY")
    print("=" * 70)
    print(f"  Files:             {'[PASS]' if files_ok else '[FAIL]'}")
    print(f"  Imports:           {'[PASS]' if imports_ok else '[FAIL]'}")
    print(f"  Integration:       {'[PASS]' if integration_ok else '[FAIL]'}")
    print(f"  Admin Panel:       {'[PASS]' if admin_panel_ok else '[FAIL] (not running)'}")
    print(f"  API Endpoints:     {'[PASS]' if api_ok else '[FAIL] (admin panel not running)'}")
    print("=" * 70)
    
    all_ok = files_ok and imports_ok and integration_ok
    
    if all_ok:
        print("\n[SUCCESS] ALL CHECKS PASSED!")
        print("\n[Next Steps]")
        print("   1. Test Login: python test_login.py")
        print("   2. Run Application: python GenVideoPro.py")
        print("\n[Guide] Read LOGIN_GUIDE.md for detailed instructions")
    else:
        print("\n[ERROR] SOME CHECKS FAILED!")
        print("\n[Fix] Please fix the issues above before running the application.")
    
    if not admin_panel_ok:
        print("\n[Warning] Admin Panel is not accessible!")
        print("   Connecting to: https://amz.io.vn")
    
    print("\n" + "=" * 70)
    
    return 0 if all_ok else 1

if __name__ == "__main__":
    sys.exit(main())

