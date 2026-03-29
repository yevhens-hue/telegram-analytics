import sqlite3
import os
import psycopg2
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load Vercel PostgreSQL configuration from .env.vercel
if os.path.exists(".env.vercel"):
    load_dotenv(".env.vercel")

POSTGRES_URL = os.environ.get("POSTGRES_URL")
SQLITE_DB = "analytics.db"

if not POSTGRES_URL:
    logger.error("POSTGRES_URL not found in environment!")
    exit(1)

def sync_table(sqlite_conn, pg_conn, table_name):
    logger.info(f"Syncing table: {table_name}")
    
    # Read from SQLite
    sc = sqlite_conn.cursor()
    sc.execute(f"SELECT * FROM {table_name}")
    rows = sc.fetchall()
    
    if not rows:
        logger.info(f"Table {table_name} is empty, skipping.")
        return
        
    # Get column names
    columns = [description[0] for description in sc.description]
    
    # Prepare Postgres insert
    pc = pg_conn.cursor()
    
    # On conflict handles app_analytics specifically
    if table_name == "app_analytics":
        placeholders = ", ".join(["%s"] * len(columns))
        col_str = ", ".join(columns)
        update_str = ", ".join([f"{c}=EXCLUDED.{c}" for c in columns if c != "id"])
        
        insert_query = f"""
            INSERT INTO {table_name} ({col_str})
            VALUES ({placeholders})
            ON CONFLICT (app_name, date) DO UPDATE SET {update_str}
        """
    else:
        placeholders = ", ".join(["%s"] * len(columns))
        col_str = ", ".join(columns)
        insert_query = f"INSERT INTO {table_name} ({col_str}) VALUES ({placeholders})"
        
    # Batch insert
    try:
        pc.executemany(insert_query, rows)
        pg_conn.commit()
        logger.info(f"Successfully synced {len(rows)} rows into {table_name}")
    except Exception as e:
        pg_conn.rollback()
        logger.error(f"Error syncing {table_name}: {e}")

def main():
    # 1. Initialize tables in Postgres if needed
    import db_utils
    db_utils.init_all_tables()
    
    # 2. Connect to both
    sqlite_conn = sqlite3.connect(SQLITE_DB)
    pg_conn = psycopg2.connect(POSTGRES_URL)
    
    tables = ["position_history", "ad_campaigns", "channel_stats", "ton_metrics", "app_analytics"]
    
    for table in tables:
        try:
            sync_table(sqlite_conn, pg_conn, table)
        except Exception as e:
            logger.error(f"Failed to sync {table}: {e}")
            
    sqlite_conn.close()
    pg_conn.close()
    logger.info("Sync completed.")

if __name__ == "__main__":
    main()
