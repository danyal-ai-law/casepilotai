# CasePilot AI - Database Schema

## Overview

PostgreSQL database schema for CasePilot AI, designed to support multi-user case management with persistent memory, audit logging, and document storage.

---

## Core Tables

### 1. `users` - User Management

Stores lawyer and admin user information.

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL CHECK (role IN ('lawyer', 'admin')),
    firm_id UUID REFERENCES law_firms(id),
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    phone VARCHAR(20),
    avatar_url TEXT,
    subscription_tier VARCHAR(50) DEFAULT 'free' CHECK (subscription_tier IN ('free', 'professional', 'enterprise')),
    subscription_expires_at TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    is_verified BOOLEAN DEFAULT false,
    last_login_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_firm_id ON users(firm_id);
```

### 2. `law_firms` - Law Firm Information

Stores information about law firms (multi-tenant support).

```sql
CREATE TABLE law_firms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    registration_number VARCHAR(255) UNIQUE,
    address TEXT,
    city VARCHAR(100),
    province VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Pakistan',
    phone VARCHAR(20),
    email VARCHAR(255),
    website VARCHAR(255),
    logo_url TEXT,
    subscription_tier VARCHAR(50) DEFAULT 'professional',
    max_users INT DEFAULT 5,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_law_firms_name ON law_firms(name);
```

### 3. `cases` - Case Management

Core table for storing case information.

```sql
CREATE TABLE cases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    firm_id UUID REFERENCES law_firms(id),
    case_name VARCHAR(255) NOT NULL,
    case_type VARCHAR(100) NOT NULL CHECK (case_type IN ('civil', 'criminal', 'family', 'constitutional', 'commercial', 'other')),
    case_number VARCHAR(255),
    court_name VARCHAR(255),
    jurisdiction VARCHAR(100),
    
    -- Client Information
    client_name VARCHAR(255),
    client_contact VARCHAR(255),
    client_email VARCHAR(255),
    client_details JSONB,
    
    -- Opposing Party
    opposing_party_name VARCHAR(255),
    opposing_party_counsel VARCHAR(255),
    opposing_party_details JSONB,
    
    -- Case Content
    facts TEXT,
    evidence JSONB,
    legal_issues JSONB,
    
    -- Case Status
    status VARCHAR(50) DEFAULT 'active' CHECK (status IN ('active', 'closed', 'pending', 'archived')),
    court_stage VARCHAR(100),
    next_hearing_date DATE,
    
    -- Strategic Information
    strategy_history JSONB,
    ai_recommendations JSONB,
    case_outcome TEXT,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    closed_at TIMESTAMP
);

CREATE INDEX idx_cases_user_id ON cases(user_id);
CREATE INDEX idx_cases_firm_id ON cases(firm_id);
CREATE INDEX idx_cases_case_type ON cases(case_type);
CREATE INDEX idx_cases_status ON cases(status);
CREATE INDEX idx_cases_created_at ON cases(created_at);
```

### 4. `case_memory` - Persistent Case Context

Stores case memory snapshots for context retrieval.

```sql
CREATE TABLE case_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    memory_type VARCHAR(100) NOT NULL CHECK (memory_type IN ('facts', 'strategy', 'legal_analysis', 'recommendation', 'document', 'custom')),
    content JSONB NOT NULL,
    context TEXT,
    embedding VECTOR(1536),  -- For semantic search (requires pgvector extension)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_case_memory_case_id ON case_memory(case_id);
CREATE INDEX idx_case_memory_type ON case_memory(memory_type);
```

### 5. `documents` - Generated Legal Documents

Stores AI-generated legal documents.

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- Document Details
    document_type VARCHAR(100) NOT NULL CHECK (document_type IN (
        'legal_notice', 'fir_draft', 'bail_application', 'written_statement',
        'appeal', 'contract', 'affidavit', 'legal_opinion', 'petition', 'other'
    )),
    title VARCHAR(255),
    
    -- Content
    content TEXT NOT NULL,
    formatted_content TEXT,
    html_content TEXT,
    
    -- File Storage
    file_path VARCHAR(255),
    file_url TEXT,
    file_size INT,
    mime_type VARCHAR(100),
    
    -- Status
    status VARCHAR(50) DEFAULT 'draft' CHECK (status IN ('draft', 'generated', 'reviewed', 'finalized', 'archived')),
    review_status VARCHAR(50),
    
    -- Metadata
    version INT DEFAULT 1,
    ai_model VARCHAR(100),
    ai_prompt TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_documents_case_id ON documents(case_id);
CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_status ON documents(status);
```

### 6. `legal_research` - Legal Research Records

Stores research queries and results.

```sql
CREATE TABLE legal_research (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id),
    
    -- Query
    query TEXT NOT NULL,
    query_type VARCHAR(100) CHECK (query_type IN ('statute', 'precedent', 'interpretation', 'general')),
    
    -- Results
    results JSONB,
    relevant_laws JSONB,
    precedents JSONB,
    
    -- Metadata
    source VARCHAR(255),
    is_saved BOOLEAN DEFAULT false,
    usefulness_rating INT CHECK (usefulness_rating >= 1 AND usefulness_rating <= 5),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_legal_research_case_id ON legal_research(case_id);
CREATE INDEX idx_legal_research_user_id ON legal_research(user_id);
```

### 7. `audit_logs` - Security & Compliance Logs

Comprehensive audit trail for all system actions.

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action VARCHAR(255) NOT NULL,
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    resource_name VARCHAR(255),
    
    -- Change Details
    changes JSONB,
    old_values JSONB,
    new_values JSONB,
    
    -- Context
    ip_address INET,
    user_agent TEXT,
    status VARCHAR(50),
    error_message TEXT,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource_type ON audit_logs(resource_type);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

### 8. `ai_recommendations` - AI Strategy Recommendations

Stores AI-generated legal recommendations.

```sql
CREATE TABLE ai_recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    case_id UUID NOT NULL REFERENCES cases(id) ON DELETE CASCADE,
    
    -- Recommendation
    title VARCHAR(255),
    description TEXT,
    recommendation_type VARCHAR(100) CHECK (recommendation_type IN (
        'strategy', 'risk_alert', 'precedent', 'legal_issue', 'procedural', 'other'
    )),
    priority VARCHAR(50) CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    
    -- Reasoning
    reasoning TEXT,
    supporting_evidence JSONB,
    
    -- User Feedback
    is_actionable BOOLEAN,
    user_feedback TEXT,
    implementation_status VARCHAR(50) DEFAULT 'pending',
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_ai_recommendations_case_id ON ai_recommendations(case_id);
CREATE INDEX idx_ai_recommendations_priority ON ai_recommendations(priority);
```

### 9. `admin_settings` - System Configuration

Stores admin-level system settings.

```sql
CREATE TABLE admin_settings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    setting_key VARCHAR(255) UNIQUE NOT NULL,
    setting_value JSONB,
    description TEXT,
    is_system BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_admin_settings_key ON admin_settings(setting_key);
```

### 10. `system_analytics` - Usage Analytics

Tracks system usage and analytics.

```sql
CREATE TABLE system_analytics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_type VARCHAR(100) NOT NULL,
    metric_key VARCHAR(255),
    metric_value INT,
    metric_data JSONB,
    
    date_recorded DATE DEFAULT CURRENT_DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_system_analytics_type ON system_analytics(metric_type);
CREATE INDEX idx_system_analytics_date ON system_analytics(date_recorded);
```

---

## Database Initialization

### Create Database

```sql
CREATE DATABASE casepilotai_db
    ENCODING 'UTF8'
    TEMPLATE template0;
```

### Enable Extensions

```sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
-- CREATE EXTENSION IF NOT EXISTS "vector";  -- For vector embeddings (optional)
```

### Run All Tables

Use Alembic migrations:

```bash
alembic upgrade head
```

---

## Relationships Diagram

```
users (1) ──── (M) cases
         ──── (M) documents
         ──── (M) legal_research
         ──── (M) audit_logs
         ──── (M) ai_recommendations

law_firms (1) ──── (M) users
           ──── (M) cases

cases (1) ──── (M) case_memory
      ──── (M) documents
      ──── (M) legal_research
      ──── (M) ai_recommendations
```

---

## Security Considerations

1. **Encryption**: Sensitive fields encrypted at application level
2. **Row-Level Security**: Implement RLS policies per tenant
3. **Audit Trail**: All changes logged in audit_logs
4. **Access Control**: Foreign keys prevent cross-user data access
5. **Soft Deletes**: Use `deleted_at` timestamp instead of hard deletes

---

## Performance Optimization

1. **Indexing**: Indexes on frequently queried columns
2. **Partitioning**: Partition `audit_logs` by date (future)
3. **Caching**: Redis for frequently accessed case data
4. **Materialized Views**: For analytics queries
5. **Connection Pooling**: PgBouncer for connection management

