import path from 'path';
import fs from 'fs';

const isProduction = !!process.env.POSTGRES_URL || !!process.env.VERCEL;

function resolveDbPath(): string {
  const envPath = process.env.ANALYTICS_DB;
  if (envPath && fs.existsSync(envPath)) return envPath;

  const candidates = [
    path.resolve(process.cwd(), '..', 'analytics.db'),
    path.resolve(process.cwd(), 'analytics.db'),
  ];

  for (const candidate of candidates) {
    if (fs.existsSync(candidate)) return candidate;
  }
  return path.resolve(process.cwd(), 'analytics.db');
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let _db: any = null;
function getSqlite() {
  if (!_db) {
    // eslint-disable-next-line @typescript-eslint/no-require-imports
    const Database = require('better-sqlite3');
    _db = new Database(resolveDbPath(), { readonly: true });
  }
  return _db;
}

export async function getTopApps() {
  try {
    if (isProduction) {
      const { sql } = await import('@vercel/postgres');
      const { rows } = await sql`
        SELECT a.app_name, p.category, MIN(a.position) as position, a.date,
               a.revenue_ton as daily_revenue_ton, a.dau as daily_active_wallets,
               a.growth, a.organic_index, a.trend_score,
               a.market_sentiment, a.prediction_7d
        FROM app_analytics a
        JOIN position_history p ON a.app_name = p.app_name AND a.date = p.date
        WHERE a.date = (SELECT MAX(date) FROM app_analytics)
        GROUP BY a.app_name, p.category, a.date, a.revenue_ton, a.dau, a.growth, a.organic_index, a.trend_score, a.market_sentiment, a.prediction_7d
        ORDER BY position ASC
        LIMIT 50
      `;
      return rows;
    }
    return getSqlite().prepare(`
      SELECT a.app_name, p.category, MIN(a.position) as position, a.date,
             a.revenue_ton as daily_revenue_ton, a.dau as daily_active_wallets,
             a.growth, a.organic_index, a.trend_score,
             a.market_sentiment, a.prediction_7d
      FROM app_analytics a
      JOIN position_history p ON a.app_name = p.app_name AND a.date = p.date
      WHERE a.date = (SELECT MAX(date) FROM app_analytics)
      GROUP BY a.app_name
      ORDER BY position ASC
      LIMIT 50
    `).all();
  } catch (e) {
    console.error('getTopApps failed:', e);
    return [];
  }
}

export async function getRevenueTrend() {
  try {
    if (isProduction) {
      const { sql } = await import('@vercel/postgres');
      const { rows } = await sql`
        SELECT date, sum(revenue_ton) as total_ton, sum(dau) as total_dau
        FROM app_analytics
        GROUP BY date
        ORDER BY date ASC
      `;
      return rows;
    }
    return getSqlite().prepare(`
      SELECT date, sum(revenue_ton) as total_ton, sum(dau) as total_dau
      FROM app_analytics
      GROUP BY date
      ORDER BY date ASC
    `).all();
  } catch (e) {
    console.error('getRevenueTrend failed:', e);
    return [];
  }
}
