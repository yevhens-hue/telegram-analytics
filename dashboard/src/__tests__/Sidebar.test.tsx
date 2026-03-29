import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { usePathname } from 'next/navigation';
import Sidebar from '../components/Sidebar';

const mockUsePathname = vi.mocked(usePathname);

describe('Sidebar', () => {
  it('renders the brand name', () => {
    mockUsePathname.mockReturnValue('/');
    render(<Sidebar />);
    expect(screen.getByText('TMA Analytics')).toBeInTheDocument();
  });

  it('renders all main menu items', () => {
    mockUsePathname.mockReturnValue('/');
    render(<Sidebar />);
    expect(screen.getByText('Overview')).toBeInTheDocument();
    expect(screen.getByText('Top Charts')).toBeInTheDocument();
    expect(screen.getByText('Market Depth')).toBeInTheDocument();
    expect(screen.getByText('TON Indexer')).toBeInTheDocument();
  });

  it('renders all system menu items', () => {
    mockUsePathname.mockReturnValue('/');
    render(<Sidebar />);
    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(screen.getByText('Documentation')).toBeInTheDocument();
  });

  it('renders PRO Access section', () => {
    mockUsePathname.mockReturnValue('/');
    render(<Sidebar />);
    expect(screen.getByText('PRO Access')).toBeInTheDocument();
    expect(screen.getByText('Upgrade Now')).toBeInTheDocument();
  });

  it('highlights active Overview link on /', () => {
    mockUsePathname.mockReturnValue('/');
    render(<Sidebar />);
    const overviewLink = screen.getByText('Overview').closest('a');
    expect(overviewLink?.className).toContain('bg-indigo-500/10');
  });

  it('highlights active Top Charts link on /top-charts', () => {
    mockUsePathname.mockReturnValue('/top-charts');
    render(<Sidebar />);
    const link = screen.getByText('Top Charts').closest('a');
    expect(link?.className).toContain('bg-indigo-500/10');
  });

  it('coming soon items show Soon badge', () => {
    mockUsePathname.mockReturnValue('/');
    const { container } = render(<Sidebar />);
    const soonBadges = container.querySelectorAll('.uppercase.tracking-widest');
    const soonTexts = Array.from(soonBadges).filter(el => el.textContent === 'Soon');
    expect(soonTexts.length).toBe(3);
  });

  it('enabled items are links', () => {
    mockUsePathname.mockReturnValue('/');
    render(<Sidebar />);
    const overview = screen.getByText('Overview');
    expect(overview.closest('a')).not.toBeNull();
    const topCharts = screen.getByText('Top Charts');
    expect(topCharts.closest('a')).not.toBeNull();
    const tonIndexer = screen.getByText('TON Indexer');
    expect(tonIndexer.closest('a')).not.toBeNull();
  });

  it('renders correct href for all enabled items', () => {
    mockUsePathname.mockReturnValue('/');
    render(<Sidebar />);
    expect(screen.getByText('Overview').closest('a')?.getAttribute('href')).toBe('/');
    expect(screen.getByText('Top Charts').closest('a')?.getAttribute('href')).toBe('/top-charts');
    expect(screen.getByText('TON Indexer').closest('a')?.getAttribute('href')).toBe('/ton-indexer');
  });

  it('renders section labels', () => {
    mockUsePathname.mockReturnValue('/');
    render(<Sidebar />);
    expect(screen.getByText('Main Menu')).toBeInTheDocument();
    expect(screen.getByText('System')).toBeInTheDocument();
  });

  it('renders Zap icon in brand section', () => {
    mockUsePathname.mockReturnValue('/');
    const { container } = render(<Sidebar />);
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('sidebar has sticky positioning', () => {
    mockUsePathname.mockReturnValue('/');
    const { container } = render(<Sidebar />);
    const sidebar = container.firstChild as HTMLElement;
    expect(sidebar.className).toContain('sticky');
  });

  it('sidebar has correct width', () => {
    mockUsePathname.mockReturnValue('/');
    const { container } = render(<Sidebar />);
    const sidebar = container.firstChild as HTMLElement;
    expect(sidebar.className).toContain('w-64');
  });
});
