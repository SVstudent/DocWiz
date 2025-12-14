'use client';

import React from 'react';
import { useSearchParams } from 'next/navigation';
import { InsuranceClaimContainer } from '@/components/insurance';
import { AppLayout } from '@/components/layout';
import { ProtectedRoute } from '@/components/auth';

export default function InsurancePage() {
  const searchParams = useSearchParams();
  const procedureId = searchParams.get('procedureId') || undefined;
  const costBreakdownId = searchParams.get('costBreakdownId') || undefined;

  return (
    <ProtectedRoute>
      <AppLayout showBreadcrumb>
        <div className="max-w-4xl mx-auto">
          <InsuranceClaimContainer
            procedureId={procedureId}
            costBreakdownId={costBreakdownId}
          />
        </div>
      </AppLayout>
    </ProtectedRoute>
  );
}
