import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { InsuranceClaim } from '../InsuranceClaim';
import { useInsurance } from '@/hooks/useInsurance';
import { useToast } from '@/hooks/useToast';

// Mock the hooks
jest.mock('@/hooks/useInsurance');
jest.mock('@/hooks/useToast');

const mockUseInsurance = useInsurance as jest.MockedFunction<typeof useInsurance>;
const mockUseToast = useToast as jest.MockedFunction<typeof useToast>;

// Mock DOM methods for download functionality
const mockCreateObjectURL = jest.fn(() => 'blob:mock-url');
const mockRevokeObjectURL = jest.fn();
const mockAppendChild = jest.fn();
const mockRemoveChild = jest.fn();
const mockClick = jest.fn();

describe('InsuranceClaim', () => {
  const mockPreAuthForm = {
    id: 'claim-123',
    patient_id: 'patient-456',
    procedure_id: 'proc-789',
    cost_breakdown_id: 'cost-101',
    cpt_codes: ['15820', '15821'],
    icd10_codes: ['Q18.0', 'Q36.9'],
    medical_justification: 'This procedure is medically necessary for the patient due to functional impairment and psychological distress. The patient has documented breathing difficulties and self-esteem issues related to the congenital condition.',
    provider_info: {
      name: 'DocWiz Surgical Center',
      npi: '1234567890',
      address: '123 Medical Plaza, Suite 100',
      phone: '(555) 123-4567',
      specialty: 'Plastic and Reconstructive Surgery',
    },
    generated_at: '2024-01-01T00:00:00Z',
  };

  const mockGenerateClaim = {
    mutateAsync: jest.fn(),
    isPending: false,
  };

  const mockShowToast = jest.fn();
  const mockDownloadPDF = jest.fn();
  const mockDownloadJSON = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Suppress console.error for expected error tests and jsdom navigation warnings
    const originalError = console.error;
    jest.spyOn(console, 'error').mockImplementation((...args) => {
      const message = args[0];
      // Suppress expected error messages from the component
      if (
        typeof message === 'string' &&
        (message.includes('Error generating claim:') ||
         message.includes('Error downloading PDF:') ||
         message.includes('Error downloading JSON:'))
      ) {
        return;
      }
      // Suppress jsdom navigation warnings
      if (message && typeof message === 'object' && message.type === 'not implemented') {
        return;
      }
      if (typeof message === 'string' && message.includes('Not implemented: navigation')) {
        return;
      }
      // Let other errors through
      originalError.apply(console, args);
    });
    
    // Mock URL methods
    global.URL.createObjectURL = mockCreateObjectURL;
    global.URL.revokeObjectURL = mockRevokeObjectURL;
    
    // Mock document.body methods for download
    const originalAppendChild = document.body.appendChild.bind(document.body);
    const originalRemoveChild = document.body.removeChild.bind(document.body);
    
    jest.spyOn(document.body, 'appendChild').mockImplementation((node: any) => {
      // Don't actually append anchor elements to avoid jsdom navigation
      if (node.tagName === 'A') {
        return node;
      }
      return originalAppendChild(node);
    });
    
    jest.spyOn(document.body, 'removeChild').mockImplementation((node: any) => {
      // Don't actually remove anchor elements
      if (node.tagName === 'A') {
        return node;
      }
      return originalRemoveChild(node);
    });
    
    mockUseInsurance.mockReturnValue({
      generateClaim: mockGenerateClaim as any,
      validateInsurance: {} as any,
      downloadPDF: mockDownloadPDF,
      downloadJSON: mockDownloadJSON,
    });
    mockUseToast.mockReturnValue({
      showToast: mockShowToast,
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Empty State', () => {
    it('should display empty state when no procedure is selected', () => {
      render(
        <InsuranceClaim
          procedureId={undefined}
          patientId="patient-123"
        />
      );

      expect(screen.getByText(/no procedure selected/i)).toBeInTheDocument();
      expect(screen.getByText(/select a procedure and complete your profile/i)).toBeInTheDocument();
    });

    it('should show placeholder icon in empty state', () => {
      render(
        <InsuranceClaim
          procedureId={undefined}
          patientId="patient-123"
        />
      );

      const icon = screen.getByText(/no procedure selected/i).parentElement?.querySelector('svg');
      expect(icon).toBeInTheDocument();
    });
  });

  describe('Provider Information Form', () => {
    it('should display provider information form when no claim is generated', () => {
      render(
        <InsuranceClaim
          procedureId="proc-123"
          patientId="patient-456"
        />
      );

      expect(screen.getByText('Provider Information')).toBeInTheDocument();
      expect(screen.getByLabelText(/provider name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/npi number/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/address/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/phone/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/specialty/i)).toBeInTheDocument();
    });

    it('should have default provider information pre-filled', () => {
      render(
        <InsuranceClaim
          procedureId="proc-123"
          patientId="patient-456"
        />
      );

      expect(screen.getByDisplayValue('DocWiz Surgical Center')).toBeInTheDocument();
      expect(screen.getByDisplayValue('1234567890')).toBeInTheDocument();
      expect(screen.getByDisplayValue('123 Medical Plaza, Suite 100')).toBeInTheDocument();
      expect(screen.getByDisplayValue('(555) 123-4567')).toBeInTheDocument();
      expect(screen.getByDisplayValue('Plastic and Reconstructive Surgery')).toBeInTheDocument();
    });

    it('should allow editing provider information', () => {
      render(
        <InsuranceClaim
          procedureId="proc-123"
          patientId="patient-456"
        />
      );

      const nameInput = screen.getByLabelText(/provider name/i);
      fireEvent.change(nameInput, { target: { value: 'New Surgical Center' } });

      expect(screen.getByDisplayValue('New Surgical Center')).toBeInTheDocument();
    });

    it('should display generate button', () => {
      render(
        <InsuranceClaim
          procedureId="proc-123"
          patientId="patient-456"
        />
      );

      expect(screen.getByRole('button', { name: /generate pre-authorization form/i })).toBeInTheDocument();
    });

    it('should disable generate button when procedure or patient is missing', () => {
      render(
        <InsuranceClaim
          procedureId={undefined}
          patientId="patient-456"
        />
      );

      const generateButton = screen.getByRole('button', { name: /generate pre-authorization form/i });
      expect(generateButton).toBeDisabled();
    });
  });

  describe('Claim Generation', () => {
    it('should call generateClaim when button is clicked', async () => {
      mockGenerateClaim.mutateAsync.mockResolvedValue(mockPreAuthForm);

      render(
        <InsuranceClaim
          procedureId="proc-123"
          patientId="patient-456"
          costBreakdownId="cost-789"
        />
      );

      const generateButton = screen.getByRole('button', { name: /generate pre-authorization form/i });
      fireEvent.click(generateButton);

      await waitFor(() => {
        expect(mockGenerateClaim.mutateAsync).toHaveBeenCalledWith({
          procedure_id: 'proc-123',
          patient_id: 'patient-456',
          cost_breakdown_id: 'cost-789',
          provider_info: {
            name: 'DocWiz Surgical Center',
            npi: '1234567890',
            address: '123 Medical Plaza, Suite 100',
            phone: '(555) 123-4567',
            specialty: 'Plastic and Reconstructive Surgery',
          },
        });
      });
    });

    it('should show success toast on successful generation', async () => {
      mockGenerateClaim.mutateAsync.mockResolvedValue(mockPreAuthForm);

      render(
        <InsuranceClaim
          procedureId="proc-123"
          patientId="patient-456"
        />
      );

      const generateButton = screen.getByRole('button', { name: /generate pre-authorization form/i });
      fireEvent.click(generateButton);

      await waitFor(() => {
        expect(mockShowToast).toHaveBeenCalledWith({
          type: 'success',
          message: 'Insurance claim generated successfully',
        });
      });
    });

    it('should show error toast on generation failure', async () => {
      mockGenerateClaim.mutateAsync.mockRejectedValue(new Error('Generation failed'));

      render(
        <InsuranceClaim
          procedureId="proc-123"
          patientId="patient-456"
        />
      );

      const generateButton = screen.getByRole('button', { name: /generate pre-authorization form/i });
      fireEvent.click(generateButton);

      await waitFor(() => {
        expect(mockShowToast).toHaveBeenCalledWith({
          type: 'error',
          message: 'Failed to generate insurance claim',
        });
      });
    });

    it('should show loading state during generation', () => {
      mockUseInsurance.mockReturnValue({
        generateClaim: { ...mockGenerateClaim, isPending: true } as any,
        validateInsurance: {} as any,
        downloadPDF: mockDownloadPDF,
        downloadJSON: mockDownloadJSON,
      });

      render(
        <InsuranceClaim
          procedureId="proc-123"
          patientId="patient-456"
        />
      );

      expect(screen.getByText(/generating claim/i)).toBeInTheDocument();
      const generateButton = screen.getByRole('button', { name: /generating claim/i });
      expect(generateButton).toBeDisabled();
    });

    it('should call onClaimGenerated callback when provided', async () => {
      const mockOnClaimGenerated = jest.fn();
      mockGenerateClaim.mutateAsync.mockResolvedValue(mockPreAuthForm);

      render(
        <InsuranceClaim
          procedureId="proc-123"
          patientId="patient-456"
          onClaimGenerated={mockOnClaimGenerated}
        />
      );

      const generateButton = screen.getByRole('button', { name: /generate pre-authorization form/i });
      fireEvent.click(generateButton);

      await waitFor(() => {
        expect(mockOnClaimGenerated).toHaveBeenCalledWith(mockPreAuthForm);
      });
    });

    it('should not allow generation when procedure or patient is missing', () => {
      render(
        <InsuranceClaim
          procedureId={undefined}
          patientId={undefined}
        />
      );

      const generateButton = screen.getByRole('button', { name: /generate pre-authorization form/i });
      
      // Button should be disabled
      expect(generateButton).toBeDisabled();
      
      // Should not call generateClaim
      expect(mockGenerateClaim.mutateAsync).not.toHaveBeenCalled();
    });
  });

  describe('Generated Claim Display', () => {
    beforeEach(async () => {
      mockGenerateClaim.mutateAsync.mockResolvedValue(mockPreAuthForm);

      render(
        <InsuranceClaim
          procedureId="proc-123"
          patientId="patient-456"
        />
      );

      const generateButton = screen.getByRole('button', { name: /generate pre-authorization form/i });
      fireEvent.click(generateButton);

      await waitFor(() => {
        expect(screen.getByText('Pre-Authorization Form')).toBeInTheDocument();
      });
    });

    it('should display claim details after generation', () => {
      expect(screen.getByText('Pre-Authorization Form')).toBeInTheDocument();
      expect(screen.getByText('Form ID')).toBeInTheDocument();
      expect(screen.getByText('claim-123')).toBeInTheDocument();
    });

    it('should display provider information', () => {
      expect(screen.getByText('Provider Information')).toBeInTheDocument();
      expect(screen.getByText('DocWiz Surgical Center')).toBeInTheDocument();
      expect(screen.getByText('1234567890')).toBeInTheDocument();
      expect(screen.getByText('123 Medical Plaza, Suite 100')).toBeInTheDocument();
      expect(screen.getByText('(555) 123-4567')).toBeInTheDocument();
      expect(screen.getByText('Plastic and Reconstructive Surgery')).toBeInTheDocument();
    });

    it('should display procedure codes', () => {
      expect(screen.getByText('Procedure Codes')).toBeInTheDocument();
      expect(screen.getByText('15820')).toBeInTheDocument();
      expect(screen.getByText('15821')).toBeInTheDocument();
      expect(screen.getByText('Q18.0')).toBeInTheDocument();
      expect(screen.getByText('Q36.9')).toBeInTheDocument();
    });

    it('should display medical justification', () => {
      expect(screen.getByText('Medical Necessity Justification')).toBeInTheDocument();
      expect(screen.getByText(/this procedure is medically necessary/i)).toBeInTheDocument();
    });

    it('should display disclaimer', () => {
      expect(screen.getByText(/important disclaimer/i)).toBeInTheDocument();
      expect(screen.getByText(/for informational purposes only/i)).toBeInTheDocument();
    });

    it('should display download buttons', () => {
      expect(screen.getByRole('button', { name: /download pdf/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /download json/i })).toBeInTheDocument();
    });

    it('should display generate new claim button', () => {
      expect(screen.getByRole('button', { name: /generate new claim/i })).toBeInTheDocument();
    });
  });

  describe('PDF Download', () => {
    beforeEach(async () => {
      mockGenerateClaim.mutateAsync.mockResolvedValue(mockPreAuthForm);

      render(
        <InsuranceClaim
          procedureId="proc-123"
          patientId="patient-456"
        />
      );

      const generateButton = screen.getByRole('button', { name: /generate pre-authorization form/i });
      fireEvent.click(generateButton);

      await waitFor(() => {
        expect(screen.getByText('Pre-Authorization Form')).toBeInTheDocument();
      });
    });

    it('should call downloadPDF when PDF button is clicked', async () => {
      const mockBlob = new Blob(['pdf content'], { type: 'application/pdf' });
      mockDownloadPDF.mockResolvedValue(mockBlob);

      const pdfButton = screen.getByRole('button', { name: /download pdf/i });
      fireEvent.click(pdfButton);

      await waitFor(() => {
        expect(mockDownloadPDF).toHaveBeenCalledWith('claim-123');
      });
    });

    it('should show success toast on successful PDF download', async () => {
      const mockBlob = new Blob(['pdf content'], { type: 'application/pdf' });
      mockDownloadPDF.mockResolvedValue(mockBlob);

      const pdfButton = screen.getByRole('button', { name: /download pdf/i });
      fireEvent.click(pdfButton);

      await waitFor(() => {
        expect(mockShowToast).toHaveBeenCalledWith({
          type: 'success',
          message: 'PDF downloaded successfully',
        });
      });
    });

    it('should show error toast on PDF download failure', async () => {
      mockDownloadPDF.mockRejectedValue(new Error('Download failed'));

      const pdfButton = screen.getByRole('button', { name: /download pdf/i });
      fireEvent.click(pdfButton);

      await waitFor(() => {
        expect(mockShowToast).toHaveBeenCalledWith({
          type: 'error',
          message: 'Failed to download PDF',
        });
      });
    });
  });

  describe('JSON Download', () => {
    beforeEach(async () => {
      mockGenerateClaim.mutateAsync.mockResolvedValue(mockPreAuthForm);

      render(
        <InsuranceClaim
          procedureId="proc-123"
          patientId="patient-456"
        />
      );

      const generateButton = screen.getByRole('button', { name: /generate pre-authorization form/i });
      fireEvent.click(generateButton);

      await waitFor(() => {
        expect(screen.getByText('Pre-Authorization Form')).toBeInTheDocument();
      });
    });

    it('should call downloadJSON when JSON button is clicked', async () => {
      const mockBlob = new Blob(['json content'], { type: 'application/json' });
      mockDownloadJSON.mockResolvedValue(mockBlob);

      const jsonButton = screen.getByRole('button', { name: /download json/i });
      fireEvent.click(jsonButton);

      await waitFor(() => {
        expect(mockDownloadJSON).toHaveBeenCalledWith('claim-123');
      });
    });

    it('should show success toast on successful JSON download', async () => {
      const mockBlob = new Blob(['json content'], { type: 'application/json' });
      mockDownloadJSON.mockResolvedValue(mockBlob);

      const jsonButton = screen.getByRole('button', { name: /download json/i });
      fireEvent.click(jsonButton);

      await waitFor(() => {
        expect(mockShowToast).toHaveBeenCalledWith({
          type: 'success',
          message: 'JSON downloaded successfully',
        });
      });
    });

    it('should show error toast on JSON download failure', async () => {
      mockDownloadJSON.mockRejectedValue(new Error('Download failed'));

      const jsonButton = screen.getByRole('button', { name: /download json/i });
      fireEvent.click(jsonButton);

      await waitFor(() => {
        expect(mockShowToast).toHaveBeenCalledWith({
          type: 'error',
          message: 'Failed to download JSON',
        });
      });
    });
  });

  describe('Generate New Claim', () => {
    it('should reset to form view when generate new claim is clicked', async () => {
      mockGenerateClaim.mutateAsync.mockResolvedValue(mockPreAuthForm);

      render(
        <InsuranceClaim
          procedureId="proc-123"
          patientId="patient-456"
        />
      );

      // Generate claim
      const generateButton = screen.getByRole('button', { name: /generate pre-authorization form/i });
      fireEvent.click(generateButton);

      await waitFor(() => {
        expect(screen.getByText('Pre-Authorization Form')).toBeInTheDocument();
      });

      // Click generate new claim
      const newClaimButton = screen.getByRole('button', { name: /generate new claim/i });
      fireEvent.click(newClaimButton);

      // Should show form again
      await waitFor(() => {
        expect(screen.getByText('Provider Information')).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /generate pre-authorization form/i })).toBeInTheDocument();
      });
    });
  });
});
