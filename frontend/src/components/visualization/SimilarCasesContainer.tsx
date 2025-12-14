'use client';

import React from 'react';
import { SimilarCases, SimilarCasesFilters } from './SimilarCases';
import { useVisualization } from '@/hooks/useVisualization';

interface SimilarCasesContainerProps {
  visualizationId: string;
}

export const SimilarCasesContainer: React.FC<SimilarCasesContainerProps> = ({
  visualizationId,
}) => {
  const { getSimilarCases } = useVisualization();

  const handleFetchSimilarCases = async (
    vizId: string,
    filters?: SimilarCasesFilters
  ) => {
    return await getSimilarCases(vizId, filters);
  };

  return (
    <SimilarCases
      visualizationId={visualizationId}
      onFetchSimilarCases={handleFetchSimilarCases}
    />
  );
};
