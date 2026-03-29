import { describe, it, expect } from 'vitest';
import { computeTrend, getTrafficLabel, getSentimentColor } from '../app/page';

describe('computeTrend', () => {
  it('returns positive trend with + sign', () => {
    expect(computeTrend(110, 100)).toBe('+10.0%');
  });

  it('returns negative trend with - sign', () => {
    expect(computeTrend(90, 100)).toBe('-10.0%');
  });

  it('returns zero trend when equal', () => {
    expect(computeTrend(100, 100)).toBe('+0.0%');
  });

  it('returns "+New" when previous is 0 and current > 0', () => {
    expect(computeTrend(100, 0)).toBe('+New');
  });

  it('returns "+0%" when both are 0', () => {
    expect(computeTrend(0, 0)).toBe('+0%');
  });

  it('handles large growth correctly', () => {
    expect(computeTrend(200, 100)).toBe('+100.0%');
  });

  it('handles decimal precision', () => {
    expect(computeTrend(103.33, 100)).toBe('+3.3%');
  });

  it('handles small values', () => {
    expect(computeTrend(1, 100)).toBe('-99.0%');
  });
});

describe('getTrafficLabel', () => {
  it('returns "Viral" for high organic index', () => {
    const result = getTrafficLabel(80);
    expect(result.label).toBe('Viral');
    expect(result.className).toContain('emerald');
  });

  it('returns "Viral" exactly at threshold boundary (76)', () => {
    const result = getTrafficLabel(76);
    expect(result.label).toBe('Viral');
  });

  it('returns "Organic" for mid-range organic index', () => {
    const result = getTrafficLabel(60);
    expect(result.label).toBe('Organic');
    expect(result.className).toContain('indigo');
  });

  it('returns "Organic" at exactly threshold boundary (46)', () => {
    const result = getTrafficLabel(46);
    expect(result.label).toBe('Organic');
  });

  it('returns "Paid Growth" for low organic index', () => {
    const result = getTrafficLabel(30);
    expect(result.label).toBe('Paid Growth');
    expect(result.className).toContain('amber');
  });

  it('returns "Paid Growth" at threshold boundary (45)', () => {
    const result = getTrafficLabel(45);
    expect(result.label).toBe('Paid Growth');
  });

  it('returns "Paid Growth" for zero', () => {
    const result = getTrafficLabel(0);
    expect(result.label).toBe('Paid Growth');
  });
});

describe('getSentimentColor', () => {
  it('returns emerald for high sentiment (>70)', () => {
    expect(getSentimentColor(75)).toBe('bg-emerald-500');
  });

  it('returns amber for medium sentiment (41-70)', () => {
    expect(getSentimentColor(50)).toBe('bg-amber-500');
  });

  it('returns red for low sentiment (<=40)', () => {
    expect(getSentimentColor(30)).toBe('bg-red-500');
  });

  it('returns amber at boundary (71)', () => {
    expect(getSentimentColor(71)).toBe('bg-emerald-500');
  });

  it('returns amber at exact boundary (41)', () => {
    expect(getSentimentColor(41)).toBe('bg-amber-500');
  });

  it('returns red at boundary (40)', () => {
    expect(getSentimentColor(40)).toBe('bg-red-500');
  });

  it('returns emerald at boundary (70)', () => {
    expect(getSentimentColor(70)).toBe('bg-amber-500');
  });
});
