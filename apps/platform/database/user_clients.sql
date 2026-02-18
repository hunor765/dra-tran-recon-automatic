-- User-Client mapping for RBAC
CREATE TABLE IF NOT EXISTS public.user_clients (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    client_id INTEGER REFERENCES public.clients(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,  -- For pre-invite (before user exists)
    role VARCHAR(20) DEFAULT 'viewer', -- 'admin', 'viewer'
    status VARCHAR(20) DEFAULT 'invited', -- 'invited', 'active', 'inactive'
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, client_id),
    UNIQUE(email, client_id)
);

-- Index for quick lookups
CREATE INDEX IF NOT EXISTS idx_user_clients_user_id ON public.user_clients(user_id);
CREATE INDEX IF NOT EXISTS idx_user_clients_client_id ON public.user_clients(client_id);
CREATE INDEX IF NOT EXISTS idx_user_clients_email ON public.user_clients(email);

-- RLS Policy: Users can only see their own assignments
ALTER TABLE public.user_clients ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view their own assignments"
ON public.user_clients FOR SELECT
USING (auth.uid() = user_id);

CREATE POLICY "Admins can manage user_clients"
ON public.user_clients FOR ALL
USING (auth.jwt() ->> 'role' = 'admin');
