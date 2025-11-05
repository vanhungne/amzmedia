# 🎛️ Admin Panel Setup & Integration Guide

## Overview

WorkFlow Admin Panel là hệ thống quản lý tập trung cho:
- **User Management**: Tạo, chỉnh sửa, xóa users (admin cấp tài khoản)
- **Project Management**: Quản lý projects với settings tự động
- **Centralized Database**: SQL Server lưu trữ users, projects, sessions
- **API Integration**: Python tool kết nối để load projects từ server

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    ADMIN PANEL (Next.js)                    │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐  │
│  │ Admin Login  │  │   Users     │  │    Projects      │  │
│  │   & Auth     │  │  Management │  │   Management     │  │
│  └──────────────┘  └─────────────┘  └──────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                      ┌────▼─────┐
                      │SQL Server│
                      │ Database │
                      └────▲─────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│              PYTHON TOOL (GenVideoPro.py)                   │
│  ┌──────────────┐  ┌─────────────┐  ┌──────────────────┐  │
│  │ User Login   │  │Load Projects│  │ Auto Workflow    │  │
│  │ via API      │  │ from Server │  │ Voice + Image    │  │
│  └──────────────┘  └─────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Setup Instructions

### 1. Install Dependencies

```bash
cd admin-panel
npm install
```

### 2. Configure Database

Create `.env` file:

```env
DB_USER=sa
DB_PASSWORD=YourPassword123
DB_SERVER=localhost
DB_NAME=WorkFlowAdmin
DB_ENCRYPT=false
DB_TRUST_CERT=true
JWT_SECRET=your-super-secret-jwt-key-change-this
NODE_ENV=development
```

### 3. Start SQL Server

Ensure SQL Server is running on your machine:
- Windows: SQL Server Management Studio
- Or use Docker:

```bash
docker run -e "ACCEPT_EULA=Y" -e "SA_PASSWORD=YourPassword123" \
   -p 1433:1433 --name sqlserver \
   -d mcr.microsoft.com/mssql/server:2022-latest
```

### 4. Run Admin Panel

```bash
npm run dev
```

Admin panel will be available at: **http://localhost:3000**

### 5. Initial Login

Default credentials:
- **Username**: `admin`
- **Password**: `admin123`

**⚠️ IMPORTANT: Change password immediately after first login!**

---

## 🔧 Database Schema

### Tables Created Automatically

#### `users` Table
```sql
CREATE TABLE [dbo].[users] (
  [id] INT IDENTITY(1,1) PRIMARY KEY,
  [username] NVARCHAR(100) NOT NULL UNIQUE,
  [email] NVARCHAR(255),
  [password_hash] NVARCHAR(255) NOT NULL,
  [role] NVARCHAR(20) NOT NULL DEFAULT 'user', -- 'admin' or 'user'
  [is_active] BIT NOT NULL DEFAULT 1,
  [created_at] DATETIME2 DEFAULT GETDATE(),
  [updated_at] DATETIME2 DEFAULT GETDATE()
);
```

#### `projects` Table
```sql
CREATE TABLE [dbo].[projects] (
  [id] INT IDENTITY(1,1) PRIMARY KEY,
  [project_id] NVARCHAR(50) NOT NULL UNIQUE, -- UUID
  [channel_name] NVARCHAR(255) NOT NULL,
  [script_template] NVARCHAR(MAX), -- Groq system prompt
  [num_prompts] INT DEFAULT 12,
  [voice_id] NVARCHAR(100), -- ElevenLabs voice ID
  [auto_workflow] BIT DEFAULT 1,
  [created_by] INT FOREIGN KEY REFERENCES [dbo].[users]([id]),
  [created_at] DATETIME2 DEFAULT GETDATE(),
  [updated_at] DATETIME2 DEFAULT GETDATE()
);
```

#### `sessions` Table
```sql
CREATE TABLE [dbo].[sessions] (
  [id] INT IDENTITY(1,1) PRIMARY KEY,
  [user_id] INT NOT NULL FOREIGN KEY REFERENCES [dbo].[users]([id]),
  [token] NVARCHAR(500) NOT NULL UNIQUE,
  [expires_at] DATETIME2 NOT NULL,
  [created_at] DATETIME2 DEFAULT GETDATE()
);
```

---

## 🎨 Admin Panel Features

### 1. Dashboard
- Overview statistics
- Total projects count
- Total users count
- System status

### 2. Projects Management
- **Create Project**: Tạo project với settings:
  - Channel Name
  - Script Template (Groq system prompt)
  - Number of Prompts
  - Voice ID (ElevenLabs)
  - Auto Workflow (on/off)
  
- **Edit Project**: Chỉnh sửa settings
- **Delete Project**: Xóa project
- **View All**: Danh sách projects với search/filter

### 3. Users Management
- **Create User**: Admin cấp tài khoản mới
  - Username
  - Password
  - Email (optional)
  - Role (admin/user)
  - Active status
  
- **Edit User**: Cập nhật thông tin, đổi password
- **Delete User**: Xóa user (không xóa được chính mình)
- **Toggle Active**: Bật/tắt khả năng đăng nhập

---

## 🔌 Python Tool Integration

### 1. Authentication

In Python tool (`GenVideoPro.py`):

```python
# Project tab has "🔐 Connect to Admin Panel" button
# User clicks -> login dialog appears
# Enter admin credentials -> authenticated
```

### 2. Load Projects from Server

```python
# After authentication, click "☁️ Load Projects from Server"
# Tool fetches all projects from admin panel
# Imports to local project manager
# Updates existing projects if already present
```

### 3. API Client Usage

Manual usage in Python:

```python
from tool_api_client import WorkFlowAPIClient

# Initialize
client = WorkFlowAPIClient("http://localhost:3000")

# Authenticate
if client.authenticate("admin", "admin123"):
    # Get all projects
    projects = client.get_projects()
    
    for project in projects:
        print(f"Channel: {project['channel_name']}")
        print(f"Voice ID: {project['voice_id']}")
        print(f"Template: {project['script_template']}")
```

---

## 📡 API Endpoints

### For Python Tool

#### `POST /api/tool/auth`
Authenticate user and get JWT token

**Request:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGci...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@workflow.com",
    "role": "admin"
  }
}
```

#### `GET /api/tool/projects`
Get all projects (requires authentication)

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "projects": [
    {
      "id": 1,
      "project_id": "uuid-here",
      "channel_name": "My Channel",
      "script_template": "GPT này chuyên...",
      "num_prompts": 12,
      "voice_id": "uju3wxzG5OhpWcoi3SMy",
      "auto_workflow": true
    }
  ]
}
```

---

## 🚀 Workflow Example

### Admin Creates Project

1. Admin logs into **http://localhost:3000**
2. Goes to **Projects** tab
3. Clicks **➕ Tạo Project Mới**
4. Fills in:
   - Channel Name: "Emotional Stories"
   - Script Template: (Groq prompt rules)
   - Num Prompts: 12
   - Voice ID: "uju3wxzG5OhpWcoi3SMy"
   - Auto Workflow: ✅
5. Click **Tạo Project**

### User Uses Project in Tool

1. User opens **GenVideoPro.py**
2. Goes to **📁 Projects** tab
3. Clicks **🔐 Connect to Admin Panel**
4. Enters login credentials
5. Clicks **☁️ Load Projects from Server**
6. Selects "Emotional Stories" project
7. Clicks **📜 Import Script**
8. Selects script.txt file
9. **100% automated**:
   - ✅ Groq generates prompts
   - ✅ ElevenLabs generates voice
   - ✅ Flux generates images
   - ✅ All saved to project folders

---

## 🔒 Security Notes

### Production Checklist

- [ ] Change default admin password
- [ ] Use strong JWT_SECRET (random 32+ chars)
- [ ] Enable SSL/TLS for database (`DB_ENCRYPT=true`)
- [ ] Use HTTPS for admin panel
- [ ] Set `NODE_ENV=production`
- [ ] Restrict database access to admin panel only
- [ ] Use environment variables for secrets
- [ ] Enable firewall rules for SQL Server port
- [ ] Regular database backups

### Password Requirements

- Minimum 8 characters
- Hash algorithm: bcrypt (cost factor 10)
- JWT expiration: 7 days (configurable)

---

## 🐛 Troubleshooting

### Database Connection Failed

**Problem**: Cannot connect to SQL Server

**Solutions**:
1. Check SQL Server is running
2. Verify credentials in `.env`
3. Check firewall allows port 1433
4. For Azure SQL, set `DB_ENCRYPT=true`
5. For local dev, set `DB_TRUST_CERT=true`

### Authentication Failed in Tool

**Problem**: Python tool cannot authenticate

**Solutions**:
1. Ensure admin panel is running (`npm run dev`)
2. Check URL is correct (`http://localhost:3000`)
3. Verify user exists and is active
4. Check console for error messages

### Projects Not Loading

**Problem**: "Load Projects from Server" fails

**Solutions**:
1. Authenticate first (click connect button)
2. Check admin panel has projects
3. Verify token is valid (re-authenticate)
4. Check network connection

---

## 📊 Monitoring

### Database Queries

Monitor slow queries in SQL Server Management Studio:

```sql
-- Check active sessions
SELECT * FROM [dbo].[sessions] 
WHERE [expires_at] > GETDATE();

-- Check user activity
SELECT 
  u.[username],
  COUNT(p.[id]) as project_count
FROM [dbo].[users] u
LEFT JOIN [dbo].[projects] p ON u.[id] = p.[created_by]
GROUP BY u.[username];
```

### API Logs

Check Next.js console for:
- Login attempts
- API errors
- Database connection status

---

## 📚 Additional Resources

- **Next.js Docs**: https://nextjs.org/docs
- **SQL Server Docs**: https://docs.microsoft.com/sql
- **JWT Guide**: https://jwt.io/introduction

---

## 🎯 Summary

✅ **Admin Panel**: Web interface for managing users & projects
✅ **SQL Server**: Centralized database
✅ **API Integration**: Python tool connects via REST API
✅ **Authentication**: JWT-based secure auth
✅ **Auto Workflow**: Projects loaded from server run automatically

**Result**: Centralized management + seamless tool integration!






