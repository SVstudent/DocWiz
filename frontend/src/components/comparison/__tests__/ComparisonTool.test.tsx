import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ComparisonTool } from '../ComparisonTool';
import { Procedure, ComparisonResult } from '@/store/visualizationStore';

describe('ComparisonTool', () => {
  const mockProcedures: Procedure[] = [
    {
      id: 'proc-1',
      name: 'Rhinoplasty',
      category: 'facial',
      description: 'Nose reshaping surgery',
      typical_cost_range: [5000, 15000],
      recovery_days: 14,
      risk_level: 'medium',
      cpt_codes: ['30400'],
      icd10_codes: ['J34.2'],
    },
    {
      id: 'proc-2',
      name: 'Breast Augmentation',
      category: 'body',
      description: 'Breast enhancement surgery',
      typical_cost_range: [6000, 12000],
      recovery_days: 21,
      risk_level: 'medium',
      cpt_codes: ['19325'],
      icd10_codes: ['N62'],
    },
    {
      id: 'proc-3',
      name: 'Facelift',
      category: 'facial',
      description: 'Facial rejuvenation surgery',
      typical_cost_range: [10000, 25000],
      recovery_days: 28,
      risk_level: 'high',
      cpt_codes: ['15824'],
      icd10_codes: ['L57.4'],
    },
  ];

  // Create a proper ComparisonResult with ProcedureComparisonData
  const mockComparison: ComparisonResult = {
    id: 'comp-123',
    source_image_id: 'img-123',
    patient_id: 'patient-1',
    procedures: [
      {
        procedure_id: 'proc-1',
        procedure_name: 'Rhinoplasty',
        visualization_id: 'viz-1',
        before_image_url: 'https://example.com/before1.jpg',
        after_image_url: 'https://example.com/after1.jpg',
        cost: 10000,
        recovery_days: 14,
        risk_level: 'medium',
      },
      {
        procedure_id: 'proc-2',
        procedure_name: 'Breast Augmentation',
        visualization_id: 'viz-2',
        before_image_url: 'https://example.com/before2.jpg',
        after_image_url: 'https://example.com/after2.jpg',
        cost: 9000,
        recovery_days: 21,
        risk_level: 'medium',
      },
    ],
    cost_differences: {
      'proc-1': 1000,
      'proc-2': 0,
    },
    recovery_differences: {
      'proc-1': -7,
      'proc-2': 0,
    },
    risk_differences: {
      'proc-1': 'medium',
      'proc-2': 'medium',
    },
    created_at: '2024-01-01T00:00:00Z',
    metadata: {},
  };

  const mockSourceImage = 'https://example.com/source.jpg';
  const mockOnCompare = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Loading State', () => {
    it('should display loading state when isLoading is true', () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={null}
          isLoading={true}
        />
      );

      expect(screen.getByText(/generating comparison/i)).toBeInTheDocument();
      expect(screen.getByText(/generating visualizations for all procedures/i)).toBeInTheDocument();
    });

    it('should show loading spinner during generation', () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={null}
          isLoading={true}
        />
      );

      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('should display skeleton cards during loading', () => {
      const { container } = render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={null}
          isLoading={true}
        />
      );

      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('Multi-Procedure Selection', () => {
    it('should display all procedures in selection grid', () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={null}
          isLoading={false}
        />
      );

      expect(screen.getByText('Rhinoplasty')).toBeInTheDocument();
      expect(screen.getByText('Breast Augmentation')).toBeInTheDocument();
      expect(screen.getByText('Facelift')).toBeInTheDocument();
    });

    it('should show procedure details in cards', () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={null}
          isLoading={false}
        />
      );

      expect(screen.getByText('Nose reshaping surgery')).toBeInTheDocument();
      expect(screen.getByText('14 days')).toBeInTheDocument();
      expect(screen.getByText('$5,000 - $15,000')).toBeInTheDocument();
    });

    it('should toggle procedure selection on click', async () => {
      const { container } = render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={null}
          isLoading={false}
        />
      );

      const rhinoplastyCard = screen.getByText('Rhinoplasty').closest('.cursor-pointer');
      
      // Initially not selected
      expect(rhinoplastyCard).not.toHaveClass('ring-2');

      // Click to select
      if (rhinoplastyCard) {
        fireEvent.click(rhinoplastyCard);
      }

      await waitFor(() => {
        expect(rhinoplastyCard).toHaveClass('ring-2');
      });

      // Click again to deselect
      if (rhinoplastyCard) {
        fireEvent.click(rhinoplastyCard);
      }

      await waitFor(() => {
        expect(rhinoplastyCard).not.toHaveClass('ring-2');
      });
    });

    it('should show checkmark on selected procedures', async () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={null}
          isLoading={false}
        />
      );

      const rhinoplastyCard = screen.getByText('Rhinoplasty').closest('.cursor-pointer');
      
      if (rhinoplastyCard) {
        fireEvent.click(rhinoplastyCard);
      }

      await waitFor(() => {
        const checkmark = rhinoplastyCard?.querySelector('svg path[d*="M5 13l4 4L19 7"]');
        expect(checkmark).toBeInTheDocument();
      });
    });

    it('should allow selecting multiple procedures', async () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={null}
          isLoading={false}
        />
      );

      const rhinoplastyCard = screen.getByText('Rhinoplasty').closest('.cursor-pointer');
      const breastCard = screen.getByText('Breast Augmentation').closest('.cursor-pointer');

      if (rhinoplastyCard) {
        fireEvent.click(rhinoplastyCard);
      }

      if (breastCard) {
        fireEvent.click(breastCard);
      }

      await waitFor(() => {
        expect(rhinoplastyCard).toHaveClass('ring-2');
        expect(breastCard).toHaveClass('ring-2');
      });
    });

    it('should display selection count in compare button', async () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={null}
          isLoading={false}
        />
      );

      const rhinoplastyCard = screen.getByText('Rhinoplasty').closest('.cursor-pointer');
      const breastCard = screen.getByText('Breast Augmentation').closest('.cursor-pointer');

      if (rhinoplastyCard) {
        fireEvent.click(rhinoplastyCard);
      }

      if (breastCard) {
        fireEvent.click(breastCard);
      }

      await waitFor(() => {
        expect(screen.getByText(/compare \(2\)/i)).toBeInTheDocument();
      });
    });

    it('should disable compare button when less than 2 procedures selected', () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={null}
          isLoading={false}
        />
      );

      const compareButton = screen.getByRole('button', { name: /compare/i });
      expect(compareButton).toBeDisabled();
    });

    it('should enable compare button when 2 or more procedures selected', async () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={null}
          isLoading={false}
        />
      );

      const rhinoplastyCard = screen.getByText('Rhinoplasty').closest('.cursor-pointer');
      const breastCard = screen.getByText('Breast Augmentation').closest('.cursor-pointer');

      if (rhinoplastyCard) {
        fireEvent.click(rhinoplastyCard);
      }

      if (breastCard) {
        fireEvent.click(breastCard);
      }

      await waitFor(() => {
        const compareButton = screen.getByRole('button', { name: /compare \(2\)/i });
        expect(compareButton).not.toBeDisabled();
      });
    });

    it('should call onCompare with selected procedure IDs', async () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={null}
          isLoading={false}
        />
      );

      const rhinoplastyCard = screen.getByText('Rhinoplasty').closest('.cursor-pointer');
      const breastCard = screen.getByText('Breast Augmentation').closest('.cursor-pointer');

      if (rhinoplastyCard) {
        fireEvent.click(rhinoplastyCard);
      }

      if (breastCard) {
        fireEvent.click(breastCard);
      }

      await waitFor(() => {
        const compareButton = screen.getByRole('button', { name: /compare \(2\)/i });
        fireEvent.click(compareButton);
      });

      expect(mockOnCompare).toHaveBeenCalledWith(['proc-1', 'proc-2']);
    });

    it('should show clear button when procedures are selected', async () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={null}
          isLoading={false}
        />
      );

      const rhinoplastyCard = screen.getByText('Rhinoplasty').closest('.cursor-pointer');

      if (rhinoplastyCard) {
        fireEvent.click(rhinoplastyCard);
      }

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /clear \(1\)/i })).toBeInTheDocument();
      });
    });

    it('should clear selection when clear button is clicked', async () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={null}
          isLoading={false}
        />
      );

      const rhinoplastyCard = screen.getByText('Rhinoplasty').closest('.cursor-pointer');

      if (rhinoplastyCard) {
        fireEvent.click(rhinoplastyCard);
      }

      await waitFor(() => {
        expect(rhinoplastyCard).toHaveClass('ring-2');
      });

      const clearButton = screen.getByRole('button', { name: /clear \(1\)/i });
      fireEvent.click(clearButton);

      await waitFor(() => {
        expect(rhinoplastyCard).not.toHaveClass('ring-2');
      });
    });
  });

  describe('Comparison Display', () => {
    it('should display comparison results when comparison is provided', () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={mockComparison}
          isLoading={false}
        />
      );

      expect(screen.getByText(/procedure comparison/i)).toBeInTheDocument();
      expect(screen.getByText(/comparing 2 procedures/i)).toBeInTheDocument();
    });

    it('should display all compared procedures', () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={mockComparison}
          isLoading={false}
        />
      );

      expect(screen.getByText('Rhinoplasty')).toBeInTheDocument();
      expect(screen.getByText('Breast Augmentation')).toBeInTheDocument();
    });

    it('should display after images for all procedures', () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={mockComparison}
          isLoading={false}
        />
      );

      const afterImages = screen.getAllByAltText(/after/i);
      expect(afterImages).toHaveLength(2);
    });

    it('should display cost for each procedure', () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={mockComparison}
          isLoading={false}
        />
      );

      expect(screen.getByText('$10,000')).toBeInTheDocument();
      expect(screen.getByText('$9,000')).toBeInTheDocument();
    });

    it('should display recovery days for each procedure', () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={mockComparison}
          isLoading={false}
        />
      );

      expect(screen.getByText('14 days')).toBeInTheDocument();
      expect(screen.getByText('21 days')).toBeInTheDocument();
    });

    it('should display risk level badges', () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={mockComparison}
          isLoading={false}
        />
      );

      const riskBadges = screen.getAllByText('medium');
      expect(riskBadges.length).toBeGreaterThan(0);
    });

    it('should show new comparison button', () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={mockComparison}
          isLoading={false}
        />
      );

      expect(screen.getByRole('button', { name: /new comparison/i })).toBeInTheDocument();
    });

    it('should display comparison summary', () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={mockComparison}
          isLoading={false}
        />
      );

      expect(screen.getByText(/comparison summary/i)).toBeInTheDocument();
      expect(screen.getByText(/cost range/i)).toBeInTheDocument();
      expect(screen.getByText(/recovery range/i)).toBeInTheDocument();
      expect(screen.getByText(/risk levels/i)).toBeInTheDocument();
    });
  });

  describe('Synchronized Zoom', () => {
    it('should display zoom controls', () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={mockComparison}
          isLoading={false}
        />
      );

      expect(screen.getByText('100%')).toBeInTheDocument();
    });

    it('should zoom in all images when zoom in button is clicked', async () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={mockComparison}
          isLoading={false}
        />
      );

      const zoomInButton = screen.getAllByRole('button').find(
        (btn) => btn.querySelector('svg path[d*="M10 7v3m0 0v3"]')
      );

      if (zoomInButton) {
        fireEvent.click(zoomInButton);
      }

      await waitFor(() => {
        expect(screen.getByText('125%')).toBeInTheDocument();
      });
    });

    it('should zoom out all images when zoom out button is clicked', async () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={mockComparison}
          isLoading={false}
        />
      );

      // First zoom in
      const zoomInButton = screen.getAllByRole('button').find(
        (btn) => btn.querySelector('svg path[d*="M10 7v3m0 0v3"]')
      );

      if (zoomInButton) {
        fireEvent.click(zoomInButton);
      }

      await waitFor(() => {
        expect(screen.getByText('125%')).toBeInTheDocument();
      });

      // Then zoom out
      const zoomOutButton = screen.getAllByRole('button').find(
        (btn) => btn.querySelector('svg path[d*="M13 10H7"]')
      );

      if (zoomOutButton) {
        fireEvent.click(zoomOutButton);
      }

      await waitFor(() => {
        expect(screen.getByText('100%')).toBeInTheDocument();
      });
    });

    it('should show reset view button when zoomed', async () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={mockComparison}
          isLoading={false}
        />
      );

      const zoomInButton = screen.getAllByRole('button').find(
        (btn) => btn.querySelector('svg path[d*="M10 7v3m0 0v3"]')
      );

      if (zoomInButton) {
        fireEvent.click(zoomInButton);
      }

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /reset view/i })).toBeInTheDocument();
      });
    });

    it('should reset zoom when reset view button is clicked', async () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={mockComparison}
          isLoading={false}
        />
      );

      const zoomInButton = screen.getAllByRole('button').find(
        (btn) => btn.querySelector('svg path[d*="M10 7v3m0 0v3"]')
      );

      if (zoomInButton) {
        fireEvent.click(zoomInButton);
      }

      await waitFor(() => {
        expect(screen.getByText('125%')).toBeInTheDocument();
      });

      const resetButton = screen.getByRole('button', { name: /reset view/i });
      fireEvent.click(resetButton);

      await waitFor(() => {
        expect(screen.getByText('100%')).toBeInTheDocument();
      });
    });
  });

  describe('Source Image Display', () => {
    it('should display source image when no comparison exists', () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={null}
          isLoading={false}
        />
      );

      expect(screen.getByText(/source image/i)).toBeInTheDocument();
      const sourceImg = screen.getByAltText('Source');
      expect(sourceImg).toHaveAttribute('src', mockSourceImage);
    });
  });

  describe('Risk Level Badges', () => {
    it('should display low risk with green badge', () => {
      const lowRiskProcedures = [
        {
          ...mockProcedures[0],
          risk_level: 'low' as const,
        },
      ];

      render(
        <ComparisonTool
          procedures={lowRiskProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={null}
          isLoading={false}
        />
      );

      const badge = screen.getByText('low');
      expect(badge).toHaveClass('bg-green-100');
    });

    it('should display medium risk with yellow badge', () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={null}
          isLoading={false}
        />
      );

      const badges = screen.getAllByText('medium');
      expect(badges[0]).toHaveClass('bg-yellow-100');
    });

    it('should display high risk with red badge', () => {
      render(
        <ComparisonTool
          procedures={mockProcedures}
          sourceImage={mockSourceImage}
          onCompare={mockOnCompare}
          comparison={null}
          isLoading={false}
        />
      );

      const badge = screen.getByText('high');
      expect(badge).toHaveClass('bg-red-100');
    });
  });
});
