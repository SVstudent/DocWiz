'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { PatientProfile } from '@/store/profileStore';

interface ProfileViewProps {
  profile: PatientProfile;
  onEdit: () => void;
  onViewHistory: () => void;
}

export function ProfileView({ profile, onEdit, onViewHistory }: ProfileViewProps) {
  const [showSensitiveData, setShowSensitiveData] = useState(false);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const maskPolicyNumber = (policyNumber: string) => {
    if (!policyNumber) return '';
    const visibleChars = 4;
    if (policyNumber.length <= visibleChars) return policyNumber;
    return '•'.repeat(policyNumber.length - visibleChars) + policyNumber.slice(-visibleChars);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold text-surgical-gray-900">{profile.name}</h1>
          <p className="text-sm text-surgical-gray-600 mt-1">
            Profile Version: {profile.version} • Last Updated: {formatDate(profile.updated_at)}
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={onViewHistory}>
            View History
          </Button>
          <Button onClick={onEdit}>
            Edit Profile
          </Button>
        </div>
      </div>

      {/* Personal Information */}
      <Card>
        <CardHeader>
          <CardTitle>Personal Information</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-surgical-gray-600">Full Name</label>
              <p className="text-base text-surgical-gray-900 mt-1">{profile.name}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-surgical-gray-600">Date of Birth</label>
              <p className="text-base text-surgical-gray-900 mt-1">
                {formatDate(profile.date_of_birth)}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Location */}
      <Card>
        <CardHeader>
          <CardTitle>Location</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-surgical-gray-600">City</label>
              <p className="text-base text-surgical-gray-900 mt-1">{profile.location.city}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-surgical-gray-600">State</label>
              <p className="text-base text-surgical-gray-900 mt-1">{profile.location.state}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-surgical-gray-600">Zip Code</label>
              <p className="text-base text-surgical-gray-900 mt-1">{profile.location.zip_code}</p>
            </div>
            <div>
              <label className="text-sm font-medium text-surgical-gray-600">Country</label>
              <p className="text-base text-surgical-gray-900 mt-1">{profile.location.country}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Insurance Information */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-start">
            <div>
              <CardTitle>Insurance Information</CardTitle>
              <CardDescription className="flex items-center gap-2 mt-2">
                <svg
                  className="w-4 h-4 text-surgical-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  />
                </svg>
                <span>Encrypted fields are protected</span>
              </CardDescription>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setShowSensitiveData(!showSensitiveData)}
            >
              {showSensitiveData ? 'Hide' : 'Show'} Sensitive Data
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="text-sm font-medium text-surgical-gray-600">Provider</label>
              <p className="text-base text-surgical-gray-900 mt-1">
                {profile.insurance_info.provider}
              </p>
            </div>
            <div>
              <label className="text-sm font-medium text-surgical-gray-600 flex items-center gap-1">
                Policy Number
                <svg
                  className="w-3 h-3 text-surgical-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                  />
                </svg>
              </label>
              <p className="text-base text-surgical-gray-900 mt-1 font-mono">
                {showSensitiveData
                  ? profile.insurance_info.policy_number
                  : maskPolicyNumber(profile.insurance_info.policy_number)}
              </p>
            </div>
            {profile.insurance_info.group_number && (
              <div>
                <label className="text-sm font-medium text-surgical-gray-600">Group Number</label>
                <p className="text-base text-surgical-gray-900 mt-1">
                  {profile.insurance_info.group_number}
                </p>
              </div>
            )}
            {profile.insurance_info.plan_type && (
              <div>
                <label className="text-sm font-medium text-surgical-gray-600">Plan Type</label>
                <p className="text-base text-surgical-gray-900 mt-1">
                  {profile.insurance_info.plan_type}
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Medical History */}
      {profile.medical_history && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              Medical History
              <svg
                className="w-4 h-4 text-surgical-blue-600"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
                />
              </svg>
            </CardTitle>
            <CardDescription>This information is encrypted and confidential</CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-base text-surgical-gray-900 whitespace-pre-wrap">
              {showSensitiveData ? profile.medical_history : '••••••••••••••••••••'}
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
