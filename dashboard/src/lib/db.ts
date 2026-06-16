import { Pool } from 'pg';

const isProduction = !!process.env.POSTGRES_URL || !!process.env.VERCEL;

// Production: Neon PostgreSQL via pg Pool
let _pool: Pool | null = null;
function getPool(): Pool {
  if (!_pool) {
    _pool = new Pool({
      connectionString: process.env.POSTGRES_URL,
      ssl: { rejectUnauthorized: false },
      max: 5,
    });
  }
  return _pool;
}

// eslint-disable-next-line @typescript-eslint/no-explicit-any
let _db: any = null;
function getSqlite() {
  if (isProduction) throw new Error('Cannot use sqlite in production');
  if (!_db) {
    const Database = eval("require('better-sqlite3')");
    _db = new Database((process.env.ANALYTICS_DB || process.cwd() + '/analytics.db'), { readonly: true });
  }
  return _db;
}

export async function getTopApps(limit = 1000) {
  try {
    if (isProduction) {
      const { rows } = await getPool().query(
        `SELECT a.app_name, p.category, MIN(a.position) as position, a.date,
               a.revenue_ton as daily_revenue_ton, a.dau as daily_active_wallets,
               a.growth, a.organic_index, a.trend_score,
               a.market_sentiment, a.prediction_7d
         FROM app_analytics a
         JOIN position_history p ON a.app_name = p.app_name AND a.date = p.date
         WHERE a.date = (SELECT MAX(date) FROM app_analytics)
         GROUP BY a.app_name, p.category, a.date, a.revenue_ton, a.dau, a.growth, a.organic_index, a.trend_score, a.market_sentiment, a.prediction_7d
         ORDER BY position ASC
         LIMIT $1`,
        [limit]
      );
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
      LIMIT ?
    `).all(limit);
  } catch (e) {
    console.error('getTopApps failed:', e);
    return [];
  }
}

export async function getAppDetail(appName: string) {
  try {
    if (isProduction) {
      const pool = getPool();
      const [analyticsRes, posHistoryRes, trendRes, tonRes, channelRes] = await Promise.all([
        pool.query(
          `SELECT a.*, p.category, p.description
           FROM app_analytics a
           LEFT JOIN position_history p ON a.app_name = p.app_name AND a.date = p.date
           WHERE a.app_name = $1
           ORDER BY a.date DESC LIMIT 1`,
          [appName]
        ),
        pool.query(
          `SELECT date, position FROM position_history WHERE app_name = $1 ORDER BY date DESC LIMIT 30`,
          [appName]
        ),
        pool.query(
          `SELECT date, revenue_ton, dau, trend_score, organic_index, market_sentiment FROM app_analytics WHERE app_name = $1 ORDER BY date DESC LIMIT 30`,
          [appName]
        ),
        pool.query(
          `SELECT contract_address, daily_revenue_ton, daily_active_wallets, date FROM ton_metrics WHERE app_id = $1 ORDER BY date DESC LIMIT 1`,
          [appName]
        ),
        pool.query(
          `SELECT handle, subscribers, avg_views, err, date FROM channel_stats WHERE app_name = $1 ORDER BY date DESC LIMIT 1`,
          [appName]
        ),
      ]);
      return {
        analytics: analyticsRes.rows[0] || null,
        positionHistory: posHistoryRes.rows,
        analyticsHistory: trendRes.rows,
        ton: tonRes.rows[0] || null,
        channel: channelRes.rows[0] || null,
      };
    }
    const db = getSqlite();
    const analytics = db.prepare(`
      SELECT a.*, p.category, p.description
      FROM app_analytics a
      LEFT JOIN position_history p ON a.app_name = p.app_name AND a.date = p.date
      WHERE a.app_name = ?
      ORDER BY a.date DESC LIMIT 1
    `).get(appName);
    const positionHistory = db.prepare(
      `SELECT date, position FROM position_history WHERE app_name = ? ORDER BY date DESC LIMIT 30`
    ).all(appName);
    const analyticsHistory = db.prepare(
      `SELECT date, revenue_ton, dau, trend_score, organic_index, market_sentiment FROM app_analytics WHERE app_name = ? ORDER BY date DESC LIMIT 30`
    ).all(appName);
    const ton = db.prepare(
      `SELECT contract_address, daily_revenue_ton, daily_active_wallets, date FROM ton_metrics WHERE app_id = ? ORDER BY date DESC LIMIT 1`
    ).get(appName);
    const channel = db.prepare(
      `SELECT handle, subscribers, avg_views, err, date FROM channel_stats WHERE app_name = ? ORDER BY date DESC LIMIT 1`
    ).get(appName);
    return { analytics, positionHistory, analyticsHistory, ton, channel };
  } catch (e) {
    console.error('getAppDetail failed:', e);
    return { analytics: null, positionHistory: [], analyticsHistory: [], ton: null, channel: null };
  }
}

export async function getRevenueTrend() {
  try {
    if (isProduction) {
      const { rows } = await getPool().query(
        `SELECT date, sum(revenue_ton) as total_ton, sum(dau) as total_dau
         FROM app_analytics
         GROUP BY date
         ORDER BY date ASC`
      );
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
      const { rows } = await getPool().query(
        `SELECT app_name, platform, estimated_budget, status, date
         FROM ad_campaigns
         WHERE date = (SELECT MAX(date) FROM ad_campaigns)
         ORDER BY estimated_budget DESC
         LIMIT 50`
      );
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
      const { rows } = await getPool().query(
        `SELECT app_name, handle, subscribers, avg_views, err, date
         FROM channel_stats
         WHERE date = (SELECT MAX(date) FROM channel_stats)
         ORDER BY subscribers DESC
         LIMIT 50`
      );
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
      const { rows } = await getPool().query(
        `SELECT price_usd, asset_id, date FROM market_data WHERE asset_id = 'TON' ORDER BY date DESC LIMIT 1`
      );
      return rows[0] || { price_usd: 1.23, asset_id: 'TON', date: new Date().toISOString().split('T')[0] };
    }
    const sqlite = getSqlite();
    const res = sqlite.prepare(`
      SELECT price_usd, asset_id, date FROM market_data WHERE asset_id = 'TON' ORDER BY date DESC LIMIT 1
    `).get();
    return res || { price_usd: 1.23, asset_id: 'TON', date: new Date().toISOString().split('T')[0] };
  } catch {
    return { price_usd: 1.23, asset_id: 'TON', date: new Date().toISOString().split('T')[0] };
  }
}

export async function getNewsSentiment() {
  try {
    if (isProduction) {
      const { rows } = await getPool().query(
        `SELECT app_name, content, sentiment_score, date FROM social_mentions ORDER BY date DESC LIMIT 20`
      );
      return rows;
    }
    return getSqlite().prepare(
      `SELECT app_name, content, sentiment_score, date FROM social_mentions ORDER BY date DESC LIMIT 20`
    ).all();
  } catch {
    return [];
  }
}

export async function getLatestAlerts() {
  try {
    if (isProduction) {
      const { rows } = await getPool().query(
        `SELECT app_name, message, status as severity, date FROM alert_history ORDER BY date DESC LIMIT 20`
      );
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      return rows.map((r: any) => ({
        ...r,
        severity: (r.severity && r.severity.includes(':')) ? r.severity.split(':')[1] : 'medium'
      }));
    }
    const rows = getSqlite().prepare(
      `SELECT app_name, message, status as severity, date FROM alert_history ORDER BY date DESC LIMIT 20`
    ).all();
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return rows.map((r: any) => ({
      ...r,
      severity: (r.severity && (r.severity as string).includes(':')) ? (r.severity as string).split(':')[1] : 'medium'
    }));
  } catch {
    return [];
  }
}
