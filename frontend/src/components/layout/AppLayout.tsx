'use client';

import { ReactNode } from 'react';
import { Header } from './Header';
import { Breadcrumb } from './Breadcrumb';

interface AppLayoutProps {
  children: ReactNode;
  showBreadcrumb?: boolean;
  breadcrumbItems?: Array<{ label: string; href: string }>;
}

export function AppLayout({
  children,
  showBreadcrumb = false,
  breadcrumbItems,
}: AppLayoutProps) {
  return (
    <div className="min-h-screen bg-surgical-gray-50">
      <Header />
      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-6">
        {showBreadcrumb && (
          <div className="mb-4">
            <Breadcrumb items={breadcrumbItems} />
          </div>
        )}
        {children}
      </main>
    </div>
  );
}
