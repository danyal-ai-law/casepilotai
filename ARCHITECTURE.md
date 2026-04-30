# 🏗️ CasePilot AI - System Architecture

## System Overview

┌─────────────────────────────────────────┐ │ React Frontend (3000) │ └─────────────────────────────────────────┘ ↓ HTTPS/API ┌─────────────────────────────────────────┐ │ FastAPI Backend (8000) │ │ ├─ Auth Routes │ │ ├─ Case Routes │ │ ├─ Document Routes │ │ ├─ Research Routes │ │ └─ Admin Routes │ └─────────────────────────────────────────┘ ↓ ┌─────────────────────────────────────────┐ │ Data Layer │ │ ├─ PostgreSQL (5432) │ │ ├─ Redis Cache (6379) │ │ └─ RabbitMQ Queue (5672) │ └─────────────────────────────────────────┘

## Core Components

### 1. Authentication
- JWT tokens with expiration
- Role-based access (Lawyer, Admin)
- Password hashing with bcrypt

### 2. Case Memory Engine
- Independent case storage
- Per-case context persistence
- Case history tracking
- Never mix case data

### 3. Legal Document Generation
- Court-ready Pakistani documents
- Legal Notices, FIR Drafts, Bail Applications
- Written Statements, Appeals, Contracts
- AI-powered document creation

### 4. Legal Research Engine
- Pakistan law references (PPC, CrPC, CPC)
- Both-sided arguments
- Risk analysis
- Strategy recommendations

### 5. Admin Dashboard
- Global case control
- User management
- Analytics & reporting
- System configuration

## Database Tables

1. **users** - User accounts
2. **cases** - Case information
3. **case_memory** - Per-case context
4. **documents** - Generated documents
5. **legal_research** - Research queries
6. **ai_recommendations** - AI suggestions
7. **audit_logs** - System logs
8. **admin_settings** - Configuration
/api/v1/ ├─ /auth/login ├─ /auth/register ├─ /cases/ (CRUD) ├─ /documents/ (Generate, Download) ├─ /research/ (Legal Search) ├─ /recommendations/ (AI Suggestions) └─ /admin/ (System Control)
## API Routes



## Deployment

### Development
- Docker Compose (local)
- 7 services running

### Production
- Cloud provider (AWS/GCP/Azure)
- Multiple backend instances
- Managed PostgreSQL
- CDN for frontend
- Monitoring & logging

## Security

- JWT authentication
- Role-based access control
- Row-level security (case isolation)
- Audit logging
- Data encryption
- GDPR compliance
- 
