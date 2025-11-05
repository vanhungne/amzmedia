# WorkFlow Admin Panel

Admin panel for managing WorkFlow projects and users.

## Features

- ✅ Admin authentication with JWT
- ✅ User management (create, edit, delete users)
- ✅ Project management (CRUD operations)
- ✅ SQL Server database integration
- ✅ Modern UI with Tailwind CSS
- ✅ TypeScript for type safety

## Tech Stack

- **Frontend**: Next.js 14, React, TypeScript
- **Styling**: Tailwind CSS
- **Database**: SQL Server (MSSQL)
- **Authentication**: JWT with HTTP-only cookies
- **Icons**: Lucide React

## Setup Instructions

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Database

Create a `.env` file based on `.env.example`:

```bash
cp .env.example .env
```

Edit `.env` with your SQL Server credentials:

```env
DB_USER=sa
DB_PASSWORD=YourPassword123
DB_SERVER=localhost
DB_NAME=WorkFlowAdmin
DB_ENCRYPT=false
DB_TRUST_CERT=true
JWT_SECRET=your-super-secret-jwt-key
```

### 3. Database Will Auto-Initialize

The database tables will be created automatically on first API request:
- `users` table
- `projects` table  
- `sessions` table
- Default admin user (username: `admin`, password: `admin123`)

### 4. Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000)

### 5. Login

Default credentials:
- Username: `admin`
- Password: `admin123`

**⚠️ Change the default password immediately after first login!**

## Project Structure

```
admin-panel/
├── app/
│   ├── api/              # API routes
│   │   ├── auth/         # Authentication endpoints
│   │   ├── projects/     # Project CRUD
│   │   └── users/        # User CRUD
│   ├── dashboard/        # Admin pages
│   │   ├── projects/
│   │   └── users/
│   ├── login/            # Login page
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   └── Layout.tsx        # Dashboard layout
├── lib/
│   ├── api.ts           # API client functions
│   ├── auth.ts          # Auth utilities
│   ├── db.ts            # Database connection
│   └── middleware.ts    # API middleware
└── public/
```

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `POST /api/auth/me` - Get current user

### Projects
- `GET /api/projects` - List all projects
- `POST /api/projects` - Create project
- `GET /api/projects/[id]` - Get project
- `PUT /api/projects/[id]` - Update project
- `DELETE /api/projects/[id]` - Delete project

### Users
- `GET /api/users` - List all users
- `POST /api/users` - Create user
- `PUT /api/users/[id]` - Update user
- `DELETE /api/users/[id]` - Delete user

## Integration with Python Tool

The Python tool (GenVideoPro.py) can fetch projects from this admin panel:

```python
import requests

# First, authenticate to get token
auth_response = requests.post("http://localhost:3000/api/tool/auth", 
                             json={"username": "admin", "password": "admin123"})
token = auth_response.json()["token"]

# Get all projects with authentication
response = requests.get("http://localhost:3000/api/tool/projects", 
                       headers={"Authorization": f"Bearer {token}"})
projects = response.json()["projects"]

# Use in tool
for project in projects:
    print(f"Channel: {project['channel_name']}")
    print(f"Template: {project['script_template']}")
    print(f"Voice ID: {project['voice_id']}")
    print(f"Video Output: {project['video_output_folder']}")
```

## Security Notes

1. **Change default admin password** after first login
2. **Use strong JWT_SECRET** in production
3. **Enable SSL/TLS** for production database connections
4. **Use HTTPS** in production
5. **Validate all user inputs** (already implemented in API routes)

## Production Deployment

### Build for production:

```bash
npm run build
npm start
```

### Environment variables for production:

```env
NODE_ENV=production
DB_ENCRYPT=true
DB_TRUST_CERT=false
JWT_SECRET=<strong-random-secret>
```

## Troubleshooting

### Database Connection Issues

1. Ensure SQL Server is running
2. Check firewall settings
3. Verify credentials in `.env`
4. For Azure SQL, set `DB_ENCRYPT=true`

### Authentication Issues

1. Clear browser cookies
2. Check JWT_SECRET is consistent
3. Verify token expiration (default: 7 days)

## License

MIT






