-- Job schedules for automated reconciliation
CREATE TABLE IF NOT EXISTS public.schedules (
    id SERIAL PRIMARY KEY,
    client_id INTEGER NOT NULL REFERENCES public.clients(id) ON DELETE CASCADE,
    frequency VARCHAR(20) NOT NULL DEFAULT 'daily', -- 'hourly', 'daily', 'weekly', 'manual'
    time_of_day TIME,  -- For daily/weekly (e.g., '02:00:00')
    day_of_week INTEGER, -- 0-6 for weekly (0 = Sunday)
    timezone VARCHAR(50) DEFAULT 'UTC',
    is_active BOOLEAN DEFAULT TRUE,
    last_run_at TIMESTAMPTZ,
    next_run_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for scheduler queries
CREATE INDEX IF NOT EXISTS idx_schedules_next_run ON public.schedules(next_run_at) WHERE is_active = TRUE;
CREATE INDEX IF NOT EXISTS idx_schedules_client_id ON public.schedules(client_id);

-- RLS
ALTER TABLE public.schedules ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admins can manage schedules"
ON public.schedules FOR ALL
USING (auth.jwt() ->> 'role' = 'admin');
