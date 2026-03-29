import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import ComingSoon from '../components/ComingSoon';

// Mock framer-motion as it can be tricky in tests
import { vi } from 'vitest';
vi.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
  },
}));

describe('ComingSoon Component', () => {
  it('renders title and description correctly', () => {
    render(<ComingSoon title="Test Title" description="Test Description" />);
    
    expect(screen.getByText('Test Title')).toBeDefined();
    expect(screen.getByText('Test Description')).toBeDefined();
  });

  it('contains "In Development" badge', () => {
    render(<ComingSoon title="Any" description="Any" />);
    expect(screen.getByText('In Development')).toBeDefined();
  });
});
