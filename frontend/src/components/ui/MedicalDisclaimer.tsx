'use client';

import React from 'react';

export type DisclaimerVariant = 'default' | 'compact' | 'inline';
export type DisclaimerContext = 
  | 'visualization' 
  | 'cost' 
  | 'procedure' 
  | 'comparison' 
  | 'insurance' 
  | 'export'
  | 'similar-cases'
  | 'general';

interface MedicalDisclaimerProps {
  variant?: DisclaimerVariant;
  context?: DisclaimerContext;
  className?: string;
}

const disclaimerMessages: Record<DisclaimerContext, { title: string; message: string }> = {
  visualization: {
    title: 'Medical Disclaimer',
    message: 'These visualizations are AI-generated estimates for educational purposes only and do not constitute medical advice. Actual surgical outcomes may vary significantly. Always consult with a qualified medical professional before making any decisions about surgical procedures.',
  },
  cost: {
    title: 'Cost Estimate Disclaimer',
    message: 'Cost estimates are approximations based on available data and may not reflect actual costs. Final pricing depends on individual circumstances, provider selection, insurance coverage, and other factors. Please consult with your healthcare provider and insurance company for accurate pricing information.',
  },
  procedure: {
    title: 'Medical Disclaimer',
    message: 'This information is for educational purposes only and does not constitute medical advice. Procedures, risks, and outcomes vary by individual. Always consult with a board-certified surgeon to discuss your specific situation and medical history.',
  },
  comparison: {
    title: 'Medical Disclaimer',
    message: 'These visualizations are AI-generated estimates for educational purposes only. Results shown are not guarantees of actual surgical outcomes. Each procedure carries unique risks and benefits that should be discussed with a qualified medical professional.',
  },
  insurance: {
    title: 'Important Disclaimer',
    message: 'This pre-authorization request is for informational purposes only. Final coverage decisions are made by your insurance provider. Approval is not guaranteed, and actual coverage may differ from estimates. Please verify all information with your insurance company.',
  },
  export: {
    title: 'MEDICAL DISCLAIMER',
    message: 'This report is for informational purposes only and does not constitute medical advice. All surgical visualizations are AI-generated predictions and may not reflect actual surgical outcomes. Cost estimates are approximations and may vary. Always consult with qualified medical professionals before making any healthcare decisions.',
  },
  'similar-cases': {
    title: 'Privacy & Medical Disclaimer',
    message: 'All cases shown are anonymized to protect patient privacy. Results are for educational comparison only and do not predict your individual outcomes. Surgical results vary based on many factors including individual anatomy, surgeon skill, and post-operative care. Consult with a qualified surgeon for personalized advice.',
  },
  general: {
    title: 'Medical Disclaimer',
    message: 'This information is for educational purposes only and does not constitute medical advice. Always consult with qualified healthcare professionals before making any medical decisions.',
  },
};

export const MedicalDisclaimer: React.FC<MedicalDisclaimerProps> = ({
  variant = 'default',
  context = 'general',
  className = '',
}) => {
  const { title, message } = disclaimerMessages[context];

  if (variant === 'inline') {
    return (
      <p className={`text-xs text-gray-600 italic ${className}`}>
        <strong>Note:</strong> {message}
      </p>
    );
  }

  if (variant === 'compact') {
    return (
      <div className={`rounded-lg border border-yellow-200 bg-yellow-50 p-3 ${className}`}>
        <p className="text-xs text-yellow-800">
          <strong>{title}:</strong> {message}
        </p>
      </div>
    );
  }

  // Default variant - full with icon
  return (
    <div className={`rounded-lg border border-yellow-200 bg-yellow-50 p-4 ${className}`}>
      <div className="flex gap-3">
        <div className="flex-shrink-0">
          <svg
            className="h-5 w-5 text-yellow-600"
            fill="currentColor"
            viewBox="0 0 20 20"
            aria-hidden="true"
          >
            <path
              fillRule="evenodd"
              d="M8.485 2.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 2.495zM10 5a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 5zm0 9a1 1 0 100-2 1 1 0 000 2z"
              clipRule="evenodd"
            />
          </svg>
        </div>
        <div className="text-sm text-yellow-800">
          <p className="font-medium mb-1">{title}</p>
          <p>{message}</p>
        </div>
      </div>
    </div>
  );
};
