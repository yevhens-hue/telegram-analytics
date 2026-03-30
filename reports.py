import logging
from datetime import datetime, timedelta
from db_utils import get_connection, get_placeholder

logger = logging.getLogger(__name__)

def generate_weekly_report():
    """Returns a simple text summary of apps with highest growth."""
    today = datetime.now().strftime("%Y-%m-%d")
    p = get_placeholder()
    
    with get_connection() as conn:
        c = conn.cursor()
        c.execute(f"SELECT app_name, growth FROM app_analytics WHERE date = {p} ORDER BY growth DESC", (today,))
        res = c.fetchall()
        
    if not res:
        return "No data for today's report."
        
    summary = [f"📊 Market Growth Leaders (Top 50 of {len(res)}) - " + today]
    for name, growth in res[:50]:
        summary.append(f"{name}: +{growth} positions")
        
    return "\n".join(summary)
