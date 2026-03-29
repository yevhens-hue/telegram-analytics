import { render, screen, fireEvent, act } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Settings from '../app/settings/page';

// Mock sidebar
vi.mock('@/components/Sidebar', () => ({
  default: () => <div data-testid="sidebar">Sidebar</div>,
}));

describe('Settings Page', () => {
  it('renders initial profile tab', () => {
    render(<Settings />);
    expect(screen.getByText('Profile Overview')).toBeDefined();
    expect(screen.getByDisplayValue('Yevhen Developer')).toBeDefined();
  });

  it('switches to AI Models tab', () => {
    render(<Settings />);
    const aiTab = screen.getByText('AI Models');
    fireEvent.click(aiTab);
    expect(screen.getByText('AI Analytics Engine')).toBeDefined();
    expect(screen.getByText('Gemini 3 Pro')).toBeDefined();
  });

  it('handles Save Changes click', async () => {
    vi.useFakeTimers();
    render(<Settings />);
    const saveBtn = screen.getByText('Save Changes');
    fireEvent.click(saveBtn);
    expect(screen.getByText('Saving...')).toBeDefined();
    
    act(() => {
      vi.advanceTimersByTime(800);
    });
    
    expect(screen.queryByText('Saving...')).toBeNull();
    expect(screen.getByText('Save Changes')).toBeDefined();
    vi.useRealTimers();
  });
});
