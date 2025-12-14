'use client';

import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Procedure } from '@/store/visualizationStore';
import { Input } from '@/components/ui/Input';
import { Button } from '@/components/ui/Button';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { cn } from '@/lib/utils';

export interface ProcedureSelectorProps {
  onProcedureSelect: (procedure: Procedure) => void;
  selectedProcedures: Procedure[];
  multiSelect?: boolean;
  onViewDetails?: (procedure: Procedure) => void;
}

interface ProcedureListResponse {
  procedures: Array<{
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
  }>;
  total: number;
}

interface CategoryListResponse {
  categories: string[];
  total: number;
}

export function ProcedureSelector({
  onProcedureSelect,
  selectedProcedures,
  multiSelect = false,
  onViewDetails,
}: ProcedureSelectorProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');

  // Fetch categories
  const { data: categoriesData } = useQuery<CategoryListResponse>({
    queryKey: ['procedure-categories'],
    queryFn: async () => {
      const response = await apiClient.get('/api/procedures/categories');
      return response.data;
    },
  });

  // Fetch procedures
  const { data: proceduresData, isLoading } = useQuery<ProcedureListResponse>({
    queryKey: ['procedures', selectedCategory, searchQuery],
    queryFn: async () => {
      const params: Record<string, string> = {};
      if (selectedCategory !== 'all') {
        params.category = selectedCategory;
      }
      if (searchQuery) {
        params.search = searchQuery;
      }
      const response = await apiClient.get('/api/procedures', { params });
      return response.data;
    },
  });

  // Convert to Procedure type
  const procedures = useMemo(() => {
    if (!proceduresData?.procedures) return [];
    return proceduresData.procedures.map((proc) => ({
      id: proc.id,
      name: proc.name,
      category: proc.category,
      description: proc.description,
      typical_cost_range: [proc.typical_cost_min, proc.typical_cost_max] as [number, number],
      recovery_days: proc.recovery_days,
      risk_level: proc.risk_level as 'low' | 'medium' | 'high',
      cpt_codes: proc.cpt_codes,
      icd10_codes: proc.icd10_codes,
    }));
  }, [proceduresData]);

  const categories = categoriesData?.categories || [];

  const isSelected = (procedure: Procedure) => {
    return selectedProcedures.some((p) => p.id === procedure.id);
  };

  const handleSelect = (procedure: Procedure) => {
    if (!multiSelect) {
      // Single select mode - always select the clicked procedure
      onProcedureSelect(procedure);
    } else {
      // Multi-select mode - toggle selection
      if (isSelected(procedure)) {
        // Deselect by passing a filtered array (handled by parent)
        // For now, just call with the procedure to let parent handle
        onProcedureSelect(procedure);
      } else {
        onProcedureSelect(procedure);
      }
    }
  };

  const getRiskLevelColor = (riskLevel: string) => {
    switch (riskLevel) {
      case 'low':
        return 'text-green-600 bg-green-50';
      case 'medium':
        return 'text-yellow-600 bg-yellow-50';
      case 'high':
        return 'text-red-600 bg-red-50';
      default:
        return 'text-surgical-gray-600 bg-surgical-gray-50';
    }
  };

  const formatCostRange = (range: [number, number]) => {
    const formatter = new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    });
    return `${formatter.format(range[0])} - ${formatter.format(range[1])}`;
  };

  return (
    <div className="space-y-6">
      {/* Search and Filter Controls */}
      <div className="space-y-4">
        <Input
          type="text"
          placeholder="Search procedures by name or description..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          fullWidth
          aria-label="Search procedures"
        />

        {/* Category Filter */}
        <div className="flex flex-wrap gap-2">
          <Button
            variant={selectedCategory === 'all' ? 'primary' : 'outline'}
            size="sm"
            onClick={() => setSelectedCategory('all')}
          >
            All Categories
          </Button>
          {categories.map((category) => (
            <Button
              key={category}
              variant={selectedCategory === category ? 'primary' : 'outline'}
              size="sm"
              onClick={() => setSelectedCategory(category)}
            >
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </Button>
          ))}
        </div>
      </div>

      {/* Results Count */}
      {!isLoading && procedures.length > 0 && (
        <p className="text-sm text-surgical-gray-600">
          Showing {procedures.length} procedure{procedures.length !== 1 ? 's' : ''}
        </p>
      )}

      {/* Procedure Cards Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-20 w-full" />
              </CardContent>
              <CardFooter>
                <Skeleton className="h-10 w-full" />
              </CardFooter>
            </Card>
          ))}
        </div>
      ) : procedures.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-surgical-gray-600">
              No procedures found. Try adjusting your search or filters.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {procedures.map((procedure) => {
            const selected = isSelected(procedure);
            return (
              <Card
                key={procedure.id}
                className={cn(
                  'transition-all hover:shadow-md',
                  selected && 'ring-2 ring-surgical-blue-500'
                )}
              >
                <CardHeader>
                  <CardTitle className="text-lg">{procedure.name}</CardTitle>
                  <CardDescription className="flex items-center gap-2">
                    <span className="text-xs font-medium text-surgical-gray-500">
                      {procedure.category.toUpperCase()}
                    </span>
                    <span
                      className={cn(
                        'rounded-full px-2 py-0.5 text-xs font-medium',
                        getRiskLevelColor(procedure.risk_level)
                      )}
                    >
                      {procedure.risk_level.toUpperCase()} RISK
                    </span>
                  </CardDescription>
                </CardHeader>

                <CardContent className="space-y-3">
                  <p className="line-clamp-3 text-sm text-surgical-gray-700">
                    {procedure.description}
                  </p>

                  <div className="space-y-1 text-sm">
                    <div className="flex items-center justify-between">
                      <span className="text-surgical-gray-600">Recovery:</span>
                      <span className="font-medium text-surgical-gray-900">
                        {procedure.recovery_days} days
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-surgical-gray-600">Cost Range:</span>
                      <span className="font-medium text-surgical-gray-900">
                        {formatCostRange(procedure.typical_cost_range)}
                      </span>
                    </div>
                  </div>
                </CardContent>

                <CardFooter className="flex gap-2">
                  <Button
                    variant={selected ? 'secondary' : 'primary'}
                    size="sm"
                    fullWidth
                    onClick={() => handleSelect(procedure)}
                  >
                    {selected ? (
                      <>
                        <svg
                          className="mr-1 h-4 w-4"
                          fill="currentColor"
                          viewBox="0 0 20 20"
                          xmlns="http://www.w3.org/2000/svg"
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
                      'Select'
                    )}
                  </Button>
                  {onViewDetails && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onViewDetails(procedure)}
                      aria-label={`View details for ${procedure.name}`}
                    >
                      Details
                    </Button>
                  )}
                </CardFooter>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
}
