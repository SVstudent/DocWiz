'use client';

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { MedicalDisclaimer } from '@/components/ui/MedicalDisclaimer';
import { useToast } from '@/hooks/useToast';
import { useInsurance } from '@/hooks/useInsurance';

interface ProviderInfo {
  name: string;
  npi: string;
  address: string;
  phone: string;
  specialty: string;
}

interface FacilityInfo {
  name: string;
  npi: string;
  address: string;
  place_of_service_code: string;
}

interface ReferringProvider {
  name?: string;
  npi?: string;
}

interface ClaimHeader {
  claim_type: string;
  place_of_service: string;
  prior_authorization_number?: string;
  referral_number?: string;
  claim_frequency_code: string;
}

interface ServiceLineItem {
  procedure_code: string;
  modifiers: string[];
  description: string;
  quantity: number;
  unit_price: number;
  total_price: number;
  diagnosis_pointers: number[];
  service_date: string;
}

interface DiagnosisInfo {
  icd10_code: string;
  description?: string;
  type: string;
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

  // New Detailed Fields
  claim_header?: ClaimHeader;
  facility_info?: FacilityInfo;
  referring_provider?: ReferringProvider;
  service_lines?: ServiceLineItem[];
  diagnosis_details?: DiagnosisInfo[];

  pdf_url?: string;
  structured_data?: any;
  generated_at: string;
}

interface InsuranceClaimProps {
  procedureId?: string;
  patientId?: string;
  costBreakdownId?: string;
  onClaimGenerated?: (claim: PreAuthForm) => void;
}

export const InsuranceClaim: React.FC<InsuranceClaimProps> = ({
  procedureId,
  patientId,
  costBreakdownId,
  onClaimGenerated,
}) => {
  const [generatedClaim, setGeneratedClaim] = useState<PreAuthForm | null>(null);
  const [isDownloading, setIsDownloading] = useState(false);
  const { success, error } = useToast();
  const { generateClaim, downloadPDF, downloadJSON } = useInsurance();

  // Provider info form state
  const [providerInfo, setProviderInfo] = useState<ProviderInfo>({
    name: 'DocWiz Surgical Center',
    npi: '1234567890',
    address: '123 Medical Plaza, Suite 100',
    phone: '(555) 123-4567',
    specialty: 'Plastic and Reconstructive Surgery',
  });

  const handleGenerateClaim = async () => {
    if (!procedureId || !patientId) {
      error('Procedure and patient information are required');
      return;
    }

    try {
      const claim = await generateClaim.mutateAsync({
        procedure_id: procedureId,
        patient_id: patientId,
        cost_breakdown_id: costBreakdownId,
        provider_info: providerInfo,
      });

      setGeneratedClaim(claim);

      success('Insurance claim generated successfully');

      if (onClaimGenerated) {
        onClaimGenerated(claim);
      }
    } catch (err) {
      console.error('Error generating claim:', err);
      error('Failed to generate insurance claim');
    }
  };

  const handleDownloadPDF = async () => {
    if (!generatedClaim) return;

    setIsDownloading(true);

    try {
      const blob = await downloadPDF(generatedClaim.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `preauth_form_${generatedClaim.id}.pdf`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      success('PDF downloaded successfully');
    } catch (err) {
      console.error('Error downloading PDF:', err);
      error('Failed to download PDF');
    } finally {
      setIsDownloading(false);
    }
  };

  const handleDownloadJSON = async () => {
    if (!generatedClaim) return;

    setIsDownloading(true);

    try {
      const blob = await downloadJSON(generatedClaim.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `preauth_form_${generatedClaim.id}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);

      success('JSON downloaded successfully');
    } catch (err) {
      console.error('Error downloading JSON:', err);
      error('Failed to download JSON');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Insurance Claim Documentation</h2>
        <p className="text-sm text-gray-500 mt-1">
          Generate pre-authorization forms for insurance submission
        </p>
      </div>

      {/* Provider Information Form */}
      {!generatedClaim && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Provider Information</h3>

          {(!patientId || !procedureId) && (
            <div className="mb-4 bg-yellow-50 border border-yellow-200 rounded-md p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-yellow-800">Cannot Generate Claim</h3>
                  <div className="mt-2 text-sm text-yellow-700">
                    <p>
                      {!patientId ? 'Patient information is missing. Please ensure you are logged in.' : ''}
                      {!procedureId ? 'Procedure information is missing. Please select a procedure.' : ''}
                    </p>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="space-y-4">
            <Input
              label="Provider Name"
              type="text"
              value={providerInfo.name}
              onChange={(e) => setProviderInfo({ ...providerInfo, name: e.target.value })}
              placeholder="Enter provider name"
            />

            <Input
              label="NPI Number"
              type="text"
              value={providerInfo.npi}
              onChange={(e) => setProviderInfo({ ...providerInfo, npi: e.target.value })}
              placeholder="Enter NPI number"
            />

            <Input
              label="Address"
              type="text"
              value={providerInfo.address}
              onChange={(e) => setProviderInfo({ ...providerInfo, address: e.target.value })}
              placeholder="Enter provider address"
            />

            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Phone"
                type="tel"
                value={providerInfo.phone}
                onChange={(e) => setProviderInfo({ ...providerInfo, phone: e.target.value })}
                placeholder="(555) 123-4567"
              />

              <Input
                label="Specialty"
                type="text"
                value={providerInfo.specialty}
                onChange={(e) => setProviderInfo({ ...providerInfo, specialty: e.target.value })}
                placeholder="Enter specialty"
              />
            </div>

            <div className="pt-4">
              <Button
                onClick={handleGenerateClaim}
                disabled={generateClaim.isPending || !procedureId || !patientId}
                className="w-full"
              >
                {generateClaim.isPending ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                        fill="none"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      />
                    </svg>
                    Generating Claim...
                  </span>
                ) : (
                  'Generate Pre-Authorization Form'
                )}
              </Button>
            </div>
          </div>
        </Card>
      )}

      {/* Generated Claim Display */}
      {generatedClaim && (
        <>
          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button
              onClick={handleDownloadPDF}
              disabled={isDownloading}
              className="flex items-center gap-2"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                />
              </svg>
              {isDownloading ? 'Downloading...' : 'Download PDF'}
            </Button>

            <Button
              variant="outline"
              onClick={handleDownloadJSON}
              disabled={isDownloading}
              className="flex items-center gap-2"
            >
              <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              {isDownloading ? 'Downloading...' : 'Download JSON'}
            </Button>

            <Button
              variant="outline"
              onClick={() => setGeneratedClaim(null)}
              className="ml-auto"
            >
              Generate New Claim
            </Button>
          </div>

          {/* Claim Details */}
          <Card className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Pre-Authorization Form</h3>
              <span className="text-sm text-gray-500">
                Generated: {new Date(generatedClaim.generated_at).toLocaleString()}
              </span>
            </div>

            <div className="space-y-6">
              {/* Form ID */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Form ID</label>
                <div className="text-sm text-gray-900 font-mono bg-gray-50 p-2 rounded">
                  {generatedClaim.id}
                </div>
              </div>

              {/* Claim Header (New) */}
              {generatedClaim.claim_header && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-2">Claim Details</h4>
                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-100 grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-gray-500 block text-xs uppercase tracking-wide font-medium">Prior Auth #</span>
                      <span className="text-gray-900 font-mono font-medium">{generatedClaim.claim_header.prior_authorization_number || 'N/A'}</span>
                    </div>
                    <div>
                      <span className="text-gray-500 block text-xs uppercase tracking-wide font-medium">Place of Service</span>
                      <span className="text-gray-900 font-medium">{generatedClaim.claim_header.place_of_service}</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Provider & Facility Information */}
              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-2">Provider & Facility</h4>
                <div className="bg-gray-50 p-4 rounded text-sm space-y-4">

                  {/* Billing Provider */}
                  <div className="space-y-1">
                    <p className="text-xs font-semibold text-gray-500 uppercase">Billing Provider</p>
                    <p className="font-medium text-gray-900">{generatedClaim.provider_info.name}</p>
                    <p className="text-gray-600">NPI: {generatedClaim.provider_info.npi}</p>
                    <p className="text-gray-600">{generatedClaim.provider_info.address}</p>
                  </div>

                  {/* Facility Info (New) */}
                  {generatedClaim.facility_info && (
                    <div className="pt-3 border-t border-gray-200 space-y-1">
                      <p className="text-xs font-semibold text-gray-500 uppercase">Service Facility</p>
                      <p className="font-medium text-gray-900">{generatedClaim.facility_info.name}</p>
                      <p className="text-gray-600">{generatedClaim.facility_info.address}</p>
                    </div>
                  )}

                  {/* Referring Provider (New) */}
                  {generatedClaim.referring_provider && generatedClaim.referring_provider.name && (
                    <div className="pt-3 border-t border-gray-200 space-y-1">
                      <p className="text-xs font-semibold text-gray-500 uppercase">Referring Provider</p>
                      <p className="font-medium text-gray-900">{generatedClaim.referring_provider.name}</p>
                      {generatedClaim.referring_provider.npi && <p className="text-gray-600">NPI: {generatedClaim.referring_provider.npi}</p>}
                    </div>
                  )}
                </div>
              </div>

              {/* Diagnosis Codes (Enhanced) */}
              <div>
                <h4 className="text-sm font-semibold text-gray-900 mb-2">Diagnosis Details</h4>
                {generatedClaim.diagnosis_details && generatedClaim.diagnosis_details.length > 0 ? (
                  <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-lg">
                    <table className="min-w-full divide-y divide-gray-300">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="py-2 pl-3 pr-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Code</th>
                          <th className="py-2 pl-3 pr-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Description</th>
                          <th className="py-2 pl-3 pr-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Type</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200 bg-white">
                        {generatedClaim.diagnosis_details.map((diag, idx) => (
                          <tr key={idx}>
                            <td className="whitespace-nowrap py-2 pl-3 pr-3 text-sm font-medium text-green-700">{diag.icd10_code}</td>
                            <td className="whitespace-nowrap py-2 pl-3 pr-3 text-sm text-gray-500">{diag.description}</td>
                            <td className="whitespace-nowrap py-2 pl-3 pr-3 text-sm text-gray-500">{diag.type}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                ) : (
                  // Fallback
                  <div className="bg-gray-50 p-4 rounded text-sm">
                    <span className="text-gray-600">ICD-10 Codes:</span>
                    <div className="mt-1 flex flex-wrap gap-2">
                      {generatedClaim.icd10_codes.map((code, index) => (
                        <span key={index} className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          {code}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Service Line Items (New) */}
              {generatedClaim.service_lines && generatedClaim.service_lines.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-gray-900 mb-2">Service Lines</h4>
                  <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 rounded-lg">
                    <table className="min-w-full divide-y divide-gray-300">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="py-2 pl-3 pr-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Date</th>
                          <th className="py-2 pl-3 pr-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Code</th>
                          <th className="py-2 pl-3 pr-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Mod</th>
                          <th className="py-2 pl-3 pr-3 text-left text-xs font-medium uppercase tracking-wide text-gray-500">Description</th>
                          <th className="py-2 pl-3 pr-3 text-right text-xs font-medium uppercase tracking-wide text-gray-500">Qty</th>
                          <th className="py-2 pl-3 pr-3 text-right text-xs font-medium uppercase tracking-wide text-gray-500">Price</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200 bg-white">
                        {generatedClaim.service_lines.map((line, idx) => (
                          <tr key={idx}>
                            <td className="whitespace-nowrap py-2 pl-3 pr-3 text-sm text-gray-500">{new Date(line.service_date).toLocaleDateString()}</td>
                            <td className="whitespace-nowrap py-2 pl-3 pr-3 text-sm font-medium text-blue-700">{line.procedure_code}</td>
                            <td className="whitespace-nowrap py-2 pl-3 pr-3 text-sm text-gray-500">{line.modifiers.join(', ')}</td>
                            <td className="whitespace-nowrap py-2 pl-3 pr-3 text-sm text-gray-500 max-w-xs truncate" title={line.description}>{line.description}</td>
                            <td className="whitespace-nowrap py-2 pl-3 pr-3 text-sm text-gray-500 text-right">{line.quantity}</td>
                            <td className="whitespace-nowrap py-2 pl-3 pr-3 text-sm text-gray-900 font-medium text-right">${line.total_price.toLocaleString(undefined, { minimumFractionDigits: 2 })}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Medical Necessity Justification (Collapsible) */}
              <div>
                <details className="group bg-gray-50 rounded-lg border border-gray-200 open:bg-white open:shadow-sm transition-all duration-200">
                  <summary className="flex items-center justify-between p-4 cursor-pointer list-none">
                    <h4 className="text-sm font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                      Medical Necessity Justification & Clinical Summary
                    </h4>
                    <span className="transform group-open:rotate-180 transition-transform duration-200 text-gray-400 group-hover:text-gray-600">
                      <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    </span>
                  </summary>
                  <div className="px-4 pb-4 pt-0 border-t border-gray-100 mt-2">
                    <div className="prose prose-sm max-w-none text-gray-700 whitespace-pre-wrap leading-relaxed">
                      {generatedClaim.medical_justification}
                    </div>
                  </div>
                </details>
              </div>

              {/* Disclaimer */}
              <MedicalDisclaimer context="insurance" />
            </div>
          </Card>
        </>
      )}

      {/* Empty State */}
      {!generatedClaim && !procedureId && (
        <Card className="p-8 text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="mt-2 text-sm font-medium text-gray-900">No procedure selected</h3>
          <p className="mt-1 text-sm text-gray-500">
            Select a procedure and complete your profile to generate insurance documentation
          </p>
        </Card>
      )}
    </div>
  );
};
