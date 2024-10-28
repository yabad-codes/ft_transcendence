# ft_transcendence

A real-time multiplayer Pong game platform with user authentication, chat, and tournament features.

## 1. Project Overview

### 1.1 Description
ft_transcendence is a web application that modernizes the classic Pong game with multiplayer capabilities, user management, and social features. The project implements real-time gameplay, chat functionality, and tournament systems in a secure environment.

### 1.2 Main Features
- Real-time multiplayer Pong game
- User authentication with 42 OAuth and 2FA
- Live chat system with direct messaging
- Tournament management
- Player profiles and statistics
- Leaderboard system

### 1.3 Technology Stack
- **Frontend**: Vanilla JavaScript, HTML5, CSS3, Bootstrap 5.3
- **Backend**: Django, Gunicorn (HTTP), Daphne (WebSocket)
- **Database**: PostgreSQL
- **Authentication**: OAuth 2.0, JWT, 2FA
- **Real-time Communication**: WebSocket
- **Containerization**: Docker
- **Web Server**: Nginx
- **Cache**: Redis

## 2. Architecture

### 2.1 Three-Tier Architecture

| Tier | Components | Description |
|------|------------|-------------|
| Frontend | SPA, WebSocket Client | Single page application handling UI and real-time communication |
| Backend | Gunicorn, Daphne | HTTP server (Gunicorn), WebSocket server (Daphne), game logic, authentication |
| Database | PostgreSQL, Redis | Data persistence and caching |

### 2.2 Component Interaction
<img width="1282" alt="Screen Shot 2024-09-20 at 9 05 52 PM" src="https://github.com/user-attachments/assets/aff2dada-23e3-4e97-8c7b-75bf3eef2bd2">

## 3. Database Schema
![Untitled](https://github.com/user-attachments/assets/2f477f2f-282d-4516-923a-fc98c01ad335)

## 4. Frontend Implementation
### 4.1 SPA Architecture
The frontend implements a single-page application pattern using vanilla JavaScript with the following key features:
- Custom router handling browser history
- Component-based architecture
- Real-time WebSocket communication
- State management

### 4.2 Main Pages
- Home (`/`): Game lobby and matchmaking
- Profile (`/profile`): User statistics and settings
- Chat (`/chat`): Real-time messaging
- Tournament (`/tournament`): Tournament management
- Leaderboard (`/leaderboard`): Player rankings
- Settings (`/settings`): User preferences

### 4.3 Key Components
- `Navbar`: Navigation and user status
- `ChatMessage`: Message handling
- `GameScreen`: Real-time game interface
- `TournamentScreen`: Tournament brackets
- Error management system
- Notification system

## 5. Deployment Guide

### 5.1 Prerequisites
- Docker and Docker Compose
- NGINX
- Python 3.12+
- PostgreSQL 16
- Modern web browser (Chrome recommended)

### 5.2 Environment Configuration

1. Root `.env` file (copy from .env_example):
```bash
cp .env_example .env
```

Configuration includes database, Redis, and OAuth settings as shown in .env_example.

2. Backend Google Cloud Configuration:

To set up Google Cloud Storage for avatar handling:

a. Create a Google Cloud project and enable Cloud Storage

b. Create a service account and generate credentials:
   - Go to Google Cloud Console
   - Navigate to "IAM & Admin" > "Service Accounts"
   - Create a new service account
   - Grant necessary Storage permissions
   - Create and download the JSON key file

c. Set up the credentials:
```bash
# Rename and move the downloaded credentials file
mv path/to/downloaded/credentials.json backend/.env
```

**Important**: Never commit the `.env` file containing Google Cloud credentials to version control. The file should look similar to this structure (with your actual credentials):
```json
{
    "type": "service_account",
    "project_id": "your-project-id",
    "private_key_id": "your-private-key-id",
    "private_key": "your-private-key",
    "client_email": "your-service-account@project.iam.gserviceaccount.com",
    "client_id": "your-client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "your-client-cert-url",
    "universe_domain": "googleapis.com"
}
```

### 5.3 NGINX Configuration
The project uses NGINX as a reverse proxy to handle:
- Static file serving
- SSL termination
- Proxy requests to Gunicorn (HTTP) and Daphne (WebSocket)
- Load balancing

Key NGINX configuration is provided in `frontend/nginx/nginx.conf`.

### 5.4 Deployment Steps

1. Build and start containers:
```bash
docker-compose up --build
```

2. Verify deployment:
- Frontend: https://localhost:8081
- Backend API: https://localhost:8081/api/
- WebSocket: wss://localhost:8081/ws/

### 5.5 Important Notes

- The application uses self-signed SSL certificates for HTTPS
- Default ports can be modified in docker-compose.yml
- Database data is persisted in Docker volumes
- Gunicorn handles HTTP requests while Daphne manages WebSocket connections
- Make sure all required ports are available before deployment

### 5.6 Security Considerations

- All passwords are hashed using Django's password hasher
- HTTPS/WSS is required for all connections
- API routes are protected with authentication
- 2FA is available for additional security
- SQL injection protection is implemented
- XSS protection is enabled

For additional information or troubleshooting, please refer to the official documentation or create an issue in the repository.
