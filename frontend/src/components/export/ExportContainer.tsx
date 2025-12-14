'use client';

import React from 'react';
import { ExportReport } from './ExportReport';
import { useAuthStore } from '@/store/authStore';

interface ExportContainerProps {
  visualizationIds?: string[];
  costBreakdownIds?: string[];
  comparisonIds?: string[];
}

export function ExportContainer({
  visualizationIds = [],
  costBreakdownIds = [],
  comparisonIds = [],
}: ExportContainerProps) {
  const { user } = useAuthStore();

  if (!user) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-600">Please log in to export reports.</p>
      </div>
    );
  }

  return (
    <ExportReport
      patientId={user.id}
      patientName={user.name || 'Patient'}
      visualizationIds={visualizationIds}
      costBreakdownIds={costBreakdownIds}
      comparisonIds={comparisonIds}
    />
  );
}
