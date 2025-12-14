import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { comparisonApi, ComparisonRequest, ComparisonResultData } from '@/lib/api-client';
import { useVisualizationStore } from '@/store/visualizationStore';
import { useToast } from './useToast';

export const useComparison = () => {
  const queryClient = useQueryClient();
  const { addComparison } = useVisualizationStore();
  const { showToast } = useToast();

  // Create comparison mutation
  const createComparisonMutation = useMutation({
    mutationFn: async (request: ComparisonRequest) => {
      return await comparisonApi.createComparison(request, false);
    },
    onSuccess: (data) => {
      if ('task_id' in data) {
        // Async processing
        showToast('Comparison generation started', 'success');
      } else {
        // Sync processing - add to store
        const comparisonResult = data as ComparisonResultData;
        addComparison({
          id: comparisonResult.id,
          source_image_id: comparisonResult.source_image_id,
          patient_id: comparisonResult.patient_id,
          procedures: comparisonResult.procedures,
          cost_differences: comparisonResult.cost_differences,
          recovery_differences: comparisonResult.recovery_differences,
          risk_differences: comparisonResult.risk_differences,
          created_at: comparisonResult.created_at,
          metadata: comparisonResult.metadata,
        });
        showToast('Comparison created successfully', 'success');
      }
      
      // Invalidate comparisons query
      queryClient.invalidateQueries({ queryKey: ['comparisons'] });
    },
    onError: (error: Error) => {
      showToast(`Failed to create comparison: ${error.message}`, 'error');
    },
  });

  // Get comparison query
  const useComparisonQuery = (comparisonId: string | null) => {
    return useQuery({
      queryKey: ['comparison', comparisonId],
      queryFn: () => comparisonApi.getComparison(comparisonId!),
      enabled: !!comparisonId,
    });
  };

  // Save comparison mutation
  const saveComparisonMutation = useMutation({
    mutationFn: async (comparisonId: string) => {
      return await comparisonApi.saveComparison(comparisonId);
    },
    onSuccess: () => {
      showToast('Comparison saved successfully', 'success');
      queryClient.invalidateQueries({ queryKey: ['comparisons'] });
    },
    onError: (error: Error) => {
      showToast(`Failed to save comparison: ${error.message}`, 'error');
    },
  });

  return {
    createComparison: createComparisonMutation.mutate,
    isCreatingComparison: createComparisonMutation.isPending,
    createComparisonError: createComparisonMutation.error,
    useComparisonQuery,
    saveComparison: saveComparisonMutation.mutate,
    isSavingComparison: saveComparisonMutation.isPending,
  };
};
