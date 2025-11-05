# WorkFlow Tool

WorkFlow - Công cụ tự động tạo video từ script với AI voice generation và image generation.

## 🚀 Features

- **AI Voice Generation**: Tích hợp ElevenLabs API cho voice synthesis
- **Image Generation**: Tạo hình ảnh tự động
- **Project Management**: Quản lý projects và scripts
- **Auto Workflow**: Tự động hóa quy trình tạo video
- **Admin Panel**: Web-based admin panel để quản lý users, projects, API keys
- **Device Lock**: Bảo mật đăng nhập theo thiết bị
- **Activity Logging**: Theo dõi hoạt động người dùng

## 📋 Requirements

### Python Dependencies
- Python 3.8+
- PySide6 (Qt for Python)
- requests
- cryptography

### Admin Panel
- Node.js 18+
- npm hoặc yarn

## 🛠️ Installation

### 1. Clone repository
```bash
git clone <your-repo-url>
cd WorkFlow
```

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Install Admin Panel dependencies
```bash
cd admin-panel
npm install
```

### 4. Setup Database
- Cấu hình SQL Server connection trong `admin-panel/lib/db.ts`
- Chạy admin panel để tự động tạo database schema

### 5. Configure
- Cấu hình server URL trong `login_dialog.py` (DEFAULT_SERVER_URL)
- Thiết lập environment variables cho admin panel nếu cần

## 🎯 Usage

### Run Admin Panel
```bash
cd admin-panel
npm run dev
```

### Run Python Tool
```bash
python GenVideoPro.py
```

## 📁 Project Structure

```
WorkFlow/
├── admin-panel/          # Next.js Admin Panel
│   ├── app/              # Next.js app directory
│   ├── components/        # React components
│   ├── lib/              # Utilities và database
│   └── public/           # Static assets
├── image/                # Image assets
├── GenVideoPro.py        # Main application
├── login_dialog.py        # Login dialog
├── tool_api_client.py    # API client
├── ElevenlabsV15.py       # ElevenLabs GUI
├── auto_workflow.py       # Auto workflow orchestrator
└── README.md             # This file
```

## 🔐 Security

- API keys được quản lý trên server, không lưu local
- Device lock để đảm bảo mỗi user chỉ đăng nhập trên 1 thiết bị
- Activity logging để theo dõi hoạt động

## 📝 License

Private - All rights reserved

## 👥 Contributors

WorkFlow Team

