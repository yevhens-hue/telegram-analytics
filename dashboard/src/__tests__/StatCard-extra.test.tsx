import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import StatCard from '../components/StatCard';

// Re-mock framer-motion for these tests
vi.mock('framer-motion', () => {
  const React = require('react');
  const handler = {
    get: (_target: unknown, tag: string) => {
      return ({ children, initial: _i, animate: _a, transition: _t, whileHover: _w, style: _s, ...rest }: Record<string, unknown>) => {
        return React.createElement(tag, rest, children);
      };
    },
  };
  return {
    motion: new Proxy({}, handler),
  };
});

describe('StatCard additional edge cases', () => {
  it('renders with empty string value', () => {
    render(<StatCard label="Empty" value="" iconName="activity" color="indigo" />);
    expect(screen.getByText('Empty')).toBeInTheDocument();
  });

  it('renders with zero numeric value', () => {
    render(<StatCard label="Zero" value={0} iconName="activity" color="indigo" />);
    expect(screen.getByText('0')).toBeInTheDocument();
  });

  it('renders with very large number', () => {
    render(<StatCard label="Large" value={999999999} iconName="coins" color="indigo" />);
    expect(screen.getByText('999999999')).toBeInTheDocument();
  });

  it('renders with emerald color scheme', () => {
    const { container } = render(
      <StatCard label="Emerald" value="100" iconName="activity" color="emerald" />
    );
    expect(container.querySelector('.bg-emerald-500\\/10')).toBeInTheDocument();
  });

  it('renders with purple color scheme', () => {
    const { container } = render(
      <StatCard label="Purple" value="100" iconName="trophy" color="purple" />
    );
    expect(container.querySelector('.bg-purple-500\\/10')).toBeInTheDocument();
  });

  it('renders with blue color scheme', () => {
    const { container } = render(
      <StatCard label="Blue" value="100" iconName="users" color="blue" />
    );
    expect(container.querySelector('.bg-blue-500\\/10')).toBeInTheDocument();
  });

  it('renders trophy icon', () => {
    const { container } = render(
      <StatCard label="Trophy" value="1st" iconName="trophy" color="purple" />
    );
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('renders activity icon', () => {
    const { container } = render(
      <StatCard label="Activity" value="100" iconName="activity" color="emerald" />
    );
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('handles trend with "New" label', () => {
    render(
      <StatCard label="New" value="100" trend="+New" iconName="coins" color="indigo" />
    );
    expect(screen.getByText('+New')).toBeInTheDocument();
  });

  it('handles trend with zero percentage', () => {
    render(
      <StatCard label="Zero" value="100" trend="+0.0%" iconName="coins" color="indigo" />
    );
    expect(screen.getByText('+0.0%')).toBeInTheDocument();
  });

  it('applies glass-card class', () => {
    const { container } = render(
      <StatCard label="Test" value="100" iconName="coins" color="indigo" />
    );
    expect(container.querySelector('.glass-card')).toBeInTheDocument();
  });
});
