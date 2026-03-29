import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import MarketDepth from '../app/market-depth/page';

// Mock DB functions
vi.mock('@/lib/db', () => ({
  getMarketDepth: vi.fn(async () => [
    { app_name: 'Test App', platform: 'Ads', estimated_budget: 1000, status: 'active' }
  ]),
  getSocialStats: vi.fn(async () => [
    { app_name: 'Test App', handle: 'test_handle', subscribers: 1000, avg_views: 500, err: 5.0 }
  ]),
}));

// Mock framer-motion client component as it can be tricky
vi.mock('framer-motion/client', () => ({
  div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  tr: ({ children, ...props }: any) => <tr {...props}>{children}</tr>,
}));

// Add sidebar mock
vi.mock('@/components/Sidebar', () => ({
  default: () => <div data-testid="sidebar">Sidebar</div>,
}));

describe('Market Depth Page', () => {
  it('renders market depth header and stats', async () => {
    // Resolve the async component
    const Page = await MarketDepth();
    render(Page);
    
    expect(screen.getByText('Market Depth')).toBeDefined();
    expect(screen.getAllByText('Test App')[0]).toBeDefined();
    expect(screen.getByText('$1,000')).toBeDefined();
    expect(screen.getByText('5.0%')).toBeDefined();
  });
});
