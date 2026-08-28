import dotenv from 'dotenv';
dotenv.config({ path: '../.env.vercel' });
import Database from 'better-sqlite3';
import { createClient } from '@vercel/postgres';

async function sync() {
  const db = new Database('../analytics.db');
  console.log("Loading SQLite data...");
  const sqliteApps = db.prepare('SELECT * FROM app_analytics').all();
  const sqlitePosition = db.prepare('SELECT * FROM position_history').all();
  
  const connectionString = (process.env.POSTGRES_URL_NON_POOLING || process.env.POSTGRES_URL || '').replace('?channel_binding=require&', '?').replace('&channel_binding=require', '').replace('?channel_binding=require', '');
  const client = createClient({ connectionString });
  console.log("Connecting to Vercel Postgres...");
  await client.connect();

  console.log(`Syncing ${sqliteApps.length} app_analytics and ${sqlitePosition.length} position_history rows...`);

  // Clear Vercel DB in specific order to avoid FKs if they existed
  // Kill hanging backend connections that are locking our tables
  console.log("Terminating hanging connections...");
  await client.query(`SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE pid <> pg_backend_pid() AND datname = current_database();`).catch(e => console.log("Kill returned error (expected if permissions low):", e.message));

  console.log("Emptying vercel DB tables with TRUNCATE...");
  await client.query('TRUNCATE TABLE position_history, app_analytics');

  function chunkArray(array, size) {
    const chunked = [];
    for (let i = 0; i < array.length; i += size) {
      chunked.push(array.slice(i, i + size));
    }
    return chunked;
  }

  const appChunks = chunkArray(sqliteApps, 1000);
  console.log(`Inserting app_analytics in ${appChunks.length} chunks...`);
  for (const chunk of appChunks) {
    const values = chunk.map((_, i) => `($${i*12+1}, $${i*12+2}, $${i*12+3}, $${i*12+4}, $${i*12+5}, $${i*12+6}, $${i*12+7}, $${i*12+8}, $${i*12+9}, $${i*12+10}, $${i*12+11}, $${i*12+12})`).join(', ');
    const params = chunk.flatMap(r => [r.app_name, r.date, r.position, r.growth, r.revenue_ton, r.dau, r.organic_index, r.trend_score, r.ad_spend_est, r.market_sentiment, r.prediction_7d, r.is_mock]);
    await client.query(`INSERT INTO app_analytics (app_name, date, position, growth, revenue_ton, dau, organic_index, trend_score, ad_spend_est, market_sentiment, prediction_7d, is_mock) VALUES ${values}`, params);
    console.log(`Inserted chunk of app_analytics`);
  }

  const posChunks = chunkArray(sqlitePosition, 1000);
  console.log(`Inserting position_history in ${posChunks.length} chunks...`);
  for (const chunk of posChunks) {
    const values = chunk.map((_, i) => `($${i*5+1}, $${i*5+2}, $${i*5+3}, $${i*5+4}, $${i*5+5})`).join(', ');
    const params = chunk.flatMap(r => [r.app_name, r.date, r.position, r.category, r.description]);
    await client.query(`INSERT INTO position_history (app_name, date, position, category, description) VALUES ${values}`, params);
    console.log(`Inserted chunk of position_history`);
  }

  console.log("Done!");
  await client.end();
}

sync().catch(console.error);
