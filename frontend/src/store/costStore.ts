import { create } from 'zustand';

export interface PaymentPlan {
  name: string;
  monthly_payment: number;
  duration_months: number;
  interest_rate: number;
  total_paid: number;
}

export interface CostBreakdown {
  id: string;
  procedure_id: string;
  patient_id: string;
  surgeon_fee: number;
  facility_fee: number;
  anesthesia_fee: number;
  post_op_care: number;
  total_cost: number;
  insurance_coverage: number;
  patient_responsibility: number;
  deductible: number;
  copay: number;
  out_of_pocket_max: number;
  payment_plans: PaymentPlan[];
  calculated_at: string;
  data_sources: string[];
}

interface CostState {
  currentCost: CostBreakdown | null;
  costHistory: CostBreakdown[];
  isCalculating: boolean;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setCurrentCost: (cost: CostBreakdown) => void;
  addCostToHistory: (cost: CostBreakdown) => void;
  setCostHistory: (history: CostBreakdown[]) => void;
  setCalculating: (isCalculating: boolean) => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
  clearCurrent: () => void;
}

export const useCostStore = create<CostState>((set) => ({
  currentCost: null,
  costHistory: [],
  isCalculating: false,
  isLoading: false,
  error: null,

  setCurrentCost: (cost) =>
    set({
      currentCost: cost,
      error: null,
    }),

  addCostToHistory: (cost) =>
    set((state) => ({
      costHistory: [...state.costHistory, cost],
      currentCost: cost,
    })),

  setCostHistory: (history) =>
    set({
      costHistory: history,
    }),

  setCalculating: (isCalculating) =>
    set({
      isCalculating,
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
      currentCost: null,
      error: null,
    }),
}));
