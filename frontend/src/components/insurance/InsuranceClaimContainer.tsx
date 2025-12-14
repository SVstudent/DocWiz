'use client';

import React from 'react';
import { InsuranceClaim } from './InsuranceClaim';
import { useAuth } from '@/hooks/useAuth';

interface InsuranceClaimContainerProps {
  procedureId?: string;
  costBreakdownId?: string;
}

export const InsuranceClaimContainer: React.FC<InsuranceClaimContainerProps> = ({
  procedureId,
  costBreakdownId,
}) => {
  const { user } = useAuth();

  return (
    <InsuranceClaim
      procedureId={procedureId}
      patientId={user?.id}
      costBreakdownId={costBreakdownId}
    />
  );
};
