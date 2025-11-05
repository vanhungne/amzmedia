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
        self.setFixedSize(500, 580)
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)
        
        # Set dialog with gradient background
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea,
                    stop:1 #764ba2
                );
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(18)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Title with icon
        title = QLabel("AMZ Work Tool")
        title.setStyleSheet("""
            font-size: 36px; 
            font-weight: bold; 
            color: #ffffff;
            margin-bottom: 10px;
            letter-spacing: 2px;
            text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        

        # Username
        username_label = QLabel("Username:")
        username_label.setStyleSheet("""
            font-weight: 600;
            font-size: 14px;
            color: #ffffff;
            margin-bottom: 8px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
        """)
        layout.addWidget(username_label)
        
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Nhập username của bạn")
        self.username_input.setStyleSheet("""
            QLineEdit {
                padding: 16px 18px;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                background-color: rgba(255, 255, 255, 0.95);
                color: #2c3e50;
                min-height: 26px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            QLineEdit:focus {
                background-color: #ffffff;
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
            QLineEdit:hover {
                background-color: #ffffff;
            }
            QLineEdit::placeholder {
                color: rgba(44, 62, 80, 0.5);
            }
        """)
        layout.addWidget(self.username_input)
        
        layout.addSpacing(20)
        
        # Password
        password_label = QLabel("Password:")
        password_label.setStyleSheet("""
            font-weight: 600;
            font-size: 14px;
            color: #ffffff;
            margin-bottom: 8px;
            text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.2);
        """)
        layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Nhập mật khẩu của bạn")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 16px 18px;
                border: none;
                border-radius: 10px;
                font-size: 15px;
                background-color: rgba(255, 255, 255, 0.95);
                color: #2c3e50;
                min-height: 26px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            QLineEdit:focus {
                background-color: #ffffff;
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
            QLineEdit:hover {
                background-color: #ffffff;
            }
            QLineEdit::placeholder {
                color: rgba(44, 62, 80, 0.5);
            }
        """)
        self.password_input.returnPressed.connect(self.on_login)
        layout.addWidget(self.password_input)
        
        layout.addSpacing(15)
        
        # Remember me checkbox
        self.remember_checkbox = QCheckBox("Ghi nhớ đăng nhập")
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 14px;
                color: #ffffff;
                spacing: 10px;
                padding: 8px 0;
                font-weight: 500;
            }
            QCheckBox::indicator {
                width: 20px;
                height: 20px;
                border: 2px solid rgba(255, 255, 255, 0.7);
                border-radius: 5px;
                background-color: rgba(255, 255, 255, 0.2);
            }
            QCheckBox::indicator:checked {
                background-color: rgba(255, 255, 255, 0.9);
                border: 2px solid rgba(255, 255, 255, 1);
                image: url(none);
            }
            QCheckBox::indicator:hover {
                border: 2px solid rgba(255, 255, 255, 1);
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        layout.addWidget(self.remember_checkbox)
        
        layout.addSpacing(25)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        self.login_button = QPushButton("Đăng nhập")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #56CCF2,
                    stop:1 #2F80ED
                );
                color: white;
                padding: 16px 32px;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                min-height: 28px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }
            QPushButton:hover {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4BB8DD,
                    stop:1 #2868D8
                );
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
            }
            QPushButton:pressed {
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3FA4C9,
                    stop:1 #1E50BE
                );
                padding-top: 17px;
                padding-bottom: 15px;
            }
            QPushButton:disabled {
                background-color: rgba(189, 195, 199, 0.5);
            }
        """)
        self.login_button.clicked.connect(self.on_login)
        button_layout.addWidget(self.login_button)
        
        self.cancel_button = QPushButton("Hủy")
        self.cancel_button.setCursor(Qt.PointingHandCursor)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.25);
                color: white;
                padding: 16px 32px;
                border: 2px solid rgba(255, 255, 255, 0.4);
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
                min-height: 28px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.35);
                border: 2px solid rgba(255, 255, 255, 0.6);
            }
            QPushButton:pressed {
                background-color: rgba(255, 255, 255, 0.15);
                padding-top: 17px;
                padding-bottom: 15px;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        layout.addSpacing(10)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            color: #ffffff; 
            font-size: 14px;
            background-color: transparent;
            padding: 0px;
            min-height: 0px;
            border-radius: 8px;
            font-weight: 500;
        """)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setVisible(False)  # Ẩn khi chưa có message
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
    def on_login(self):
        """Handle login button click"""
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        
        # Validation
        if not username:
            self.status_label.setVisible(True)
            self.status_label.setText("⚠️ Vui lòng nhập username")
            self.status_label.setStyleSheet("""
                color: #ffffff; 
                font-size: 14px;
                background-color: rgba(231, 76, 60, 0.8);
                padding: 12px 16px;
                border-radius: 8px;
                min-height: 22px;
                font-weight: 500;
            """)
            self.username_input.setFocus()
            return
            
        if not password:
            self.status_label.setVisible(True)
            self.status_label.setText("⚠️ Vui lòng nhập password")
            self.status_label.setStyleSheet("""
                color: #ffffff; 
                font-size: 14px;
                background-color: rgba(231, 76, 60, 0.8);
                padding: 12px 16px;
                border-radius: 8px;
                min-height: 22px;
                font-weight: 500;
            """)
            self.password_input.setFocus()
            return
        
        # Disable inputs during authentication
        self.set_inputs_enabled(False)
        self.status_label.setVisible(True)
        self.status_label.setText("🔄 Đang xác thực...")
        self.status_label.setStyleSheet("""
            color: #ffffff; 
            font-size: 14px;
            background-color: rgba(52, 152, 219, 0.8);
            padding: 12px 16px;
            border-radius: 8px;
            min-height: 22px;
            font-weight: 500;
        """)
        
        # Authenticate
        try:
            self.api_client = WorkFlowAPIClient(self.server_url)
            
            if self.api_client.authenticate(username, password):
                # Success
                self.status_label.setVisible(True)
                self.status_label.setText("✅ Đăng nhập thành công!")
                self.status_label.setStyleSheet("""
                    color: #ffffff; 
                    font-size: 14px;
                    background-color: rgba(39, 174, 96, 0.9);
                    padding: 12px 16px;
                    border-radius: 8px;
                    min-height: 22px;
                    font-weight: 500;
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
                self.status_label.setVisible(True)
                self.status_label.setText("❌ Đăng nhập thất bại! Kiểm tra lại thông tin.")
                self.status_label.setStyleSheet("""
                    color: #ffffff; 
                    font-size: 14px;
                    background-color: rgba(231, 76, 60, 0.9);
                    padding: 12px 16px;
                    border-radius: 8px;
                    min-height: 22px;
                    font-weight: 500;
                """)
                self.set_inputs_enabled(True)
                self.password_input.clear()
                self.password_input.setFocus()
                
        except Exception as e:
            self.status_label.setVisible(True)
            self.status_label.setText(f"❌ Lỗi kết nối: {str(e)}")
            self.status_label.setStyleSheet("""
                color: #ffffff; 
                font-size: 14px;
                background-color: rgba(231, 76, 60, 0.9);
                padding: 12px 16px;
                border-radius: 8px;
                min-height: 22px;
                font-weight: 500;
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

