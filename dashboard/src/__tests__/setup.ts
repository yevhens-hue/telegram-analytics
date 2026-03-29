import '@testing-library/jest-dom/vitest';
import { vi } from 'vitest';
import React from 'react';

vi.mock('next/navigation', () => ({
  usePathname: vi.fn(() => '/'),
  useRouter: vi.fn(() => ({ push: vi.fn() })),
}));

vi.mock('framer-motion', () => {
  const handler = {
    get: (_target: unknown, tag: string) => {
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      return ({ children, initial: _i, animate: _a, transition: _t, whileHover: _w, style: _s, ...rest }: Record<string, unknown>) => {
        return React.createElement(tag, rest, children);
      };
    },
  };
  return {
    motion: new Proxy({}, handler),
  };
});
