'use client';

import React, { useState, useEffect } from 'react';
import { VisualizationContainer, SavedVisualizations, SimilarCasesContainer } from '@/components/visualization';
import { ImageUpload } from '@/components/image';
import { ProcedureSelector } from '@/components/procedure';
import { Card } from '@/components/ui/Card';
import { AppLayout } from '@/components/layout';
import { useAuthStore } from '@/store/authStore';
import { useImageStore } from '@/store/imageStore';
import { Procedure } from '@/store/visualizationStore';
import { useVisualizationStore } from '@/store/visualizationStore';

export default function VisualizationPage() {
  const { user, isAuthenticated, isLoading } = useAuthStore();
  const { currentImage } = useImageStore();
  const { currentVisualization } = useVisualizationStore();
  const [selectedProcedure, setSelectedProcedure] = useState<Procedure | null>(null);
  const [step, setStep] = useState<'upload' | 'select' | 'visualize'>('upload');
  const [showSimilarCases, setShowSimilarCases] = useState(false);
  const [hydrated, setHydrated] = useState(false);

  // Wait for Zustand to hydrate from localStorage
  useEffect(() => {
    setHydrated(true);
  }, []);

  // Debug logging
  console.log('VisualizationPage - hydrated:', hydrated, 'isAuthenticated:', isAuthenticated, 'user:', user, 'isLoading:', isLoading);

  const handleUploadComplete = () => {
    setStep('select');
  };

  const handleProcedureSelect = (procedure: Procedure) => {
    setSelectedProcedure(procedure);
    setStep('visualize');
  };

  const handleVisualizationComplete = () => {
    // Optionally navigate or show success message
    console.log('Visualization complete!');
  };

  // Show loading state while hydrating or loading
  if (!hydrated || isLoading) {
    return (
      <AppLayout>
        <div className="flex items-center justify-center min-h-[400px]">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="ml-4 text-gray-600">Loading...</p>
        </div>
      </AppLayout>
    );
  }

  // Check authentication
  if (!isAuthenticated || !user) {
    return (
      <AppLayout>
        <Card className="p-8 text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Authentication Required
          </h2>
          <p className="text-gray-600 mb-4">
            Please log in to access the visualization tool.
          </p>
          <a
            href="/login"
            className="inline-block px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Go to Login
          </a>
        </Card>
      </AppLayout>
    );
  }

  return (
    <AppLayout showBreadcrumb>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Surgical Visualization
        </h1>
        <p className="text-gray-600">
          Upload your photo and select a procedure to see a realistic preview
        </p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center justify-center space-x-4">
          <div className={`flex items-center ${step === 'upload' ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`flex h-10 w-10 items-center justify-center rounded-full border-2 ${
              step === 'upload' ? 'border-blue-600 bg-blue-50' : 'border-gray-300'
            }`}>
              1
            </div>
            <span className="ml-2 font-medium">Upload Photo</span>
          </div>
          
          <div className="h-0.5 w-16 bg-gray-300" />
          
          <div className={`flex items-center ${step === 'select' ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`flex h-10 w-10 items-center justify-center rounded-full border-2 ${
              step === 'select' ? 'border-blue-600 bg-blue-50' : 'border-gray-300'
            }`}>
              2
            </div>
            <span className="ml-2 font-medium">Select Procedure</span>
          </div>
          
          <div className="h-0.5 w-16 bg-gray-300" />
          
          <div className={`flex items-center ${step === 'visualize' ? 'text-blue-600' : 'text-gray-400'}`}>
            <div className={`flex h-10 w-10 items-center justify-center rounded-full border-2 ${
              step === 'visualize' ? 'border-blue-600 bg-blue-50' : 'border-gray-300'
            }`}>
              3
            </div>
            <span className="ml-2 font-medium">View Results</span>
          </div>
        </div>
      </div>

      {/* Step 1: Upload Image */}
      {step === 'upload' && (
        <Card className="p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Step 1: Upload Your Photo
          </h2>
          <ImageUpload
            onUploadComplete={handleUploadComplete}
            maxSizeMB={10}
          />
        </Card>
      )}

      {/* Step 2: Select Procedure */}
      {step === 'select' && currentImage && (
        <Card className="p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Step 2: Select a Procedure
          </h2>
          <ProcedureSelector
            onProcedureSelect={handleProcedureSelect}
            selectedProcedures={selectedProcedure ? [selectedProcedure] : []}
            multiSelect={false}
          />
        </Card>
      )}

      {/* Step 3: View Visualization */}
      {step === 'visualize' && currentImage && selectedProcedure && user.id && (
        <Card className="p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Step 3: Your Surgical Preview
          </h2>
          <VisualizationContainer
            procedureId={selectedProcedure.id}
            patientId={user.id}
            onVisualizationComplete={handleVisualizationComplete}
          />
        </Card>
      )}

      {/* Similar Cases Section */}
      {currentVisualization && (
        <Card className="p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Similar Cases
            </h2>
            <button
              onClick={() => setShowSimilarCases(!showSimilarCases)}
              className="text-sm text-blue-600 hover:text-blue-700 font-medium"
            >
              {showSimilarCases ? 'Hide' : 'Show'} Similar Cases
            </button>
          </div>
          {showSimilarCases && (
            <SimilarCasesContainer visualizationId={currentVisualization.id} />
          )}
        </Card>
      )}

      {/* Saved Visualizations */}
      {user.id && (
        <Card className="p-6">
          <SavedVisualizations
            patientId={user.id}
            onVisualizationSelect={(viz) => {
              console.log('Selected visualization:', viz);
            }}
          />
        </Card>
      )}
    </AppLayout>
  );
}
