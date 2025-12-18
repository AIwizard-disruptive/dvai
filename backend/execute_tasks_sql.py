#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import psycopg2

# Load environment variables
backend_path = Path(__file__).parent
load_dotenv(backend_path / '.env')

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL not found in .env")
    sys.exit(1)

# Read SQL file
sql_file = backend_path / 'migrations' / 'CREATE_TASKS_SERGE_WIZARD.sql'

with open(sql_file, 'r') as f:
    sql = f.read()

print("Executing SQL...")

# Connect and execute
conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

try:
    cur.execute(sql)
    conn.commit()
    print("✅ Tasks created successfully!")
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    cur.close()
    conn.close()


