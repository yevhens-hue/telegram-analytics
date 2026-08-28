import sqlite3
import os
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(name)s: %(message)s')
logger = logging.getLogger(__name__)

# Load Vercel PostgreSQL configuration from .env.vercel
if os.path.exists(".env.vercel"):
    load_dotenv(".env.vercel")

POSTGRES_URL = os.environ.get("POSTGRES_URL_NON_POOLING") or os.environ.get("POSTGRES_URL")
if POSTGRES_URL:
    POSTGRES_URL = POSTGRES_URL.replace("?channel_binding=require&", "?").replace("&channel_binding=require", "").replace("?channel_binding=require", "")

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
    
    col_str = ", ".join(columns)
    
    if table_name == "app_analytics":
        update_str = ", ".join([f"{c}=EXCLUDED.{c}" for c in columns if c != "id"])
        insert_query = f"""
            INSERT INTO {table_name} ({col_str})
            VALUES %s
            ON CONFLICT (app_name, date) DO UPDATE SET {update_str}
        """
    elif "id" in columns:
        update_str = ", ".join([f"{c}=EXCLUDED.{c}" for c in columns if c != "id"])
        insert_query = f"""
            INSERT INTO {table_name} ({col_str})
            VALUES %s
            ON CONFLICT (id) DO UPDATE SET {update_str}
        """
    else:
        insert_query = f"INSERT INTO {table_name} ({col_str}) VALUES %s"
        
    # Batch insert using execute_values
    try:
        batch_size = 1000
        for i in range(0, len(rows), batch_size):
            batch = rows[i : i + batch_size]
            execute_values(pc, insert_query, batch)
            pg_conn.commit()
            logger.info(f"  Synced {min(i + batch_size, len(rows))}/{len(rows)} rows into {table_name}")
        
        logger.info(f"Successfully synced {len(rows)} rows into {table_name}")
    except Exception as e:
        pg_conn.rollback()
        logger.error(f"Error syncing {table_name}: {e}")

def main():
    # 1. Initialize tables in Postgres if needed
    import db_utils
    db_utils.init_all_tables()
    
    # 2. Connect to both
    logger.info("Connecting to databases...")
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
