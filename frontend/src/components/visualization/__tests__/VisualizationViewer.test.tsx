import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { VisualizationViewer } from '../VisualizationViewer';
import { VisualizationResult } from '@/store/visualizationStore';

describe('VisualizationViewer', () => {
  const mockVisualization: VisualizationResult = {
    id: 'viz-123',
    patient_id: 'patient-456',
    procedure_id: 'proc-789',
    before_image_url: 'https://example.com/before.jpg',
    after_image_url: 'https://example.com/after.jpg',
    prompt_used: 'Test prompt',
    generated_at: '2024-01-01T00:00:00Z',
    confidence_score: 0.95,
    embedding: [0.1, 0.2, 0.3],
    metadata: { test: 'data' },
  };

  const mockOnSave = jest.fn();
  const mockOnRegenerate = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Loading State', () => {
    it('should display loading state when isLoading is true', () => {
      render(
        <VisualizationViewer
          visualization={null}
          isLoading={true}
          onSave={mockOnSave}
          onRegenerate={mockOnRegenerate}
        />
      );

      expect(screen.getByText(/generating surgical preview/i)).toBeInTheDocument();
      expect(screen.getByText(/this may take up to 10 seconds/i)).toBeInTheDocument();
    });

    it('should show loading spinner during generation', () => {
      render(
        <VisualizationViewer
          visualization={null}
          isLoading={true}
        />
      );

      const spinner = document.querySelector('.animate-spin');
      expect(spinner).toBeInTheDocument();
    });

    it('should not display action buttons during loading', () => {
      render(
        <VisualizationViewer
          visualization={null}
          isLoading={true}
          onSave={mockOnSave}
          onRegenerate={mockOnRegenerate}
        />
      );

      expect(screen.queryByRole('button', { name: /save/i })).not.toBeInTheDocument();
      expect(screen.queryByRole('button', { name: /regenerate/i })).not.toBeInTheDocument();
    });
  });

  describe('Empty State', () => {
    it('should display empty state when no visualization is provided', () => {
      render(
        <VisualizationViewer
          visualization={null}
          isLoading={false}
        />
      );

      expect(screen.getByText(/no visualization yet/i)).toBeInTheDocument();
      expect(screen.getByText(/upload an image and select a procedure/i)).toBeInTheDocument();
    });

    it('should show placeholder icon in empty state', () => {
      render(
        <VisualizationViewer
          visualization={null}
          isLoading={false}
        />
      );

      const icon = screen.getByText(/no visualization yet/i).parentElement?.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });
  });

  describe('Image Display', () => {
    it('should display before and after images when visualization is provided', () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      const beforeImage = screen.getByAltText(/before surgery/i);
      const afterImage = screen.getByAltText(/after surgery preview/i);

      expect(beforeImage).toBeInTheDocument();
      expect(afterImage).toBeInTheDocument();
      expect(beforeImage).toHaveAttribute('src', mockVisualization.before_image_url);
      expect(afterImage).toHaveAttribute('src', mockVisualization.after_image_url);
    });

    it('should display before and after labels', () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      expect(screen.getByText('Before')).toBeInTheDocument();
      expect(screen.getByText('After')).toBeInTheDocument();
    });

    it('should display confidence score', () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      expect(screen.getByText(/confidence: 95\.0%/i)).toBeInTheDocument();
    });

    it('should display generation timestamp', () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      expect(screen.getByText(/generated on/i)).toBeInTheDocument();
    });
  });

  describe('Comparison Slider', () => {
    it('should render comparison slider', () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      const slider = document.querySelector('.cursor-ew-resize');
      expect(slider).toBeInTheDocument();
    });

    it('should start slider at 50% position', () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      const slider = document.querySelector('.cursor-ew-resize') as HTMLElement;
      expect(slider.style.left).toBe('50%');
    });

    it('should update slider position on mouse drag', async () => {
      const { container } = render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      const slider = container.querySelector('.cursor-ew-resize') as HTMLElement;
      const viewerContainer = container.querySelector('.cursor-move') as HTMLElement;

      // Simulate mouse down on slider
      fireEvent.mouseDown(slider);

      // Simulate mouse move on container
      fireEvent.mouseMove(viewerContainer, {
        clientX: 300,
        clientY: 200,
      });

      // The slider position should have changed
      await waitFor(() => {
        expect(slider.style.left).not.toBe('50%');
      });

      // Simulate mouse up
      fireEvent.mouseUp(viewerContainer);
    });

    it('should handle touch events for mobile', async () => {
      const { container } = render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      const slider = container.querySelector('.cursor-ew-resize') as HTMLElement;
      const viewerContainer = container.querySelector('.cursor-move') as HTMLElement;

      // Simulate touch start
      fireEvent.touchStart(slider);

      // Simulate touch move
      fireEvent.touchMove(viewerContainer, {
        touches: [{ clientX: 400, clientY: 200 }],
      });

      await waitFor(() => {
        expect(slider.style.left).not.toBe('50%');
      });

      // Simulate touch end
      fireEvent.touchEnd(viewerContainer);
    });

    it('should constrain slider position between 0% and 100%', async () => {
      const { container } = render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      const slider = container.querySelector('.cursor-ew-resize') as HTMLElement;
      const viewerContainer = container.querySelector('.cursor-move') as HTMLElement;

      // Mock getBoundingClientRect
      jest.spyOn(viewerContainer, 'getBoundingClientRect').mockReturnValue({
        left: 0,
        width: 1000,
        top: 0,
        right: 1000,
        bottom: 500,
        height: 500,
        x: 0,
        y: 0,
        toJSON: () => ({}),
      });

      fireEvent.mouseDown(slider);

      // Try to move beyond right edge
      fireEvent.mouseMove(viewerContainer, {
        clientX: 2000,
        clientY: 200,
      });

      await waitFor(() => {
        const position = parseFloat(slider.style.left);
        expect(position).toBeLessThanOrEqual(100);
      });

      fireEvent.mouseUp(viewerContainer);
    });
  });

  describe('Zoom Controls', () => {
    it('should display zoom controls', () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      expect(screen.getByText('100%')).toBeInTheDocument();
    });

    it('should zoom in when zoom in button is clicked', async () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      const zoomInButton = screen.getAllByRole('button').find(
        (btn) => btn.querySelector('svg path[d*="M10 7v3m0 0v3"]')
      );

      expect(screen.getByText('100%')).toBeInTheDocument();

      if (zoomInButton) {
        fireEvent.click(zoomInButton);
      }

      await waitFor(() => {
        expect(screen.getByText('125%')).toBeInTheDocument();
      });
    });

    it('should zoom out when zoom out button is clicked', async () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
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

    it('should disable zoom out button at minimum zoom', () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      const zoomOutButton = screen.getAllByRole('button').find(
        (btn) => btn.querySelector('svg path[d*="M13 10H7"]')
      );

      expect(zoomOutButton).toBeDisabled();
    });

    it('should disable zoom in button at maximum zoom', async () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      const zoomInButton = screen.getAllByRole('button').find(
        (btn) => btn.querySelector('svg path[d*="M10 7v3m0 0v3"]')
      );

      // Zoom in to maximum (3x = 300%)
      if (zoomInButton) {
        for (let i = 0; i < 8; i++) {
          fireEvent.click(zoomInButton);
        }
      }

      await waitFor(() => {
        expect(zoomInButton).toBeDisabled();
      });
    });

    it('should show reset button when zoomed in', async () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
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
        expect(screen.getByRole('button', { name: /reset/i })).toBeInTheDocument();
      });
    });

    it('should reset zoom when reset button is clicked', async () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
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

      const resetButton = screen.getByRole('button', { name: /reset/i });
      fireEvent.click(resetButton);

      await waitFor(() => {
        expect(screen.getByText('100%')).toBeInTheDocument();
      });
    });
  });

  describe('Save Functionality', () => {
    it('should display save button when onSave is provided', () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
          onSave={mockOnSave}
        />
      );

      expect(screen.getByRole('button', { name: /save/i })).toBeInTheDocument();
    });

    it('should not display save button when onSave is not provided', () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      expect(screen.queryByRole('button', { name: /save/i })).not.toBeInTheDocument();
    });

    it('should call onSave when save button is clicked', async () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
          onSave={mockOnSave}
        />
      );

      const saveButton = screen.getByRole('button', { name: /save/i });
      fireEvent.click(saveButton);

      await waitFor(() => {
        expect(mockOnSave).toHaveBeenCalledTimes(1);
      });
    });
  });

  describe('Regenerate Functionality', () => {
    it('should display regenerate button when onRegenerate is provided', () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
          onRegenerate={mockOnRegenerate}
        />
      );

      expect(screen.getByRole('button', { name: /regenerate/i })).toBeInTheDocument();
    });

    it('should not display regenerate button when onRegenerate is not provided', () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      expect(screen.queryByRole('button', { name: /regenerate/i })).not.toBeInTheDocument();
    });

    it('should call onRegenerate when regenerate button is clicked', async () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
          onRegenerate={mockOnRegenerate}
        />
      );

      const regenerateButton = screen.getByRole('button', { name: /regenerate/i });
      fireEvent.click(regenerateButton);

      await waitFor(() => {
        expect(mockOnRegenerate).toHaveBeenCalledTimes(1);
      });
    });
  });

  describe('Metadata Display', () => {
    it('should display metadata section', () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      expect(screen.getByText(/view technical details/i)).toBeInTheDocument();
    });

    it('should expand metadata details when clicked', async () => {
      render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      const detailsToggle = screen.getByText(/view technical details/i);
      fireEvent.click(detailsToggle);

      await waitFor(() => {
        expect(screen.getByText(/"test": "data"/i)).toBeInTheDocument();
      });
    });

    it('should not show metadata details when metadata is empty', () => {
      const vizWithoutMetadata = {
        ...mockVisualization,
        metadata: {},
      };

      render(
        <VisualizationViewer
          visualization={vizWithoutMetadata}
          isLoading={false}
        />
      );

      expect(screen.queryByText(/view technical details/i)).not.toBeInTheDocument();
    });
  });

  describe('State Reset', () => {
    it('should reset zoom and pan when visualization changes', async () => {
      const { rerender } = render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      // Zoom in
      const zoomInButton = screen.getAllByRole('button').find(
        (btn) => btn.querySelector('svg path[d*="M10 7v3m0 0v3"]')
      );

      if (zoomInButton) {
        fireEvent.click(zoomInButton);
      }

      await waitFor(() => {
        expect(screen.getByText('125%')).toBeInTheDocument();
      });

      // Change visualization
      const newVisualization = {
        ...mockVisualization,
        id: 'viz-new',
      };

      rerender(
        <VisualizationViewer
          visualization={newVisualization}
          isLoading={false}
        />
      );

      // Zoom should be reset
      await waitFor(() => {
        expect(screen.getByText('100%')).toBeInTheDocument();
      });
    });

    it('should reset slider position when visualization changes', async () => {
      const { container, rerender } = render(
        <VisualizationViewer
          visualization={mockVisualization}
          isLoading={false}
        />
      );

      const slider = container.querySelector('.cursor-ew-resize') as HTMLElement;
      const viewerContainer = container.querySelector('.cursor-move') as HTMLElement;

      // Move slider
      fireEvent.mouseDown(slider);
      fireEvent.mouseMove(viewerContainer, {
        clientX: 300,
        clientY: 200,
      });
      fireEvent.mouseUp(viewerContainer);

      // Change visualization
      const newVisualization = {
        ...mockVisualization,
        id: 'viz-new-2',
      };

      rerender(
        <VisualizationViewer
          visualization={newVisualization}
          isLoading={false}
        />
      );

      // Slider should be reset to 50%
      await waitFor(() => {
        expect(slider.style.left).toBe('50%');
      });
    });
  });
});
