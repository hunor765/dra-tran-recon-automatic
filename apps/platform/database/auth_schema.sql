-- Auth Schema for User-Client Search
-- 5. User Clients Mapping
CREATE TABLE IF NOT EXISTS public.user_clients (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    client_id INTEGER NOT NULL REFERENCES public.clients(id) ON DELETE CASCADE,
    role VARCHAR(50) DEFAULT 'viewer', -- 'admin', 'viewer'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure one email isn't mapped to the same client twice
    UNIQUE(email, client_id)
);

-- Index for lookup by email (Fast Login check)
CREATE INDEX IF NOT EXISTS idx_user_clients_email ON public.user_clients(email);

-- =============================================================================
-- RLS POLICIES - Enable Row Level Security on main tables
-- =============================================================================

-- Enable RLS on main tables
ALTER TABLE public.clients ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.connectors ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.jobs ENABLE ROW LEVEL SECURITY;

-- Drop existing policies if they exist (for idempotency)
DROP POLICY IF EXISTS "Admins can manage all clients" ON public.clients;
DROP POLICY IF EXISTS "Users can view their assigned client" ON public.clients;
DROP POLICY IF EXISTS "Admins can manage all connectors" ON public.connectors;
DROP POLICY IF EXISTS "Users can view their client connectors" ON public.connectors;
DROP POLICY IF EXISTS "Admins can manage all jobs" ON public.jobs;
DROP POLICY IF EXISTS "Users can view their client jobs" ON public.jobs;

-- Clients policies
CREATE POLICY "Admins can manage all clients"
ON public.clients FOR ALL
USING (auth.jwt() ->> 'role' = 'admin');

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

-- Connectors policies
CREATE POLICY "Admins can manage all connectors"
ON public.connectors FOR ALL
USING (auth.jwt() ->> 'role' = 'admin');

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

-- Jobs policies
CREATE POLICY "Admins can manage all jobs"
ON public.jobs FOR ALL
USING (auth.jwt() ->> 'role' = 'admin');

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
