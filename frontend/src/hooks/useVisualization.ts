'use client';

import { useState, useCallback, useEffect } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient, getErrorMessage } from '@/lib/api-client';
import { useVisualizationStore, VisualizationResult } from '@/store/visualizationStore';
import { useToast } from '@/hooks/useToast';

interface GenerateVisualizationRequest {
  image_id: string;
  procedure_id: string;
  patient_id: string;
}

interface GenerateVisualizationResponse {
  id: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  visualization?: VisualizationResult;
  error?: string;
  progress?: number;
}

export const useVisualization = () => {
  const toast = useToast();
  const {
    setCurrentVisualization,
    addVisualization,
    setGenerating,
    setError,
  } = useVisualizationStore();

  const [pollingId, setPollingId] = useState<string | null>(null);

  // Generate visualization mutation
  const generateMutation = useMutation({
    mutationFn: async (data: GenerateVisualizationRequest) => {
      setGenerating(true);
      setError(null);
      
      const response = await apiClient.post<GenerateVisualizationResponse>(
        '/api/visualizations',
        data
      );
      
      return response.data;
    },
    onSuccess: (data) => {
      if (data.status === 'completed' && data.visualization) {
        // Visualization completed immediately
        setCurrentVisualization(data.visualization);
        addVisualization(data.visualization);
        setGenerating(false);
        toast.success('Visualization generated successfully!');
      } else {
        // Start polling for status
        setPollingId(data.id);
      }
    },
    onError: (error) => {
      const message = getErrorMessage(error);
      setError(message);
      setGenerating(false);
      toast.error(`Failed to generate visualization: ${message}`);
    },
  });

  // Poll for visualization status
  const { data: pollingData } = useQuery({
    queryKey: ['visualization-status', pollingId],
    queryFn: async () => {
      if (!pollingId) return null;
      
      const response = await apiClient.get<GenerateVisualizationResponse>(
        `/api/visualizations/${pollingId}`
      );
      
      return response.data;
    },
    enabled: !!pollingId,
    refetchInterval: (query) => {
      const data = query.state.data;
      // Stop polling if completed or failed
      if (!data || data.status === 'completed' || data.status === 'failed') {
        return false;
      }
      // Poll every 2 seconds while processing
      return 2000;
    },
  });

  // Handle polling data changes
  useEffect(() => {
    if (!pollingData) return;

    if (pollingData.status === 'completed' && pollingData.visualization) {
      setCurrentVisualization(pollingData.visualization);
      addVisualization(pollingData.visualization);
      setGenerating(false);
      setPollingId(null);
      toast.success('Visualization generated successfully!');
    } else if (pollingData.status === 'failed') {
      const errorMsg = pollingData.error || 'Visualization generation failed';
      setError(errorMsg);
      setGenerating(false);
      setPollingId(null);
      toast.error(`Failed to generate visualization: ${errorMsg}`);
    }
  }, [pollingData, setCurrentVisualization, addVisualization, setGenerating, setError, toast]);

  // Get visualization by ID
  const getVisualization = useCallback(
    async (id: string): Promise<VisualizationResult | null> => {
      try {
        const response = await apiClient.get<VisualizationResult>(
          `/api/visualizations/${id}`
        );
        return response.data;
      } catch (error) {
        const message = getErrorMessage(error);
        toast.error(`Failed to fetch visualization: ${message}`);
        return null;
      }
    },
    [toast]
  );

  // Get similar cases
  const getSimilarCases = useCallback(
    async (visualizationId: string, filters?: {
      procedure_type?: string;
      outcome_quality?: number;
      age_range?: string;
      limit?: number;
    }) => {
      try {
        const response = await apiClient.get(
          `/api/visualizations/${visualizationId}/similar`,
          { params: filters }
        );
        // Return the similar_cases array from the response
        return response.data.similar_cases || [];
      } catch (error) {
        const message = getErrorMessage(error);
        toast.error(`Failed to fetch similar cases: ${message}`);
        return [];
      }
    },
    [toast]
  );

  // Save visualization to profile
  const saveVisualization = useCallback(
    async (visualizationId: string) => {
      try {
        await apiClient.post(`/api/visualizations/${visualizationId}/save`);
        toast.success('Visualization saved to your profile!');
        return true;
      } catch (error) {
        const message = getErrorMessage(error);
        toast.error(`Failed to save visualization: ${message}`);
        return false;
      }
    },
    [toast]
  );

  return {
    generateVisualization: generateMutation.mutate,
    isGenerating: generateMutation.isPending || !!pollingId,
    generationProgress: pollingData?.progress,
    getVisualization,
    getSimilarCases,
    saveVisualization,
  };
};
