import { create } from 'zustand';

export interface Procedure {
  id: string;
  name: string;
  category: string;
  description: string;
  typical_cost_range: [number, number];
  recovery_days: number;
  risk_level: 'low' | 'medium' | 'high';
  cpt_codes: string[];
  icd10_codes: string[];
}

export interface VisualizationResult {
  id: string;
  patient_id: string;
  procedure_id: string;
  before_image_url: string;
  after_image_url: string;
  prompt_used: string;
  generated_at: string;
  confidence_score: number;
  embedding: number[];
  metadata: Record<string, unknown>;
}

export interface SimilarCase {
  id: string;
  before_image_url: string;
  after_image_url: string;
  procedure_type: string;
  similarity_score: number;
  outcome_rating: number;
  patient_satisfaction: number;
  anonymized: boolean;
}

export interface ProcedureComparisonData {
  procedure_id: string;
  procedure_name: string;
  visualization_id: string;
  before_image_url: string;
  after_image_url: string;
  cost: number;
  recovery_days: number;
  risk_level: string;
}

export interface ComparisonResult {
  id: string;
  source_image_id: string;
  patient_id?: string;
  procedures: ProcedureComparisonData[];
  cost_differences: Record<string, number>;
  recovery_differences: Record<string, number>;
  risk_differences: Record<string, string>;
  created_at: string;
  metadata: Record<string, unknown>;
}

interface VisualizationState {
  currentVisualization: VisualizationResult | null;
  visualizations: VisualizationResult[];
  similarCases: SimilarCase[];
  comparisons: ComparisonResult[];
  isGenerating: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setCurrentVisualization: (visualization: VisualizationResult) => void;
  addVisualization: (visualization: VisualizationResult) => void;
  setVisualizations: (visualizations: VisualizationResult[]) => void;
  setSimilarCases: (cases: SimilarCase[]) => void;
  addComparison: (comparison: ComparisonResult) => void;
  setComparisons: (comparisons: ComparisonResult[]) => void;
  setGenerating: (isGenerating: boolean) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  clearCurrent: () => void;
}

export const useVisualizationStore = create<VisualizationState>((set) => ({
  currentVisualization: null,
  visualizations: [],
  similarCases: [],
  comparisons: [],
  isGenerating: false,
  isLoading: false,
  error: null,

  setCurrentVisualization: (visualization) =>
    set({
      currentVisualization: visualization,
      error: null,
    }),

  addVisualization: (visualization) =>
    set((state) => ({
      visualizations: [...state.visualizations, visualization],
      currentVisualization: visualization,
    })),

  setVisualizations: (visualizations) =>
    set({
      visualizations,
    }),

  setSimilarCases: (cases) =>
    set({
      similarCases: cases,
    }),

  addComparison: (comparison) =>
    set((state) => ({
      comparisons: [...state.comparisons, comparison],
    })),

  setComparisons: (comparisons) =>
    set({
      comparisons,
    }),

  setGenerating: (isGenerating) =>
    set({
      isGenerating,
    }),

  setLoading: (isLoading) =>
    set({
      isLoading,
    }),

  setError: (error) =>
    set({
      error,
    }),

  clearCurrent: () =>
    set({
      currentVisualization: null,
      error: null,
    }),
}));
