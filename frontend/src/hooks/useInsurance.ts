import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';

interface ProviderInfo {
  name: string;
  npi: string;
  address: string;
  phone: string;
  specialty: string;
}

interface PreAuthForm {
  id: string;
  patient_id: string;
  procedure_id: string;
  cost_breakdown_id?: string;
  cpt_codes: string[];
  icd10_codes: string[];
  medical_justification: string;
  provider_info: ProviderInfo;
  pdf_url?: string;
  structured_data?: any;
  generated_at: string;
}

interface GenerateClaimRequest {
  procedure_id: string;
  patient_id: string;
  cost_breakdown_id?: string;
  provider_info?: ProviderInfo;
}

interface ValidateInsuranceRequest {
  provider: string;
  policy_number: string;
  group_number?: string;
}

interface ValidateInsuranceResponse {
  is_valid: boolean;
  provider: string;
  message: string;
  supported_procedures?: string[];
}

export const useInsurance = () => {
  // Generate insurance claim
  const generateClaim = useMutation({
    mutationFn: async (request: GenerateClaimRequest): Promise<PreAuthForm> => {
      const response = await apiClient.post('/api/insurance/claims', request);
      return response.data;
    },
  });

  // Validate insurance
  const validateInsurance = useMutation({
    mutationFn: async (request: ValidateInsuranceRequest): Promise<ValidateInsuranceResponse> => {
      const response = await apiClient.post('/api/insurance/validate', request);
      return response.data;
    },
  });

  // Download PDF
  const downloadPDF = async (claimId: string): Promise<Blob> => {
    const response = await apiClient.get(`/api/insurance/claims/${claimId}/pdf`, {
      responseType: 'blob',
    });
    return response.data;
  };

  // Download JSON
  const downloadJSON = async (claimId: string): Promise<Blob> => {
    const response = await apiClient.get(`/api/insurance/claims/${claimId}/json`, {
      responseType: 'blob',
    });
    return response.data;
  };

  return {
    generateClaim,
    validateInsurance,
    downloadPDF,
    downloadJSON,
  };
};
