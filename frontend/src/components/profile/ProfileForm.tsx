'use client';

import { useState, useEffect } from 'react';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { PatientProfile, InsuranceInfo, Location } from '@/store/profileStore';

interface ProfileFormProps {
  initialData?: Partial<PatientProfile>;
  onSubmit: (data: ProfileFormData) => Promise<void>;
  onCancel?: () => void;
  isLoading?: boolean;
}

export interface ProfileFormData {
  name: string;
  date_of_birth: string;
  location: Location;
  insurance_info: InsuranceInfo;
  medical_history?: string;
}

interface FormErrors {
  name?: string;
  date_of_birth?: string;
  'location.zip_code'?: string;
  'location.city'?: string;
  'location.state'?: string;
  'insurance_info.provider'?: string;
  'insurance_info.policy_number'?: string;
  'insurance_info.plan_type'?: string;
}

const INSURANCE_PROVIDERS = [
  'Blue Cross Blue Shield',
  'UnitedHealthcare',
  'Aetna',
  'Cigna',
  'Humana',
  'Kaiser Permanente',
  'Anthem',
  'Medicare',
  'Medicaid',
  'Other',
];

const US_STATES = [
  'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
  'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
  'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
  'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
  'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
];

export function ProfileForm({ initialData, onSubmit, onCancel, isLoading = false }: ProfileFormProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [errors, setErrors] = useState<FormErrors>({});
  const [providerSearch, setProviderSearch] = useState('');
  const [showProviderDropdown, setShowProviderDropdown] = useState(false);

  // Form state
  const [formData, setFormData] = useState<ProfileFormData>({
    name: initialData?.name || '',
    date_of_birth: initialData?.date_of_birth || '',
    location: {
      zip_code: initialData?.location?.zip_code || '',
      city: initialData?.location?.city || '',
      state: initialData?.location?.state || '',
      country: initialData?.location?.country || 'USA',
    },
    insurance_info: {
      provider: initialData?.insurance_info?.provider || '',
      policy_number: initialData?.insurance_info?.policy_number || '',
      group_number: initialData?.insurance_info?.group_number || '',
      plan_type: initialData?.insurance_info?.plan_type || '',
      coverage_details: initialData?.insurance_info?.coverage_details || {},
    },
    medical_history: initialData?.medical_history || '',
  });

  // Filter insurance providers based on search
  const filteredProviders = INSURANCE_PROVIDERS.filter((provider) =>
    provider.toLowerCase().includes(providerSearch.toLowerCase())
  );

  // Validate current step
  const validateStep = (step: number): boolean => {
    const newErrors: FormErrors = {};

    if (step === 1) {
      if (!formData.name.trim()) {
        newErrors.name = 'Name is required';
      }
      if (!formData.date_of_birth) {
        newErrors.date_of_birth = 'Date of birth is required';
      } else {
        const dob = new Date(formData.date_of_birth);
        const today = new Date();
        const age = today.getFullYear() - dob.getFullYear();
        if (age < 0 || age > 120) {
          newErrors.date_of_birth = 'Please enter a valid date of birth';
        }
      }
    }

    if (step === 2) {
      if (!formData.location.zip_code.trim()) {
        newErrors['location.zip_code'] = 'Zip code is required';
      } else if (!/^\d{5}(-\d{4})?$/.test(formData.location.zip_code)) {
        newErrors['location.zip_code'] = 'Invalid zip code format (e.g., 12345 or 12345-6789)';
      }
      if (!formData.location.city.trim()) {
        newErrors['location.city'] = 'City is required';
      }
      if (!formData.location.state.trim()) {
        newErrors['location.state'] = 'State is required';
      }
    }

    if (step === 3) {
      if (!formData.insurance_info.provider.trim()) {
        newErrors['insurance_info.provider'] = 'Insurance provider is required';
      }
      if (!formData.insurance_info.policy_number.trim()) {
        newErrors['insurance_info.policy_number'] = 'Policy number is required';
      }
      if (!formData.insurance_info.plan_type.trim()) {
        newErrors['insurance_info.plan_type'] = 'Plan type is required';
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // Handle zip code lookup
  const handleZipCodeLookup = async (zipCode: string) => {
    if (!/^\d{5}(-\d{4})?$/.test(zipCode)) {
      return;
    }

    try {
      // In a real app, you would call a zip code lookup API
      // For now, we'll just clear the error if the format is valid
      setErrors((prev) => {
        const newErrors = { ...prev };
        delete newErrors['location.zip_code'];
        return newErrors;
      });
    } catch (error) {
      console.error('Zip code lookup failed:', error);
    }
  };

  // Handle next step
  const handleNext = () => {
    if (validateStep(currentStep)) {
      setCurrentStep((prev) => Math.min(prev + 1, 4));
    }
  };

  // Handle previous step
  const handlePrevious = () => {
    setCurrentStep((prev) => Math.max(prev - 1, 1));
  };

  // Handle form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateStep(currentStep)) {
      return;
    }

    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Form submission error:', error);
    }
  };

  // Update form field
  const updateField = (field: string, value: string) => {
    setFormData((prev) => {
      const keys = field.split('.');
      if (keys.length === 1) {
        return { ...prev, [field]: value };
      } else if (keys.length === 2) {
        const parentKey = keys[0] as 'location' | 'insurance_info';
        const childKey = keys[1];
        return {
          ...prev,
          [parentKey]: {
            ...prev[parentKey],
            [childKey]: value,
          },
        };
      }
      return prev;
    });

    // Clear error for this field
    setErrors((prev) => {
      const newErrors = { ...prev };
      delete newErrors[field as keyof FormErrors];
      return newErrors;
    });
  };

  const totalSteps = 4;
  const progressPercentage = (currentStep / totalSteps) * 100;

  return (
    <Card className="max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>
          {initialData ? 'Edit Profile' : 'Create Your Profile'}
        </CardTitle>
        <CardDescription>
          Step {currentStep} of {totalSteps}
        </CardDescription>
        
        {/* Progress bar */}
        <div className="w-full bg-surgical-gray-200 rounded-full h-2 mt-4">
          <div
            className="bg-surgical-blue-600 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
      </CardHeader>

      <CardContent>
        <form onSubmit={handleSubmit}>
          {/* Step 1: Personal Information */}
          {currentStep === 1 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-surgical-gray-900">
                Personal Information
              </h3>
              
              <Input
                label="Full Name"
                value={formData.name}
                onChange={(e) => updateField('name', e.target.value)}
                error={errors.name}
                required
                fullWidth
                placeholder="John Doe"
              />

              <Input
                label="Date of Birth"
                type="date"
                value={formData.date_of_birth}
                onChange={(e) => updateField('date_of_birth', e.target.value)}
                error={errors.date_of_birth}
                required
                fullWidth
              />
            </div>
          )}

          {/* Step 2: Location */}
          {currentStep === 2 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-surgical-gray-900">
                Location
              </h3>
              
              <Input
                label="Zip Code"
                value={formData.location.zip_code}
                onChange={(e) => {
                  updateField('location.zip_code', e.target.value);
                  if (e.target.value.length === 5) {
                    handleZipCodeLookup(e.target.value);
                  }
                }}
                error={errors['location.zip_code']}
                required
                fullWidth
                placeholder="12345"
                helperText="We'll use this to provide region-specific pricing"
              />

              <Input
                label="City"
                value={formData.location.city}
                onChange={(e) => updateField('location.city', e.target.value)}
                error={errors['location.city']}
                required
                fullWidth
                placeholder="New York"
              />

              <div>
                <label className="text-sm font-medium text-surgical-gray-900 block mb-1.5">
                  State <span className="text-red-600">*</span>
                </label>
                <select
                  value={formData.location.state}
                  onChange={(e) => updateField('location.state', e.target.value)}
                  className="flex h-10 w-full rounded border border-surgical-gray-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-surgical-blue-500 focus-visible:ring-offset-2"
                  required
                >
                  <option value="">Select a state</option>
                  {US_STATES.map((state) => (
                    <option key={state} value={state}>
                      {state}
                    </option>
                  ))}
                </select>
                {errors['location.state'] && (
                  <p className="text-sm text-red-600 mt-1.5">{errors['location.state']}</p>
                )}
              </div>
            </div>
          )}

          {/* Step 3: Insurance Information */}
          {currentStep === 3 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-surgical-gray-900">
                Insurance Information
              </h3>
              
              <div className="relative">
                <Input
                  label="Insurance Provider"
                  value={providerSearch || formData.insurance_info.provider}
                  onChange={(e) => {
                    setProviderSearch(e.target.value);
                    updateField('insurance_info.provider', e.target.value);
                    setShowProviderDropdown(true);
                  }}
                  onFocus={() => setShowProviderDropdown(true)}
                  onBlur={() => setTimeout(() => setShowProviderDropdown(false), 200)}
                  error={errors['insurance_info.provider']}
                  required
                  fullWidth
                  placeholder="Start typing to search..."
                />
                
                {showProviderDropdown && filteredProviders.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-white border border-surgical-gray-300 rounded shadow-lg max-h-60 overflow-auto">
                    {filteredProviders.map((provider) => (
                      <button
                        key={provider}
                        type="button"
                        className="w-full text-left px-4 py-2 hover:bg-surgical-blue-50 text-sm"
                        onClick={() => {
                          updateField('insurance_info.provider', provider);
                          setProviderSearch(provider);
                          setShowProviderDropdown(false);
                        }}
                      >
                        {provider}
                      </button>
                    ))}
                  </div>
                )}
              </div>

              <Input
                label="Policy Number"
                value={formData.insurance_info.policy_number}
                onChange={(e) => updateField('insurance_info.policy_number', e.target.value)}
                error={errors['insurance_info.policy_number']}
                required
                fullWidth
                placeholder="ABC123456789"
                helperText="This information will be encrypted"
              />

              <Input
                label="Group Number (Optional)"
                value={formData.insurance_info.group_number}
                onChange={(e) => updateField('insurance_info.group_number', e.target.value)}
                fullWidth
                placeholder="GRP12345"
              />

              <Input
                label="Plan Type"
                value={formData.insurance_info.plan_type}
                onChange={(e) => updateField('insurance_info.plan_type', e.target.value)}
                error={errors['insurance_info.plan_type']}
                required
                fullWidth
                placeholder="PPO, HMO, EPO, etc."
              />
            </div>
          )}

          {/* Step 4: Medical History */}
          {currentStep === 4 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-surgical-gray-900">
                Medical History (Optional)
              </h3>
              
              <div>
                <label className="text-sm font-medium text-surgical-gray-900 block mb-1.5">
                  Medical History
                </label>
                <textarea
                  value={formData.medical_history}
                  onChange={(e) => updateField('medical_history', e.target.value)}
                  className="flex min-h-[120px] w-full rounded border border-surgical-gray-300 bg-white px-3 py-2 text-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-surgical-blue-500 focus-visible:ring-offset-2"
                  placeholder="Any relevant medical history, allergies, or previous surgeries..."
                />
                <p className="text-sm text-surgical-gray-600 mt-1.5">
                  This information will be encrypted and kept confidential
                </p>
              </div>
            </div>
          )}

          {/* Navigation buttons */}
          <div className="flex justify-between mt-8">
            <div>
              {currentStep > 1 && (
                <Button
                  type="button"
                  variant="outline"
                  onClick={handlePrevious}
                  disabled={isLoading}
                >
                  Previous
                </Button>
              )}
            </div>

            <div className="flex gap-2">
              {onCancel && (
                <Button
                  type="button"
                  variant="ghost"
                  onClick={onCancel}
                  disabled={isLoading}
                >
                  Cancel
                </Button>
              )}
              
              {currentStep < totalSteps ? (
                <Button
                  type="button"
                  onClick={handleNext}
                  disabled={isLoading}
                >
                  Next
                </Button>
              ) : (
                <Button
                  type="submit"
                  isLoading={isLoading}
                  disabled={isLoading}
                >
                  {initialData ? 'Update Profile' : 'Create Profile'}
                </Button>
              )}
            </div>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
