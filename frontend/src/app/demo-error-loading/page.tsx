'use client';

import { useState } from 'react';
import {
  Spinner,
  PageSpinner,
  OverlaySpinner,
  InlineSpinner,
  ProgressBar,
  IndeterminateProgressBar,
  StepProgress,
  SkeletonCard,
  SkeletonText,
  SkeletonAvatar,
  Button,
  Card,
  CardHeader,
  CardTitle,
  CardContent,
  useToastContext,
  Step,
} from '@/components/ui';
import { SectionErrorBoundary } from '@/components/error';

// Component that throws an error for testing
function ErrorComponent(): never {
  throw new Error('This is a test error!');
}

export default function DemoPage() {
  const [showOverlay, setShowOverlay] = useState(false);
  const [showPageSpinner, setShowPageSpinner] = useState(false);
  const [progress, setProgress] = useState(45);
  const [showError, setShowError] = useState(false);
  const [currentStep, setCurrentStep] = useState(1);
  const toast = useToastContext();

  const steps: Step[] = [
    {
      label: 'Upload Photo',
      status: currentStep > 0 ? 'complete' : currentStep === 0 ? 'current' : 'upcoming',
    },
    {
      label: 'Select Procedure',
      status: currentStep > 1 ? 'complete' : currentStep === 1 ? 'current' : 'upcoming',
    },
    {
      label: 'Generate Preview',
      status: currentStep > 2 ? 'complete' : currentStep === 2 ? 'current' : 'upcoming',
    },
  ];

  if (showPageSpinner) {
    return <PageSpinner />;
  }

  return (
    <div className="min-h-screen bg-surgical-gray-50 p-8">
      <div className="mx-auto max-w-6xl space-y-8">
        <div>
          <h1 className="mb-2 text-3xl font-bold text-surgical-gray-900">
            Error Handling & Loading States Demo
          </h1>
          <p className="text-surgical-gray-600">
            Demonstration of all error handling and loading state components
          </p>
        </div>

        {/* Toast Notifications */}
        <Card>
          <CardHeader>
            <CardTitle>Toast Notifications</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-3">
              <Button
                onClick={() => toast.success('Operation completed successfully!')}
                variant="primary"
              >
                Success Toast
              </Button>
              <Button
                onClick={() => toast.error('Something went wrong. Please try again.')}
                variant="outline"
              >
                Error Toast
              </Button>
              <Button
                onClick={() => toast.warning('This action cannot be undone.')}
                variant="outline"
              >
                Warning Toast
              </Button>
              <Button
                onClick={() => toast.info('New features are now available!')}
                variant="outline"
              >
                Info Toast
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Spinners */}
        <Card>
          <CardHeader>
            <CardTitle>Spinners</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <h3 className="mb-3 text-sm font-semibold text-surgical-gray-700">
                  Sizes
                </h3>
                <div className="flex items-center gap-6">
                  <div className="text-center">
                    <Spinner size="sm" />
                    <p className="mt-2 text-xs text-surgical-gray-600">Small</p>
                  </div>
                  <div className="text-center">
                    <Spinner size="md" />
                    <p className="mt-2 text-xs text-surgical-gray-600">Medium</p>
                  </div>
                  <div className="text-center">
                    <Spinner size="lg" />
                    <p className="mt-2 text-xs text-surgical-gray-600">Large</p>
                  </div>
                  <div className="text-center">
                    <Spinner size="xl" />
                    <p className="mt-2 text-xs text-surgical-gray-600">Extra Large</p>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="mb-3 text-sm font-semibold text-surgical-gray-700">
                  Variants
                </h3>
                <div className="flex items-center gap-6">
                  <div className="text-center">
                    <Spinner variant="primary" />
                    <p className="mt-2 text-xs text-surgical-gray-600">Primary</p>
                  </div>
                  <div className="rounded bg-surgical-gray-800 p-4 text-center">
                    <Spinner variant="white" />
                    <p className="mt-2 text-xs text-white">White</p>
                  </div>
                  <div className="text-center">
                    <Spinner variant="gray" />
                    <p className="mt-2 text-xs text-surgical-gray-600">Gray</p>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="mb-3 text-sm font-semibold text-surgical-gray-700">
                  Specialized Spinners
                </h3>
                <div className="flex flex-wrap gap-3">
                  <Button onClick={() => setShowPageSpinner(true)} variant="outline">
                    Show Page Spinner
                  </Button>
                  <Button onClick={() => setShowOverlay(true)} variant="outline">
                    Show Overlay Spinner
                  </Button>
                  <Button variant="outline" disabled>
                    <InlineSpinner className="mr-2" />
                    Loading...
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Progress Bars */}
        <Card>
          <CardHeader>
            <CardTitle>Progress Bars</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <h3 className="mb-3 text-sm font-semibold text-surgical-gray-700">
                  Determinate Progress
                </h3>
                <div className="space-y-4">
                  <ProgressBar value={progress} showLabel label="Upload Progress" />
                  <div className="flex gap-2">
                    <Button
                      onClick={() => setProgress(Math.max(0, progress - 10))}
                      variant="outline"
                      size="sm"
                    >
                      -10%
                    </Button>
                    <Button
                      onClick={() => setProgress(Math.min(100, progress + 10))}
                      variant="outline"
                      size="sm"
                    >
                      +10%
                    </Button>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="mb-3 text-sm font-semibold text-surgical-gray-700">
                  Variants
                </h3>
                <div className="space-y-3">
                  <ProgressBar value={75} variant="primary" showLabel label="Primary" />
                  <ProgressBar value={60} variant="success" showLabel label="Success" />
                  <ProgressBar value={45} variant="warning" showLabel label="Warning" />
                  <ProgressBar value={30} variant="error" showLabel label="Error" />
                </div>
              </div>

              <div>
                <h3 className="mb-3 text-sm font-semibold text-surgical-gray-700">
                  Indeterminate Progress
                </h3>
                <IndeterminateProgressBar variant="primary" />
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Step Progress */}
        <Card>
          <CardHeader>
            <CardTitle>Step Progress</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <StepProgress steps={steps} />
              <div className="flex gap-2">
                <Button
                  onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
                  variant="outline"
                  disabled={currentStep === 0}
                >
                  Previous
                </Button>
                <Button
                  onClick={() => setCurrentStep(Math.min(2, currentStep + 1))}
                  variant="primary"
                  disabled={currentStep === 2}
                >
                  Next
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Skeleton Screens */}
        <Card>
          <CardHeader>
            <CardTitle>Skeleton Screens</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div>
                <h3 className="mb-3 text-sm font-semibold text-surgical-gray-700">
                  Skeleton Card
                </h3>
                <SkeletonCard />
              </div>

              <div>
                <h3 className="mb-3 text-sm font-semibold text-surgical-gray-700">
                  Skeleton Text
                </h3>
                <SkeletonText lines={4} />
              </div>

              <div>
                <h3 className="mb-3 text-sm font-semibold text-surgical-gray-700">
                  Skeleton Avatar
                </h3>
                <div className="flex items-center gap-4">
                  <SkeletonAvatar size={40} />
                  <SkeletonAvatar size={60} />
                  <SkeletonAvatar size={80} />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Error Boundary */}
        <Card>
          <CardHeader>
            <CardTitle>Error Boundary</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <p className="text-sm text-surgical-gray-600">
                Click the button below to trigger an error and see the error boundary in
                action.
              </p>
              <Button onClick={() => setShowError(true)} variant="outline">
                Trigger Error
              </Button>

              {showError && (
                <SectionErrorBoundary sectionName="Demo Section">
                  <ErrorComponent />
                </SectionErrorBoundary>
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Overlay Spinner */}
      {showOverlay && (
        <>
          <OverlaySpinner message="Processing your request..." />
          {setTimeout(() => {
            setShowOverlay(false);
            toast.success('Operation completed!');
          }, 3000) && null}
        </>
      )}

      {/* Auto-hide page spinner */}
      {showPageSpinner &&
        setTimeout(() => {
          setShowPageSpinner(false);
        }, 2000) &&
        null}
    </div>
  );
}
