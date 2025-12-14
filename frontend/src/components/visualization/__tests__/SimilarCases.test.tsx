import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SimilarCases, SimilarCase, SimilarCasesFilters } from '../SimilarCases';

describe('SimilarCases', () => {
  const mockSimilarCases: SimilarCase[] = [
    {
      id: 'case-1',
      before_image_url: 'https://example.com/before1.jpg',
      after_image_url: 'https://example.com/after1.jpg',
      procedure_type: 'rhinoplasty',
      similarity_score: 0.92,
      outcome_rating: 0.88,
      patient_satisfaction: 5,
      age_range: '26-35',
      anonymized: true,
    },
    {
      id: 'case-2',
      before_image_url: 'https://example.com/before2.jpg',
      after_image_url: 'https://example.com/after2.jpg',
      procedure_type: 'rhinoplasty',
      similarity_score: 0.85,
      outcome_rating: 0.90,
      patient_satisfaction: 4,
      age_range: '26-35',
      anonymized: true,
    },
    {
      id: 'case-3',
      before_image_url: 'https://example.com/before3.jpg',
      after_image_url: 'https://example.com/after3.jpg',
      procedure_type: 'facelift',
      similarity_score: 0.78,
      outcome_rating: 0.85,
      patient_satisfaction: 5,
      age_range: '36-45',
      anonymized: true,
    },
  ];

  const mockFetchSimilarCases = jest.fn();
  const visualizationId = 'viz-123';

  beforeEach(() => {
    jest.clearAllMocks();
    mockFetchSimilarCases.mockResolvedValue(mockSimilarCases);
  });

  describe('Loading State', () => {
    it('should display loading state when isLoading is true', () => {
      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
          isLoading={true}
        />
      );

      // Should show skeleton loaders
      const skeletons = document.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBeGreaterThan(0);
    });

    it('should display loading state while fetching data', async () => {
      mockFetchSimilarCases.mockImplementation(
        () => new Promise((resolve) => setTimeout(() => resolve(mockSimilarCases), 100))
      );

      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      // Should show skeleton loaders initially
      const skeletons = document.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBeGreaterThan(0);

      // Wait for data to load
      await waitFor(() => {
        expect(screen.getByText(/showing 3 similar cases/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error State', () => {
    it('should display error message when fetch fails', async () => {
      const errorMessage = 'Failed to fetch similar cases';
      mockFetchSimilarCases.mockRejectedValue(new Error(errorMessage));

      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/error loading similar cases/i)).toBeInTheDocument();
        expect(screen.getByText(errorMessage)).toBeInTheDocument();
      });
    });

    it('should show try again button on error', async () => {
      mockFetchSimilarCases.mockRejectedValue(new Error('Network error'));

      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
      });
    });

    it('should retry fetch when try again button is clicked', async () => {
      mockFetchSimilarCases
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce(mockSimilarCases);

      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/error loading similar cases/i)).toBeInTheDocument();
      });

      const tryAgainButton = screen.getByRole('button', { name: /try again/i });
      fireEvent.click(tryAgainButton);

      await waitFor(() => {
        expect(mockFetchSimilarCases).toHaveBeenCalledTimes(2);
        expect(screen.getByText(/showing 3 similar cases/i)).toBeInTheDocument();
      });
    });
  });

  describe('Results Display', () => {
    it('should display similar cases in grid layout', async () => {
      const { container } = render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/showing 3 similar cases/i)).toBeInTheDocument();
      });

      // Check that grid is rendered with cases
      const grid = container.querySelector('.grid');
      expect(grid).toBeInTheDocument();
      expect(grid?.children.length).toBe(3);
    });

    it('should display before and after images for each case', async () => {
      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        const images = screen.getAllByRole('img');
        expect(images.length).toBeGreaterThan(0);
      });
    });

    it('should display similarity scores', async () => {
      const { container } = render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/showing 3 similar cases/i)).toBeInTheDocument();
      });

      // Check for similarity score labels
      const similarityLabels = container.querySelectorAll('span');
      const hasSimilarityText = Array.from(similarityLabels).some(
        span => span.textContent?.includes('Similarity')
      );
      expect(hasSimilarityText).toBe(true);
    });

    it('should display outcome ratings', async () => {
      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText('88%')).toBeInTheDocument();
        expect(screen.getByText('90%')).toBeInTheDocument();
      });
    });

    it('should display patient satisfaction stars', async () => {
      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        // Check for star icons (5-star ratings)
        const stars = document.querySelectorAll('.text-yellow-400');
        expect(stars.length).toBeGreaterThan(0);
      });
    });

    it('should display age ranges', async () => {
      const { container } = render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/showing 3 similar cases/i)).toBeInTheDocument();
      });

      // Check for age range text
      const ageTexts = container.querySelectorAll('p');
      const hasAgeText = Array.from(ageTexts).some(
        p => p.textContent?.includes('Age:')
      );
      expect(hasAgeText).toBe(true);
    });
  });

  describe('Empty State', () => {
    it('should display empty state when no cases are found', async () => {
      mockFetchSimilarCases.mockResolvedValue([]);

      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/no similar cases found/i)).toBeInTheDocument();
        expect(screen.getByText(/try adjusting your filters/i)).toBeInTheDocument();
      });
    });

    it('should show results count as 0 when no cases found', async () => {
      mockFetchSimilarCases.mockResolvedValue([]);

      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/showing 0 similar case/i)).toBeInTheDocument();
      });
    });
  });

  describe('Filter Application', () => {
    it('should display filter sidebar', async () => {
      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/filters/i)).toBeInTheDocument();
        expect(screen.getByText(/procedure type/i)).toBeInTheDocument();
        expect(screen.getByText(/minimum outcome quality/i)).toBeInTheDocument();
        expect(screen.getByText(/age range/i)).toBeInTheDocument();
      });
    });

    it('should apply procedure type filter', async () => {
      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/filters/i)).toBeInTheDocument();
      });

      const procedureSelect = screen.getByLabelText(/procedure type/i);
      fireEvent.change(procedureSelect, { target: { value: 'rhinoplasty' } });

      await waitFor(() => {
        expect(mockFetchSimilarCases).toHaveBeenCalledWith(
          visualizationId,
          expect.objectContaining({ procedure_type: 'rhinoplasty' })
        );
      });
    });

    it('should apply outcome quality filter', async () => {
      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/filters/i)).toBeInTheDocument();
      });

      const qualitySlider = screen.getByLabelText(/minimum outcome quality/i);
      fireEvent.change(qualitySlider, { target: { value: '0.8' } });

      await waitFor(() => {
        expect(mockFetchSimilarCases).toHaveBeenCalledWith(
          visualizationId,
          expect.objectContaining({ outcome_quality: 0.8 })
        );
      });
    });

    it('should apply age range filter', async () => {
      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/filters/i)).toBeInTheDocument();
      });

      const ageSelect = screen.getByLabelText(/age range/i);
      fireEvent.change(ageSelect, { target: { value: '26-35' } });

      await waitFor(() => {
        expect(mockFetchSimilarCases).toHaveBeenCalledWith(
          visualizationId,
          expect.objectContaining({ age_range: '26-35' })
        );
      });
    });

    it('should apply results limit filter', async () => {
      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/filters/i)).toBeInTheDocument();
      });

      const limitSelect = screen.getByLabelText(/results to show/i);
      fireEvent.change(limitSelect, { target: { value: '20' } });

      await waitFor(() => {
        expect(mockFetchSimilarCases).toHaveBeenCalledWith(
          visualizationId,
          expect.objectContaining({ limit: 20 })
        );
      });
    });

    it('should show clear all button when filters are applied', async () => {
      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/filters/i)).toBeInTheDocument();
      });

      const procedureSelect = screen.getByLabelText(/procedure type/i);
      fireEvent.change(procedureSelect, { target: { value: 'rhinoplasty' } });

      await waitFor(() => {
        expect(screen.getByText(/clear all/i)).toBeInTheDocument();
      });
    });

    it('should clear all filters when clear all is clicked', async () => {
      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/showing 3 similar cases/i)).toBeInTheDocument();
      });

      // Apply filters
      const procedureSelect = screen.getByLabelText(/procedure type/i);
      fireEvent.change(procedureSelect, { target: { value: 'rhinoplasty' } });

      await waitFor(() => {
        expect(screen.getByText(/clear all/i)).toBeInTheDocument();
      });

      // Clear filters
      const clearButton = screen.getByText(/clear all/i);
      fireEvent.click(clearButton);

      await waitFor(() => {
        // After clearing, should fetch with only limit set
        const lastCall = mockFetchSimilarCases.mock.calls[mockFetchSimilarCases.mock.calls.length - 1];
        expect(lastCall[1]).toEqual({ limit: 10 });
      });
    });
  });

  describe('Case Detail Modal', () => {
    it('should open modal when case is clicked', async () => {
      const { container } = render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/showing 3 similar cases/i)).toBeInTheDocument();
      });

      // Click on first case card
      const caseCard = container.querySelector('.cursor-pointer');
      if (caseCard) {
        fireEvent.click(caseCard);
      }

      await waitFor(() => {
        // Modal should show detailed metrics (check for unique text in modal)
        expect(screen.getByText(/based on facial features and procedure type/i)).toBeInTheDocument();
      });
    });

    it('should display privacy notice in modal', async () => {
      const { container } = render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/showing 3 similar cases/i)).toBeInTheDocument();
      });

      // Click on first case card
      const caseCard = container.querySelector('.cursor-pointer');
      if (caseCard) {
        fireEvent.click(caseCard);
      }

      await waitFor(() => {
        expect(screen.getByText(/privacy protected/i)).toBeInTheDocument();
        expect(screen.getByText(/all patient data has been anonymized/i)).toBeInTheDocument();
      });
    });

    it('should close modal when close button is clicked', async () => {
      const { container } = render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/showing 3 similar cases/i)).toBeInTheDocument();
      });

      // Open modal
      const caseCard = container.querySelector('.cursor-pointer');
      if (caseCard) {
        fireEvent.click(caseCard);
      }

      await waitFor(() => {
        expect(screen.getByText(/similarity score/i)).toBeInTheDocument();
      });

      // Close modal
      const closeButtons = screen.getAllByRole('button');
      const closeButton = closeButtons.find(btn => 
        btn.querySelector('svg path[d*="M6 18L18 6M6 6l12 12"]')
      );
      
      if (closeButton) {
        fireEvent.click(closeButton);
      }

      await waitFor(() => {
        expect(screen.queryByText(/similarity score/i)).not.toBeInTheDocument();
      });
    });

    it('should close modal when clicking outside', async () => {
      const { container } = render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/showing 3 similar cases/i)).toBeInTheDocument();
      });

      // Open modal
      const caseCard = container.querySelector('.cursor-pointer');
      if (caseCard) {
        fireEvent.click(caseCard);
      }

      await waitFor(() => {
        expect(screen.getByText(/similarity score/i)).toBeInTheDocument();
      });

      // Click on backdrop (the fixed inset-0 div)
      const backdrop = container.querySelector('.fixed.inset-0');
      if (backdrop) {
        fireEvent.click(backdrop);
      }

      await waitFor(() => {
        expect(screen.queryByText(/similarity score/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Results Count', () => {
    it('should display correct count for single result', async () => {
      mockFetchSimilarCases.mockResolvedValue([mockSimilarCases[0]]);

      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/showing 1 similar case$/i)).toBeInTheDocument();
      });
    });

    it('should display correct count for multiple results', async () => {
      render(
        <SimilarCases
          visualizationId={visualizationId}
          onFetchSimilarCases={mockFetchSimilarCases}
        />
      );

      await waitFor(() => {
        expect(screen.getByText(/showing 3 similar cases/i)).toBeInTheDocument();
      });
    });
  });
});
