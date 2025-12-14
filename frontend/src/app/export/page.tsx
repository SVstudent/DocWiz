'use client';

import React from 'react';
import { ExportContainer } from '@/components/export';
import { AppLayout } from '@/components/layout';

export default function ExportPage() {
  return (
    <AppLayout showBreadcrumb>
      <div className="max-w-4xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Export Report</h1>
          <p className="text-gray-600 mt-2">
            Create a comprehensive report of your surgical analysis, cost estimates, and comparisons.
          </p>
        </div>

        <ExportContainer />
      </div>
    </AppLayout>
  );
}
