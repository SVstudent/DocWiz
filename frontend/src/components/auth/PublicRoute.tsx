'use client';

import { useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';

interface PublicRouteProps {
  children: React.ReactNode;
  redirectTo?: string;
}

/**
 * Component that wraps public routes (login, register)
 * Redirects to home if user is already authenticated
 */
export function PublicRoute({
  children,
  redirectTo = '/',
}: PublicRouteProps) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, isLoading } = useAuthStore();

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      // Check if there's a return URL from the query params
      const returnUrl = searchParams.get('returnUrl');
      const destination = returnUrl || redirectTo;
      router.push(destination);
    }
  }, [isAuthenticated, isLoading, router, searchParams, redirectTo]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  // Don't render children if already authenticated
  if (isAuthenticated) {
    return null;
  }

  return <>{children}</>;
}
