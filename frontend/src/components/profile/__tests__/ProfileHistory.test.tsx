import { render, screen, fireEvent } from '@testing-library/react';
import { ProfileHistory } from '../ProfileHistory';

describe('ProfileHistory', () => {
  const mockVersions = [
    {
      id: 'v3',
      profile_id: 'profile123',
      version: 3,
      data: {
        name: 'John Doe',
        insurance_info: { provider: 'Updated Provider' },
      },
      created_at: '2024-01-15T10:30:00Z',
    },
    {
      id: 'v2',
      profile_id: 'profile123',
      version: 2,
      data: {
        location: { city: 'New York' },
      },
      created_at: '2024-01-10T14:20:00Z',
    },
    {
      id: 'v1',
      profile_id: 'profile123',
      version: 1,
      data: {
        name: 'John Doe',
        date_of_birth: '1990-01-15',
      },
      created_at: '2024-01-01T09:00:00Z',
    },
  ];

  const mockOnClose = jest.fn();
  const mockOnRestore = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Version History Display', () => {
    it('should display all versions', () => {
      render(
        <ProfileHistory
          versions={mockVersions}
          onClose={mockOnClose}
          onRestore={mockOnRestore}
        />
      );

      expect(screen.getByText('Version 3')).toBeInTheDocument();
      expect(screen.getByText('Version 2')).toBeInTheDocument();
      expect(screen.getByText('Version 1')).toBeInTheDocument();
    });

    it('should mark the latest version as current', () => {
      render(
        <ProfileHistory
          versions={mockVersions}
          onClose={mockOnClose}
          onRestore={mockOnRestore}
        />
      );

      // Latest version should have "Current" badge
      const version3Card = screen.getByText('Version 3').closest('div');
      expect(version3Card).toHaveTextContent('Current');
    });

    it('should display formatted timestamps', () => {
      render(
        <ProfileHistory
          versions={mockVersions}
          onClose={mockOnClose}
          onRestore={mockOnRestore}
        />
      );

      // Check that dates are formatted (exact format may vary by locale)
      expect(screen.getByText(/january 15, 2024/i)).toBeInTheDocument();
      expect(screen.getByText(/january 10, 2024/i)).toBeInTheDocument();
      expect(screen.getByText(/january 1, 2024/i)).toBeInTheDocument();
    });

    it('should display change summaries', () => {
      render(
        <ProfileHistory
          versions={mockVersions}
          onClose={mockOnClose}
          onRestore={mockOnRestore}
        />
      );

      // Use getAllByText since there may be multiple instances
      expect(screen.getAllByText(/name updated/i).length).toBeGreaterThan(0);
      expect(screen.getByText(/insurance information updated/i)).toBeInTheDocument();
      expect(screen.getByText(/location updated/i)).toBeInTheDocument();
    });

    it('should show "Profile created" for initial version', () => {
      const initialVersion = [
        {
          id: 'v1',
          profile_id: 'profile123',
          version: 1,
          data: {},
          created_at: '2024-01-01T09:00:00Z',
        },
      ];

      render(
        <ProfileHistory
          versions={initialVersion}
          onClose={mockOnClose}
          onRestore={mockOnRestore}
        />
      );

      expect(screen.getByText(/profile created/i)).toBeInTheDocument();
    });

    it('should display empty state when no versions', () => {
      render(
        <ProfileHistory
          versions={[]}
          onClose={mockOnClose}
          onRestore={mockOnRestore}
        />
      );

      expect(screen.getByText(/no version history available/i)).toBeInTheDocument();
    });
  });

  describe('Action Buttons', () => {
    it('should call onClose when close button is clicked', () => {
      render(
        <ProfileHistory
          versions={mockVersions}
          onClose={mockOnClose}
          onRestore={mockOnRestore}
        />
      );

      const closeButton = screen.getByRole('button', { name: /close/i });
      fireEvent.click(closeButton);

      expect(mockOnClose).toHaveBeenCalledTimes(1);
    });

    it('should not show restore button for current version', () => {
      render(
        <ProfileHistory
          versions={mockVersions}
          onClose={mockOnClose}
          onRestore={mockOnRestore}
        />
      );

      // Get all restore buttons
      const restoreButtons = screen.getAllByRole('button', { name: /restore/i });
      
      // Should have restore buttons for versions 2 and 1, but not for version 3 (current)
      expect(restoreButtons).toHaveLength(2);
    });

    it('should call onRestore with correct version when restore is clicked', () => {
      render(
        <ProfileHistory
          versions={mockVersions}
          onClose={mockOnClose}
          onRestore={mockOnRestore}
        />
      );

      const restoreButtons = screen.getAllByRole('button', { name: /restore/i });
      
      // Click first restore button (should be for version 2)
      fireEvent.click(restoreButtons[0]);

      expect(mockOnRestore).toHaveBeenCalledWith(mockVersions[1]);
    });

    it('should not show restore buttons when onRestore is not provided', () => {
      render(
        <ProfileHistory
          versions={mockVersions}
          onClose={mockOnClose}
        />
      );

      const restoreButtons = screen.queryAllByRole('button', { name: /restore/i });
      expect(restoreButtons).toHaveLength(0);
    });
  });

  describe('Version Ordering', () => {
    it('should display versions in descending order', () => {
      render(
        <ProfileHistory
          versions={mockVersions}
          onClose={mockOnClose}
          onRestore={mockOnRestore}
        />
      );

      const versionElements = screen.getAllByText(/version \d+/i);
      
      expect(versionElements[0]).toHaveTextContent('Version 3');
      expect(versionElements[1]).toHaveTextContent('Version 2');
      expect(versionElements[2]).toHaveTextContent('Version 1');
    });
  });

  describe('Change Detection', () => {
    it('should detect multiple changes in a single version', () => {
      const multiChangeVersion = [
        {
          id: 'v2',
          profile_id: 'profile123',
          version: 2,
          data: {
            name: 'Updated Name',
            location: { city: 'New City' },
            insurance_info: { provider: 'New Provider' },
          },
          created_at: '2024-01-10T14:20:00Z',
        },
      ];

      render(
        <ProfileHistory
          versions={multiChangeVersion}
          onClose={mockOnClose}
          onRestore={mockOnRestore}
        />
      );

      expect(screen.getByText(/name updated/i)).toBeInTheDocument();
      expect(screen.getByText(/location updated/i)).toBeInTheDocument();
      expect(screen.getByText(/insurance information updated/i)).toBeInTheDocument();
    });

    it('should detect medical history changes', () => {
      const medicalHistoryVersion = [
        {
          id: 'v2',
          profile_id: 'profile123',
          version: 2,
          data: {
            medical_history: 'Updated medical history',
          },
          created_at: '2024-01-10T14:20:00Z',
        },
      ];

      render(
        <ProfileHistory
          versions={medicalHistoryVersion}
          onClose={mockOnClose}
          onRestore={mockOnRestore}
        />
      );

      expect(screen.getByText(/medical history updated/i)).toBeInTheDocument();
    });
  });
});
