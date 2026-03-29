import { NextResponse } from 'next/server';
import { getRevenueTrend } from '@/lib/db';

export async function GET() {
  try {
    const trend = await getRevenueTrend();
    return NextResponse.json(trend);
  } catch (e) {
    console.error('API /api/trend failed:', e);
    return NextResponse.json({ error: 'Failed to fetch trend data' }, { status: 500 });
  }
}
