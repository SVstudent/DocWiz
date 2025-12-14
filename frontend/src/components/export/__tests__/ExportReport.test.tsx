import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ExportReport } from '../ExportReport';
import { useExport } from '@/hooks/useExport';
import { useToast } from '@/hooks/useToast';

// Mock the hooks
jest.mock('@/hooks/useExport');
jest.mock('@/hooks/useToast');

const mockUseExport = useExport as jest.MockedFunction<typeof useExport>;
const mockUseToast = useToast as jest.MockedFunction<typeof useToast>;

describe('ExportReport', () => {
  const mockCreateExport = {
    mutateAsync: jest.fn(),
    isPending: false,
  };

  const mockDownloadExport = jest.fn();
  const mockPollExportStatus = jest.fn(() => ({ isPolling: false, stopPolling: jest.fn() }));
  const mockShowToast = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Suppress console.error for expected error tests
    const originalError = console.error;
    jest.spyOn(console, 'error').mockImplementation((...args) => {
      const message = args[0];
      // Suppress expected error messages from the component
      if (
        typeof message === 'string' &&
        (message.includes('Error creating export:') ||
         message.includes('Error downloading export:'))
      ) {
        return;
      }
      // Let other errors through
      originalError.apply(console, args);
    });
    
    mockUseExport.mockReturnValue({
      createExport: mockCreateExport as any,
      downloadExport: mockDownloadExport,
      pollExportStatus: mockPollExportStatus as any,
      getExportMetadata: jest.fn() as any,
    });
    mockUseToast.mockReturnValue({
      showToast: mockShowToast,
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Format Selection', () => {
    it('should display all format options', () => {
      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      expect(screen.getByText('pdf')).toBeInTheDocument();
      expect(screen.getByText('png')).toBeInTheDocument();
      expect(screen.getByText('jpeg')).toBeInTheDocument();
      expect(screen.getByText('json')).toBeInTheDocument();
    });

    it('should select PDF format by default', () => {
      const { container } = render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      const pdfButton = screen.getByText('pdf').closest('button');
      expect(pdfButton).toHaveClass('border-blue-600');
    });

    it('should change format when a different option is clicked', () => {
      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      const pngButton = screen.getByText('png').closest('button');
      if (pngButton) {
        fireEvent.click(pngButton);
        expect(pngButton).toHaveClass('border-blue-600');
      }
    });

    it('should display format descriptions', () => {
      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      expect(screen.getByText('Document')).toBeInTheDocument();
      expect(screen.getAllByText('Image').length).toBe(2); // PNG and JPEG
      expect(screen.getByText('Data')).toBeInTheDocument();
    });
  });

  describe('Content Selection', () => {
    it('should display all content checkboxes', () => {
      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      expect(screen.getByText('Surgical Visualizations')).toBeInTheDocument();
      expect(screen.getByText('Cost Estimates')).toBeInTheDocument();
      expect(screen.getByText('Procedure Comparisons')).toBeInTheDocument();
    });

    it('should have all content options checked by default', () => {
      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      const checkboxes = screen.getAllByRole('checkbox');
      // First 3 checkboxes are content options (4th is shareable toggle)
      expect(checkboxes[0]).toBeChecked(); // Visualizations
      expect(checkboxes[1]).toBeChecked(); // Cost Estimates
      expect(checkboxes[2]).toBeChecked(); // Comparisons
    });

    it('should toggle content options when clicked', () => {
      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      const visualizationsCheckbox = screen.getByText('Surgical Visualizations')
        .closest('label')
        ?.querySelector('input[type="checkbox"]');

      if (visualizationsCheckbox) {
        fireEvent.click(visualizationsCheckbox);
        expect(visualizationsCheckbox).not.toBeChecked();

        fireEvent.click(visualizationsCheckbox);
        expect(visualizationsCheckbox).toBeChecked();
      }
    });

    it('should display count of selected items when provided', () => {
      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
          visualizationIds={['viz-1', 'viz-2', 'viz-3']}
          costBreakdownIds={['cost-1', 'cost-2']}
          comparisonIds={['comp-1']}
        />
      );

      expect(screen.getByText('(3 selected)')).toBeInTheDocument();
      expect(screen.getByText('(2 selected)')).toBeInTheDocument();
      expect(screen.getByText('(1 selected)')).toBeInTheDocument();
    });
  });

  describe('Shareable Toggle', () => {
    it('should display shareable toggle', () => {
      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      expect(screen.getByText('Create Shareable Version')).toBeInTheDocument();
    });

    it('should have shareable toggle unchecked by default', () => {
      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      const shareableCheckbox = screen.getByText('Create Shareable Version')
        .closest('label')
        ?.querySelector('input[type="checkbox"]');

      expect(shareableCheckbox).not.toBeChecked();
    });

    it('should display shareable description', () => {
      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      expect(screen.getByText(/removes sensitive information/i)).toBeInTheDocument();
    });

    it('should toggle shareable option when clicked', () => {
      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      const shareableCheckbox = screen.getByText('Create Shareable Version')
        .closest('label')
        ?.querySelector('input[type="checkbox"]');

      if (shareableCheckbox) {
        fireEvent.click(shareableCheckbox);
        expect(shareableCheckbox).toBeChecked();
      }
    });
  });

  describe('Export Creation', () => {
    it('should display create export button', () => {
      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      expect(screen.getByRole('button', { name: /create export/i })).toBeInTheDocument();
    });

    it('should call createExport with correct parameters', async () => {
      mockCreateExport.mutateAsync.mockResolvedValue({
        id: 'export-123',
        patient_id: 'patient-123',
        patient_name: 'John Doe',
        format: 'pdf',
        shareable: false,
        created_at: '2024-01-01T00:00:00Z',
        status: 'completed',
        download_url: '/api/exports/export-123/download',
      });

      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      const createButton = screen.getByRole('button', { name: /create export/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(mockCreateExport.mutateAsync).toHaveBeenCalledWith({
          patient_id: 'patient-123',
          format: 'pdf',
          shareable: false,
          include_visualizations: true,
          include_cost_estimates: true,
          include_comparisons: true,
          visualization_ids: undefined,
          cost_breakdown_ids: undefined,
          comparison_ids: undefined,
        });
      });
    });

    it('should include specific IDs when provided', async () => {
      mockCreateExport.mutateAsync.mockResolvedValue({
        id: 'export-123',
        patient_id: 'patient-123',
        patient_name: 'John Doe',
        format: 'pdf',
        shareable: false,
        created_at: '2024-01-01T00:00:00Z',
        status: 'completed',
      });

      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
          visualizationIds={['viz-1', 'viz-2']}
          costBreakdownIds={['cost-1']}
          comparisonIds={['comp-1']}
        />
      );

      const createButton = screen.getByRole('button', { name: /create export/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(mockCreateExport.mutateAsync).toHaveBeenCalledWith(
          expect.objectContaining({
            visualization_ids: ['viz-1', 'viz-2'],
            cost_breakdown_ids: ['cost-1'],
            comparison_ids: ['comp-1'],
          })
        );
      });
    });

    it('should show success toast on successful export creation', async () => {
      mockCreateExport.mutateAsync.mockResolvedValue({
        id: 'export-123',
        patient_id: 'patient-123',
        patient_name: 'John Doe',
        format: 'pdf',
        shareable: false,
        created_at: '2024-01-01T00:00:00Z',
        status: 'completed',
        download_url: '/api/exports/export-123/download',
      });

      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      const createButton = screen.getByRole('button', { name: /create export/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(mockShowToast).toHaveBeenCalledWith({
          type: 'success',
          message: 'Export created successfully!',
        });
      });
    });

    it('should show error toast on export creation failure', async () => {
      mockCreateExport.mutateAsync.mockRejectedValue(new Error('Export failed'));

      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      const createButton = screen.getByRole('button', { name: /create export/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(mockShowToast).toHaveBeenCalledWith({
          type: 'error',
          message: 'Failed to create export. Please try again.',
        });
      });
    });

    it('should disable button during export creation', () => {
      mockUseExport.mockReturnValue({
        createExport: { ...mockCreateExport, isPending: true } as any,
        downloadExport: mockDownloadExport,
        pollExportStatus: mockPollExportStatus as any,
        getExportMetadata: jest.fn() as any,
      });

      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      const createButton = screen.getByRole('button', { name: /creating export/i });
      expect(createButton).toBeDisabled();
    });
  });

  describe('Export Preview', () => {
    it('should display export preview after creation', async () => {
      mockCreateExport.mutateAsync.mockResolvedValue({
        id: 'export-123',
        patient_id: 'patient-123',
        patient_name: 'John Doe',
        format: 'pdf',
        shareable: false,
        created_at: '2024-01-01T00:00:00Z',
        status: 'completed',
        download_url: '/api/exports/export-123/download',
      });

      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      const createButton = screen.getByRole('button', { name: /create export/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByText('Export Preview')).toBeInTheDocument();
      });
    });

    it('should display export details in preview', async () => {
      mockCreateExport.mutateAsync.mockResolvedValue({
        id: 'export-123',
        patient_id: 'patient-123',
        patient_name: 'John Doe',
        format: 'pdf',
        shareable: false,
        created_at: '2024-01-01T00:00:00Z',
        status: 'completed',
        download_url: '/api/exports/export-123/download',
      });

      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      const createButton = screen.getByRole('button', { name: /create export/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByText('Export Preview')).toBeInTheDocument();
        expect(screen.getByText('John Doe')).toBeInTheDocument();
        expect(screen.getByText('Full Report')).toBeInTheDocument();
        expect(screen.getByText('export-123')).toBeInTheDocument();
      });
    });

    it('should show shareable type in preview when shareable is enabled', async () => {
      mockCreateExport.mutateAsync.mockResolvedValue({
        id: 'export-123',
        patient_id: 'patient-123',
        patient_name: 'John Doe',
        format: 'pdf',
        shareable: true,
        created_at: '2024-01-01T00:00:00Z',
        status: 'completed',
        download_url: '/api/exports/export-123/download',
      });

      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      // Enable shareable
      const shareableCheckbox = screen.getByText('Create Shareable Version')
        .closest('label')
        ?.querySelector('input[type="checkbox"]');
      if (shareableCheckbox) {
        fireEvent.click(shareableCheckbox);
      }

      const createButton = screen.getByRole('button', { name: /create export/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByText('Shareable (No Sensitive Data)')).toBeInTheDocument();
      });
    });
  });

  describe('Download Functionality', () => {
    it('should display download button after export creation', async () => {
      mockCreateExport.mutateAsync.mockResolvedValue({
        id: 'export-123',
        patient_id: 'patient-123',
        patient_name: 'John Doe',
        format: 'pdf',
        shareable: false,
        created_at: '2024-01-01T00:00:00Z',
        status: 'completed',
        download_url: '/api/exports/export-123/download',
      });

      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      const createButton = screen.getByRole('button', { name: /create export/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /download/i })).toBeInTheDocument();
      });
    });

    it('should call downloadExport when download button is clicked', async () => {
      mockCreateExport.mutateAsync.mockResolvedValue({
        id: 'export-123',
        patient_id: 'patient-123',
        patient_name: 'John Doe',
        format: 'pdf',
        shareable: false,
        created_at: '2024-01-01T00:00:00Z',
        status: 'completed',
        download_url: '/api/exports/export-123/download',
      });

      mockDownloadExport.mockResolvedValue(undefined);

      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      const createButton = screen.getByRole('button', { name: /create export/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        const downloadButton = screen.getByRole('button', { name: /download/i });
        fireEvent.click(downloadButton);
      });

      await waitFor(() => {
        expect(mockDownloadExport).toHaveBeenCalledWith('export-123');
      });
    });

    it('should show success toast on successful download', async () => {
      mockCreateExport.mutateAsync.mockResolvedValue({
        id: 'export-123',
        patient_id: 'patient-123',
        patient_name: 'John Doe',
        format: 'pdf',
        shareable: false,
        created_at: '2024-01-01T00:00:00Z',
        status: 'completed',
        download_url: '/api/exports/export-123/download',
      });

      mockDownloadExport.mockResolvedValue(undefined);

      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      const createButton = screen.getByRole('button', { name: /create export/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        const downloadButton = screen.getByRole('button', { name: /download/i });
        fireEvent.click(downloadButton);
      });

      await waitFor(() => {
        expect(mockShowToast).toHaveBeenCalledWith({
          type: 'success',
          message: 'Export downloaded successfully!',
        });
      });
    });

    it('should show error toast on download failure', async () => {
      mockCreateExport.mutateAsync.mockResolvedValue({
        id: 'export-123',
        patient_id: 'patient-123',
        patient_name: 'John Doe',
        format: 'pdf',
        shareable: false,
        created_at: '2024-01-01T00:00:00Z',
        status: 'completed',
        download_url: '/api/exports/export-123/download',
      });

      mockDownloadExport.mockRejectedValue(new Error('Download failed'));

      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      const createButton = screen.getByRole('button', { name: /create export/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        const downloadButton = screen.getByRole('button', { name: /download/i });
        fireEvent.click(downloadButton);
      });

      await waitFor(() => {
        expect(mockShowToast).toHaveBeenCalledWith({
          type: 'error',
          message: 'Failed to download export. Please try again.',
        });
      });
    });
  });

  describe('Share Link Generation', () => {
    it('should display share link button when shareable is enabled', async () => {
      mockCreateExport.mutateAsync.mockResolvedValue({
        id: 'export-123',
        patient_id: 'patient-123',
        patient_name: 'John Doe',
        format: 'pdf',
        shareable: true,
        created_at: '2024-01-01T00:00:00Z',
        status: 'completed',
        download_url: '/api/exports/export-123/download',
      });

      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      // Enable shareable
      const shareableCheckbox = screen.getByText('Create Shareable Version')
        .closest('label')
        ?.querySelector('input[type="checkbox"]');
      if (shareableCheckbox) {
        fireEvent.click(shareableCheckbox);
      }

      const createButton = screen.getByRole('button', { name: /create export/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /copy share link/i })).toBeInTheDocument();
      });
    });

    it('should not display share link button when shareable is disabled', async () => {
      mockCreateExport.mutateAsync.mockResolvedValue({
        id: 'export-123',
        patient_id: 'patient-123',
        patient_name: 'John Doe',
        format: 'pdf',
        shareable: false,
        created_at: '2024-01-01T00:00:00Z',
        status: 'completed',
        download_url: '/api/exports/export-123/download',
      });

      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      const createButton = screen.getByRole('button', { name: /create export/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        expect(screen.queryByRole('button', { name: /copy share link/i })).not.toBeInTheDocument();
      });
    });

    it('should copy share link to clipboard when button is clicked', async () => {
      mockCreateExport.mutateAsync.mockResolvedValue({
        id: 'export-123',
        patient_id: 'patient-123',
        patient_name: 'John Doe',
        format: 'pdf',
        shareable: true,
        created_at: '2024-01-01T00:00:00Z',
        status: 'completed',
        download_url: '/api/exports/export-123/download',
      });

      // Mock clipboard API
      Object.assign(navigator, {
        clipboard: {
          writeText: jest.fn().mockResolvedValue(undefined),
        },
      });

      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      // Enable shareable
      const shareableCheckbox = screen.getByText('Create Shareable Version')
        .closest('label')
        ?.querySelector('input[type="checkbox"]');
      if (shareableCheckbox) {
        fireEvent.click(shareableCheckbox);
      }

      const createButton = screen.getByRole('button', { name: /create export/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        const shareButton = screen.getByRole('button', { name: /copy share link/i });
        fireEvent.click(shareButton);
      });

      await waitFor(() => {
        expect(navigator.clipboard.writeText).toHaveBeenCalledWith(
          expect.stringContaining('/shared/exports/export-123')
        );
      });
    });

    it('should show success toast when share link is copied', async () => {
      mockCreateExport.mutateAsync.mockResolvedValue({
        id: 'export-123',
        patient_id: 'patient-123',
        patient_name: 'John Doe',
        format: 'pdf',
        shareable: true,
        created_at: '2024-01-01T00:00:00Z',
        status: 'completed',
        download_url: '/api/exports/export-123/download',
      });

      Object.assign(navigator, {
        clipboard: {
          writeText: jest.fn().mockResolvedValue(undefined),
        },
      });

      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      // Enable shareable
      const shareableCheckbox = screen.getByText('Create Shareable Version')
        .closest('label')
        ?.querySelector('input[type="checkbox"]');
      if (shareableCheckbox) {
        fireEvent.click(shareableCheckbox);
      }

      const createButton = screen.getByRole('button', { name: /create export/i });
      fireEvent.click(createButton);

      await waitFor(() => {
        const shareButton = screen.getByRole('button', { name: /copy share link/i });
        fireEvent.click(shareButton);
      });

      await waitFor(() => {
        expect(mockShowToast).toHaveBeenCalledWith({
          type: 'success',
          message: 'Share link copied to clipboard!',
        });
      });
    });
  });

  describe('Medical Disclaimer', () => {
    it('should display medical disclaimer', () => {
      render(
        <ExportReport
          patientId="patient-123"
          patientName="John Doe"
        />
      );

      expect(screen.getByText(/MEDICAL DISCLAIMER/i)).toBeInTheDocument();
      expect(screen.getByText(/for informational purposes only/i)).toBeInTheDocument();
      expect(screen.getByText(/AI-generated predictions/i)).toBeInTheDocument();
      expect(screen.getByText(/consult with qualified medical professionals/i)).toBeInTheDocument();
    });
  });
});
