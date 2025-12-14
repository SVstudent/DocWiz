import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient, getErrorMessage } from '@/lib/api-client';
import { CostBreakdown, useCostStore } from '@/store/costStore';

interface CostEstimateRequest {
  procedure_id: string;
  patient_id: string;
  zip_code: string;
}

interface ExportRequest {
  patient_id: string;
  format: 'pdf' | 'png' | 'jpeg' | 'json';
  shareable?: boolean;
  include_visualizations?: boolean;
  include_cost_estimates?: boolean;
  include_comparisons?: boolean;
  visualization_ids?: string[];
  cost_breakdown_ids?: string[];
  comparison_ids?: string[];
}

interface ExportResponse {
  id: string;
  patient_id: string;
  patient_name: string;
  format: string;
  shareable: boolean;
  created_at: string;
  status: string;
  download_url: string;
}

export const useCost = () => {
  const { setCurrentCost, setCalculating, setError } = useCostStore();

  // Calculate cost estimate
  const calculateCost = useMutation({
    mutationFn: async (request: CostEstimateRequest) => {
      const response = await apiClient.post<{ cost_breakdown: CostBreakdown }>(
        '/api/costs/estimate',
        request
      );
      return response.data.cost_breakdown;
    },
    onMutate: () => {
      setCalculating(true);
      setError(null);
    },
    onSuccess: (data) => {
      setCurrentCost(data);
      setCalculating(false);
    },
    onError: (error) => {
      const errorMessage = getErrorMessage(error);
      setError(errorMessage);
      setCalculating(false);
    },
  });

  // Get cost breakdown by ID
  const getCostBreakdown = (costId: string) => {
    return useQuery({
      queryKey: ['cost', costId],
      queryFn: async () => {
        const response = await apiClient.get<{ cost_breakdown: CostBreakdown }>(
          `/api/costs/${costId}`
        );
        return response.data.cost_breakdown;
      },
      enabled: !!costId,
    });
  };

  // Export cost data
  const exportCost = useMutation({
    mutationFn: async ({
      costBreakdownId,
      format,
      patientId,
    }: {
      costBreakdownId: string;
      format: 'pdf' | 'png' | 'json';
      patientId: string;
    }) => {
      const exportRequest: ExportRequest = {
        patient_id: patientId,
        format,
        include_cost_estimates: true,
        cost_breakdown_ids: [costBreakdownId],
      };

      const response = await apiClient.post<ExportResponse>(
        '/api/exports',
        exportRequest
      );
      return response.data;
    },
    onSuccess: async (data) => {
      // Download the file
      const downloadUrl = data.download_url;
      const response = await apiClient.get(downloadUrl, {
        responseType: 'blob',
      });

      // Create a blob URL and trigger download
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      
      const extensions: Record<string, string> = {
        pdf: 'pdf',
        png: 'png',
        jpeg: 'jpg',
        json: 'json',
      };
      
      link.download = `cost-estimate-${data.id}.${extensions[data.format] || 'bin'}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    },
    onError: (error) => {
      const errorMessage = getErrorMessage(error);
      setError(errorMessage);
    },
  });

  // Get cost infographic
  const getCostInfographic = async (
    costBreakdownId: string,
    format: 'png' | 'jpeg' = 'png'
  ) => {
    try {
      const response = await apiClient.get(
        `/api/costs/${costBreakdownId}/infographic`,
        {
          params: { format },
          responseType: 'blob',
        }
      );

      return new Blob([response.data], {
        type: format === 'png' ? 'image/png' : 'image/jpeg',
      });
    } catch (error) {
      throw new Error(getErrorMessage(error));
    }
  };

  return {
    calculateCost,
    getCostBreakdown,
    exportCost,
    getCostInfographic,
  };
};
