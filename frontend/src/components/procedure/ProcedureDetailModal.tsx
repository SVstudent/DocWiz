'use client';

import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Procedure } from '@/store/visualizationStore';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { Skeleton } from '@/components/ui/Skeleton';
import { MedicalDisclaimer } from '@/components/ui/MedicalDisclaimer';
import { cn } from '@/lib/utils';

export interface ProcedureDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  procedureId: string;
  onSelect?: (procedure: Procedure) => void;
  isSelected?: boolean;
}

interface ProcedureDetailResponse {
  id: string;
  name: string;
  category: string;
  description: string;
  recovery_days: number;
  risk_level: string;
  cost_range: {
    min: number;
    max: number;
  };
}

export function ProcedureDetailModal({
  isOpen,
  onClose,
  procedureId,
  onSelect,
  isSelected = false,
}: ProcedureDetailModalProps) {
  const { data: procedureDetail, isLoading } = useQuery<ProcedureDetailResponse>({
    queryKey: ['procedure-detail', procedureId],
    queryFn: async () => {
      const response = await apiClient.get(`/api/procedures/${procedureId}`);
      return response.data;
    },
    enabled: isOpen && !!procedureId,
  });

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low':
        return 'text-green-600 bg-green-50 border-green-200';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'high':
        return 'text-red-600 bg-red-50 border-red-200';
      default:
        return 'text-surgical-gray-600 bg-surgical-gray-50 border-surgical-gray-200';
    }
  };

  const getRiskDescription = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low':
        return 'This procedure has a low risk profile with minimal complications expected.';
      case 'medium':
        return 'This procedure has a moderate risk profile. Discuss potential complications with your surgeon.';
      case 'high':
        return 'This procedure has a higher risk profile. Comprehensive consultation with your surgeon is essential.';
      default:
        return 'Risk level information not available.';
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getRecoveryTimeline = (days: number) => {
    if (days <= 7) return 'Short recovery period';
    if (days <= 21) return 'Moderate recovery period';
    return 'Extended recovery period';
  };

  const handleSelect = () => {
    if (onSelect && procedureDetail) {
      // Convert to Procedure type
      const procedure: Procedure = {
        id: procedureDetail.id,
        name: procedureDetail.name,
        category: procedureDetail.category,
        description: procedureDetail.description,
        typical_cost_range: [
          procedureDetail.cost_range.min,
          procedureDetail.cost_range.max,
        ],
        recovery_days: procedureDetail.recovery_days,
        risk_level: procedureDetail.risk_level as 'low' | 'medium' | 'high',
        cpt_codes: [],
        icd10_codes: [],
      };
      onSelect(procedure);
      onClose();
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={isLoading ? 'Loading...' : procedureDetail?.name}
      size="lg"
    >
      {isLoading ? (
        <div className="space-y-4">
          <Skeleton className="h-6 w-1/4" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-32 w-full" />
          <Skeleton className="h-12 w-full" />
        </div>
      ) : procedureDetail ? (
        <div className="space-y-6">
          {/* Category and Risk Badge */}
          <div className="flex items-center gap-3">
            <span className="rounded-full bg-surgical-blue-50 px-3 py-1 text-sm font-medium text-surgical-blue-700">
              {procedureDetail.category.toUpperCase()}
            </span>
            <span
              className={cn(
                'rounded-full border px-3 py-1 text-sm font-semibold',
                getRiskLevelColor(procedureDetail.risk_level)
              )}
            >
              {procedureDetail.risk_level.toUpperCase()} RISK
            </span>
          </div>

          {/* Description */}
          <div>
            <h3 className="mb-2 text-lg font-semibold text-surgical-gray-900">
              About This Procedure
            </h3>
            <p className="text-surgical-gray-700">{procedureDetail.description}</p>
          </div>

          {/* Cost Information */}
          <div className="rounded-lg border border-surgical-gray-200 bg-surgical-gray-50 p-4">
            <h3 className="mb-3 text-lg font-semibold text-surgical-gray-900">
              Typical Cost Range
            </h3>
            <div className="flex items-baseline gap-2">
              <span className="text-3xl font-bold text-surgical-blue-600">
                {formatCurrency(procedureDetail.cost_range.min)}
              </span>
              <span className="text-surgical-gray-600">to</span>
              <span className="text-3xl font-bold text-surgical-blue-600">
                {formatCurrency(procedureDetail.cost_range.max)}
              </span>
            </div>
            <p className="mt-2 text-sm text-surgical-gray-600">
              Actual costs may vary based on your location, insurance coverage, and
              specific circumstances. Use our cost estimator for a personalized quote.
            </p>
          </div>

          {/* Recovery Timeline */}
          <div className="rounded-lg border border-surgical-gray-200 bg-white p-4">
            <h3 className="mb-3 text-lg font-semibold text-surgical-gray-900">
              Recovery Timeline
            </h3>
            <div className="flex items-center gap-4">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-surgical-blue-100">
                <span className="text-2xl font-bold text-surgical-blue-600">
                  {procedureDetail.recovery_days}
                </span>
              </div>
              <div>
                <p className="font-medium text-surgical-gray-900">
                  {procedureDetail.recovery_days} days typical recovery
                </p>
                <p className="text-sm text-surgical-gray-600">
                  {getRecoveryTimeline(procedureDetail.recovery_days)}
                </p>
              </div>
            </div>
            <p className="mt-3 text-sm text-surgical-gray-600">
              Recovery time varies by individual. Follow your surgeon's post-operative
              instructions carefully for optimal healing.
            </p>
          </div>

          {/* Risk Factors and Considerations */}
          <div className="rounded-lg border border-surgical-gray-200 bg-white p-4">
            <h3 className="mb-3 text-lg font-semibold text-surgical-gray-900">
              Risk Factors & Considerations
            </h3>
            <div
              className={cn(
                'mb-3 rounded-lg border p-3',
                getRiskLevelColor(procedureDetail.risk_level)
              )}
            >
              <p className="font-medium">
                {procedureDetail.risk_level.charAt(0).toUpperCase() +
                  procedureDetail.risk_level.slice(1)}{' '}
                Risk Level
              </p>
              <p className="mt-1 text-sm">{getRiskDescription(procedureDetail.risk_level)}</p>
            </div>
            <ul className="space-y-2 text-sm text-surgical-gray-700">
              <li className="flex items-start gap-2">
                <svg
                  className="mt-0.5 h-5 w-5 flex-shrink-0 text-surgical-blue-600"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>
                  All surgical procedures carry some risk. Discuss your medical history
                  with your surgeon.
                </span>
              </li>
              <li className="flex items-start gap-2">
                <svg
                  className="mt-0.5 h-5 w-5 flex-shrink-0 text-surgical-blue-600"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>
                  Choose a board-certified surgeon with experience in this specific
                  procedure.
                </span>
              </li>
              <li className="flex items-start gap-2">
                <svg
                  className="mt-0.5 h-5 w-5 flex-shrink-0 text-surgical-blue-600"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                    clipRule="evenodd"
                  />
                </svg>
                <span>
                  Ensure you understand all pre-operative and post-operative care
                  requirements.
                </span>
              </li>
            </ul>
          </div>

          {/* Medical Disclaimer */}
          <MedicalDisclaimer context="procedure" />

          {/* Action Button */}
          {onSelect && (
            <div className="flex gap-3 pt-4">
              <Button
                variant={isSelected ? 'secondary' : 'primary'}
                size="lg"
                fullWidth
                onClick={handleSelect}
              >
                {isSelected ? (
                  <>
                    <svg
                      className="mr-2 h-5 w-5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                    Selected
                  </>
                ) : (
                  'Select This Procedure'
                )}
              </Button>
              <Button variant="outline" size="lg" onClick={onClose}>
                Close
              </Button>
            </div>
          )}
        </div>
      ) : (
        <div className="py-12 text-center">
          <p className="text-surgical-gray-600">Procedure details not available.</p>
        </div>
      )}
    </Modal>
  );
}
