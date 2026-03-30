import { describe, it, expect, vi, beforeEach } from 'vitest';
import * as db from '../lib/db';

// Mocking @vercel/postgres for production cases
vi.mock('@vercel/postgres', () => ({
  sql: vi.fn(),
}));

// Mocking better-sqlite3 for local cases
vi.mock('better-sqlite3', () => {
    return {
        default: vi.fn().mockImplementation(() => ({
            prepare: vi.fn().mockReturnValue({
                all: vi.fn().mockReturnValue([]),
                get: vi.fn().mockReturnValue(null),
            }),
        })),
    };
});

describe('New DB Functions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('getLatestTonMetrics should return the latest TON price and volume', async () => {
    const metrics = await db.getLatestTonMetrics();
    expect(metrics).toBeDefined();
  });

  it('getNewsSentiment should return a list of news items', async () => {
    const news = await db.getNewsSentiment();
    expect(Array.isArray(news)).toBe(true);
  });

  it('getLatestAlerts should return recent system alerts', async () => {
    const alerts = await db.getLatestAlerts();
    expect(Array.isArray(alerts)).toBe(true);
  });
});
