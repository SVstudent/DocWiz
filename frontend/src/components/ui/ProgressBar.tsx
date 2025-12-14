import { HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

export interface ProgressBarProps extends HTMLAttributes<HTMLDivElement> {
  value: number; // 0-100
  max?: number;
  variant?: 'primary' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
  label?: string;
}

export function ProgressBar({
  value,
  max = 100,
  variant = 'primary',
  size = 'md',
  showLabel = false,
  label,
  className,
  ...props
}: ProgressBarProps) {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);

  const sizes = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };

  const variants = {
    primary: 'bg-surgical-blue-600',
    success: 'bg-green-600',
    warning: 'bg-yellow-600',
    error: 'bg-red-600',
  };

  return (
    <div className={cn('w-full', className)} {...props}>
      {(showLabel || label) && (
        <div className="mb-2 flex items-center justify-between">
          <span className="text-sm font-medium text-surgical-gray-700">
            {label || 'Progress'}
          </span>
          <span className="text-sm font-medium text-surgical-gray-900">
            {Math.round(percentage)}%
          </span>
        </div>
      )}
      <div
        className={cn(
          'w-full overflow-hidden rounded-full bg-surgical-gray-200',
          sizes[size]
        )}
        role="progressbar"
        aria-valuenow={value}
        aria-valuemin={0}
        aria-valuemax={max}
      >
        <div
          className={cn(
            'h-full transition-all duration-300 ease-in-out',
            variants[variant]
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

// Indeterminate progress bar for unknown duration
export function IndeterminateProgressBar({
  variant = 'primary',
  size = 'md',
  className,
}: {
  variant?: 'primary' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
  className?: string;
}) {
  const sizes = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
  };

  const variants = {
    primary: 'bg-surgical-blue-600',
    success: 'bg-green-600',
    warning: 'bg-yellow-600',
    error: 'bg-red-600',
  };

  return (
    <div
      className={cn(
        'w-full overflow-hidden rounded-full bg-surgical-gray-200',
        sizes[size],
        className
      )}
      role="progressbar"
      aria-busy="true"
    >
      <div
        className={cn(
          'h-full w-1/3 animate-progress-indeterminate',
          variants[variant]
        )}
      />
    </div>
  );
}

// Step progress indicator
export interface Step {
  label: string;
  status: 'complete' | 'current' | 'upcoming';
}

export function StepProgress({
  steps,
  className,
}: {
  steps: Step[];
  className?: string;
}) {
  return (
    <nav aria-label="Progress" className={className}>
      <ol className="flex items-center">
        {steps.map((step, index) => (
          <li
            key={step.label}
            className={cn(
              'relative',
              index !== steps.length - 1 ? 'flex-1 pr-8' : ''
            )}
          >
            {/* Connector line */}
            {index !== steps.length - 1 && (
              <div
                className={cn(
                  'absolute left-4 top-4 -ml-px mt-0.5 h-0.5 w-full',
                  step.status === 'complete'
                    ? 'bg-surgical-blue-600'
                    : 'bg-surgical-gray-200'
                )}
                aria-hidden="true"
              />
            )}

            <div className="group relative flex items-start">
              <span className="flex h-9 items-center">
                {step.status === 'complete' ? (
                  <span className="relative z-10 flex h-8 w-8 items-center justify-center rounded-full bg-surgical-blue-600">
                    <svg
                      className="h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      viewBox="0 0 20 20"
                      fill="currentColor"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </span>
                ) : step.status === 'current' ? (
                  <span className="relative z-10 flex h-8 w-8 items-center justify-center rounded-full border-2 border-surgical-blue-600 bg-white">
                    <span className="h-2.5 w-2.5 rounded-full bg-surgical-blue-600" />
                  </span>
                ) : (
                  <span className="relative z-10 flex h-8 w-8 items-center justify-center rounded-full border-2 border-surgical-gray-300 bg-white">
                    <span className="h-2.5 w-2.5 rounded-full bg-transparent" />
                  </span>
                )}
              </span>
              <span className="ml-4 flex min-w-0 flex-col">
                <span
                  className={cn(
                    'text-sm font-medium',
                    step.status === 'complete' || step.status === 'current'
                      ? 'text-surgical-gray-900'
                      : 'text-surgical-gray-500'
                  )}
                >
                  {step.label}
                </span>
              </span>
            </div>
          </li>
        ))}
      </ol>
    </nav>
  );
}
