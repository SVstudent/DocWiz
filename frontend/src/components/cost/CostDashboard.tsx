'use client';

import React, { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { MedicalDisclaimer } from '@/components/ui/MedicalDisclaimer';
import { CostBreakdown } from '@/store/costStore';
import { useCost } from '@/hooks/useCost';
import { useToast } from '@/hooks/useToast';

interface CostDashboardProps {
  costBreakdown: CostBreakdown | null;
  isLoading?: boolean;
  onExport?: (format: 'pdf' | 'png' | 'json') => void;
}

export const CostDashboard: React.FC<CostDashboardProps> = ({
  costBreakdown,
  isLoading = false,
  onExport,
}) => {
  const [expandedPlan, setExpandedPlan] = useState<number | null>(null);
  const { exportCost } = useCost();
  const { showToast } = useToast();

  const handleExport = async (format: 'pdf' | 'png' | 'json') => {
    if (!costBreakdown) return;

    try {
      await exportCost.mutateAsync({
        costBreakdownId: costBreakdown.id,
        format,
        patientId: costBreakdown.patient_id,
      });

      showToast({
        type: 'success',
        message: `Cost estimate exported as ${format.toUpperCase()}`,
      });

      if (onExport) {
        onExport(format);
      }
    } catch (error) {
      showToast({
        type: 'error',
        message: 'Failed to export cost estimate',
      });
    }
  };

  if (isLoading) {
    return (
      <div className="w-full space-y-4">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-64 bg-gray-200 rounded mb-4"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!costBreakdown) {
    return (
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
            d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <h3 className="mt-2 text-sm font-medium text-gray-900">
          No cost estimate available
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          Select a procedure and complete your profile to get a cost estimate
        </p>
      </Card>
    );
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const costItems = [
    { label: 'Surgeon Fee', amount: costBreakdown.surgeon_fee, color: 'bg-blue-500' },
    { label: 'Facility Fee', amount: costBreakdown.facility_fee, color: 'bg-green-500' },
    { label: 'Anesthesia', amount: costBreakdown.anesthesia_fee, color: 'bg-yellow-500' },
    { label: 'Post-Op Care', amount: costBreakdown.post_op_care, color: 'bg-purple-500' },
  ];

  const totalAmount = costBreakdown.total_cost;
  const percentages = costItems.map(item => (item.amount / totalAmount) * 100);

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Cost Breakdown</h2>
          <p className="text-sm text-gray-500">
            Calculated on {new Date(costBreakdown.calculated_at).toLocaleDateString()}
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExport('pdf')}
            disabled={exportCost.isPending}
            className="flex items-center gap-2"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            {exportCost.isPending ? 'Exporting...' : 'PDF'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExport('png')}
            disabled={exportCost.isPending}
            className="flex items-center gap-2"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            {exportCost.isPending ? 'Exporting...' : 'PNG'}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleExport('json')}
            disabled={exportCost.isPending}
            className="flex items-center gap-2"
          >
            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            {exportCost.isPending ? 'Exporting...' : 'JSON'}
          </Button>
        </div>
      </div>

      {/* Visual Cost Breakdown - Bar Chart */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Cost Components</h3>
        
        {/* Horizontal stacked bar chart */}
        <div className="mb-6">
          <div className="flex h-12 rounded-lg overflow-hidden">
            {costItems.map((item, index) => (
              <div
                key={item.label}
                className={`${item.color} flex items-center justify-center text-white text-xs font-medium transition-all hover:opacity-90`}
                style={{ width: `${percentages[index]}%` }}
                title={`${item.label}: ${formatCurrency(item.amount)} (${percentages[index].toFixed(1)}%)`}
              >
                {percentages[index] > 10 && (
                  <span className="px-2">{percentages[index].toFixed(0)}%</span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Legend and amounts */}
        <div className="space-y-3">
          {costItems.map((item) => (
            <div key={item.label} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className={`w-4 h-4 rounded ${item.color}`}></div>
                <span className="text-sm text-gray-700">{item.label}</span>
              </div>
              <span className="text-sm font-semibold text-gray-900">
                {formatCurrency(item.amount)}
              </span>
            </div>
          ))}
          <div className="border-t pt-3 flex items-center justify-between">
            <span className="text-base font-bold text-gray-900">Total Cost</span>
            <span className="text-base font-bold text-gray-900">
              {formatCurrency(costBreakdown.total_cost)}
            </span>
          </div>
        </div>
      </Card>

      {/* Insurance Coverage Calculator */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Insurance Coverage</h3>
        
        <div className="space-y-4">
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-sm text-gray-600">Total Procedure Cost</span>
            <span className="text-sm font-semibold text-gray-900">
              {formatCurrency(costBreakdown.total_cost)}
            </span>
          </div>
          
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-sm text-gray-600">Insurance Coverage</span>
            <span className="text-sm font-semibold text-green-600">
              -{formatCurrency(costBreakdown.insurance_coverage)}
            </span>
          </div>
          
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-sm text-gray-600">Deductible</span>
            <span className="text-sm font-semibold text-gray-900">
              {formatCurrency(costBreakdown.deductible)}
            </span>
          </div>
          
          <div className="flex justify-between items-center py-2 border-b">
            <span className="text-sm text-gray-600">Co-pay</span>
            <span className="text-sm font-semibold text-gray-900">
              {formatCurrency(costBreakdown.copay)}
            </span>
          </div>
          
          <div className="flex justify-between items-center py-3 bg-blue-50 rounded-lg px-4">
            <span className="text-base font-bold text-gray-900">Your Responsibility</span>
            <span className="text-base font-bold text-blue-600">
              {formatCurrency(costBreakdown.patient_responsibility)}
            </span>
          </div>
          
          <div className="flex justify-between items-center py-2 text-xs text-gray-500">
            <span>Out-of-Pocket Maximum</span>
            <span>{formatCurrency(costBreakdown.out_of_pocket_max)}</span>
          </div>
        </div>
      </Card>

      {/* Payment Plan Options */}
      {costBreakdown.payment_plans && costBreakdown.payment_plans.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Payment Plan Options</h3>
          
          <div className="space-y-3">
            {costBreakdown.payment_plans.map((plan, index) => (
              <div
                key={index}
                className="border rounded-lg overflow-hidden transition-all hover:shadow-md"
              >
                <button
                  onClick={() => setExpandedPlan(expandedPlan === index ? null : index)}
                  className="w-full px-4 py-3 flex items-center justify-between bg-gray-50 hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div className="text-left">
                      <div className="font-semibold text-gray-900">{plan.name}</div>
                      <div className="text-sm text-gray-600">
                        {formatCurrency(plan.monthly_payment)}/month for {plan.duration_months} months
                      </div>
                    </div>
                  </div>
                  <svg
                    className={`h-5 w-5 text-gray-400 transition-transform ${
                      expandedPlan === index ? 'rotate-180' : ''
                    }`}
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                
                {expandedPlan === index && (
                  <div className="px-4 py-3 bg-white space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Monthly Payment</span>
                      <span className="font-semibold">{formatCurrency(plan.monthly_payment)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Duration</span>
                      <span className="font-semibold">{plan.duration_months} months</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Interest Rate</span>
                      <span className="font-semibold">{(plan.interest_rate * 100).toFixed(2)}% APR</span>
                    </div>
                    <div className="flex justify-between pt-2 border-t">
                      <span className="text-gray-900 font-semibold">Total Amount Paid</span>
                      <span className="font-bold text-gray-900">{formatCurrency(plan.total_paid)}</span>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Data Source Citations */}
      {costBreakdown.data_sources && costBreakdown.data_sources.length > 0 && (
        <Card className="p-4 bg-gray-50">
          <details className="text-sm">
            <summary className="cursor-pointer font-medium text-gray-700 flex items-center gap-2">
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Data Sources & Methodology
            </summary>
            <div className="mt-3 space-y-2 text-gray-600">
              <p className="font-medium">Cost estimates are based on:</p>
              <ul className="list-disc list-inside space-y-1 ml-2">
                {costBreakdown.data_sources.map((source, index) => (
                  <li key={index}>{source}</li>
                ))}
              </ul>
            </div>
          </details>
        </Card>
      )}

      {/* Medical Disclaimer */}
      <MedicalDisclaimer context="cost" />
    </div>
  );
};
