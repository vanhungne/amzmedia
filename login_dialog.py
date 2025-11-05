"""
Login Dialog for WorkFlow Tool
Authenticates users via Admin Panel API before allowing tool access
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QCheckBox, QFrame
)
from PySide6.QtGui import QPixmap, QIcon
from tool_api_client import WorkFlowAPIClient
import json
from pathlib import Path

# ============================================================
# SERVER CONFIGURATION - Thay đổi URL server tại đây
# ============================================================
DEFAULT_SERVER_URL = "https://amz.io.vn"  # Production server
# Để đổi server, sửa URL ở trên, ví dụ:
# DEFAULT_SERVER_URL = "http://localhost:3000"  # Local development
# DEFAULT_SERVER_URL = "http://14.226.226.126:3000"  # Remote server
# DEFAULT_SERVER_URL = "http://192.168.1.100:3000"  # LAN
# ============================================================


class LoginDialog(QDialog):
    """
    Login dialog with username/password authentication
    Connects to WorkFlow Admin Panel API
    """
    
    login_successful = Signal(object)  # Emits WorkFlowAPIClient on success
    
    def __init__(self, parent=None, server_url=None):
        super().__init__(parent)
        self.api_client = None
        # Sử dụng server_url được truyền vào, hoặc dùng DEFAULT_SERVER_URL
        self.server_url = server_url if server_url else DEFAULT_SERVER_URL
        self.setup_ui()
        self.load_saved_credentials()
        
    def setup_ui(self):
        """Setup login dialog UI"""
        self.setWindowTitle("WorkFlow - Đăng nhập")
        self.setFixedSize(420, 400)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        
        # Set dialog background color
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title with icon
        title = QLabel("WorkFlow Tool")
        title.setStyleSheet("""
            font-size: 32px; 
            font-weight: bold; 
            color: #1a1a1a;
            margin-bottom: 8px;
            letter-spacing: 1px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Vui lòng đăng nhập để tiếp tục")
        subtitle.setStyleSheet("""
            font-size: 14px; 
            color: #666666;
            margin-bottom: 25px;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)
        
        layout.addSpacing(10)
        
        # Username
        username_label = QLabel("Username:")
        username_label.setStyleSheet("""
            font-weight: bold;
            font-size: 13px;
            color: #2c3e50;
            margin-bottom: 5px;
        """)
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập username của bạn")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                color: #1a1a1a;
                min-height: 22px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #ffffff;
            }
            QLineEdit:hover {
                border: 2px solid #bdbdbd;
            }
        """)
        layout.addWidget(self.username_input)
        
        layout.addSpacing(8)
        
        # Password
        password_label = QLabel("Password:")
        password_label.setStyleSheet("""
            font-weight: bold;
            font-size: 13px;
            color: #2c3e50;
            margin-bottom: 5px;
        """)
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Nhập mật khẩu của bạn")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid #e0e0e0;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
                color: #1a1a1a;
                min-height: 22px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #ffffff;
            }
            QLineEdit:hover {
                border: 2px solid #bdbdbd;
            }
        """)
        self.password_input.returnPressed.connect(self.on_login)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(5)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Ghi nhớ đăng nhập")
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                color: #2c3e50;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #bdc3c7;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border: 2px solid #3498db;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #3498db;
            }
        """)
        layout.addWidget(self.remember_checkbox)
        
        layout.addSpacing(15)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.login_button = QPushButton("Đăng nhập")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 13px 24px;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                min-height: 22px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        self.login_button.clicked.connect(self.on_login)
        button_layout.addWidget(self.login_button)
        
        self.cancel_button = QPushButton("Hủy")
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #555555;
                padding: 13px 24px;
                border: none;
                border-radius: 8px;
                font-size: 15px;
                font-weight: bold;
                min-height: 22px;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QPushButton:pressed {
                background-color: #c0c0c0;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        layout.addSpacing(10)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            color: #e74c3c; 
            font-size: 12px;
            background-color: transparent;
            padding: 5px;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def on_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # Validation
        if not username:
            self.status_label.setText("⚠️ Vui lòng nhập username")
            self.status_label.setStyleSheet("""
                color: #e74c3c; 
                font-size: 12px;
                background-color: #fadbd8;
                padding: 8px;
                border-radius: 4px;
            """)
            self.username_input.setFocus()
            return
            
        if not password:
            self.status_label.setText("⚠️ Vui lòng nhập password")
            self.status_label.setStyleSheet("""
                color: #e74c3c; 
                font-size: 12px;
                background-color: #fadbd8;
                padding: 8px;
                border-radius: 4px;
            """)
            self.password_input.setFocus()
            return
        
        # Disable inputs during authentication
        self.set_inputs_enabled(False)
        self.status_label.setText("🔄 Đang xác thực...")
        self.status_label.setStyleSheet("""
            color: #3498db; 
            font-size: 12px;
            background-color: #d6eaf8;
            padding: 8px;
            border-radius: 4px;
        """)
        
        # Authenticate
        try:
            self.api_client = WorkFlowAPIClient(self.server_url)
            
            if self.api_client.authenticate(username, password):
                # Success
                self.status_label.setText("✅ Đăng nhập thành công!")
                self.status_label.setStyleSheet("""
                    color: #27ae60; 
                    font-size: 12px;
                    background-color: #d5f4e6;
                    padding: 8px;
                    border-radius: 4px;
                """)
                
                # Save credentials if remember me is checked
                if self.remember_checkbox.isChecked():
                    self.save_credentials(self.server_url, username, password)
                else:
                    self.clear_saved_credentials()
                
                # Emit success signal
                self.login_successful.emit(self.api_client)
                
                # Close dialog
                self.accept()
            else:
                # Failed
                self.status_label.setText("❌ Đăng nhập thất bại! Kiểm tra lại thông tin.")
                self.status_label.setStyleSheet("""
                    color: #e74c3c; 
                    font-size: 12px;
                    background-color: #fadbd8;
                    padding: 8px;
                    border-radius: 4px;
                """)
                self.set_inputs_enabled(True)
                self.password_input.clear()
                self.password_input.setFocus()
                
        except Exception as e:
            self.status_label.setText(f"❌ Lỗi kết nối: {str(e)}")
            self.status_label.setStyleSheet("""
                color: #e74c3c; 
                font-size: 12px;
                background-color: #fadbd8;
                padding: 8px;
                border-radius: 4px;
            """)
            self.set_inputs_enabled(True)
    
    def set_inputs_enabled(self, enabled: bool):
        """Enable/disable all input fields"""
        self.username_input.setEnabled(enabled)
        self.password_input.setEnabled(enabled)
        self.remember_checkbox.setEnabled(enabled)
        self.login_button.setEnabled(enabled)
        self.cancel_button.setEnabled(enabled)
    
    def save_credentials(self, server: str, username: str, password: str):
        """Save login credentials to file (encrypted in production)"""
        try:
            creds_file = Path(__file__).parent / ".workflow_creds"
            data = {
                "server": server,
                "username": username,
                "password": password  # TODO: Encrypt this in production
            }
            with open(creds_file, 'w', encoding='utf-8') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Failed to save credentials: {e}")
    
    def load_saved_credentials(self):
        """Load saved credentials if available"""
        try:
            creds_file = Path(__file__).parent / ".workflow_creds"
            if creds_file.exists():
                with open(creds_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Server URL is now fixed, only load username and password
                    self.username_input.setText(data.get("username", ""))
                    self.password_input.setText(data.get("password", ""))
                    self.remember_checkbox.setChecked(True)
        except Exception as e:
            print(f"Failed to load credentials: {e}")
    
    def clear_saved_credentials(self):
        """Clear saved credentials file"""
        try:
            creds_file = Path(__file__).parent / ".workflow_creds"
            if creds_file.exists():
                creds_file.unlink()
        except Exception as e:
            print(f"Failed to clear credentials: {e}")


# Test the dialog
if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    
    dialog = LoginDialog()
    
    def on_success(api_client):
        print(f"✅ Login successful!")
        print(f"User: {api_client.user_info}")
        print(f"Token: {api_client.token[:20]}...")
    
    dialog.login_successful.connect(on_success)
    
    result = dialog.exec()
    if result == QDialog.Accepted:
        print("Dialog accepted")
    else:
        print("Dialog rejected")
    
    sys.exit(0)

