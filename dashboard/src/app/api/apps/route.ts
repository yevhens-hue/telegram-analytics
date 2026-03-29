import { NextResponse } from 'next/server';
import { getTopApps } from '@/lib/db';

export async function GET() {
  try {
    const apps = await getTopApps();
    return NextResponse.json(apps);
  } catch (e) {
    console.error('API /api/apps failed:', e);
    return NextResponse.json({ error: 'Failed to fetch apps' }, { status: 500 });
  }
}
