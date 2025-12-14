'use client';

import React from 'react';
import { ResultComparison } from './ResultComparison';
import { useVisualizationStore } from '@/store/visualizationStore';

interface ComparisonContainerProps {
  procedureName?: string;
  procedureDescription?: string;
}

export const ComparisonContainer: React.FC<ComparisonContainerProps> = ({
  procedureName,
  procedureDescription,
}) => {
  const { currentVisualization } = useVisualizationStore();

  return (
    <ResultComparison
      aiVisualizationUrl={currentVisualization?.after_image_url}
      procedureName={procedureName || 'Procedure'}
      procedureDescription={procedureDescription}
      beforeImageUrl={currentVisualization?.before_image_url}
    />
  );
};
