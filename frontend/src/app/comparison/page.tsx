'use client';

import React, { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { ComparisonContainer } from '@/components/comparison';
import { ImageUpload } from '@/components/image';
import { AppLayout } from '@/components/layout';
import { useAuthStore } from '@/store/authStore';
import { Procedure } from '@/store/visualizationStore';
import { apiClient } from '@/lib/api-client';
import { Skeleton } from '@/components/ui/Skeleton';

export default function ComparisonPage() {
  const router = useRouter();
  const { isAuthenticated } = useAuthStore();
  const [procedures, setProcedures] = useState<Procedure[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Redirect if not authenticated
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, router]);

  // Fetch procedures
  useEffect(() => {
    interface ApiProcedure {
      id: string;
      name: string;
      category: string;
      description: string;
      typical_cost_min: number;
      typical_cost_max: number;
      recovery_days: number;
      risk_level: string;
      cpt_codes: string[];
      icd10_codes: string[];
    }

    const transformProcedure = (proc: ApiProcedure): Procedure => ({
      id: proc.id,
      name: proc.name,
      category: proc.category,
      description: proc.description,
      typical_cost_range: [proc.typical_cost_min, proc.typical_cost_max],
      recovery_days: proc.recovery_days,
      risk_level: proc.risk_level as 'low' | 'medium' | 'high',
      cpt_codes: proc.cpt_codes,
      icd10_codes: proc.icd10_codes,
    });

    const fetchProcedures = async () => {
      try {
        setIsLoading(true);
        const response = await apiClient.get<{ procedures: ApiProcedure[]; total: number } | ApiProcedure[]>('/api/procedures');
        // Handle both response formats - nested object or direct array
        const data = response.data;
        let rawProcedures: ApiProcedure[] = [];

        if (Array.isArray(data)) {
          rawProcedures = data;
        } else if (data && Array.isArray(data.procedures)) {
          rawProcedures = data.procedures;
        }

        // Transform to match Procedure type
        setProcedures(rawProcedures.map(transformProcedure));
      } catch (err) {
        setError('Failed to load procedures');
        console.error('Error fetching procedures:', err);
      } finally {
        setIsLoading(false);
      }
    };

    if (isAuthenticated) {
      fetchProcedures();
    }
  }, [isAuthenticated]);

  if (!isAuthenticated) {
    return null;
  }

  return (
    <AppLayout showBreadcrumb>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Compare Procedures
        </h1>
        <p className="mt-2 text-gray-600">
          Compare multiple surgical procedures side-by-side to make an informed
          decision
        </p>
      </div>

      {/* Image upload section */}
      <div className="mb-8">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Step 1: Upload Your Photo
        </h2>
        <ImageUpload
          onUploadComplete={(imageId, imageUrl) => {
            console.log('Image uploaded:', imageId, imageUrl);
          }}
          maxSizeMB={10}
          acceptedFormats={['image/jpeg', 'image/png', 'image/webp']}
        />
      </div>

      {/* Comparison section */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          Step 2: Select and Compare Procedures
        </h2>
        {isLoading ? (
          <div className="space-y-4">
            <Skeleton className="h-48 w-full" />
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[1, 2, 3].map((i) => (
                <Skeleton key={i} className="h-64 w-full" />
              ))}
            </div>
          </div>
        ) : error ? (
          <div className="rounded-lg bg-red-50 p-4 text-red-800">
            <p>{error}</p>
          </div>
        ) : (
          <ComparisonContainer procedures={procedures} />
        )}
      </div>
    </AppLayout>
  );
}
