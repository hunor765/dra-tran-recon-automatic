-- ============================================================
-- DRA PLATFORM - COMPLETE DATABASE SETUP (Safe Version)
-- Run this in Supabase SQL Editor to set up everything
-- ============================================================

-- ============================================================
-- 1. CORE TABLES (Business Entities)
-- ============================================================

-- Clients Table - Stores being monitored (NOT user accounts!)
CREATE TABLE IF NOT EXISTS public.clients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(255) NOT NULL UNIQUE,
    logo_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Connectors Table - API credentials for each client
CREATE TABLE IF NOT EXISTS public.connectors (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES public.clients(id) ON DELETE CASCADE,
    type VARCHAR(50) NOT NULL, -- 'ga4', 'woocommerce', 'shopify'
    config_json TEXT NOT NULL, -- Encrypted credentials
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Jobs Table - Reconciliation runs
CREATE TABLE IF NOT EXISTS public.jobs (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES public.clients(id) ON DELETE CASCADE,
    status VARCHAR(50) DEFAULT 'pending', -- 'pending', 'running', 'completed', 'failed'
    result_summary JSONB, -- Match rate, missing orders, etc.
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    logs TEXT
);

-- ============================================================
-- 2. USER-CLIENT MAPPING (RBAC)
-- ============================================================

-- First, create the table WITHOUT the foreign key constraint
-- The constraint will be added separately to avoid auth schema issues
CREATE TABLE IF NOT EXISTS public.user_clients (
    id SERIAL PRIMARY KEY,
    user_id UUID,  -- References auth.users(id) - added separately below
    client_id INTEGER REFERENCES public.clients(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,  -- For lookup before user registers
    role VARCHAR(20) DEFAULT 'viewer', -- 'admin', 'viewer'
    status VARCHAR(20) DEFAULT 'invited', -- 'invited', 'active', 'inactive'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, client_id),
    UNIQUE(email, client_id)
);

-- Add foreign key constraint separately (this might fail if auth schema not ready, but table will exist)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints 
        WHERE constraint_name = 'user_clients_user_id_fkey'
        AND table_name = 'user_clients'
    ) THEN
        ALTER TABLE public.user_clients 
        ADD CONSTRAINT user_clients_user_id_fkey 
        FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE;
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Could not add foreign key constraint to auth.users. This is OK - constraint will be handled by application.';
END $$;

-- ============================================================
-- 3. INDEXES FOR PERFORMANCE
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_clients_slug ON public.clients(slug);
CREATE INDEX IF NOT EXISTS idx_connectors_client_id ON public.connectors(client_id);
CREATE INDEX IF NOT EXISTS idx_jobs_client_id ON public.jobs(client_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON public.jobs(status);
CREATE INDEX IF NOT EXISTS idx_user_clients_user_id ON public.user_clients(user_id);
CREATE INDEX IF NOT EXISTS idx_user_clients_client_id ON public.user_clients(client_id);
CREATE INDEX IF NOT EXISTS idx_user_clients_email ON public.user_clients(email);

-- ============================================================
-- 4. ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================

-- Enable RLS
ALTER TABLE public.clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.connectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_clients ENABLE ROW LEVEL SECURITY;

-- Drop existing policies (for clean re-run)
DROP POLICY IF EXISTS "Admins can manage all clients" ON public.clients;
DROP POLICY IF EXISTS "Users can view their assigned client" ON public.clients;
DROP POLICY IF EXISTS "Admins can manage all connectors" ON public.connectors;
DROP POLICY IF EXISTS "Users can view their client connectors" ON public.connectors;
DROP POLICY IF EXISTS "Admins can manage all jobs" ON public.jobs;
DROP POLICY IF EXISTS "Users can view their client jobs" ON public.jobs;
DROP POLICY IF EXISTS "Users can view their own assignments" ON public.user_clients;
DROP POLICY IF EXISTS "Admins can manage user_clients" ON public.user_clients;

-- Admin policies (full access)
CREATE POLICY "Admins can manage all clients"
ON public.clients FOR ALL
USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Admins can manage all connectors"
ON public.connectors FOR ALL
USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Admins can manage all jobs"
ON public.jobs FOR ALL
USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Admins can manage user_clients"
ON public.user_clients FOR ALL
USING (auth.jwt() ->> 'role' = 'admin');

-- User policies (view only their assigned client)
CREATE POLICY "Users can view their assigned client"
ON public.clients FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.user_clients uc 
        WHERE uc.client_id = clients.id 
        AND uc.user_id = auth.uid()
        AND uc.status = 'active'
    )
);

CREATE POLICY "Users can view their client connectors"
ON public.connectors FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.user_clients uc 
        WHERE uc.client_id = connectors.client_id 
        AND uc.user_id = auth.uid()
        AND uc.status = 'active'
    )
);

CREATE POLICY "Users can view their client jobs"
ON public.jobs FOR SELECT
USING (
    EXISTS (
        SELECT 1 FROM public.user_clients uc 
        WHERE uc.client_id = jobs.client_id 
        AND uc.user_id = auth.uid()
        AND uc.status = 'active'
    )
);

CREATE POLICY "Users can view their own assignments"
ON public.user_clients FOR SELECT
USING (auth.uid() = user_id);

-- ============================================================
-- 5. INSERT SAMPLE DATA (Optional - for testing)
-- ============================================================

-- Create a test client (business entity)
INSERT INTO public.clients (name, slug, is_active)
VALUES ('Test Store', 'test-store', true)
ON CONFLICT (slug) DO NOTHING;

-- Note: Users must be created in Supabase Auth dashboard
-- Then linked to clients via user_clients table

-- ============================================================
-- DONE! Now create users in Supabase Auth dashboard
-- ============================================================
