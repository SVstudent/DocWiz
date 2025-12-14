'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { Procedure, ComparisonResult } from '@/store/visualizationStore';

interface ComparisonToolProps {
  procedures: Procedure[];
  sourceImage: string;
  onCompare: (procedureIds: string[]) => void;
  comparison: ComparisonResult | null;
  isLoading?: boolean;
}

export const ComparisonTool: React.FC<ComparisonToolProps> = ({
  procedures,
  sourceImage,
  onCompare,
  comparison,
  isLoading = false,
}) => {
  const [selectedProcedures, setSelectedProcedures] = useState<string[]>([]);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const imageRefs = useRef<{ [key: string]: HTMLImageElement | null }>({});

  // Reset zoom and pan when comparison changes
  useEffect(() => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  }, [comparison?.id]);

  const handleProcedureToggle = (procedureId: string) => {
    setSelectedProcedures((prev) => {
      if (prev.includes(procedureId)) {
        return prev.filter((id) => id !== procedureId);
      } else {
        return [...prev, procedureId];
      }
    });
  };

  const handleCompare = () => {
    if (selectedProcedures.length >= 2) {
      onCompare(selectedProcedures);
    }
  };

  const handleClearSelection = () => {
    setSelectedProcedures([]);
  };

  // Pan handlers
  const handlePanStart = (e: React.MouseEvent) => {
    if (zoom <= 1) return;
    setIsPanning(true);
    setPanStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  };

  const handlePanMove = (e: React.MouseEvent) => {
    if (!isPanning) return;
    setPan({
      x: e.clientX - panStart.x,
      y: e.clientY - panStart.y,
    });
  };

  const handlePanEnd = () => {
    setIsPanning(false);
  };

  // Zoom handlers
  const handleZoomIn = () => {
    setZoom((prev) => Math.min(prev + 0.25, 3));
  };

  const handleZoomOut = () => {
    setZoom((prev) => {
      const newZoom = Math.max(prev - 0.25, 1);
      if (newZoom === 1) {
        setPan({ x: 0, y: 0 });
      }
      return newZoom;
    });
  };

  const handleResetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  // Get cost difference text
  const getCostDifferenceText = (procedureId: string): string => {
    if (!comparison?.cost_differences) return '';
    const diff = comparison.cost_differences[procedureId];
    if (diff === undefined) return '';
    if (diff === 0) return 'Baseline';
    return diff > 0 ? `+$${diff.toLocaleString()}` : `-$${Math.abs(diff).toLocaleString()}`;
  };

  // Get recovery difference text
  const getRecoveryDifferenceText = (procedureId: string): string => {
    if (!comparison?.recovery_differences) return '';
    const diff = comparison.recovery_differences[procedureId];
    if (diff === undefined) return '';
    if (diff === 0) return 'Baseline';
    return diff > 0 ? `+${diff} days` : `${diff} days`;
  };

  // Get risk level badge color
  const getRiskBadgeColor = (riskLevel: string): string => {
    switch (riskLevel.toLowerCase()) {
      case 'low':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'high':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <div className="w-full space-y-6">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            Generating Comparison...
          </h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="p-4">
              <Skeleton className="h-48 w-full mb-4" />
              <Skeleton className="h-6 w-3/4 mb-2" />
              <Skeleton className="h-4 w-full mb-2" />
              <Skeleton className="h-4 w-2/3" />
            </Card>
          ))}
        </div>
        <div className="flex items-center justify-center py-8">
          <div className="text-center">
            <div className="mb-4 h-12 w-12 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600 mx-auto"></div>
            <p className="text-sm text-gray-600">
              Generating visualizations for all procedures...
            </p>
          </div>
        </div>
      </div>
    );
  }

  // No comparison yet - show procedure selection
  if (!comparison) {
    return (
      <div className="w-full space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">
              Compare Procedures
            </h3>
            <p className="text-sm text-gray-500">
              Select at least 2 procedures to compare side-by-side
            </p>
          </div>
          <div className="flex gap-2">
            {selectedProcedures.length > 0 && (
              <Button variant="outline" onClick={handleClearSelection}>
                Clear ({selectedProcedures.length})
              </Button>
            )}
            <Button
              onClick={handleCompare}
              disabled={selectedProcedures.length < 2}
            >
              Compare {selectedProcedures.length > 0 && `(${selectedProcedures.length})`}
            </Button>
          </div>
        </div>

        {/* Source image preview */}
        {sourceImage && (
          <Card className="p-4">
            <h4 className="text-sm font-medium text-gray-700 mb-2">
              Source Image
            </h4>
            <div className="relative aspect-video w-full max-w-md overflow-hidden rounded-lg bg-gray-100">
              <img
                src={sourceImage}
                alt="Source"
                className="h-full w-full object-contain"
              />
            </div>
          </Card>
        )}

        {/* Procedure selection grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Array.isArray(procedures) && procedures.length > 0 ? (
            procedures.map((procedure) => {
              const isSelected = selectedProcedures.includes(procedure.id);
              return (
                <Card
                  key={procedure.id}
                  className={`p-4 cursor-pointer transition-all ${isSelected
                    ? 'ring-2 ring-blue-600 bg-blue-50'
                    : 'hover:shadow-md'
                    }`}
                  onClick={() => handleProcedureToggle(procedure.id)}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-semibold text-gray-900">
                      {procedure.name}
                    </h4>
                    <div
                      className={`flex h-5 w-5 items-center justify-center rounded border-2 ${isSelected
                        ? 'border-blue-600 bg-blue-600'
                        : 'border-gray-300'
                        }`}
                    >
                      {isSelected && (
                        <svg
                          className="h-3 w-3 text-white"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={3}
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      )}
                    </div>
                  </div>
                  <p className="text-sm text-gray-600 mb-3 line-clamp-2">
                    {procedure.description}
                  </p>
                  <div className="space-y-1 text-xs text-gray-500">
                    <div className="flex items-center justify-between">
                      <span>Cost Range:</span>
                      <span className="font-medium">
                        ${procedure.typical_cost_range[0].toLocaleString()} - $
                        {procedure.typical_cost_range[1].toLocaleString()}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Recovery:</span>
                      <span className="font-medium">
                        {procedure.recovery_days} days
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Risk Level:</span>
                      <span
                        className={`px-2 py-0.5 rounded text-xs font-medium ${getRiskBadgeColor(
                          procedure.risk_level
                        )}`}
                      >
                        {procedure.risk_level}
                      </span>
                    </div>
                  </div>
                </Card>
              );
            })
          ) : (
            <div className="col-span-3 text-center py-8 text-gray-500">
              No procedures available to compare
            </div>
          )}
        </div>
      </div>
    );
  }

  // Show comparison results
  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Procedure Comparison
          </h3>
          <p className="text-sm text-gray-500">
            Comparing {comparison.procedures.length} procedures
          </p>
        </div>
        <Button variant="outline" onClick={() => setSelectedProcedures([])}>
          New Comparison
        </Button>
      </div>

      {/* Synchronized zoom controls */}
      <div className="flex items-center justify-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={handleZoomOut}
          disabled={zoom <= 1}
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
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7"
            />
          </svg>
        </Button>
        <span className="text-sm text-gray-600 min-w-[60px] text-center">
          {(zoom * 100).toFixed(0)}%
        </span>
        <Button
          variant="outline"
          size="sm"
          onClick={handleZoomIn}
          disabled={zoom >= 3}
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
              d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"
            />
          </svg>
        </Button>
        {zoom > 1 && (
          <Button variant="outline" size="sm" onClick={handleResetView}>
            Reset View
          </Button>
        )}
      </div>

      {/* Comparison grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {comparison.procedures.map((procData) => (
          <Card key={procData.procedure_id} className="overflow-hidden">
            {/* Before/After images */}
            <div
              className="relative aspect-video bg-gray-900 cursor-move"
              onMouseDown={handlePanStart}
              onMouseMove={handlePanMove}
              onMouseUp={handlePanEnd}
              onMouseLeave={handlePanEnd}
            >
              {/* After image */}
              <img
                ref={(el) => {
                  imageRefs.current[`${procData.procedure_id}-after`] = el;
                }}
                src={procData.after_image_url}
                alt={`${procData.procedure_name} - After`}
                className="absolute inset-0 h-full w-full object-contain"
                style={{
                  transform: `scale(${zoom}) translate(${pan.x / zoom}px, ${pan.y / zoom
                    }px)`,
                  transformOrigin: 'center',
                  transition: isPanning ? 'none' : 'transform 0.2s ease-out',
                }}
              />
              <div className="absolute top-2 right-2 rounded bg-black/50 px-2 py-1 text-xs font-medium text-white">
                After
              </div>
            </div>

            {/* Procedure info */}
            <div className="p-4 space-y-3">
              <div>
                <h4 className="font-semibold text-gray-900">
                  {procData.procedure_name}
                </h4>
              </div>

              {/* Cost comparison */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Cost:</span>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-900">
                    ${procData.cost.toLocaleString()}
                  </span>
                  {getCostDifferenceText(procData.procedure_id) && (
                    <span
                      className={`text-xs ${comparison.cost_differences[procData.procedure_id] > 0
                        ? 'text-red-600'
                        : comparison.cost_differences[
                          procData.procedure_id
                        ] < 0
                          ? 'text-green-600'
                          : 'text-gray-500'
                        }`}
                    >
                      {getCostDifferenceText(procData.procedure_id)}
                    </span>
                  )}
                </div>
              </div>

              {/* Recovery comparison */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Recovery:</span>
                <div className="flex items-center gap-2">
                  <span className="font-medium text-gray-900">
                    {procData.recovery_days} days
                  </span>
                  {getRecoveryDifferenceText(procData.procedure_id) && (
                    <span
                      className={`text-xs ${comparison.recovery_differences[procData.procedure_id] >
                        0
                        ? 'text-red-600'
                        : comparison.recovery_differences[
                          procData.procedure_id
                        ] < 0
                          ? 'text-green-600'
                          : 'text-gray-500'
                        }`}
                    >
                      {getRecoveryDifferenceText(procData.procedure_id)}
                    </span>
                  )}
                </div>
              </div>

              {/* Risk level */}
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Risk Level:</span>
                <span
                  className={`px-2 py-1 rounded text-xs font-medium ${getRiskBadgeColor(
                    procData.risk_level
                  )}`}
                >
                  {procData.risk_level}
                </span>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* Summary section */}
      <Card className="p-6 bg-blue-50 border-blue-200">
        <h4 className="font-semibold text-gray-900 mb-4">Comparison Summary</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-gray-600 mb-1">Cost Range:</p>
            <p className="font-medium text-gray-900">
              ${Math.min(...comparison.procedures.map((p) => p.cost)).toLocaleString()} - $
              {Math.max(...comparison.procedures.map((p) => p.cost)).toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-gray-600 mb-1">Recovery Range:</p>
            <p className="font-medium text-gray-900">
              {Math.min(...comparison.procedures.map((p) => p.recovery_days))} -{' '}
              {Math.max(...comparison.procedures.map((p) => p.recovery_days))} days
            </p>
          </div>
          <div>
            <p className="text-gray-600 mb-1">Risk Levels:</p>
            <div className="flex gap-2">
              {Array.from(
                new Set(comparison.procedures.map((p) => p.risk_level))
              ).map((risk) => (
                <span
                  key={risk}
                  className={`px-2 py-1 rounded text-xs font-medium ${getRiskBadgeColor(
                    risk
                  )}`}
                >
                  {risk}
                </span>
              ))}
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};
