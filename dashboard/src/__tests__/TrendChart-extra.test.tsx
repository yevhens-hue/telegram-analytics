import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import TrendChart from '../components/TrendChart';

// Mock recharts
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

describe('TrendChart additional edge cases', () => {
  it('renders single data point', () => {
    const singleData = [{ date: '2024-01-01', total_ton: 1000, total_dau: 5000 }];
    render(<TrendChart data={singleData} />);
    const chart = screen.getByTestId('area-chart');
    expect(chart.getAttribute('data-points')).toBe('1');
  });

  it('renders large dataset', () => {
    const largeData = Array.from({ length: 365 }, (_, i) => ({
      date: `2024-01-${String(i + 1).padStart(2, '0')}`,
      total_ton: Math.random() * 10000,
      total_dau: Math.random() * 50000,
    }));
    render(<TrendChart data={largeData} />);
    const chart = screen.getByTestId('area-chart');
    expect(chart.getAttribute('data-points')).toBe('365');
  });

  it('switches mode multiple times', () => {
    render(<TrendChart data={mockData} />);

    const usersBtn = screen.getByText('Users');
    const revenueBtn = screen.getByText('Revenue');

    fireEvent.click(usersBtn);
    expect(usersBtn.className).toContain('bg-indigo-600');

    fireEvent.click(revenueBtn);
    expect(revenueBtn.className).toContain('bg-indigo-600');

    fireEvent.click(usersBtn);
    expect(usersBtn.className).toContain('bg-indigo-600');
  });

  it('renders area chart component', () => {
    render(<TrendChart data={mockData} />);
    expect(screen.getByTestId('area-total_ton')).toBeInTheDocument();
  });

  it('switches to users mode shows correct area', () => {
    render(<TrendChart data={mockData} />);
    fireEvent.click(screen.getByText('Users'));
    expect(screen.getByTestId('area-total_dau')).toBeInTheDocument();
  });

  it('renders both toggle buttons', () => {
    render(<TrendChart data={mockData} />);
    const buttons = screen.getAllByRole('button');
    expect(buttons).toHaveLength(2);
  });

  it('renders x-axis and y-axis', () => {
    render(<TrendChart data={mockData} />);
    expect(screen.getByTestId('x-axis')).toBeInTheDocument();
    expect(screen.getByTestId('y-axis')).toBeInTheDocument();
  });

  it('renders cartesian grid', () => {
    render(<TrendChart data={mockData} />);
    expect(screen.getByTestId('grid')).toBeInTheDocument();
  });

  it('renders tooltip component', () => {
    render(<TrendChart data={mockData} />);
    expect(screen.getByTestId('tooltip')).toBeInTheDocument();
  });

  it('data with zero values renders correctly', () => {
    const zeroData = [
      { date: '2024-01-01', total_ton: 0, total_dau: 0 },
    ];
    render(<TrendChart data={zeroData} />);
    expect(screen.getByTestId('area-chart')).toBeInTheDocument();
  });

  it('revenue area has correct name attribute', () => {
    render(<TrendChart data={mockData} />);
    const area = screen.getByTestId('area-total_ton');
    expect(area.getAttribute('data-name')).toBe('Revenue');
  });

  it('users area has correct name attribute', () => {
    render(<TrendChart data={mockData} />);
    fireEvent.click(screen.getByText('Users'));
    const area = screen.getByTestId('area-total_dau');
    expect(area.getAttribute('data-name')).toBe('Wallets');
  });
});
