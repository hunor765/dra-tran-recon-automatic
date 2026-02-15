-- Audit logging for compliance
CREATE TABLE IF NOT EXISTS public.audit_logs (
    id SERIAL PRIMARY KEY,
    user_id UUID,
    user_email VARCHAR(255),
    action VARCHAR(50) NOT NULL, -- 'login', 'logout', 'job_triggered', 'config_updated', 'client_created', etc.
    resource_type VARCHAR(50), -- 'client', 'job', 'connector', 'user'
    resource_id INTEGER,
    details JSONB, -- Additional context
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for audit queries
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON public.audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_action ON public.audit_logs(action);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON public.audit_logs(resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_created_at ON public.audit_logs(created_at DESC);

-- RLS
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admins can view audit logs"
ON public.audit_logs FOR SELECT
USING (auth.jwt() ->> 'role' = 'admin');

CREATE POLICY "Users can view their own audit logs"
ON public.audit_logs FOR SELECT
USING (auth.uid() = user_id);
