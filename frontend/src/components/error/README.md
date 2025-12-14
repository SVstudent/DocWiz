# Error Handling and Loading States

This directory contains components for error handling and loading states throughout the application.

## Error Boundary

The `ErrorBoundary` component catches JavaScript errors anywhere in the child component tree and displays a fallback UI.

### Usage

#### Global Error Boundary (Already configured in providers)

```tsx
import { ErrorBoundary } from '@/components/error';

<ErrorBoundary>
  <YourApp />
</ErrorBoundary>
```

#### Section-specific Error Boundary

```tsx
import { SectionErrorBoundary } from '@/components/error';

<SectionErrorBoundary sectionName="Cost Dashboard">
  <CostDashboard />
</SectionErrorBoundary>
```

#### Custom Fallback

```tsx
import { ErrorBoundary } from '@/components/error';

<ErrorBoundary
  fallback={(error, reset) => (
    <div>
      <h2>Custom Error UI</h2>
      <p>{error.message}</p>
      <button onClick={reset}>Try Again</button>
    </div>
  )}
  onError={(error, errorInfo) => {
    // Send to error tracking service
    console.error('Error:', error, errorInfo);
  }}
>
  <YourComponent />
</ErrorBoundary>
```

## Loading States

### Spinner

Use spinners for loading states.

```tsx
import { Spinner, PageSpinner, OverlaySpinner, InlineSpinner } from '@/components/ui';

// Small inline spinner
<InlineSpinner />

// Standard spinner
<Spinner size="md" variant="primary" />

// Full page loading
<PageSpinner />

// Blocking overlay
<OverlaySpinner message="Generating visualization..." />
```

### Skeleton Screens

Use skeleton screens for content loading.

```tsx
import { Skeleton, SkeletonText, SkeletonCard, SkeletonAvatar } from '@/components/ui';

// Basic skeleton
<Skeleton width={200} height={20} />

// Text skeleton
<SkeletonText lines={3} />

// Card skeleton
<SkeletonCard />

// Avatar skeleton
<SkeletonAvatar size={48} />
```

### Progress Bars

Use progress bars for operations with known progress.

```tsx
import { ProgressBar, IndeterminateProgressBar, StepProgress } from '@/components/ui';

// Determinate progress
<ProgressBar value={75} max={100} showLabel label="Uploading..." />

// Indeterminate progress
<IndeterminateProgressBar variant="primary" />

// Step progress
<StepProgress
  steps={[
    { label: 'Upload Photo', status: 'complete' },
    { label: 'Select Procedure', status: 'current' },
    { label: 'Generate Preview', status: 'upcoming' },
  ]}
/>
```

## Toast Notifications

Toast notifications are globally available through the `useToastContext` hook.

### Usage

```tsx
import { useToastContext } from '@/components/ui';

function MyComponent() {
  const toast = useToastContext();

  const handleSuccess = () => {
    toast.success('Operation completed successfully!');
  };

  const handleError = () => {
    toast.error('Something went wrong. Please try again.');
  };

  const handleWarning = () => {
    toast.warning('This action cannot be undone.', 7000); // Custom duration
  };

  const handleInfo = () => {
    toast.info('New features available!');
  };

  return (
    <div>
      <button onClick={handleSuccess}>Success</button>
      <button onClick={handleError}>Error</button>
      <button onClick={handleWarning}>Warning</button>
      <button onClick={handleInfo}>Info</button>
    </div>
  );
}
```

## Best Practices

### Error Boundaries

1. **Wrap at appropriate levels**: Use global error boundary for the entire app, and section-specific boundaries for independent features.
2. **Provide context**: Use the `sectionName` prop to help users understand what failed.
3. **Enable recovery**: Always provide a way to retry or navigate away.
4. **Log errors**: Use the `onError` callback to send errors to monitoring services like Sentry.

### Loading States

1. **Use skeleton screens for initial loads**: They provide better perceived performance than spinners.
2. **Use spinners for actions**: Button clicks, form submissions, etc.
3. **Use progress bars for long operations**: When you can track progress (uploads, AI generation).
4. **Provide feedback**: Always tell users what's happening ("Generating preview...", "Uploading image...").

### Toast Notifications

1. **Keep messages concise**: Users should understand at a glance.
2. **Use appropriate types**: Success for confirmations, error for failures, warning for cautions, info for updates.
3. **Don't overuse**: Too many toasts can be annoying.
4. **Auto-dismiss**: Let toasts disappear automatically (default 5 seconds).

## Examples

### Loading State with Error Handling

```tsx
import { useState } from 'react';
import { SectionErrorBoundary } from '@/components/error';
import { Spinner, SkeletonCard } from '@/components/ui';
import { useToastContext } from '@/components/ui';

function DataComponent() {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const toast = useToastContext();

  const fetchData = async () => {
    try {
      setIsLoading(true);
      const data = await api.getData();
      toast.success('Data loaded successfully!');
    } catch (err) {
      setError(err as Error);
      toast.error('Failed to load data');
    } finally {
      setIsLoading(false);
    }
  };

  if (error) throw error; // Let error boundary handle it

  if (isLoading) {
    return <SkeletonCard />;
  }

  return <div>Your content here</div>;
}

// Wrap with error boundary
export default function DataPage() {
  return (
    <SectionErrorBoundary sectionName="Data">
      <DataComponent />
    </SectionErrorBoundary>
  );
}
```

### Multi-step Process with Progress

```tsx
import { useState } from 'react';
import { StepProgress, ProgressBar, OverlaySpinner } from '@/components/ui';
import { useToastContext } from '@/components/ui';

function MultiStepProcess() {
  const [currentStep, setCurrentStep] = useState(0);
  const [progress, setProgress] = useState(0);
  const [isProcessing, setIsProcessing] = useState(false);
  const toast = useToastContext();

  const steps = [
    { label: 'Upload Photo', status: currentStep > 0 ? 'complete' : currentStep === 0 ? 'current' : 'upcoming' },
    { label: 'Select Procedure', status: currentStep > 1 ? 'complete' : currentStep === 1 ? 'current' : 'upcoming' },
    { label: 'Generate Preview', status: currentStep > 2 ? 'complete' : currentStep === 2 ? 'current' : 'upcoming' },
  ];

  const handleNext = async () => {
    setIsProcessing(true);
    try {
      // Simulate processing
      await processStep(currentStep);
      setCurrentStep(currentStep + 1);
      toast.success(`Step ${currentStep + 1} completed!`);
    } catch (err) {
      toast.error('Failed to complete step');
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div>
      <StepProgress steps={steps} className="mb-8" />
      
      {isProcessing && (
        <OverlaySpinner message={`Processing step ${currentStep + 1}...`} />
      )}

      {currentStep === 2 && (
        <ProgressBar
          value={progress}
          showLabel
          label="Generating visualization"
          variant="primary"
        />
      )}

      <button onClick={handleNext}>Next Step</button>
    </div>
  );
}
```
