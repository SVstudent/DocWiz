'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { MedicalDisclaimer } from '@/components/ui/MedicalDisclaimer';

export interface SimilarCase {
  id: string;
  before_image_url: string;
  after_image_url: string;
  procedure_type: string;
  similarity_score: number;
  outcome_rating: number;
  patient_satisfaction: number;
  age_range: string;
  anonymized: boolean;
}

export interface SimilarCasesFilters {
  procedure_type?: string;
  outcome_quality?: number;
  age_range?: string;
  limit?: number;
}

interface SimilarCasesProps {
  visualizationId: string;
  onFetchSimilarCases: (
    visualizationId: string,
    filters?: SimilarCasesFilters
  ) => Promise<SimilarCase[]>;
  isLoading?: boolean;
}

export const SimilarCases: React.FC<SimilarCasesProps> = ({
  visualizationId,
  onFetchSimilarCases,
  isLoading = false,
}) => {
  const [similarCases, setSimilarCases] = useState<SimilarCase[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedCase, setSelectedCase] = useState<SimilarCase | null>(null);

  // Filters state
  const [filters, setFilters] = useState<SimilarCasesFilters>({
    limit: 10,
  });

  // Fetch similar cases
  useEffect(() => {
    const fetchCases = async () => {
      if (!visualizationId) return;

      setLoading(true);
      setError(null);

      try {
        const cases = await onFetchSimilarCases(visualizationId, filters);
        setSimilarCases(cases);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch similar cases');
      } finally {
        setLoading(false);
      }
    };

    fetchCases();
  }, [visualizationId, filters, onFetchSimilarCases]);

  const handleFilterChange = (key: keyof SimilarCasesFilters, value: any) => {
    setFilters((prev) => ({
      ...prev,
      [key]: value,
    }));
  };

  const handleClearFilters = () => {
    setFilters({ limit: 10 });
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <svg
            key={star}
            className={`h-4 w-4 ${
              star <= rating ? 'text-yellow-400' : 'text-gray-300'
            }`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
          </svg>
        ))}
      </div>
    );
  };

  // Loading state
  if (isLoading || loading) {
    return (
      <div className="w-full space-y-4">
        <div className="flex gap-6">
          {/* Sidebar skeleton */}
          <div className="w-64 space-y-4">
            <Skeleton className="h-8 w-full" />
            <Skeleton className="h-32 w-full" />
            <Skeleton className="h-32 w-full" />
          </div>
          {/* Grid skeleton */}
          <div className="flex-1 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3, 4, 5, 6].map((i) => (
              <Skeleton key={i} className="h-64 w-full" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="w-full rounded-lg border border-red-200 bg-red-50 p-6 text-center">
        <svg
          className="mx-auto h-12 w-12 text-red-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-red-900">Error loading similar cases</h3>
        <p className="mt-1 text-sm text-red-700">{error}</p>
        <Button
          variant="outline"
          onClick={() => setFilters({ ...filters })}
          className="mt-4"
        >
          Try Again
        </Button>
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900">Similar Cases</h2>
        <p className="mt-1 text-sm text-gray-600">
          Explore anonymized cases with similar features and procedures
        </p>
      </div>

      {/* Medical Disclaimer */}
      <MedicalDisclaimer context="similar-cases" className="mb-6" />

      <div className="flex gap-6">
        {/* Sidebar filters */}
        <div className="w-64 flex-shrink-0 space-y-4">
          <Card className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-semibold text-gray-900">Filters</h3>
              {(filters.procedure_type || filters.outcome_quality || filters.age_range) && (
                <button
                  onClick={handleClearFilters}
                  className="text-xs text-blue-600 hover:text-blue-700"
                >
                  Clear all
                </button>
              )}
            </div>

            {/* Procedure Type Filter */}
            <div className="mb-4">
              <label htmlFor="procedure-type-filter" className="block text-sm font-medium text-gray-700 mb-2">
                Procedure Type
              </label>
              <select
                id="procedure-type-filter"
                value={filters.procedure_type || ''}
                onChange={(e) =>
                  handleFilterChange('procedure_type', e.target.value || undefined)
                }
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="">All procedures</option>
                <option value="rhinoplasty">Rhinoplasty</option>
                <option value="breast_augmentation">Breast Augmentation</option>
                <option value="facelift">Facelift</option>
                <option value="liposuction">Liposuction</option>
                <option value="cleft_lip_repair">Cleft Lip Repair</option>
                <option value="scar_revision">Scar Revision</option>
              </select>
            </div>

            {/* Outcome Quality Filter */}
            <div className="mb-4">
              <label htmlFor="outcome-quality-filter" className="block text-sm font-medium text-gray-700 mb-2">
                Minimum Outcome Quality
              </label>
              <div className="space-y-2">
                <input
                  id="outcome-quality-filter"
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={filters.outcome_quality || 0}
                  onChange={(e) =>
                    handleFilterChange(
                      'outcome_quality',
                      parseFloat(e.target.value) || undefined
                    )
                  }
                  className="w-full"
                />
                <div className="flex justify-between text-xs text-gray-500">
                  <span>Any</span>
                  <span className="font-medium text-gray-700">
                    {filters.outcome_quality
                      ? `${(filters.outcome_quality * 100).toFixed(0)}%+`
                      : 'Any'}
                  </span>
                  <span>Excellent</span>
                </div>
              </div>
            </div>

            {/* Age Range Filter */}
            <div className="mb-4">
              <label htmlFor="age-range-filter" className="block text-sm font-medium text-gray-700 mb-2">
                Age Range
              </label>
              <select
                id="age-range-filter"
                value={filters.age_range || ''}
                onChange={(e) =>
                  handleFilterChange('age_range', e.target.value || undefined)
                }
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="">All ages</option>
                <option value="18-25">18-25</option>
                <option value="26-35">26-35</option>
                <option value="36-45">36-45</option>
                <option value="46-55">46-55</option>
                <option value="56+">56+</option>
              </select>
            </div>

            {/* Results Limit */}
            <div>
              <label htmlFor="results-limit-filter" className="block text-sm font-medium text-gray-700 mb-2">
                Results to show
              </label>
              <select
                id="results-limit-filter"
                value={filters.limit || 10}
                onChange={(e) =>
                  handleFilterChange('limit', parseInt(e.target.value))
                }
                className="w-full rounded-md border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              >
                <option value="5">5</option>
                <option value="10">10</option>
                <option value="20">20</option>
                <option value="50">50</option>
              </select>
            </div>
          </Card>

          {/* Results count */}
          <div className="text-sm text-gray-600">
            Showing {similarCases.length} similar case{similarCases.length !== 1 ? 's' : ''}
          </div>
        </div>

        {/* Results grid */}
        <div className="flex-1">
          {similarCases.length === 0 ? (
            <div className="rounded-lg border-2 border-dashed border-gray-300 bg-gray-50 p-12 text-center">
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
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                No similar cases found
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Try adjusting your filters to see more results
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {similarCases.map((case_) => (
                <Card
                  key={case_.id}
                  className="overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => setSelectedCase(case_)}
                >
                  {/* Before/After Images */}
                  <div className="relative aspect-video bg-gray-100">
                    <div className="absolute inset-0 flex">
                      <div className="w-1/2 relative">
                        <img
                          src={case_.before_image_url}
                          alt="Before"
                          className="h-full w-full object-cover"
                        />
                        <div className="absolute top-2 left-2 rounded bg-black/50 px-2 py-1 text-xs font-medium text-white">
                          Before
                        </div>
                      </div>
                      <div className="w-1/2 relative">
                        <img
                          src={case_.after_image_url}
                          alt="After"
                          className="h-full w-full object-cover"
                        />
                        <div className="absolute top-2 right-2 rounded bg-black/50 px-2 py-1 text-xs font-medium text-white">
                          After
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Case details */}
                  <div className="p-4 space-y-3">
                    {/* Procedure type */}
                    <div>
                      <h4 className="font-semibold text-gray-900 capitalize">
                        {case_.procedure_type.replace(/_/g, ' ')}
                      </h4>
                      <p className="text-xs text-gray-500">Age: {case_.age_range}</p>
                    </div>

                    {/* Similarity score */}
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Similarity</span>
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-24 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-blue-600 rounded-full"
                            style={{ width: `${case_.similarity_score * 100}%` }}
                          />
                        </div>
                        <span className="text-xs font-medium text-gray-900">
                          {(case_.similarity_score * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>

                    {/* Outcome rating */}
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Outcome Quality</span>
                      <div className="flex items-center gap-2">
                        <div className="h-2 w-24 bg-gray-200 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-green-600 rounded-full"
                            style={{ width: `${case_.outcome_rating * 100}%` }}
                          />
                        </div>
                        <span className="text-xs font-medium text-gray-900">
                          {(case_.outcome_rating * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>

                    {/* Patient satisfaction */}
                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-600">Satisfaction</span>
                      {renderStars(case_.patient_satisfaction)}
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Modal for selected case */}
      {selectedCase && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
          onClick={() => setSelectedCase(null)}
        >
          <div
            className="max-w-4xl w-full bg-white rounded-lg shadow-xl overflow-hidden"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-900 capitalize">
                  {selectedCase.procedure_type.replace(/_/g, ' ')}
                </h3>
                <button
                  onClick={() => setSelectedCase(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg
                    className="h-6 w-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M6 18L18 6M6 6l12 12"
                    />
                  </svg>
                </button>
              </div>

              {/* Large before/after view */}
              <div className="relative aspect-video bg-gray-100 rounded-lg overflow-hidden mb-4">
                <div className="absolute inset-0 flex">
                  <div className="w-1/2 relative">
                    <img
                      src={selectedCase.before_image_url}
                      alt="Before"
                      className="h-full w-full object-contain"
                    />
                    <div className="absolute top-4 left-4 rounded bg-black/50 px-3 py-1 text-sm font-medium text-white">
                      Before
                    </div>
                  </div>
                  <div className="w-1/2 relative">
                    <img
                      src={selectedCase.after_image_url}
                      alt="After"
                      className="h-full w-full object-contain"
                    />
                    <div className="absolute top-4 right-4 rounded bg-black/50 px-3 py-1 text-sm font-medium text-white">
                      After
                    </div>
                  </div>
                </div>
              </div>

              {/* Detailed metrics */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-600 mb-1">Similarity Score</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {(selectedCase.similarity_score * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Based on facial features and procedure type
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-600 mb-1">Outcome Quality</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {(selectedCase.outcome_rating * 100).toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Professional assessment rating
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-600 mb-1">Patient Satisfaction</div>
                  <div className="flex items-center gap-2">
                    {renderStars(selectedCase.patient_satisfaction)}
                    <span className="text-lg font-bold text-gray-900">
                      {selectedCase.patient_satisfaction}/5
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Self-reported satisfaction score
                  </div>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="text-sm text-gray-600 mb-1">Age Range</div>
                  <div className="text-2xl font-bold text-gray-900">
                    {selectedCase.age_range}
                  </div>
                  <div className="text-xs text-gray-500 mt-1">
                    Patient age at time of procedure
                  </div>
                </div>
              </div>

              {/* Privacy notice */}
              {selectedCase.anonymized && (
                <div className="mt-4 rounded-lg bg-blue-50 p-3 text-sm text-blue-800">
                  <div className="flex items-start gap-2">
                    <svg
                      className="h-5 w-5 flex-shrink-0 mt-0.5"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                        clipRule="evenodd"
                      />
                    </svg>
                    <div>
                      <strong>Privacy Protected:</strong> All patient data has been anonymized
                      to protect privacy. Images and information are used with consent for
                      educational purposes only.
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
