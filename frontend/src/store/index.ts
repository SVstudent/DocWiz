export { useAuthStore } from './authStore';
export type { User } from './authStore';

export { useProfileStore } from './profileStore';
export type { PatientProfile, Location, InsuranceInfo } from './profileStore';

export { useVisualizationStore } from './visualizationStore';
export type {
  Procedure,
  VisualizationResult,
  SimilarCase,
  ComparisonResult,
} from './visualizationStore';

export { useCostStore } from './costStore';
export type { CostBreakdown, PaymentPlan } from './costStore';

export { useImageStore } from './imageStore';
export type { UploadedImage } from './imageStore';
