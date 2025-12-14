'use client';

import React, { useEffect, useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient, getErrorMessage } from '@/lib/api-client';
import { VisualizationResult } from '@/store/visualizationStore';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import { useToast } from '@/hooks/useToast';

interface SavedVisualizationsProps {
  patientId: string;
  onVisualizationSelect?: (visualization: VisualizationResult) => void;
}

export const SavedVisualizations: React.FC<SavedVisualizationsProps> = ({
  patientId,
  onVisualizationSelect,
}) => {
  const toast = useToast();
  const [selectedId, setSelectedId] = useState<string | null>(null);

  // Fetch saved visualizations
  const { data: visualizations, isLoading, error, refetch } = useQuery({
    queryKey: ['saved-visualizations', patientId],
    queryFn: async () => {
      const response = await apiClient.get<VisualizationResult[]>(
        `/api/profiles/${patientId}/visualizations`
      );
      return response.data;
    },
    enabled: !!patientId,
  });

  useEffect(() => {
    if (error) {
      toast.error(`Failed to load visualizations: ${getErrorMessage(error)}`);
    }
  }, [error]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleVisualizationClick = (visualization: VisualizationResult) => {
    setSelectedId(visualization.id);
    if (onVisualizationSelect) {
      onVisualizationSelect(visualization);
    }
  };

  const handleDelete = async (visualizationId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    
    if (!window.confirm('Are you sure you want to delete this visualization?')) {
      return;
    }

    try {
      await apiClient.delete(`/api/visualizations/${visualizationId}`);
      toast.success('Visualization deleted successfully');
      refetch();
    } catch (error) {
      toast.error(`Failed to delete visualization: ${getErrorMessage(error)}`);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">
          Saved Visualizations
        </h3>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="p-4">
              <Skeleton className="aspect-video w-full mb-2" />
              <Skeleton className="h-4 w-3/4 mb-2" />
              <Skeleton className="h-3 w-1/2" />
            </Card>
          ))}
        </div>
      </div>
    );
  }

  if (!visualizations || visualizations.length === 0) {
    return (
      <div className="rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 p-8 text-center">
        <svg
          className="mx-auto h-12 w-12 text-gray-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">
          No saved visualizations
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          Generate and save visualizations to see them here
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900">
          Saved Visualizations
        </h3>
        <span className="text-sm text-gray-500">
          {visualizations.length} {visualizations.length === 1 ? 'visualization' : 'visualizations'}
        </span>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
        {visualizations.map((visualization) => (
          <Card
            key={visualization.id}
            className={`cursor-pointer transition-all hover:shadow-lg ${
              selectedId === visualization.id ? 'ring-2 ring-blue-500' : ''
            }`}
            onClick={() => handleVisualizationClick(visualization)}
          >
            <div className="relative aspect-video w-full overflow-hidden rounded-t-lg bg-gray-100">
              {/* Split view thumbnail */}
              <div className="absolute inset-0 flex">
                <div className="w-1/2 overflow-hidden">
                  <img
                    src={visualization.before_image_url}
                    alt="Before"
                    className="h-full w-full object-cover"
                  />
                  <div className="absolute bottom-2 left-2 rounded bg-black/50 px-2 py-1 text-xs text-white">
                    Before
                  </div>
                </div>
                <div className="w-1/2 overflow-hidden border-l-2 border-white">
                  <img
                    src={visualization.after_image_url}
                    alt="After"
                    className="h-full w-full object-cover"
                  />
                  <div className="absolute bottom-2 right-2 rounded bg-black/50 px-2 py-1 text-xs text-white">
                    After
                  </div>
                </div>
              </div>
            </div>

            <div className="p-4">
              <div className="mb-2 flex items-start justify-between">
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">
                    Procedure ID: {visualization.procedure_id}
                  </p>
                  <p className="text-xs text-gray-500">
                    {new Date(visualization.generated_at).toLocaleDateString()}
                  </p>
                </div>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={(e) => handleDelete(visualization.id, e)}
                  className="ml-2"
                >
                  <svg
                    className="h-4 w-4 text-red-600"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                    />
                  </svg>
                </Button>
              </div>

              <div className="flex items-center justify-between text-xs text-gray-500">
                <span>
                  Confidence: {(visualization.confidence_score * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
};
