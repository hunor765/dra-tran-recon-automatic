-- ============================================================
-- USER SETUP SCRIPT
-- Run this AFTER creating users in Supabase Auth dashboard
-- ============================================================

-- Step 1: Get the UUIDs of your created users
-- Run this query first to see the user IDs:
-- SELECT id, email FROM auth.users WHERE email IN ('admin@dra.com', 'client@example.com');

-- Step 2: Insert a test client (if not exists)
INSERT INTO public.clients (name, slug, is_active)
VALUES ('Test Store', 'test-store', true)
ON CONFLICT (slug) DO NOTHING;

-- Step 3: Get the client ID
-- SELECT id FROM public.clients WHERE slug = 'test-store';

-- Step 4: Link users to client
-- NOTE: Replace the UUIDs below with actual values from auth.users!

-- Admin user (replace 'ADMIN_UUID_HERE' with actual UUID from auth.users)
INSERT INTO public.user_clients (user_id, client_id, email, role, status)
VALUES (
    'ADMIN_UUID_HERE',  -- Get this from: SELECT id FROM auth.users WHERE email = 'admin@dra.com';
    (SELECT id FROM public.clients WHERE slug = 'test-store'),
    'admin@dra.com',
    'admin',
    'active'
)
ON CONFLICT (email, client_id) DO UPDATE 
SET user_id = EXCLUDED.user_id, role = 'admin', status = 'active';

-- Client user (replace 'CLIENT_UUID_HERE' with actual UUID from auth.users)
INSERT INTO public.user_clients (user_id, client_id, email, role, status)
VALUES (
    'CLIENT_UUID_HERE',  -- Get this from: SELECT id FROM auth.users WHERE email = 'client@example.com';
    (SELECT id FROM public.clients WHERE slug = 'test-store'),
    'client@example.com',
    'viewer',
    'active'
)
ON CONFLICT (email, client_id) DO UPDATE 
SET user_id = EXCLUDED.user_id, role = 'viewer', status = 'active';

-- ============================================================
-- VERIFICATION QUERIES
-- ============================================================

-- Check everything is set up correctly:
-- SELECT * FROM public.clients;
-- SELECT * FROM public.user_clients;
-- SELECT id, email, created_at FROM auth.users;

-- Combined view:
-- SELECT 
--     uc.email,
--     uc.role,
--     uc.status,
--     c.name as client_name,
--     c.slug as client_slug
-- FROM public.user_clients uc
-- JOIN public.clients c ON uc.client_id = c.id;
