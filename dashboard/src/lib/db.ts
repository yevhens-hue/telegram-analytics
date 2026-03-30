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

export async function getMarketDepth() {
  try {
    if (isProduction) {
      const { sql } = await import('@vercel/postgres');
      const { rows } = await sql`
        SELECT app_name, platform, estimated_budget, status, date
        FROM ad_campaigns
        WHERE date = (SELECT MAX(date) FROM ad_campaigns)
        ORDER BY estimated_budget DESC
        LIMIT 50
      `;
      return rows;
    }
    return getSqlite().prepare(`
      SELECT app_name, platform, estimated_budget, status, date
      FROM ad_campaigns
      WHERE date = (SELECT MAX(date) FROM ad_campaigns)
      ORDER BY estimated_budget DESC
      LIMIT 50
    `).all();
  } catch (e) {
    console.error('getMarketDepth failed:', e);
    return [];
  }
}

export async function getSocialStats() {
  try {
    if (isProduction) {
      const { sql } = await import('@vercel/postgres');
      const { rows } = await sql`
        SELECT app_name, handle, subscribers, avg_views, err, date
        FROM channel_stats
        WHERE date = (SELECT MAX(date) FROM channel_stats)
        ORDER BY subscribers DESC
        LIMIT 50
      `;
      return rows;
    }
    return getSqlite().prepare(`
      SELECT app_name, handle, subscribers, avg_views, err, date
      FROM channel_stats
      WHERE date = (SELECT MAX(date) FROM channel_stats)
      ORDER BY subscribers DESC
      LIMIT 50
    `).all();
  } catch (e) {
    console.error('getSocialStats failed:', e);
    return [];
  }
}


export async function getLatestTonMetrics() {
  try {
    if (isProduction) {
      const { sql } = await import('@vercel/postgres');
      try {
          const { rows } = await sql`
            SELECT price_usd, asset_id, date
            FROM market_data
            WHERE asset_id = 'TON'
            ORDER BY date DESC
            LIMIT 1
          `;
          return rows[0] || { price_usd: 1.23, asset_id: 'TON', date: new Date().toISOString().split('T')[0] };
      } catch (sqlError) {
          return { price_usd: 1.23, asset_id: 'TON', date: new Date().toISOString().split('T')[0] };
      }
    }
    const sqlite = getSqlite();
    const res = sqlite.prepare(`
      SELECT price_usd, asset_id, date
      FROM market_data
      WHERE asset_id = 'TON'
      ORDER BY date DESC
      LIMIT 1
    `).get();
    return res || { price_usd: 1.23, asset_id: 'TON', date: new Date().toISOString().split('T')[0] };
  } catch (e) {
    return { price_usd: 1.23, asset_id: 'TON', date: new Date().toISOString().split('T')[0] };
  }
}

export async function getNewsSentiment() {
  try {
    if (isProduction) {
      const { sql } = await import('@vercel/postgres');
      try {
          const { rows } = await sql`
            SELECT app_name, content, sentiment_score, date
            FROM social_mentions
            ORDER BY date DESC
            LIMIT 20
          `;
          return rows;
      } catch (sqlError) {
          return [];
      }
    }
    return getSqlite().prepare(`
      SELECT app_name, content, sentiment_score, date
      FROM social_mentions
      ORDER BY date DESC
      LIMIT 20
    `).all();
  } catch (e) {
    return [];
  }
}

export async function getLatestAlerts() {
  try {
    if (isProduction) {
      const { sql } = await import('@vercel/postgres');
      try {
          const { rows } = await sql`
            SELECT app_name, message, status as severity, date
            FROM alert_history
            ORDER BY date DESC
            LIMIT 20
          `;
          return rows.map((r: any) => ({
            ...r,
            severity: (r.severity && r.severity.includes(':')) ? r.severity.split(':')[1] : 'medium'
          }));
      } catch (sqlError) {
          return [];
      }
    }
    const rows = getSqlite().prepare(`
      SELECT app_name, message, status as severity, date
      FROM alert_history
      ORDER BY date DESC
      LIMIT 20
    `).all();
    return rows.map((r: any) => ({
        ...r,
        severity: (r.severity && (r.severity as string).includes(':')) ? (r.severity as string).split(':')[1] : 'medium'
      }));
  } catch (e) {
    return [];
  }
}
