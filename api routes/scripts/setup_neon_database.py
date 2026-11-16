"""Initialize an empty Nexus database without inserting demonstration accounts."""
import os
from pathlib import Path
import psycopg2
from dotenv import load_dotenv

root = Path(__file__).resolve().parents[2]
load_dotenv(root / '.env.local')
load_dotenv(root / '.env')
url = os.getenv('DATABASE_URL_UNPOOLED')
if not url:
    raise SystemExit('DATABASE_URL_UNPOOLED is required for schema setup.')

try:
    with psycopg2.connect(url, connect_timeout=15, options='-c lock_timeout=5000 -c statement_timeout=30000') as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT tablename FROM pg_tables WHERE schemaname='public'")
            tables = {row[0] for row in cursor.fetchall()}
            expected = {'users', 'refreshtoken', 'userlibrary'}
            if tables:
                if not expected.issubset(tables):
                    raise SystemExit('Existing schema detected. Review versioned migrations before modifying it.')
                cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='users'")
                if 'login' not in {row[0] for row in cursor.fetchall()}:
                    raise SystemExit('Existing accounts require migration 004_users_login.sql; no changes made.')
                cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_schema='public' AND table_name='userlibrary'")
                if 'favorite' not in {row[0] for row in cursor.fetchall()}:
                    raise SystemExit('Existing library requires migration 003_library_favorites.sql; no changes made.')
                print('Existing Nexus schema detected; preserved without changes.')
            else:
                statements = (root / 'originais/sql_proj.psql').read_text(encoding='utf-8-sig').split(';')[:3]
                for statement in statements:
                    cursor.execute(statement)
                cursor.execute('CREATE UNIQUE INDEX users_login_lower_unique ON users (lower(login))')
                # Execute only index statements, retaining one atomic transaction.
                migration = (root / 'api routes/migrations/002_library_uniqueness.sql').read_text(encoding='utf-8')
                for statement in migration.split(';'):
                    cleaned = '\n'.join(line for line in statement.splitlines() if not line.lstrip().startswith('--')).strip()
                    if cleaned and cleaned not in {'BEGIN', 'COMMIT'}:
                        cursor.execute(cleaned)
                print('Created Nexus tables and uniqueness indexes; no example data inserted.')
except psycopg2.Error as error:
    print('Database setup failed: ' + type(error).__name__)
    raise SystemExit(1)
