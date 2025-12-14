'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import { MedicalDisclaimer } from '@/components/ui/MedicalDisclaimer';
import { VisualizationResult } from '@/store/visualizationStore';

interface VisualizationViewerProps {
  visualization: VisualizationResult | null;
  isLoading?: boolean;
  onSave?: () => void;
  onRegenerate?: () => void;
}

export const VisualizationViewer: React.FC<VisualizationViewerProps> = ({
  visualization,
  isLoading = false,
  onSave,
  onRegenerate,
}) => {
  const [sliderPosition, setSliderPosition] = useState(50);
  const [isDragging, setIsDragging] = useState(false);
  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [panStart, setPanStart] = useState({ x: 0, y: 0 });
  const containerRef = useRef<HTMLDivElement>(null);
  const beforeImageRef = useRef<HTMLImageElement>(null);
  const afterImageRef = useRef<HTMLImageElement>(null);

  // Reset zoom and pan when visualization changes
  useEffect(() => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
    setSliderPosition(50);
  }, [visualization?.id]);

  const handleSliderMouseDown = (e: React.MouseEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleSliderTouchStart = (e: React.TouchEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (!isDragging || !containerRef.current) return;
    
    const rect = containerRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = (x / rect.width) * 100;
    setSliderPosition(Math.max(0, Math.min(100, percentage)));
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    if (!isDragging || !containerRef.current) return;
    
    const rect = containerRef.current.getBoundingClientRect();
    const x = e.touches[0].clientX - rect.left;
    const percentage = (x / rect.width) * 100;
    setSliderPosition(Math.max(0, Math.min(100, percentage)));
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleTouchEnd = () => {
    setIsDragging(false);
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

  // Loading state
  if (isLoading) {
    return (
      <div className="w-full space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900">
            Generating Surgical Preview...
          </h3>
          <div className="flex gap-2">
            <Skeleton className="h-10 w-24" />
            <Skeleton className="h-10 w-24" />
          </div>
        </div>
        <div className="relative aspect-video w-full overflow-hidden rounded-lg bg-gray-100">
          <Skeleton className="h-full w-full" />
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center">
              <div className="mb-4 h-12 w-12 animate-spin rounded-full border-4 border-gray-300 border-t-blue-600 mx-auto"></div>
              <p className="text-sm text-gray-600">
                This may take up to 10 seconds...
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // No visualization state
  if (!visualization) {
    return (
      <div className="w-full rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 p-12 text-center">
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
          No visualization yet
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          Upload an image and select a procedure to generate a preview
        </p>
      </div>
    );
  }

  return (
    <div className="w-full space-y-4">
      {/* Header with actions */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">
            Surgical Preview
          </h3>
          <p className="text-sm text-gray-500">
            Confidence: {(visualization.confidence_score * 100).toFixed(1)}%
          </p>
        </div>
        <div className="flex gap-2">
          {onRegenerate && (
            <Button
              variant="outline"
              onClick={onRegenerate}
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
              Regenerate
            </Button>
          )}
          {onSave && (
            <Button
              onClick={onSave}
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
                  d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"
                />
              </svg>
              Save
            </Button>
          )}
        </div>
      </div>

      {/* Zoom controls */}
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
            Reset
          </Button>
        )}
      </div>

      {/* Comparison viewer */}
      <div
        ref={containerRef}
        className="relative aspect-video w-full overflow-hidden rounded-lg bg-gray-900 cursor-move"
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onTouchMove={handleTouchMove}
        onTouchEnd={handleTouchEnd}
        onMouseDown={handlePanStart}
        onMouseMoveCapture={handlePanMove}
        onMouseUpCapture={handlePanEnd}
      >
        {/* After image (right side) */}
        <div className="absolute inset-0">
          <img
            ref={afterImageRef}
            src={visualization.after_image_url}
            alt="After surgery preview"
            className="h-full w-full object-contain"
            style={{
              transform: `scale(${zoom}) translate(${pan.x / zoom}px, ${pan.y / zoom}px)`,
              transformOrigin: 'center',
              transition: isPanning ? 'none' : 'transform 0.2s ease-out',
            }}
          />
          <div className="absolute top-4 right-4 rounded bg-black/50 px-3 py-1 text-sm font-medium text-white">
            After
          </div>
        </div>

        {/* Before image (left side, clipped by slider) */}
        <div
          className="absolute inset-0"
          style={{
            clipPath: `inset(0 ${100 - sliderPosition}% 0 0)`,
          }}
        >
          <img
            ref={beforeImageRef}
            src={visualization.before_image_url}
            alt="Before surgery"
            className="h-full w-full object-contain"
            style={{
              transform: `scale(${zoom}) translate(${pan.x / zoom}px, ${pan.y / zoom}px)`,
              transformOrigin: 'center',
              transition: isPanning ? 'none' : 'transform 0.2s ease-out',
            }}
          />
          <div className="absolute top-4 left-4 rounded bg-black/50 px-3 py-1 text-sm font-medium text-white">
            Before
          </div>
        </div>

        {/* Slider */}
        <div
          className="absolute inset-y-0 z-10 w-1 cursor-ew-resize bg-white shadow-lg"
          style={{ left: `${sliderPosition}%` }}
          onMouseDown={handleSliderMouseDown}
          onTouchStart={handleSliderTouchStart}
        >
          <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white p-2 shadow-lg">
            <svg
              className="h-4 w-4 text-gray-700"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M8 9l4-4 4 4m0 6l-4 4-4-4"
              />
            </svg>
          </div>
        </div>
      </div>

      {/* Metadata */}
      <div className="rounded-lg bg-gray-50 p-4 text-sm text-gray-600">
        <p>
          Generated on {new Date(visualization.generated_at).toLocaleString()}
        </p>
        {visualization.metadata && Object.keys(visualization.metadata).length > 0 && (
          <details className="mt-2">
            <summary className="cursor-pointer font-medium text-gray-700">
              View technical details
            </summary>
            <pre className="mt-2 overflow-auto text-xs">
              {JSON.stringify(visualization.metadata, null, 2)}
            </pre>
          </details>
        )}
      </div>

      {/* Medical Disclaimer */}
      <MedicalDisclaimer context="visualization" />
    </div>
  );
};
