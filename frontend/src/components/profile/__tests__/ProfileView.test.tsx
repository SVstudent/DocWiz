import { render, screen, fireEvent } from '@testing-library/react';
import { ProfileView } from '../ProfileView';
import { PatientProfile } from '@/store/profileStore';

describe('ProfileView', () => {
  const mockProfile: PatientProfile = {
    id: '123',
    user_id: 'user123',
    name: 'John Doe',
    date_of_birth: '1990-01-15',
    location: {
      zip_code: '12345',
      city: 'New York',
      state: 'NY',
      country: 'USA',
    },
    insurance_info: {
      provider: 'Blue Cross Blue Shield',
      policy_number: 'BC123456789',
      group_number: 'GRP123',
      plan_type: 'PPO',
      coverage_details: {},
    },
    medical_history: 'No known allergies. Previous appendectomy in 2015.',
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-15T10:30:00Z',
    version: 2,
  };

  const mockOnEdit = jest.fn();
  const mockOnViewHistory = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Profile Display', () => {
    it('should display profile name and version info', () => {
      render(
        <ProfileView
          profile={mockProfile}
          onEdit={mockOnEdit}
          onViewHistory={mockOnViewHistory}
        />
      );

      expect(screen.getByRole('heading', { name: 'John Doe' })).toBeInTheDocument();
      expect(screen.getByText(/profile version: 2/i)).toBeInTheDocument();
      expect(screen.getByText(/last updated:/i)).toBeInTheDocument();
    });

    it('should display personal information', () => {
      render(
        <ProfileView
          profile={mockProfile}
          onEdit={mockOnEdit}
          onViewHistory={mockOnViewHistory}
        />
      );

      expect(screen.getByText(/personal information/i)).toBeInTheDocument();
      expect(screen.getByRole('heading', { name: 'John Doe' })).toBeInTheDocument();
      // Date formatting may vary by timezone, just check it's present
      expect(screen.getByText(/january \d+, 1990/i)).toBeInTheDocument();
    });

    it('should display location information', () => {
      render(
        <ProfileView
          profile={mockProfile}
          onEdit={mockOnEdit}
          onViewHistory={mockOnViewHistory}
        />
      );

      expect(screen.getByText(/location/i)).toBeInTheDocument();
      expect(screen.getByText('New York')).toBeInTheDocument();
      expect(screen.getByText('NY')).toBeInTheDocument();
      expect(screen.getByText('12345')).toBeInTheDocument();
      expect(screen.getByText('USA')).toBeInTheDocument();
    });

    it('should display insurance information', () => {
      render(
        <ProfileView
          profile={mockProfile}
          onEdit={mockOnEdit}
          onViewHistory={mockOnViewHistory}
        />
      );

      expect(screen.getByText(/insurance information/i)).toBeInTheDocument();
      expect(screen.getByText('Blue Cross Blue Shield')).toBeInTheDocument();
      expect(screen.getByText('GRP123')).toBeInTheDocument();
      expect(screen.getByText('PPO')).toBeInTheDocument();
    });

    it('should display medical history when present', () => {
      render(
        <ProfileView
          profile={mockProfile}
          onEdit={mockOnEdit}
          onViewHistory={mockOnViewHistory}
        />
      );

      expect(screen.getByText(/medical history/i)).toBeInTheDocument();
    });

    it('should not display medical history section when not present', () => {
      const profileWithoutHistory = { ...mockProfile, medical_history: undefined };
      
      render(
        <ProfileView
          profile={profileWithoutHistory}
          onEdit={mockOnEdit}
          onViewHistory={mockOnViewHistory}
        />
      );

      // Should only have one "Medical History" heading (in the card title)
      const medicalHistoryElements = screen.queryAllByText(/medical history/i);
      expect(medicalHistoryElements.length).toBe(0);
    });
  });

  describe('Encrypted Fields', () => {
    it('should mask policy number by default', () => {
      render(
        <ProfileView
          profile={mockProfile}
          onEdit={mockOnEdit}
          onViewHistory={mockOnViewHistory}
        />
      );

      // Should show masked version
      expect(screen.getByText(/•••••••6789/)).toBeInTheDocument();
      expect(screen.queryByText('BC123456789')).not.toBeInTheDocument();
    });

    it('should show encrypted field indicators', () => {
      render(
        <ProfileView
          profile={mockProfile}
          onEdit={mockOnEdit}
          onViewHistory={mockOnViewHistory}
        />
      );

      expect(screen.getByText(/encrypted fields are protected/i)).toBeInTheDocument();
    });

    it('should toggle sensitive data visibility', () => {
      render(
        <ProfileView
          profile={mockProfile}
          onEdit={mockOnEdit}
          onViewHistory={mockOnViewHistory}
        />
      );

      // Initially masked
      expect(screen.getByText(/•••••••6789/)).toBeInTheDocument();

      // Click show button
      const showButton = screen.getByRole('button', { name: /show sensitive data/i });
      fireEvent.click(showButton);

      // Should show unmasked
      expect(screen.getByText('BC123456789')).toBeInTheDocument();
      expect(screen.queryByText(/•••••••6789/)).not.toBeInTheDocument();

      // Should show medical history
      expect(screen.getByText(/No known allergies/i)).toBeInTheDocument();

      // Click hide button
      const hideButton = screen.getByRole('button', { name: /hide sensitive data/i });
      fireEvent.click(hideButton);

      // Should mask again
      expect(screen.getByText(/•••••••6789/)).toBeInTheDocument();
      expect(screen.queryByText('BC123456789')).not.toBeInTheDocument();
    });

    it('should mask medical history by default', () => {
      render(
        <ProfileView
          profile={mockProfile}
          onEdit={mockOnEdit}
          onViewHistory={mockOnViewHistory}
        />
      );

      // Should show masked version
      expect(screen.getByText(/••••••••••••••••••••/)).toBeInTheDocument();
      expect(screen.queryByText(/No known allergies/i)).not.toBeInTheDocument();
    });
  });

  describe('Action Buttons', () => {
    it('should call onEdit when edit button is clicked', () => {
      render(
        <ProfileView
          profile={mockProfile}
          onEdit={mockOnEdit}
          onViewHistory={mockOnViewHistory}
        />
      );

      const editButton = screen.getByRole('button', { name: /edit profile/i });
      fireEvent.click(editButton);

      expect(mockOnEdit).toHaveBeenCalledTimes(1);
    });

    it('should call onViewHistory when view history button is clicked', () => {
      render(
        <ProfileView
          profile={mockProfile}
          onEdit={mockOnEdit}
          onViewHistory={mockOnViewHistory}
        />
      );

      const historyButton = screen.getByRole('button', { name: /view history/i });
      fireEvent.click(historyButton);

      expect(mockOnViewHistory).toHaveBeenCalledTimes(1);
    });
  });

  describe('Optional Fields', () => {
    it('should handle missing group number', () => {
      const profileWithoutGroupNumber = {
        ...mockProfile,
        insurance_info: {
          ...mockProfile.insurance_info,
          group_number: undefined,
        },
      };

      render(
        <ProfileView
          profile={profileWithoutGroupNumber}
          onEdit={mockOnEdit}
          onViewHistory={mockOnViewHistory}
        />
      );

      // Should not show group number label
      expect(screen.queryByText(/group number/i)).not.toBeInTheDocument();
    });

    it('should handle missing plan type', () => {
      const profileWithoutPlanType = {
        ...mockProfile,
        insurance_info: {
          ...mockProfile.insurance_info,
          plan_type: undefined,
        },
      };

      render(
        <ProfileView
          profile={profileWithoutPlanType}
          onEdit={mockOnEdit}
          onViewHistory={mockOnViewHistory}
        />
      );

      // Should not show plan type label
      expect(screen.queryByText(/plan type/i)).not.toBeInTheDocument();
    });
  });
});
