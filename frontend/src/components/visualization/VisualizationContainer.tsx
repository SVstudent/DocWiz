'use client';

import React, { useEffect } from 'react';
import { VisualizationViewer } from './VisualizationViewer';
import { useVisualization } from '@/hooks/useVisualization';
import { useVisualizationStore } from '@/store/visualizationStore';
import { useImageStore } from '@/store/imageStore';
import { useToast } from '@/hooks/useToast';

interface VisualizationContainerProps {
  procedureId: string;
  patientId: string;
  onVisualizationComplete?: () => void;
}

export const VisualizationContainer: React.FC<VisualizationContainerProps> = ({
  procedureId,
  patientId,
  onVisualizationComplete,
}) => {
  const toast = useToast();
  const { currentImage } = useImageStore();
  const { currentVisualization } = useVisualizationStore();
  const {
    generateVisualization,
    isGenerating,
    generationProgress,
    saveVisualization,
  } = useVisualization();

  // Auto-generate visualization when component mounts if we have an image
  useEffect(() => {
    if (currentImage && procedureId && patientId && !currentVisualization && !isGenerating) {
      generateVisualization({
        image_id: currentImage.id,
        procedure_id: procedureId,
        patient_id: patientId,
      });
    }
  }, [currentImage, procedureId, patientId, currentVisualization, isGenerating, generateVisualization]);

  // Notify parent when visualization is complete
  useEffect(() => {
    if (currentVisualization && onVisualizationComplete) {
      onVisualizationComplete();
    }
  }, [currentVisualization, onVisualizationComplete]);

  const handleRegenerate = () => {
    if (!currentImage) {
      toast.error('Please upload an image first');
      return;
    }

    if (window.confirm('Are you sure you want to regenerate this visualization? This will create a new preview.')) {
      generateVisualization({
        image_id: currentImage.id,
        procedure_id: procedureId,
        patient_id: patientId,
      });
    }
  };

  const handleSave = async () => {
    if (!currentVisualization) {
      toast.error('No visualization to save');
      return;
    }

    const success = await saveVisualization(currentVisualization.id);
    if (success) {
      toast.success('Visualization saved successfully!');
    }
  };

  return (
    <div className="w-full">
      {/* Progress indicator */}
      {isGenerating && generationProgress !== undefined && (
        <div className="mb-4 rounded-lg bg-blue-50 p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-blue-900">
              Generating visualization...
            </span>
            <span className="text-sm text-blue-700">
              {generationProgress}%
            </span>
          </div>
          <div className="h-2 w-full overflow-hidden rounded-full bg-blue-200">
            <div
              className="h-full bg-blue-600 transition-all duration-300"
              style={{ width: `${generationProgress}%` }}
            />
          </div>
        </div>
      )}

      {/* Visualization viewer */}
      <VisualizationViewer
        visualization={currentVisualization}
        isLoading={isGenerating}
        onSave={handleSave}
        onRegenerate={handleRegenerate}
      />
    </div>
  );
};
