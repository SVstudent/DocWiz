'use client';

import { QueryClientProvider } from '@tanstack/react-query';
import { ReactNode } from 'react';
import { queryClient } from '@/lib/query-client';
import { useTokenRefresh } from '@/hooks/useAuth';
import { ErrorBoundary } from '@/components/error';
import { ToastProvider } from '@/components/ui/ToastProvider';

interface ProvidersProps {
  children: ReactNode;
}

function AuthProvider({ children }: { children: ReactNode }) {
  // Automatically refresh token before expiration
  useTokenRefresh();
  return <>{children}</>;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ToastProvider>
          <AuthProvider>{children}</AuthProvider>
        </ToastProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
