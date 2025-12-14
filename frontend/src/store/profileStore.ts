import { create } from 'zustand';

export interface Location {
  zip_code: string;
  city: string;
  state: string;
  country: string;
}

export interface InsuranceInfo {
  provider: string;
  policy_number: string;
  group_number?: string;
  plan_type: string;
  coverage_details: Record<string, unknown>;
}

export interface PatientProfile {
  id: string;
  user_id: string;
  name: string;
  date_of_birth: string;
  location: Location;
  insurance_info: InsuranceInfo;
  medical_history?: string;
  created_at: string;
  updated_at: string;
  version: number;
}

interface ProfileState {
  profile: PatientProfile | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setProfile: (profile: PatientProfile) => void;
  updateProfile: (updates: Partial<PatientProfile>) => void;
  clearProfile: () => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useProfileStore = create<ProfileState>((set) => ({
  profile: null,
  isLoading: false,
  error: null,

  setProfile: (profile) =>
    set({
      profile,
      error: null,
    }),

  updateProfile: (updates) =>
    set((state) => ({
      profile: state.profile
        ? { ...state.profile, ...updates }
        : null,
    })),

  clearProfile: () =>
    set({
      profile: null,
      error: null,
    }),

  setLoading: (isLoading) =>
    set({
      isLoading,
    }),

  setError: (error) =>
    set({
      error,
    }),
}));
