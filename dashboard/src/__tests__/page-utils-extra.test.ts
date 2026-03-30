import { describe, it, expect } from 'vitest';
import { computeTrend, getTrafficLabel, getSentimentColor } from '../lib/formatters';

describe('computeTrend additional edge cases', () => {
  it('handles very small previous value', () => {
    expect(computeTrend(2, 1)).toBe('+100.0%');
  });

  it('handles negative current value', () => {
    // When current < previous, should be negative
    expect(computeTrend(-10, 100)).toBe('-110.0%');
  });

  it('handles float values with many decimals', () => {
    const result = computeTrend(100.123456, 99.987654);
    expect(result).toMatch(/^\+0\.1%$/);
  });

  it('handles extremely large values', () => {
    expect(computeTrend(1000000, 500000)).toBe('+100.0%');
  });

  it('handles negative previous value', () => {
    // previous === 0 check only, negative previous is treated normally
    const result = computeTrend(50, -100);
    expect(result).toMatch(/^-150\.0%$/);
  });
});

describe('getTrafficLabel additional edge cases', () => {
  it('returns Viral for exactly 76', () => {
    const result = getTrafficLabel(76);
    expect(result.label).toBe('Viral');
  });

  it('returns Organic for exactly 46', () => {
    const result = getTrafficLabel(46);
    expect(result.label).toBe('Organic');
  });

  it('returns Paid Growth for exactly 45', () => {
    const result = getTrafficLabel(45);
    expect(result.label).toBe('Paid Growth');
  });

  it('returns Paid Growth for exactly 75', () => {
    // 75 is NOT > 75, so should be Organic (75 > 45)
    const result = getTrafficLabel(75);
    expect(result.label).toBe('Organic');
  });

  it('returns Viral for 100', () => {
    const result = getTrafficLabel(100);
    expect(result.label).toBe('Viral');
  });

  it('returns Paid Growth for negative value', () => {
    const result = getTrafficLabel(-10);
    expect(result.label).toBe('Paid Growth');
  });
});

describe('getSentimentColor additional edge cases', () => {
  it('returns emerald for exactly 71', () => {
    expect(getSentimentColor(71)).toBe('bg-emerald-500');
  });

  it('returns red for exactly 40', () => {
    expect(getSentimentColor(40)).toBe('bg-red-500');
  });

  it('returns emerald for 100', () => {
    expect(getSentimentColor(100)).toBe('bg-emerald-500');
  });

  it('returns red for 0', () => {
    expect(getSentimentColor(0)).toBe('bg-red-500');
  });

  it('returns amber for 55', () => {
    expect(getSentimentColor(55)).toBe('bg-amber-500');
  });
});
