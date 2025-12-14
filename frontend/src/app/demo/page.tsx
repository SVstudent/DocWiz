'use client';

import { useState } from 'react';
import {
  Button,
  Input,
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  Modal,
  ToastContainer,
  Skeleton,
  SkeletonCard,
} from '@/components/ui';
import { useToast } from '@/hooks/useToast';

export default function DemoPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { toasts, success, error, warning, info } = useToast();

  return (
    <div className="min-h-screen bg-surgical-gray-50 p-8">
      <div className="mx-auto max-w-6xl space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-surgical-blue-600">
            DocWiz Design System
          </h1>
          <p className="mt-2 text-surgical-gray-600">
            Surgically effective components
          </p>
        </div>

        {/* Buttons */}
        <Card>
          <CardHeader>
            <CardTitle>Buttons</CardTitle>
            <CardDescription>
              Various button styles and states
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-4">
              <Button variant="primary">Primary</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="danger">Danger</Button>
              <Button variant="primary" size="sm">
                Small
              </Button>
              <Button variant="primary" size="lg">
                Large
              </Button>
              <Button variant="primary" disabled>
                Disabled
              </Button>
              <Button
                variant="primary"
                isLoading={isLoading}
                onClick={() => {
                  setIsLoading(true);
                  setTimeout(() => setIsLoading(false), 2000);
                }}
              >
                Click to Load
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Inputs */}
        <Card>
          <CardHeader>
            <CardTitle>Inputs</CardTitle>
            <CardDescription>Form input components</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Input
                label="Email"
                type="email"
                placeholder="Enter your email"
                helperText="We'll never share your email"
              />
              <Input
                label="Password"
                type="password"
                placeholder="Enter password"
                required
              />
              <Input
                label="Error Example"
                placeholder="This field has an error"
                error="This field is required"
              />
              <Input label="Disabled" placeholder="Disabled input" disabled />
            </div>
          </CardContent>
        </Card>

        {/* Cards */}
        <div className="grid gap-4 md:grid-cols-3">
          <Card variant="default">
            <CardHeader>
              <CardTitle>Default Card</CardTitle>
              <CardDescription>Standard card style</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-surgical-gray-700">
                This is a default card with border.
              </p>
            </CardContent>
          </Card>

          <Card variant="outlined">
            <CardHeader>
              <CardTitle>Outlined Card</CardTitle>
              <CardDescription>Thicker border</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-surgical-gray-700">
                This card has a thicker outline.
              </p>
            </CardContent>
          </Card>

          <Card variant="elevated">
            <CardHeader>
              <CardTitle>Elevated Card</CardTitle>
              <CardDescription>With shadow</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-surgical-gray-700">
                This card has a shadow effect.
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Modal */}
        <Card>
          <CardHeader>
            <CardTitle>Modal</CardTitle>
            <CardDescription>Dialog component</CardDescription>
          </CardHeader>
          <CardContent>
            <Button onClick={() => setIsModalOpen(true)}>Open Modal</Button>
          </CardContent>
        </Card>

        {/* Toasts */}
        <Card>
          <CardHeader>
            <CardTitle>Toast Notifications</CardTitle>
            <CardDescription>
              Temporary notification messages
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-4">
              <Button onClick={() => success('Operation successful!')}>
                Success Toast
              </Button>
              <Button
                variant="danger"
                onClick={() => error('Something went wrong!')}
              >
                Error Toast
              </Button>
              <Button
                variant="secondary"
                onClick={() => warning('Please be careful!')}
              >
                Warning Toast
              </Button>
              <Button
                variant="outline"
                onClick={() => info('Here is some information')}
              >
                Info Toast
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Skeletons */}
        <Card>
          <CardHeader>
            <CardTitle>Loading States</CardTitle>
            <CardDescription>Skeleton screens</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <Skeleton height={40} />
              <Skeleton height={100} width="80%" />
              <div className="grid gap-4 md:grid-cols-2">
                <SkeletonCard />
                <SkeletonCard />
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Example Modal"
        description="This is a modal dialog component"
        size="md"
      >
        <div className="space-y-4">
          <p className="text-surgical-gray-700">
            This is the modal content. You can put any content here.
          </p>
          <Input label="Name" placeholder="Enter your name" />
          <div className="flex justify-end gap-2">
            <Button variant="ghost" onClick={() => setIsModalOpen(false)}>
              Cancel
            </Button>
            <Button
              variant="primary"
              onClick={() => {
                success('Modal action completed!');
                setIsModalOpen(false);
              }}
            >
              Confirm
            </Button>
          </div>
        </div>
      </Modal>

      {/* Toast Container */}
      <ToastContainer toasts={toasts} />
    </div>
  );
}
