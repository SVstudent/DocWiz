'use client';

import React from 'react';
import { CostDashboard } from './CostDashboard';
import { CostInfographic } from './CostInfographic';
import { useCostStore } from '@/store/costStore';

interface CostContainerProps {
  showInfographic?: boolean;
}

export const CostContainer: React.FC<CostContainerProps> = ({
  showInfographic = true,
}) => {
  const { currentCost, isLoading } = useCostStore();

  return (
    <div className="space-y-6">
      <CostDashboard
        costBreakdown={currentCost}
        isLoading={isLoading}
      />
      
      {showInfographic && currentCost && (
        <CostInfographic
          costBreakdownId={currentCost.id}
          format="png"
        />
      )}
    </div>
  );
};
