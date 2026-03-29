import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import TrendChart from '../components/TrendChart';

// Mock recharts to avoid canvas rendering issues
vi.mock('recharts', () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div data-testid="chart-container">{children}</div>,
  AreaChart: ({ children, data }: { children: React.ReactNode; data: unknown[] }) => (
    <div data-testid="area-chart" data-points={data.length}>{children}</div>
  ),
  Area: ({ dataKey, name }: { dataKey: string; name: string }) => (
    <div data-testid={`area-${dataKey}`} data-name={name} />
  ),
  XAxis: () => <div data-testid="x-axis" />,
  YAxis: () => <div data-testid="y-axis" />,
  Tooltip: () => <div data-testid="tooltip" />,
  CartesianGrid: () => <div data-testid="grid" />,
}));

const mockData = [
  { date: '2024-01-01', total_ton: 1000, total_dau: 5000 },
  { date: '2024-01-02', total_ton: 1500, total_dau: 6000 },
  { date: '2024-01-03', total_ton: 2000, total_dau: 7000 },
];

describe('TrendChart', () => {
  it('renders chart with data', () => {
    render(<TrendChart data={mockData} />);
    const chart = screen.getByTestId('area-chart');
    expect(chart).toBeInTheDocument();
    expect(chart.getAttribute('data-points')).toBe('3');
  });

  it('renders Revenue and Users buttons', () => {
    render(<TrendChart data={mockData} />);
    expect(screen.getByText('Revenue')).toBeInTheDocument();
    expect(screen.getByText('Users')).toBeInTheDocument();
  });

  it('starts in Revenue mode', () => {
    render(<TrendChart data={mockData} />);
    const revenueBtn = screen.getByText('Revenue');
    expect(revenueBtn.className).toContain('bg-indigo-600');
  });

  it('switches to Users mode on click', () => {
    render(<TrendChart data={mockData} />);
    const usersBtn = screen.getByText('Users');
    fireEvent.click(usersBtn);

    expect(usersBtn.className).toContain('bg-indigo-600');
    const revenueBtn = screen.getByText('Revenue');
    expect(revenueBtn.className).not.toContain('bg-indigo-600');
  });

  it('switches back to Revenue mode', () => {
    render(<TrendChart data={mockData} />);
    const usersBtn = screen.getByText('Users');
    fireEvent.click(usersBtn);
    const revenueBtn = screen.getByText('Revenue');
    fireEvent.click(revenueBtn);

    expect(revenueBtn.className).toContain('bg-indigo-600');
  });

  it('shows correct description for Revenue mode', () => {
    render(<TrendChart data={mockData} />);
    expect(screen.getByText('Aggregate network activity across tracked smart contracts')).toBeInTheDocument();
  });

  it('shows correct description for Users mode', () => {
    render(<TrendChart data={mockData} />);
    fireEvent.click(screen.getByText('Users'));
    expect(screen.getByText('Unique active wallets interacting with tracked contracts')).toBeInTheDocument();
  });

  it('renders with empty data', () => {
    render(<TrendChart data={[]} />);
    expect(screen.getByTestId('area-chart')).toBeInTheDocument();
  });

  it('renders chart heading', () => {
    render(<TrendChart data={mockData} />);
    expect(screen.getByText('Consolidated Growth')).toBeInTheDocument();
  });
});
