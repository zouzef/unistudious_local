# Local Server API

A Flask-based REST API server for managing attendance, sessions, devices, and physical infrastructure for an educational institution.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Server](#running-the-server)
- [API Documentation](#api-documentation)
- [Architecture](#architecture)
- [Technologies](#technologies)
- [Contributing](#contributing)

---

## 🎯 Overview

This server provides a comprehensive API for managing:

- **Attendance tracking** with face recognition integration
- **Session and calendar management**
- **Device management** (tablets and cameras)
- **User and group management**
- **Physical infrastructure** (rooms, locals/buildings)
- **Moderator dashboard** with statistics

The server integrates with an external face detection system (`academie_attendance_system`) for automated attendance verification.

---

## ✨ Features

### Core Features

- 🔐 **JWT Authentication** - Secure token-based authentication for users and devices
- 📊 **Attendance Management** - Mark, update, delete, and track attendance
- 📅 **Calendar & Sessions** - Manage academic sessions and schedules
- 👥 **User & Group Management** - Organize students into groups
- 🎥 **Device Management** - Track cameras and tablets
- 🏢 **Infrastructure Management** - Manage rooms and buildings
- 🤖 **Face Recognition Integration** - Automated attendance via face detection
- 📈 **Statistics & Reports** - Real-time attendance statistics
- 🔒 **SSL/HTTPS Support** - Secure communication

### Advanced Features

- **Audit Trail** - Track all attendance modifications
- **Group Assignment** - Automatic and manual group management
- **Unknown Face Handling** - Identify and associate unknown faces
- **Token Management** - Device and session token handling
- **Multi-timezone Support** - Tunisia timezone (UTC+1)

---

## 📁 Project Structure

```
server_local_api/
│
├── app.py                      # Main application entry point
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── cert.pem                    # SSL certificate
├── key.pem                     # SSL private key
├── README.md                   # This file
│
├── core/                       # Core functionality
│   ├── __init__.py
│   ├── auth.py                 # Authentication helpers (check_user, check_slc)
│   ├── database.py             # Database connection manager
│   └── middleware.py           # JWT middleware (@token_required)
│
├── api/                        # API endpoints (organized by domain)
│   │
│   ├── auth/                   # Authentication endpoints
│   │   ├── routes.py           # Login endpoints (user & device)
│   │   └── README.md           # Auth API documentation
│   │
│   ├── attendance/             # Attendance management
│   │   ├── routes.py           # 14 attendance endpoints
│   │   └── README.md           # Attendance API documentation
│   │
│   ├── calendar/               # Calendar & session scheduling
│   │   ├── routes.py           # 7 calendar endpoints
│   │   └── README.md           # Calendar API documentation
│   │
│   ├── devices/                # Device management (cameras & tablets)
│   │   ├── routes.py           # 6 device endpoints
│   │   └── README.md           # Devices API documentation
│   │
│   ├── moderator/              # Moderator dashboard
│   │   ├── routes.py           # 2 moderator endpoints
│   │   └── README.md           # Moderator API documentation
│   │
│   ├── presence/               # Face detection & unknown students
│   │   ├── routes.py           # 6 presence endpoints
│   │   └── README.md           # Presence API documentation
│   │
│   ├── sessions/               # Academic session management
│   │   ├── routes.py           # 1 session endpoint
│   │   └── README.md           # Sessions API documentation
│   │
│   ├── slc/                    # Physical infrastructure (rooms, locals)
│   │   ├── routes.py           # 3 infrastructure endpoints
│   │   └── README.md           # SLC API documentation
│   │
│   └── users/                  # User & group management
│       ├── routes.py           # 4 user endpoints
│       └── README.md           # Users API documentation
│
└── util/                       # Utility functions (future use)
    └── __init__.py
```

---

## 🔧 Installation

### Prerequisites

- **Python 3.10+**
- **MySQL 5.7+** or **MariaDB 10.3+**
- **SSL Certificates** (for HTTPS)

### Step 1: Clone Repository

```bash
git clone <repository_url>
cd server_local_api
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Dependencies Include:

- `Flask==3.0.0` - Web framework
- `PyJWT==2.8.0` - JWT authentication
- `mysql-connector-python==8.2.0` - MySQL database driver

---

## ⚙️ Configuration

### Database Configuration

Edit `config.py`:

```python
class Config:
    # Database Configuration
    DB_USER = "root"
    DB_PASSWORD = ""
    DB_HOST = "127.0.0.1"
    DB_PORT = 3306
    DB_NAME = "testing"
    DB_CHARSET = "utf8mb4"
    DB_CONNECT_TIMEOUT = 10

    # Security
    SECRET_KEY = "localhost123"  # Change in production!

    # Server Configuration
    SERVER_HOST = '0.0.0.0'
    SERVER_PORT = 5004
    DEBUG = True

    # SSL Configuration
    SSL_CERT = 'cert.pem'
    SSL_KEY = 'key.pem'
```

### Database Setup

1. Create database:

```sql
CREATE DATABASE testing CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

2. Import your database schema
3. Ensure tables exist: `user`, `attendance`, `session`, `tablet`, `camera`, `room`, `local`, etc.

---

## 🚀 Running the Server

### Development Mode

```bash
python app.py
```

The server will start on:

```
https://0.0.0.0:5004
```

### Production Mode

For production, use a production WSGI server like **Gunicorn**:

```bash
pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5004 \
    --certfile=cert.pem \
    --keyfile=key.pem \
    app:create_app()
```

### Access the Server

- **Local:** `https://localhost:5004`
- **Network:** `https://<your_ip>:5004`
- **Test:** `https://localhost:5004/` (should return "Local Server is running!")

---

## 📚 API Documentation

All endpoints are prefixed with `/scl`.

### Quick Links

| Module                   | Endpoints    | Documentation                                    |
| ------------------------ | ------------ | ------------------------------------------------ |
| **Authentication**       | 2 endpoints  | [auth/README.md](api/auth/README.md)             |
| **Attendance**           | 14 endpoints | [attendance/README.md](api/attendance/README.md) |
| **Calendar**             | 7 endpoints  | [calendar/README.md](api/calendar/README.md)     |
| **Devices**              | 6 endpoints  | [devices/README.md](api/devices/README.md)       |
| **Moderator**            | 2 endpoints  | [moderator/README.md](api/moderator/README.md)   |
| **Presence**             | 6 endpoints  | [presence/README.md](api/presence/README.md)     |
| **Sessions**             | 1 endpoint   | [sessions/README.md](api/sessions/README.md)     |
| **SLC (Infrastructure)** | 3 endpoints  | [slc/README.md](api/slc/README.md)               |
| **Users**                | 4 endpoints  | [users/README.md](api/users/README.md)           |

### Authentication Flow

1. **Login:**

```bash
POST /scl/login
Body: {"username": "user", "password": "pass"}
Response: {"token": "eyJhbGc..."}
```

2. **Use Token:**

```bash
GET /scl/get-all-room
Header: Authorization: Bearer eyJhbGc...
```

### Example Requests

**Get Today's Attendance:**

```bash
curl -X GET https://localhost:5004/scl/get-attendance/1 \
  -H "Authorization: Bearer <token>" \
  -k
```

**Mark Student Present:**

```bash
curl -X POST https://localhost:5004/scl/attendance-save-user \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"userId":123,"calendarId":456}' \
  -k
```

---

## 🏗️ Architecture

### Design Patterns

- **Blueprint Pattern** - Modular route organization
- **Factory Pattern** - Application factory in `create_app()`
- **Singleton Pattern** - Database connection management
- **Decorator Pattern** - JWT authentication middleware

### Database Architecture

```
┌─────────────┐
│   Account   │
└──────┬──────┘
       │
       ├──► Session ──► Groups ──► Users (Students)
       │                   │
       ├──► Local ──► Room ├──► Cameras
       │                   └──► Tablets
       │
       └──► Attendance ──► Audit Trail
```

### Key Tables

- **user** - User accounts (students, teachers, moderators)
- **session** - Academic sessions/courses
- **attendance** - Attendance records
- **relation_calander_group_session** - Calendar entries
- **relation_group_local_session** - Groups within sessions
- **relation_user_session** - User-to-session-to-group relationships
- **tablet** - Tablet devices
- **camera** - Camera devices
- **room** - Physical rooms
- **local** - Buildings/locations

---

## 🔐 Security

### Authentication

- **JWT Tokens** - Stateless authentication
- **Token Expiration** - Configurable (currently disabled for development)
- **Role-based Access** - Moderator role verification

### SSL/TLS

- HTTPS enforced with self-signed certificates (development)
- Use valid certificates in production

### Best Practices

- ✅ Password hashing (implement bcrypt/argon2)
- ✅ SQL injection prevention (parameterized queries)
- ✅ Input validation
- ❌ **TODO:** Rate limiting
- ❌ **TODO:** CORS configuration

---

## 🛠️ Technologies

### Backend

- **Flask 3.0.0** - Python web framework
- **Python 3.13** - Programming language
- **MySQL** - Relational database

### Authentication & Security

- **PyJWT 2.8.0** - JSON Web Tokens
- **SSL/TLS** - Encrypted communication

### External Integration

- **academie_attendance_system** - Face detection system
  - Located at: `../academie_attendance_system/`
  - Dataset: `dataset/session_{id}/face_crops/`
  - User faces: `user_students/{user_id}/`

---

## 📊 API Statistics

- **Total Endpoints:** 45+
- **Authentication Endpoints:** 2
- **Attendance Endpoints:** 14
- **Calendar Endpoints:** 7
- **Device Endpoints:** 6
- **Moderator Endpoints:** 2
- **Presence Endpoints:** 6
- **Session Endpoints:** 1
- **Infrastructure Endpoints:** 3
- **User Management Endpoints:** 4

---

## 🧪 Testing

### Manual Testing with API Dog/Postman

1. Import the collection (if available)
2. Set base URL: `https://localhost:5004`
3. Configure SSL certificate verification
4. Test authentication first
5. Use returned token for protected endpoints

### Test Checklist

- [ ] Login with valid credentials
- [ ] Login with invalid credentials (should fail)
- [ ] Get attendance without token (should fail)
- [ ] Get attendance with token (should succeed)
- [ ] Mark student present
- [ ] Update attendance note
- [ ] Get statistics
- [ ] Test device endpoints
- [ ] Test moderator authentication

---

## 🚨 Troubleshooting

### Common Issues

**1. SSL Certificate Error**

```
Solution: Accept self-signed certificate or disable SSL verification in testing
```

**2. Database Connection Failed**

```
Check config.py database credentials
Ensure MySQL is running
Verify database exists
```

**3. Token is Invalid**

```
Check SECRET_KEY matches between login and verification
Ensure token is sent in Authorization header
Format: "Bearer <token>"
```

**4. Module Not Found Error**

```
Ensure all __init__.py files exist in api folders
Clear __pycache__: rmdir /s /q __pycache__
```

**5. Port Already in Use**

```
Change SERVER_PORT in config.py
Or kill process using port 5004
```

---

## 📝 Development Guidelines

### Adding New Endpoints

1. **Choose the appropriate module** (attendance, calendar, etc.)
2. **Add route to `routes.py`** in that module
3. **Add `@token_required` decorator** if authentication needed
4. **Use `Database.execute_query()`** for database operations
5. **Update module's README.md** with new endpoint documentation
6. **Test thoroughly**

### Code Style

- Use **snake_case** for functions and variables
- Use **PascalCase** for classes
- Add docstrings to functions
- Keep functions focused (single responsibility)
- Use type hints where applicable

---

## 🔄 Changelog

### Version 2.0.0 (2026-01-20)

- ✅ Complete restructuring into modular architecture
- ✅ Separated 40+ endpoints into 9 logical modules
- ✅ Created centralized database management
- ✅ Added JWT middleware
- ✅ Comprehensive API documentation
- ✅ Improved error handling
- ✅ SSL/HTTPS support

### Version 1.0.0 (Previous)

- Initial monolithic structure
- Basic endpoints
- Direct MySQL connections

---

## 👥 Contributing

### Guidelines

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -m "Add new feature"`
6. Push: `git push origin feature/new-feature`
7. Create Pull Request

---

## 📄 License

[Your License Here]

---

## 📞 Contact & Support

- **Project Maintainer:** [Your Name]
- **Email:** [Your Email]
- **Documentation:** See individual API README files in each `api/` subfolder

---

## 🎯 Future Enhancements

- [ ] Rate limiting
- [ ] CORS configuration
- [ ] API versioning
- [ ] Automated testing suite
- [ ] Docker containerization
- [ ] CI/CD pipeline
- [ ] API documentation UI (Swagger/ReDoc)
- [ ] WebSocket support for real-time updates
- [ ] Caching layer (Redis)
- [ ] Logging system
- [ ] Password hashing (bcrypt)
- [ ] Email notifications
- [ ] Backup/restore utilities

---

## 🙏 Acknowledgments

- Flask framework
- MySQL database
- Face detection integration with academie_attendance_system

---

**Built with ❤️ for educational institutions**
