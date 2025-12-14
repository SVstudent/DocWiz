'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { MedicalDisclaimer } from '@/components/ui/MedicalDisclaimer';
import { useExport, ExportRequest } from '@/hooks/useExport';
import { useToast } from '@/hooks/useToast';

interface ExportReportProps {
  patientId: string;
  patientName: string;
  visualizationIds?: string[];
  costBreakdownIds?: string[];
  comparisonIds?: string[];
}

export function ExportReport({
  patientId,
  patientName,
  visualizationIds = [],
  costBreakdownIds = [],
  comparisonIds = [],
}: ExportReportProps) {
  const [format, setFormat] = useState<'pdf' | 'png' | 'jpeg' | 'json'>('pdf');
  const [shareable, setShareable] = useState(false);
  const [includeVisualizations, setIncludeVisualizations] = useState(true);
  const [includeCostEstimates, setIncludeCostEstimates] = useState(true);
  const [includeComparisons, setIncludeComparisons] = useState(true);
  const [exportId, setExportId] = useState<string | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);

  const { createExport, downloadExport, pollExportStatus } = useExport();
  const { success, error, info } = useToast();

  // Poll for export completion if processing
  const { isPolling } = pollExportStatus(
    exportId || '',
    (metadata) => {
      setIsProcessing(false);
      success('Export completed! Ready to download.');
    }
  );

  const handleCreateExport = async () => {
    try {
      const request: ExportRequest = {
        patient_id: patientId,
        format,
        shareable,
        include_visualizations: includeVisualizations,
        include_cost_estimates: includeCostEstimates,
        include_comparisons: includeComparisons,
        visualization_ids: visualizationIds.length > 0 ? visualizationIds : undefined,
        cost_breakdown_ids: costBreakdownIds.length > 0 ? costBreakdownIds : undefined,
        comparison_ids: comparisonIds.length > 0 ? comparisonIds : undefined,
      };

      const response = await createExport.mutateAsync(request);
      setExportId(response.id);

      // Check if export is processing asynchronously
      if (response.status === 'processing' || response.task_id) {
        setIsProcessing(true);
        info('Export is being generated. This may take a moment...');
      } else if (response.status === 'completed' && response.download_url) {
        // Auto-download if completed immediately
        success('Export created successfully!');
        await handleDownload(response.id);
      } else {
        success('Export created successfully!');
      }
    } catch (err) {
      console.error('Error creating export:', err);
      error('Failed to create export. Please try again.');
    }
  };

  const handleDownload = async (id: string) => {
    try {
      await downloadExport(id);
      success('Export downloaded successfully!');
    } catch (err) {
      console.error('Error downloading export:', err);
      error('Failed to download export. Please try again.');
    }
  };

  const handleGenerateShareLink = () => {
    if (!exportId) return;

    const shareUrl = `${window.location.origin}/shared/exports/${exportId}`;
    navigator.clipboard.writeText(shareUrl);

    success('Share link copied to clipboard!');
  };

  return (
    <div className="space-y-6">
      <Card className="p-6">
        <h2 className="text-2xl font-semibold mb-6">Export Report</h2>

        {/* Export Options */}
        <div className="space-y-6">
          {/* Format Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Export Format
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {(['pdf', 'png', 'jpeg', 'json'] as const).map((fmt) => (
                <button
                  key={fmt}
                  onClick={() => setFormat(fmt)}
                  className={`px-4 py-3 rounded-lg border-2 transition-all ${format === fmt
                      ? 'border-blue-600 bg-blue-50 text-blue-700'
                      : 'border-gray-300 hover:border-gray-400'
                    }`}
                >
                  <div className="font-medium uppercase">{fmt}</div>
                  <div className="text-xs text-gray-500 mt-1">
                    {fmt === 'pdf' && 'Document'}
                    {fmt === 'png' && 'Image'}
                    {fmt === 'jpeg' && 'Image'}
                    {fmt === 'json' && 'Data'}
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Content Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Include in Export
            </label>
            <div className="space-y-2">
              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={includeVisualizations}
                  onChange={(e) => setIncludeVisualizations(e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">
                  Surgical Visualizations
                  {visualizationIds.length > 0 && (
                    <span className="ml-2 text-gray-500">
                      ({visualizationIds.length} selected)
                    </span>
                  )}
                </span>
              </label>

              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={includeCostEstimates}
                  onChange={(e) => setIncludeCostEstimates(e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">
                  Cost Estimates
                  {costBreakdownIds.length > 0 && (
                    <span className="ml-2 text-gray-500">
                      ({costBreakdownIds.length} selected)
                    </span>
                  )}
                </span>
              </label>

              <label className="flex items-center space-x-3 cursor-pointer">
                <input
                  type="checkbox"
                  checked={includeComparisons}
                  onChange={(e) => setIncludeComparisons(e.target.checked)}
                  className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                />
                <span className="text-sm text-gray-700">
                  Procedure Comparisons
                  {comparisonIds.length > 0 && (
                    <span className="ml-2 text-gray-500">
                      ({comparisonIds.length} selected)
                    </span>
                  )}
                </span>
              </label>
            </div>
          </div>

          {/* Shareable Toggle */}
          <div className="border-t pt-4">
            <label className="flex items-start space-x-3 cursor-pointer">
              <input
                type="checkbox"
                checked={shareable}
                onChange={(e) => setShareable(e.target.checked)}
                className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500 mt-1"
              />
              <div>
                <span className="text-sm font-medium text-gray-700">
                  Create Shareable Version
                </span>
                <p className="text-xs text-gray-500 mt-1">
                  Removes sensitive information (policy numbers, medical history) for safe sharing
                  with family, friends, or advisors.
                </p>
              </div>
            </label>
          </div>
        </div>

        {/* Export Preview */}
        {exportId && (
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="text-sm font-medium text-gray-700 mb-2">Export Preview</h3>
            <div className="space-y-2 text-sm text-gray-600">
              <div className="flex justify-between">
                <span>Patient:</span>
                <span className="font-medium">{patientName}</span>
              </div>
              <div className="flex justify-between">
                <span>Format:</span>
                <span className="font-medium uppercase">{format}</span>
              </div>
              <div className="flex justify-between">
                <span>Type:</span>
                <span className="font-medium">
                  {shareable ? 'Shareable (No Sensitive Data)' : 'Full Report'}
                </span>
              </div>
              <div className="flex justify-between">
                <span>Export ID:</span>
                <span className="font-mono text-xs">{exportId}</span>
              </div>
            </div>
          </div>
        )}

        {/* Processing Status */}
        {isProcessing && (
          <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center space-x-3">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
              <p className="text-sm text-blue-800">
                Generating your export... This may take a moment.
              </p>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="mt-6 flex flex-col sm:flex-row gap-3">
          <Button
            onClick={handleCreateExport}
            disabled={createExport.isPending || isProcessing}
            className="flex-1"
          >
            {createExport.isPending || isProcessing ? 'Creating Export...' : 'Create Export'}
          </Button>

          {exportId && !isProcessing && (
            <>
              <Button
                onClick={() => handleDownload(exportId)}
                variant="secondary"
                className="flex-1"
              >
                Download
              </Button>

              {shareable && (
                <Button
                  onClick={handleGenerateShareLink}
                  variant="outline"
                  className="flex-1"
                >
                  Copy Share Link
                </Button>
              )}
            </>
          )}
        </div>

        {/* Medical Disclaimer */}
        <MedicalDisclaimer context="export" variant="compact" className="mt-6" />
      </Card>
    </div>
  );
}
