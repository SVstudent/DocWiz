'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { apiClient, getErrorMessage } from '@/lib/api-client';

interface CostInfographicProps {
  costBreakdownId: string;
  format?: 'png' | 'jpeg';
  onDownload?: (url: string) => void;
}

export const CostInfographic: React.FC<CostInfographicProps> = ({
  costBreakdownId,
  format = 'png',
  onDownload,
}) => {
  const [infographicUrl, setInfographicUrl] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  useEffect(() => {
    if (costBreakdownId) {
      fetchInfographic();
    }
  }, [costBreakdownId, format]);

  const fetchInfographic = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await apiClient.get(
        `/api/costs/${costBreakdownId}/infographic`,
        {
          params: { format },
          responseType: 'blob',
        }
      );

      // Create a URL for the blob
      const blob = new Blob([response.data], {
        type: format === 'png' ? 'image/png' : 'image/jpeg',
      });
      const url = URL.createObjectURL(blob);
      setInfographicUrl(url);
    } catch (err) {
      const errorMessage = getErrorMessage(err);
      setError(errorMessage);
      console.error('Failed to fetch infographic:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerate = async () => {
    setIsGenerating(true);
    setError(null);

    try {
      // Call the API to generate the infographic
      await apiClient.post(`/api/costs/${costBreakdownId}/infographic`, {
        format,
      });

      // Fetch the newly generated infographic
      await fetchInfographic();
    } catch (err) {
      const errorMessage = getErrorMessage(err);
      setError(errorMessage);
      console.error('Failed to generate infographic:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleDownload = () => {
    if (!infographicUrl) return;

    // Create a temporary link and trigger download
    const link = document.createElement('a');
    link.href = infographicUrl;
    link.download = `cost-breakdown-${costBreakdownId}.${format}`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    if (onDownload) {
      onDownload(infographicUrl);
    }
  };

  const handleRefresh = () => {
    // Revoke the old URL to free memory
    if (infographicUrl) {
      URL.revokeObjectURL(infographicUrl);
    }
    fetchInfographic();
  };

  // Cleanup URL on unmount
  useEffect(() => {
    return () => {
      if (infographicUrl) {
        URL.revokeObjectURL(infographicUrl);
      }
    };
  }, [infographicUrl]);

  if (isLoading || isGenerating) {
    return (
      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">
              {isGenerating ? 'Generating Visual Breakdown...' : 'Loading Visual Breakdown...'}
            </h3>
          </div>
          
          <div className="relative aspect-video w-full overflow-hidden rounded-lg bg-gray-100">
            <Skeleton className="h-full w-full" />
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <div className="mb-4 h-12 w-12 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600 mx-auto"></div>
                <p className="text-sm text-gray-600">
                  {isGenerating 
                    ? 'Creating your visual cost breakdown...' 
                    : 'Loading infographic...'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </Card>
    );
  }

  if (error) {
    return (
      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Visual Cost Breakdown</h3>
          </div>
          
          <div className="rounded-lg border-2 border-dashed border-red-300 bg-red-50 p-8 text-center">
            <svg
              className="mx-auto h-12 w-12 text-red-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
              />
            </svg>
            <h3 className="mt-2 text-sm font-medium text-red-900">
              Failed to load infographic
            </h3>
            <p className="mt-1 text-sm text-red-700">{error}</p>
            <div className="mt-4 flex gap-2 justify-center">
              <Button variant="outline" onClick={handleRefresh}>
                Try Again
              </Button>
              <Button onClick={handleGenerate}>
                Generate New
              </Button>
            </div>
          </div>
        </div>
      </Card>
    );
  }

  if (!infographicUrl) {
    return (
      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900">Visual Cost Breakdown</h3>
          </div>
          
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
              No infographic available
            </h3>
            <p className="mt-1 text-sm text-gray-500">
              Generate a visual breakdown of your cost estimate
            </p>
            <Button className="mt-4" onClick={handleGenerate}>
              Generate Infographic
            </Button>
          </div>
        </div>
      </Card>
    );
  }

  return (
    <Card className="p-6">
      <div className="space-y-4">
        {/* Header with actions */}
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">Visual Cost Breakdown</h3>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              className="flex items-center gap-2"
            >
              <svg
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                />
              </svg>
              Refresh
            </Button>
            <Button
              size="sm"
              onClick={handleDownload}
              className="flex items-center gap-2"
            >
              <svg
                className="h-4 w-4"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                />
              </svg>
              Download
            </Button>
          </div>
        </div>

        {/* Infographic display */}
        <div className="relative rounded-lg overflow-hidden bg-gray-100">
          <img
            src={infographicUrl}
            alt="Cost breakdown infographic"
            className="w-full h-auto"
            style={{ maxHeight: '600px', objectFit: 'contain' }}
          />
        </div>

        {/* Format info */}
        <div className="text-xs text-gray-500 text-center">
          Format: {format.toUpperCase()} • High resolution for printing
        </div>
      </div>
    </Card>
  );
};
