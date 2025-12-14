import { HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export interface SpinnerProps extends HTMLAttributes<HTMLDivElement> {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'primary' | 'white' | 'gray';
}

export function Spinner({
  size = 'md',
  variant = 'primary',
  className,
  ...props
}: SpinnerProps) {
  const sizes = {
    sm: 'h-4 w-4 border-2',
    md: 'h-8 w-8 border-2',
    lg: 'h-12 w-12 border-3',
    xl: 'h-16 w-16 border-4',
  };

  const variants = {
    primary: 'border-surgical-blue-200 border-t-surgical-blue-600',
    white: 'border-white/30 border-t-white',
    gray: 'border-surgical-gray-200 border-t-surgical-gray-600',
  };

  return (
    <div
      role="status"
      aria-label="Loading"
      className={cn('inline-block', className)}
      {...props}
    >
      <div
        className={cn(
          'animate-spin rounded-full',
          sizes[size],
          variants[variant]
        )}
      />
      <span className="sr-only">Loading...</span>
    </div>
  );
}

// Full page loading spinner
export function PageSpinner() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-surgical-gray-50">
      <div className="text-center">
        <Spinner size="xl" />
        <p className="mt-4 text-sm text-surgical-gray-600">Loading...</p>
      </div>
    </div>
  );
}

// Overlay spinner for blocking operations
export function OverlaySpinner({ message }: { message?: string }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm">
      <div className="rounded-lg bg-white p-8 shadow-xl">
        <div className="flex flex-col items-center gap-4">
          <Spinner size="lg" />
          {message && (
            <p className="text-sm font-medium text-surgical-gray-900">
              {message}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

// Inline spinner for buttons and small spaces
export function InlineSpinner({ className }: { className?: string }) {
  return (
    <Spinner
      size="sm"
      className={cn('inline-block', className)}
    />
  );
}
