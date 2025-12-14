import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CostDashboard } from '../CostDashboard';
import { CostBreakdown } from '@/store/costStore';
import { useCost } from '@/hooks/useCost';
import { useToast } from '@/hooks/useToast';

// Mock the hooks
jest.mock('@/hooks/useCost');
jest.mock('@/hooks/useToast');

const mockUseCost = useCost as jest.MockedFunction<typeof useCost>;
const mockUseToast = useToast as jest.MockedFunction<typeof useToast>;

describe('CostDashboard', () => {
  const mockCostBreakdown: CostBreakdown = {
    id: 'cost-123',
    procedure_id: 'proc-456',
    patient_id: 'patient-789',
    surgeon_fee: 5000,
    facility_fee: 3000,
    anesthesia_fee: 1500,
    post_op_care: 500,
    total_cost: 10000,
    insurance_coverage: 7000,
    patient_responsibility: 3000,
    deductible: 1000,
    copay: 500,
    out_of_pocket_max: 5000,
    payment_plans: [
      {
        name: '12-Month Plan',
        monthly_payment: 275,
        duration_months: 12,
        interest_rate: 0.05,
        total_paid: 3300,
      },
      {
        name: '24-Month Plan',
        monthly_payment: 145,
        duration_months: 24,
        interest_rate: 0.08,
        total_paid: 3480,
      },
    ],
    calculated_at: '2024-01-01T00:00:00Z',
    data_sources: [
      'National Average Pricing Database',
      'Regional Healthcare Cost Index',
      'Insurance Provider Network Rates',
    ],
  };

  const mockExportCost = {
    mutateAsync: jest.fn(),
    isPending: false,
  };

  const mockShowToast = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    mockUseCost.mockReturnValue({
      exportCost: mockExportCost as any,
      calculateCost: {} as any,
      getCostBreakdown: jest.fn() as any,
      getCostInfographic: jest.fn() as any,
    });
    mockUseToast.mockReturnValue({
      showToast: mockShowToast,
    });
  });

  describe('Loading State', () => {
    it('should display loading skeleton when isLoading is true', () => {
      render(
        <CostDashboard
          costBreakdown={null}
          isLoading={true}
        />
      );

      const loadingElements = document.querySelectorAll('.animate-pulse');
      expect(loadingElements.length).toBeGreaterThan(0);
    });

    it('should not display cost data during loading', () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={true}
        />
      );

      expect(screen.queryByText(/cost breakdown/i)).not.toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('should display empty state when no cost breakdown is provided', () => {
      render(
        <CostDashboard
          costBreakdown={null}
          isLoading={false}
        />
      );

      expect(screen.getByText(/no cost estimate available/i)).toBeInTheDocument();
      expect(screen.getByText(/select a procedure and complete your profile/i)).toBeInTheDocument();
    });

    it('should show placeholder icon in empty state', () => {
      render(
        <CostDashboard
          costBreakdown={null}
          isLoading={false}
        />
      );

      const icon = screen.getByText(/no cost estimate available/i).parentElement?.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });
  });

  describe('Cost Display', () => {
    it('should display all cost components', () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      expect(screen.getByText('Surgeon Fee')).toBeInTheDocument();
      expect(screen.getByText('Facility Fee')).toBeInTheDocument();
      expect(screen.getByText('Anesthesia')).toBeInTheDocument();
      expect(screen.getByText('Post-Op Care')).toBeInTheDocument();
    });

    it('should display formatted currency amounts', () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      expect(screen.getAllByText('$5,000').length).toBeGreaterThan(0);
      expect(screen.getAllByText('$3,000').length).toBeGreaterThan(0);
      expect(screen.getAllByText('$1,500').length).toBeGreaterThan(0);
      expect(screen.getAllByText('$500').length).toBeGreaterThan(0);
    });

    it('should display total cost', () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      expect(screen.getByText('Total Cost')).toBeInTheDocument();
      const totalCostElements = screen.getAllByText('$10,000');
      expect(totalCostElements.length).toBeGreaterThan(0);
    });

    it('should display calculation date', () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      expect(screen.getByText(/calculated on/i)).toBeInTheDocument();
    });
  });

  describe('Visual Cost Breakdown', () => {
    it('should render horizontal bar chart', () => {
      const { container } = render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      const barChart = container.querySelector('.flex.h-12.rounded-lg');
      expect(barChart).toBeInTheDocument();
    });

    it('should display correct percentages in bar chart', () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      // Surgeon fee: 5000/10000 = 50%
      expect(screen.getByText('50%')).toBeInTheDocument();
      // Facility fee: 3000/10000 = 30%
      expect(screen.getByText('30%')).toBeInTheDocument();
      // Anesthesia: 1500/10000 = 15%
      expect(screen.getByText('15%')).toBeInTheDocument();
    });

    it('should show color-coded legend', () => {
      const { container } = render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      const colorBoxes = container.querySelectorAll('.w-4.h-4.rounded');
      expect(colorBoxes.length).toBe(4); // One for each cost component
    });
  });

  describe('Insurance Coverage Calculator', () => {
    it('should display insurance coverage section', () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      const insuranceCoverageElements = screen.getAllByText('Insurance Coverage');
      expect(insuranceCoverageElements.length).toBeGreaterThan(0);
    });

    it('should display all insurance calculation fields', () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      expect(screen.getByText('Total Procedure Cost')).toBeInTheDocument();
      const insuranceCoverageElements = screen.getAllByText('Insurance Coverage');
      expect(insuranceCoverageElements.length).toBeGreaterThan(0);
      expect(screen.getByText('Deductible')).toBeInTheDocument();
      expect(screen.getByText('Co-pay')).toBeInTheDocument();
      expect(screen.getByText('Your Responsibility')).toBeInTheDocument();
      expect(screen.getByText('Out-of-Pocket Maximum')).toBeInTheDocument();
    });

    it('should display insurance coverage as negative amount', () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      expect(screen.getByText('-$7,000')).toBeInTheDocument();
    });

    it('should highlight patient responsibility', () => {
      const { container } = render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      const responsibilitySection = container.querySelector('.bg-blue-50');
      expect(responsibilitySection).toBeInTheDocument();
      expect(responsibilitySection?.textContent).toContain('Your Responsibility');
      expect(responsibilitySection?.textContent).toContain('$3,000');
    });
  });

  describe('Payment Plan Options', () => {
    it('should display payment plan section when plans are available', () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      expect(screen.getByText('Payment Plan Options')).toBeInTheDocument();
    });

    it('should display all payment plans', () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      expect(screen.getByText('12-Month Plan')).toBeInTheDocument();
      expect(screen.getByText('24-Month Plan')).toBeInTheDocument();
    });

    it('should display monthly payment and duration for each plan', () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      expect(screen.getByText(/\$275\/month for 12 months/i)).toBeInTheDocument();
      expect(screen.getByText(/\$145\/month for 24 months/i)).toBeInTheDocument();
    });

    it('should expand payment plan details when clicked', async () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      const planButton = screen.getByText('12-Month Plan').closest('button');
      expect(planButton).toBeInTheDocument();

      if (planButton) {
        fireEvent.click(planButton);
      }

      await waitFor(() => {
        expect(screen.getByText('Monthly Payment')).toBeInTheDocument();
        expect(screen.getByText('Duration')).toBeInTheDocument();
        expect(screen.getByText('Interest Rate')).toBeInTheDocument();
        expect(screen.getByText('Total Amount Paid')).toBeInTheDocument();
      });
    });

    it('should display interest rate as percentage', async () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      const planButton = screen.getByText('12-Month Plan').closest('button');
      if (planButton) {
        fireEvent.click(planButton);
      }

      await waitFor(() => {
        expect(screen.getByText('5.00% APR')).toBeInTheDocument();
      });
    });

    it('should collapse payment plan when clicked again', async () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      const planButton = screen.getByText('12-Month Plan').closest('button');
      
      if (planButton) {
        // Expand
        fireEvent.click(planButton);
        await waitFor(() => {
          expect(screen.getByText('Monthly Payment')).toBeInTheDocument();
        });

        // Collapse
        fireEvent.click(planButton);
        await waitFor(() => {
          expect(screen.queryByText('Monthly Payment')).not.toBeInTheDocument();
        });
      }
    });

    it('should not display payment plan section when no plans are available', () => {
      const costWithoutPlans = {
        ...mockCostBreakdown,
        payment_plans: [],
      };

      render(
        <CostDashboard
          costBreakdown={costWithoutPlans}
          isLoading={false}
        />
      );

      expect(screen.queryByText('Payment Plan Options')).not.toBeInTheDocument();
    });
  });

  describe('Export Functionality', () => {
    it('should display export buttons', () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      expect(screen.getByRole('button', { name: /pdf/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /png/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /json/i })).toBeInTheDocument();
    });

    it('should call export function when PDF button is clicked', async () => {
      mockExportCost.mutateAsync.mockResolvedValue({});

      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      const pdfButton = screen.getByRole('button', { name: /pdf/i });
      fireEvent.click(pdfButton);

      await waitFor(() => {
        expect(mockExportCost.mutateAsync).toHaveBeenCalledWith({
          costBreakdownId: 'cost-123',
          format: 'pdf',
          patientId: 'patient-789',
        });
      });
    });

    it('should call export function when PNG button is clicked', async () => {
      mockExportCost.mutateAsync.mockResolvedValue({});

      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      const pngButton = screen.getByRole('button', { name: /png/i });
      fireEvent.click(pngButton);

      await waitFor(() => {
        expect(mockExportCost.mutateAsync).toHaveBeenCalledWith({
          costBreakdownId: 'cost-123',
          format: 'png',
          patientId: 'patient-789',
        });
      });
    });

    it('should call export function when JSON button is clicked', async () => {
      mockExportCost.mutateAsync.mockResolvedValue({});

      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      const jsonButton = screen.getByRole('button', { name: /json/i });
      fireEvent.click(jsonButton);

      await waitFor(() => {
        expect(mockExportCost.mutateAsync).toHaveBeenCalledWith({
          costBreakdownId: 'cost-123',
          format: 'json',
          patientId: 'patient-789',
        });
      });
    });

    it('should show success toast on successful export', async () => {
      mockExportCost.mutateAsync.mockResolvedValue({});

      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      const pdfButton = screen.getByRole('button', { name: /pdf/i });
      fireEvent.click(pdfButton);

      await waitFor(() => {
        expect(mockShowToast).toHaveBeenCalledWith({
          type: 'success',
          message: 'Cost estimate exported as PDF',
        });
      });
    });

    it('should show error toast on export failure', async () => {
      mockExportCost.mutateAsync.mockRejectedValue(new Error('Export failed'));

      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      const pdfButton = screen.getByRole('button', { name: /pdf/i });
      fireEvent.click(pdfButton);

      await waitFor(() => {
        expect(mockShowToast).toHaveBeenCalledWith({
          type: 'error',
          message: 'Failed to export cost estimate',
        });
      });
    });

    it('should disable export buttons during export', () => {
      mockUseCost.mockReturnValue({
        exportCost: { ...mockExportCost, isPending: true } as any,
        calculateCost: {} as any,
        getCostBreakdown: jest.fn() as any,
        getCostInfographic: jest.fn() as any,
      });

      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      const exportingButtons = screen.getAllByRole('button', { name: /exporting/i });
      exportingButtons.forEach(button => {
        expect(button).toBeDisabled();
      });
    });

    it('should call onExport callback when provided', async () => {
      const mockOnExport = jest.fn();
      mockExportCost.mutateAsync.mockResolvedValue({});

      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
          onExport={mockOnExport}
        />
      );

      const pdfButton = screen.getByRole('button', { name: /pdf/i });
      fireEvent.click(pdfButton);

      await waitFor(() => {
        expect(mockOnExport).toHaveBeenCalledWith('pdf');
      });
    });
  });

  describe('Data Sources', () => {
    it('should display data sources section when sources are available', () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      expect(screen.getByText(/data sources & methodology/i)).toBeInTheDocument();
    });

    it('should expand data sources when clicked', async () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      const detailsToggle = screen.getByText(/data sources & methodology/i);
      fireEvent.click(detailsToggle);

      await waitFor(() => {
        expect(screen.getByText('National Average Pricing Database')).toBeInTheDocument();
        expect(screen.getByText('Regional Healthcare Cost Index')).toBeInTheDocument();
        expect(screen.getByText('Insurance Provider Network Rates')).toBeInTheDocument();
      });
    });

    it('should display medical disclaimer', () => {
      render(
        <CostDashboard
          costBreakdown={mockCostBreakdown}
          isLoading={false}
        />
      );

      // Check for the medical disclaimer component
      expect(screen.getByText('Cost Estimate Disclaimer')).toBeInTheDocument();
      expect(screen.getByText(/approximations based on available data/i)).toBeInTheDocument();
      expect(screen.getByText(/consult with your healthcare provider/i)).toBeInTheDocument();
    });

    it('should not display data sources section when no sources are available', () => {
      const costWithoutSources = {
        ...mockCostBreakdown,
        data_sources: [],
      };

      render(
        <CostDashboard
          costBreakdown={costWithoutSources}
          isLoading={false}
        />
      );

      expect(screen.queryByText(/data sources & methodology/i)).not.toBeInTheDocument();
    });
  });
});
