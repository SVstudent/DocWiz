import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ProcedureDetailModal } from '../ProcedureDetailModal';
import { apiClient } from '@/lib/api-client';

// Mock the API client
jest.mock('@/lib/api-client', () => ({
  apiClient: {
    get: jest.fn(),
  },
}));

// Helper to wrap component with QueryClient
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('ProcedureDetailModal', () => {
  const mockOnClose = jest.fn();
  const mockOnSelect = jest.fn();

  const mockProcedureDetail = {
    id: 'proc-1',
    name: 'Rhinoplasty',
    category: 'facial',
    description: 'Nose reshaping surgery to improve appearance and/or breathing function.',
    recovery_days: 14,
    risk_level: 'medium',
    cost_range: {
      min: 5000,
      max: 15000,
    },
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (apiClient.get as jest.Mock).mockResolvedValue({
      data: mockProcedureDetail,
    });
  });

  describe('Modal Display', () => {
    it('should not render when isOpen is false', () => {
      render(
        <ProcedureDetailModal
          isOpen={false}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    });

    it('should render when isOpen is true', async () => {
      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });
    });

    it('should fetch procedure details when opened', async () => {
      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(apiClient.get).toHaveBeenCalledWith('/api/procedures/proc-1');
      });
    });

    it('should display procedure name in title', async () => {
      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByText('Rhinoplasty')).toBeInTheDocument();
      });
    });
  });

  describe('Procedure Information Display', () => {
    it('should display category badge', async () => {
      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByText('FACIAL')).toBeInTheDocument();
      });
    });

    it('should display risk level badge', async () => {
      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByText('MEDIUM RISK')).toBeInTheDocument();
      });
    });

    it('should display procedure description', async () => {
      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(
          screen.getByText(/nose reshaping surgery to improve appearance/i)
        ).toBeInTheDocument();
      });
    });

    it('should display cost range', async () => {
      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByText('$5,000')).toBeInTheDocument();
        expect(screen.getByText('$15,000')).toBeInTheDocument();
      });
    });

    it('should display recovery timeline', async () => {
      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByText('14')).toBeInTheDocument();
        expect(screen.getByText(/14 days typical recovery/i)).toBeInTheDocument();
      });
    });

    it('should display risk factors section', async () => {
      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByText(/risk factors & considerations/i)).toBeInTheDocument();
      });
    });

    it('should display medical disclaimer', async () => {
      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByText(/medical disclaimer/i)).toBeInTheDocument();
        expect(
          screen.getByText(/this information is for educational purposes only/i)
        ).toBeInTheDocument();
      });
    });
  });

  describe('Risk Level Variations', () => {
    it('should display low risk level correctly', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: {
          ...mockProcedureDetail,
          risk_level: 'low',
        },
      });

      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByText('LOW RISK')).toBeInTheDocument();
        expect(
          screen.getByText(/low risk profile with minimal complications/i)
        ).toBeInTheDocument();
      });
    });

    it('should display medium risk level correctly', async () => {
      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByText('MEDIUM RISK')).toBeInTheDocument();
        expect(
          screen.getByText(/moderate risk profile/i)
        ).toBeInTheDocument();
      });
    });

    it('should display high risk level correctly', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: {
          ...mockProcedureDetail,
          risk_level: 'high',
        },
      });

      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByText('HIGH RISK')).toBeInTheDocument();
        expect(
          screen.getByText(/higher risk profile/i)
        ).toBeInTheDocument();
      });
    });
  });

  describe('Recovery Timeline', () => {
    it('should show short recovery period for <= 7 days', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: {
          ...mockProcedureDetail,
          recovery_days: 7,
        },
      });

      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByText(/short recovery period/i)).toBeInTheDocument();
      });
    });

    it('should show moderate recovery period for 8-21 days', async () => {
      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByText(/moderate recovery period/i)).toBeInTheDocument();
      });
    });

    it('should show extended recovery period for > 21 days', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: {
          ...mockProcedureDetail,
          recovery_days: 30,
        },
      });

      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByText(/extended recovery period/i)).toBeInTheDocument();
      });
    });
  });

  describe('Selection Functionality', () => {
    it('should show select button when onSelect is provided', async () => {
      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
          onSelect={mockOnSelect}
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(
          screen.getByRole('button', { name: /select this procedure/i })
        ).toBeInTheDocument();
      });
    });

    it('should not show select button when onSelect is not provided', async () => {
      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByText('Rhinoplasty')).toBeInTheDocument();
      });

      expect(
        screen.queryByRole('button', { name: /select this procedure/i })
      ).not.toBeInTheDocument();
    });

    it('should call onSelect and onClose when select button is clicked', async () => {
      const user = userEvent.setup();

      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
          onSelect={mockOnSelect}
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /select this procedure/i })).toBeInTheDocument();
      });

      const selectButton = screen.getByRole('button', { name: /select this procedure/i });
      await user.click(selectButton);

      expect(mockOnSelect).toHaveBeenCalledWith(
        expect.objectContaining({
          id: 'proc-1',
          name: 'Rhinoplasty',
          category: 'facial',
          description: expect.any(String),
          typical_cost_range: [5000, 15000],
          recovery_days: 14,
          risk_level: 'medium',
        })
      );
      expect(mockOnClose).toHaveBeenCalled();
    });

    it('should show "Selected" button when isSelected is true', async () => {
      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
          onSelect={mockOnSelect}
          isSelected={true}
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /selected/i })).toBeInTheDocument();
      });
    });
  });

  describe('Close Functionality', () => {
    it('should call onClose when close button is clicked', async () => {
      const user = userEvent.setup();

      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });

      const closeButton = screen.getByRole('button', { name: /close modal/i });
      await user.click(closeButton);

      expect(mockOnClose).toHaveBeenCalled();
    });

    it('should call onClose when Close button in footer is clicked', async () => {
      const user = userEvent.setup();

      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
          onSelect={mockOnSelect}
        />,
        { wrapper: createWrapper() }
      );

      // Wait for the modal content to load
      await waitFor(() => {
        expect(screen.getByText('Rhinoplasty')).toBeInTheDocument();
      });

      const closeButton = screen.getByRole('button', { name: /^close$/i });
      await user.click(closeButton);

      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  describe('Loading State', () => {
    it('should display loading skeletons while fetching', () => {
      (apiClient.get as jest.Mock).mockImplementation(() => {
        return new Promise(() => {}); // Never resolves
      });

      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });
  });

  describe('Error State', () => {
    it('should display error message when procedure not found', async () => {
      (apiClient.get as jest.Mock).mockResolvedValue({
        data: null,
      });

      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="invalid-id"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(
          screen.getByText(/procedure details not available/i)
        ).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('should have proper ARIA attributes', async () => {
      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        const dialog = screen.getByRole('dialog');
        expect(dialog).toHaveAttribute('aria-modal', 'true');
      });
    });

    it('should be keyboard accessible', async () => {
      const user = userEvent.setup();

      render(
        <ProcedureDetailModal
          isOpen={true}
          onClose={mockOnClose}
          procedureId="proc-1"
          onSelect={mockOnSelect}
        />,
        { wrapper: createWrapper() }
      );

      await waitFor(() => {
        expect(screen.getByRole('dialog')).toBeInTheDocument();
      });

      // Tab through interactive elements
      await user.tab();
      expect(screen.getByRole('button', { name: /close modal/i })).toHaveFocus();
    });
  });
});
