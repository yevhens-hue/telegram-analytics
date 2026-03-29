import { describe, it, expect, vi, beforeEach } from 'vitest';
import { THRESHOLDS } from '../lib/config';

describe('THRESHOLDS config', () => {
  it('has viral threshold higher than organic', () => {
    expect(THRESHOLDS.viral).toBeGreaterThan(THRESHOLDS.organic);
  });

  it('has sentiment high higher than medium', () => {
    expect(THRESHOLDS.sentiment.high).toBeGreaterThan(THRESHOLDS.sentiment.medium);
  });

  it('viral threshold is 75', () => {
    expect(THRESHOLDS.viral).toBe(75);
  });

  it('organic threshold is 45', () => {
    expect(THRESHOLDS.organic).toBe(45);
  });

  it('sentiment high is 70', () => {
    expect(THRESHOLDS.sentiment.high).toBe(70);
  });

  it('sentiment medium is 40', () => {
    expect(THRESHOLDS.sentiment.medium).toBe(40);
  });

  it('trendPositive is 0', () => {
    expect(THRESHOLDS.trendPositive).toBe(0);
  });

  it('revalidateSeconds is 3600', () => {
    expect(THRESHOLDS.revalidateSeconds).toBe(3600);
  });

  it('all thresholds are positive numbers', () => {
    expect(THRESHOLDS.viral).toBeGreaterThan(0);
    expect(THRESHOLDS.organic).toBeGreaterThan(0);
    expect(THRESHOLDS.sentiment.high).toBeGreaterThan(0);
    expect(THRESHOLDS.sentiment.medium).toBeGreaterThan(0);
    expect(THRESHOLDS.revalidateSeconds).toBeGreaterThan(0);
  });
});
