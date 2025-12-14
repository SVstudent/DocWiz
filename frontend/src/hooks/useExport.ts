import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { useState, useEffect } from 'react';

export interface ExportRequest {
  patient_id: string;
  format: 'pdf' | 'png' | 'jpeg' | 'json';
  shareable: boolean;
  include_visualizations?: boolean;
  include_cost_estimates?: boolean;
  include_comparisons?: boolean;
  visualization_ids?: string[];
  cost_breakdown_ids?: string[];
  comparison_ids?: string[];
}

export interface ExportMetadata {
  id: string;
  patient_id: string;
  patient_name: string;
  format: string;
  shareable: boolean;
  created_at: string;
  file_size_bytes?: number;
  download_url?: string;
  expires_at?: string;
}

export interface ExportResponse {
  id: string;
  patient_id: string;
  patient_name: string;
  format: string;
  shareable: boolean;
  created_at: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  download_url?: string;
  error_message?: string;
  task_id?: string;
  status_url?: string;
}

export function useExport() {
  const createExport = useMutation({
    mutationFn: async (request: ExportRequest): Promise<ExportResponse> => {
      const response = await apiClient.post('/api/exports', request);
      return response.data;
    },
  });

  const getExportMetadata = (exportId: string) =>
    useQuery({
      queryKey: ['export', exportId],
      queryFn: async (): Promise<ExportMetadata> => {
        const response = await apiClient.get(`/api/exports/${exportId}`);
        return response.data;
      },
      enabled: !!exportId,
    });

  // Poll for export completion
  const pollExportStatus = (exportId: string, onComplete?: (metadata: ExportMetadata) => void) => {
    const [isPolling, setIsPolling] = useState(true);

    useEffect(() => {
      if (!exportId || !isPolling) return;

      const pollInterval = setInterval(async () => {
        try {
          const response = await apiClient.get(`/api/exports/${exportId}`);
          const metadata: ExportMetadata = response.data;

          // Check if export is complete
          if (metadata.download_url) {
            setIsPolling(false);
            clearInterval(pollInterval);
            if (onComplete) {
              onComplete(metadata);
            }
          }
        } catch (error) {
          console.error('Error polling export status:', error);
          setIsPolling(false);
          clearInterval(pollInterval);
        }
      }, 2000); // Poll every 2 seconds

      return () => clearInterval(pollInterval);
    }, [exportId, isPolling, onComplete]);

    return { isPolling, stopPolling: () => setIsPolling(false) };
  };

  const downloadExport = async (exportId: string) => {
    try {
      const response = await apiClient.get(`/api/exports/${exportId}/download`, {
        responseType: 'blob',
      });

      // Extract filename from content-disposition header
      const contentDisposition = response.headers['content-disposition'];
      let filename = `docwiz_report_${exportId}.pdf`;

      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }

      // Create blob URL and trigger download
      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading export:', error);
      throw error;
    }
  };

  return {
    createExport,
    getExportMetadata,
    downloadExport,
    pollExportStatus,
  };
}
