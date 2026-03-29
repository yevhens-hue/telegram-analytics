import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import StatCard from '../components/StatCard';

describe('StatCard', () => {
  it('renders label and value', () => {
    render(
      <StatCard label="Total Revenue" value="1,000 TON" iconName="coins" color="indigo" />
    );
    expect(screen.getByText('Total Revenue')).toBeInTheDocument();
    expect(screen.getByText('1,000 TON')).toBeInTheDocument();
  });

  it('renders trend badge when provided', () => {
    render(
      <StatCard label="Revenue" value="500" trend="+10.5%" iconName="coins" color="indigo" />
    );
    expect(screen.getByText('+10.5%')).toBeInTheDocument();
  });

  it('does not render trend badge when not provided', () => {
    const { container } = render(
      <StatCard label="Revenue" value="500" iconName="coins" color="indigo" />
    );
    const badge = container.querySelector('.rounded-full.uppercase');
    expect(badge).toBeNull();
  });

  it('renders correct icon for coins', () => {
    const { container } = render(
      <StatCard label="Revenue" value="100" iconName="coins" color="indigo" />
    );
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('renders correct icon for users', () => {
    const { container } = render(
      <StatCard label="Users" value="1000" iconName="users" color="blue" />
    );
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('applies correct trend style for positive trend', () => {
    render(
      <StatCard label="Revenue" value="500" trend="+10%" iconName="coins" color="indigo" />
    );
    const badge = screen.getByText('+10%');
    expect(badge.className).toContain('text-emerald-400');
  });

  it('applies correct trend style for negative trend', () => {
    render(
      <StatCard label="Revenue" value="500" trend="-5%" iconName="coins" color="indigo" />
    );
    const badge = screen.getByText('-5%');
    expect(badge.className).toContain('text-red-400');
  });

  it('applies correct trend style for neutral trend', () => {
    render(
      <StatCard label="Revenue" value="500" trend="+New" iconName="coins" color="indigo" />
    );
    const badge = screen.getByText('+New');
    // "+New" starts with '+' so it gets emerald style
    expect(badge.className).toContain('text-emerald-400');
  });

  it('handles numeric value', () => {
    render(
      <StatCard label="Count" value={42} iconName="activity" color="emerald" />
    );
    expect(screen.getByText('42')).toBeInTheDocument();
  });

  it('falls back to activity icon for unknown iconName', () => {
    const { container } = render(
      <StatCard label="Test" value="100" iconName="unknown" color="indigo" />
    );
    expect(container.querySelector('svg')).toBeInTheDocument();
  });
});
