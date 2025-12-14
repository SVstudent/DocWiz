'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { AppLayout } from '@/components/layout';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { useAuthStore } from '@/store/authStore';
import { useVisualizationStore, Procedure } from '@/store/visualizationStore';
import { useImageStore } from '@/store/imageStore';

// Component imports
import { ImageUpload } from '@/components/image';
import { ProcedureSelector } from '@/components/procedure';
import { VisualizationContainer } from '@/components/visualization';
import { ComparisonContainer } from '@/components/comparison';
import { InsuranceClaimContainer } from '@/components/insurance';
import { ExportContainer } from '@/components/export';
import { apiClient } from '@/lib/api-client';

// Flow steps
type FlowStep = 'visualization' | 'comparison' | 'insurance' | 'export';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, user, isLoading } = useAuthStore();
  const { currentVisualization } = useVisualizationStore();
  const { currentImage } = useImageStore();
  const [hydrated, setHydrated] = useState(false);

  // Flow state
  const [currentStep, setCurrentStep] = useState<FlowStep>('visualization');
  const [selectedProcedure, setSelectedProcedure] = useState<Procedure | null>(null);
  const [showProcedureSelector, setShowProcedureSelector] = useState(false);
  const [procedures, setProcedures] = useState<Procedure[]>([]);
  const [completedSteps, setCompletedSteps] = useState<Set<FlowStep>>(new Set());

  // Refs for scrolling
  const comparisonRef = useRef<HTMLDivElement>(null);
  const insuranceRef = useRef<HTMLDivElement>(null);
  const exportRef = useRef<HTMLDivElement>(null);

  // Wait for Zustand to hydrate from localStorage
  useEffect(() => {
    setHydrated(true);
  }, []);

  // Fetch procedures for comparison
  useEffect(() => {
    const fetchProcedures = async () => {
      try {
        interface ApiProcedure {
          id: string;
          name: string;
          category: string;
          description: string;
          typical_cost_min: number;
          typical_cost_max: number;
          recovery_days: number;
          risk_level: string;
          cpt_codes: string[];
          icd10_codes: string[];
        }

        const response = await apiClient.get<{ procedures: ApiProcedure[]; total: number }>('/api/procedures');
        const data = response.data;
        const rawProcedures = data.procedures || [];

        setProcedures(rawProcedures.map((proc) => ({
          id: proc.id,
          name: proc.name,
          category: proc.category,
          description: proc.description,
          typical_cost_range: [proc.typical_cost_min, proc.typical_cost_max] as [number, number],
          recovery_days: proc.recovery_days,
          risk_level: proc.risk_level as 'low' | 'medium' | 'high',
          cpt_codes: proc.cpt_codes,
          icd10_codes: proc.icd10_codes,
        })));
      } catch (err) {
        console.error('Error fetching procedures:', err);
      }
    };

    if (isAuthenticated) {
      fetchProcedures();
    }
  }, [isAuthenticated]);

  // Redirect to login if not authenticated (only after hydration)
  useEffect(() => {
    if (hydrated && !isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [hydrated, isAuthenticated, isLoading, router]);

  // Show loading while hydrating
  if (!hydrated || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto mb-3"></div>
          <p className="text-sm text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Redirect screen
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-sm text-gray-600">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  const handleUploadComplete = () => {
    setShowProcedureSelector(true);
  };

  const handleProcedureSelect = (procedure: Procedure) => {
    setSelectedProcedure(procedure);
    setShowProcedureSelector(false);
  };

  const handleVisualizationComplete = () => {
    setCompletedSteps(prev => new Set(prev).add('visualization'));
  };

  const handleMoveToComparison = () => {
    setCurrentStep('comparison');
    setCompletedSteps(prev => new Set(prev).add('visualization'));
    setTimeout(() => {
      comparisonRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleMoveToInsurance = () => {
    setCurrentStep('insurance');
    setCompletedSteps(prev => new Set(prev).add('comparison'));
    setTimeout(() => {
      insuranceRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleMoveToExport = () => {
    setCurrentStep('export');
    setCompletedSteps(prev => new Set(prev).add('insurance'));
    setTimeout(() => {
      exportRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, 100);
  };

  const handleStartNew = () => {
    // Reset all state for a fresh demo
    useImageStore.getState().clearCurrentImage();
    useVisualizationStore.getState().clearCurrent();
    setSelectedProcedure(null);
    setCurrentStep('visualization');
    setCompletedSteps(new Set());
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const steps = [
    { key: 'visualization', label: '1. Visualize', completed: completedSteps.has('visualization') },
    { key: 'comparison', label: '2. Compare', completed: completedSteps.has('comparison') },
    { key: 'insurance', label: '3. Insurance', completed: completedSteps.has('insurance') },
    { key: 'export', label: '4. Export', completed: completedSteps.has('export') },
  ];

  return (
    <AppLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-gray-900">
              Welcome, {user?.name}
            </h1>
            <p className="text-sm text-gray-600">
              Surgical visualization and cost estimation
            </p>
          </div>

          <div className="flex items-center gap-4">
            {/* Progress Indicator */}
            <div className="hidden md:flex items-center gap-2">
              {steps.map((step, idx) => (
                <div key={step.key} className="flex items-center">
                  <div className={`px-2 py-1 rounded text-xs font-medium ${step.completed
                    ? 'bg-green-100 text-green-700'
                    : currentStep === step.key
                      ? 'bg-blue-100 text-blue-700'
                      : 'bg-gray-100 text-gray-500'
                    }`}>
                    {step.label}
                  </div>
                  {idx < steps.length - 1 && (
                    <div className="w-4 h-px bg-gray-300 mx-1" />
                  )}
                </div>
              ))}
            </div>

            {/* Start New Button */}
            <Button variant="outline" size="sm" onClick={handleStartNew}>
              Start New
            </Button>
          </div>
        </div>

        {/* ========== SECTION 1: VISUALIZATION ========== */}
        <Card className="p-4">
          <h2 className="text-lg font-semibold text-gray-900 mb-3">
            Step 1: Generate Surgical Preview
          </h2>

          {/* Image Upload Section */}
          <div className="mb-4">
            {!currentImage ? (
              <>
                <p className="text-sm text-gray-600 mb-2">Upload a photo to begin</p>
                <ImageUpload
                  onUploadComplete={handleUploadComplete}
                  maxSizeMB={10}
                />
              </>
            ) : (
              <div className="flex items-start gap-4">
                <div className="w-32 h-32 rounded-lg overflow-hidden bg-gray-100 flex-shrink-0">
                  <img
                    src={currentImage.url}
                    alt="Uploaded"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-900">Image uploaded</p>
                  <p className="text-xs text-gray-500 mb-2">{currentImage.format} • {currentImage.width}x{currentImage.height}</p>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => {
                      useImageStore.getState().clearCurrentImage();
                      setSelectedProcedure(null);
                    }}
                  >
                    Change Image
                  </Button>
                </div>
              </div>
            )}
          </div>

          {/* Procedure Selection */}
          {currentImage && !selectedProcedure && (
            <div className="mb-4">
              <p className="text-sm text-gray-600 mb-2">Select a procedure</p>
              <ProcedureSelector
                onProcedureSelect={handleProcedureSelect}
                selectedProcedures={selectedProcedure ? [selectedProcedure] : []}
                multiSelect={false}
              />
            </div>
          )}

          {/* Visualization Result */}
          {currentImage && selectedProcedure && user?.id && (
            <div>
              <VisualizationContainer
                procedureId={selectedProcedure.id}
                patientId={user.id}
                onVisualizationComplete={handleVisualizationComplete}
              />

              {/* Compare Button - appears after visualization */}
              {currentVisualization && (
                <div className="mt-4 flex justify-end">
                  <Button onClick={handleMoveToComparison} variant="primary">
                    Compare Procedures →
                  </Button>
                </div>
              )}
            </div>
          )}
        </Card>

        {/* ========== SECTION 2: COMPARISON ========== */}
        {(currentStep === 'comparison' || currentStep === 'insurance' || currentStep === 'export') && (
          <div ref={comparisonRef}>
            <Card className="p-4">
              <div className="flex items-center justify-between mb-3">
                <h2 className="text-lg font-semibold text-gray-900">
                  Step 2: Compare AI Prediction vs Real Result
                </h2>
              </div>

              <ComparisonContainer
                procedureName={selectedProcedure?.name}
                procedureDescription={selectedProcedure?.description}
              />

              {/* Insurance Button */}
              <div className="mt-4 flex justify-end">
                <Button onClick={handleMoveToInsurance} variant="primary">
                  Check Insurance Coverage →
                </Button>
              </div>
            </Card>
          </div>
        )}

        {/* ========== SECTION 3: INSURANCE ========== */}
        {(currentStep === 'insurance' || currentStep === 'export') && (
          <div ref={insuranceRef}>
            <Card className="p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">
                Step 3: Insurance & Coverage
              </h2>

              <InsuranceClaimContainer
                procedureId={selectedProcedure?.id}
              />

              {/* Export Button */}
              <div className="mt-4 flex justify-end">
                <Button onClick={handleMoveToExport} variant="primary">
                  Generate Report →
                </Button>
              </div>
            </Card>
          </div>
        )}

        {/* ========== SECTION 4: EXPORT ========== */}
        {currentStep === 'export' && (
          <div ref={exportRef}>
            <Card className="p-4">
              <h2 className="text-lg font-semibold text-gray-900 mb-3">
                Step 4: Export Report
              </h2>

              <ExportContainer />
            </Card>
          </div>
        )}
      </div>
    </AppLayout>
  );
}
