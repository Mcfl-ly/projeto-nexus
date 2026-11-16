BEGIN;
SET LOCAL lock_timeout = '3s';
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'email')
       AND NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'login') THEN
        ALTER TABLE users RENAME COLUMN email TO login;
    END IF;
END $$;
CREATE UNIQUE INDEX IF NOT EXISTS users_login_lower_unique ON users (lower(login));
COMMIT;
