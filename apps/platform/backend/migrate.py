import os
import psycopg2
from dotenv import load_dotenv

def run_migration():
    print("--- Running Migration ---")
    
    # Load env manually since we are running as a script
    load_dotenv(dotenv_path=".env")
    
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("Error: DATABASE_URL not found in .env")
        return

    # Convert asyncpg url to psycopg2 if needed
    if "+asyncpg" in db_url:
        db_url = db_url.replace("+asyncpg", "")
        
    print(f"Connecting to: {db_url.split('@')[1]}...") # Hide password in logs

    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cur = conn.cursor()
        
        # Read schema.sql
        schema_path = "../database/schema.sql"
        with open(schema_path, "r") as f:
            schema_sql = f.read()
            
        print("Applying schema...")
        cur.execute(schema_sql)
        
        print("✅ Schema applied successfully!")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")

if __name__ == "__main__":
    run_migration()
