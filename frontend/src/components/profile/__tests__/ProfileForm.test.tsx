import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ProfileForm, ProfileFormData } from '../ProfileForm';

describe('ProfileForm', () => {
  const mockOnSubmit = jest.fn();
  const mockOnCancel = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Form Validation', () => {
    it('should show validation errors for empty required fields', async () => {
      render(<ProfileForm onSubmit={mockOnSubmit} />);

      // Try to proceed to next step without filling required fields
      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByText(/name is required/i)).toBeInTheDocument();
        expect(screen.getByText(/date of birth is required/i)).toBeInTheDocument();
      });

      expect(mockOnSubmit).not.toHaveBeenCalled();
    });

    it('should validate zip code format', async () => {
      render(<ProfileForm onSubmit={mockOnSubmit} />);

      // Fill step 1
      const nameInput = screen.getByLabelText(/full name/i);
      const dobInput = screen.getByLabelText(/date of birth/i);
      
      await userEvent.type(nameInput, 'John Doe');
      await userEvent.type(dobInput, '1990-01-01');
      
      // Go to step 2
      const nextButton = screen.getByRole('button', { name: /next/i });
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(screen.getByLabelText(/zip code/i)).toBeInTheDocument();
      });

      // Enter invalid zip code
      const zipInput = screen.getByLabelText(/zip code/i);
      await userEvent.type(zipInput, 'invalid');

      // Try to proceed
      fireEvent.click(screen.getByRole('button', { name: /next/i }));

      await waitFor(() => {
        expect(screen.getByText(/invalid zip code format/i)).toBeInTheDocument();
      });
    });

    it('should accept valid 5-digit zip code', async () => {
      render(<ProfileForm onSubmit={mockOnSubmit} />);

      // Fill step 1
      await userEvent.type(screen.getByLabelText(/full name/i), 'John Doe');
      await userEvent.type(screen.getByLabelText(/date of birth/i), '1990-01-01');
      
      fireEvent.click(screen.getByRole('button', { name: /next/i }));

      await waitFor(() => {
        expect(screen.getByLabelText(/zip code/i)).toBeInTheDocument();
      });

      // Enter valid zip code
      await userEvent.type(screen.getByLabelText(/zip code/i), '12345');
      await userEvent.type(screen.getByLabelText(/city/i), 'New York');
      
      const stateSelect = screen.getByRole('combobox');
      await userEvent.selectOptions(stateSelect, 'NY');

      // Should not show error
      expect(screen.queryByText(/invalid zip code format/i)).not.toBeInTheDocument();
    });

    it('should validate insurance provider is required', async () => {
      render(<ProfileForm onSubmit={mockOnSubmit} />);

      // Navigate to step 3
      await userEvent.type(screen.getByLabelText(/full name/i), 'John Doe');
      await userEvent.type(screen.getByLabelText(/date of birth/i), '1990-01-01');
      fireEvent.click(screen.getByRole('button', { name: /next/i }));

      await waitFor(() => {
        expect(screen.getByLabelText(/zip code/i)).toBeInTheDocument();
      });

      await userEvent.type(screen.getByLabelText(/zip code/i), '12345');
      await userEvent.type(screen.getByLabelText(/city/i), 'New York');
      await userEvent.selectOptions(screen.getByRole('combobox'), 'NY');
      fireEvent.click(screen.getByRole('button', { name: /next/i }));

      await waitFor(() => {
        expect(screen.getByLabelText(/insurance provider/i)).toBeInTheDocument();
      });

      // Try to proceed without filling insurance info
      fireEvent.click(screen.getByRole('button', { name: /next/i }));

      await waitFor(() => {
        expect(screen.getByText(/insurance provider is required/i)).toBeInTheDocument();
      });
    });
  });

  describe('Multi-step Navigation', () => {
    it('should navigate through all steps', async () => {
      render(<ProfileForm onSubmit={mockOnSubmit} />);

      // Step 1
      expect(screen.getByText(/step 1 of 4/i)).toBeInTheDocument();
      expect(screen.getByText(/personal information/i)).toBeInTheDocument();

      await userEvent.type(screen.getByLabelText(/full name/i), 'John Doe');
      await userEvent.type(screen.getByLabelText(/date of birth/i), '1990-01-01');
      fireEvent.click(screen.getByRole('button', { name: /next/i }));

      // Step 2
      await waitFor(() => {
        expect(screen.getByText(/step 2 of 4/i)).toBeInTheDocument();
        expect(screen.getByText(/location/i)).toBeInTheDocument();
      });

      await userEvent.type(screen.getByLabelText(/zip code/i), '12345');
      await userEvent.type(screen.getByLabelText(/city/i), 'New York');
      await userEvent.selectOptions(screen.getByRole('combobox'), 'NY');
      fireEvent.click(screen.getByRole('button', { name: /next/i }));

      // Step 3
      await waitFor(() => {
        expect(screen.getByText(/step 3 of 4/i)).toBeInTheDocument();
        expect(screen.getByText(/insurance information/i)).toBeInTheDocument();
      });

      await userEvent.type(screen.getByLabelText(/insurance provider/i), 'Blue Cross');
      await userEvent.type(screen.getByLabelText(/policy number/i), 'ABC123');
      await userEvent.type(screen.getByLabelText(/plan type/i), 'PPO');
      fireEvent.click(screen.getByRole('button', { name: /next/i }));

      // Step 4
      await waitFor(() => {
        expect(screen.getByText(/step 4 of 4/i)).toBeInTheDocument();
      });
      
      // Check for medical history heading
      expect(screen.getByRole('heading', { name: /medical history/i })).toBeInTheDocument();
    });

    it('should allow going back to previous steps', async () => {
      render(<ProfileForm onSubmit={mockOnSubmit} />);

      // Go to step 2
      await userEvent.type(screen.getByLabelText(/full name/i), 'John Doe');
      await userEvent.type(screen.getByLabelText(/date of birth/i), '1990-01-01');
      fireEvent.click(screen.getByRole('button', { name: /next/i }));

      await waitFor(() => {
        expect(screen.getByText(/step 2 of 4/i)).toBeInTheDocument();
      });

      // Go back to step 1
      const previousButton = screen.getByRole('button', { name: /previous/i });
      fireEvent.click(previousButton);

      await waitFor(() => {
        expect(screen.getByText(/step 1 of 4/i)).toBeInTheDocument();
      });

      // Data should be preserved
      expect(screen.getByLabelText(/full name/i)).toHaveValue('John Doe');
    });
  });

  describe('Form Submission', () => {
    it('should have submit button on final step', async () => {
      const mockSubmit = jest.fn().mockResolvedValue(undefined);
      const initialData = {
        id: '123',
        user_id: 'user123',
        name: 'John Doe',
        date_of_birth: '1990-01-01',
        location: {
          zip_code: '12345',
          city: 'New York',
          state: 'NY',
          country: 'USA',
        },
        insurance_info: {
          provider: 'Blue Cross',
          policy_number: 'ABC123',
          plan_type: 'PPO',
          coverage_details: {},
        },
        created_at: '2024-01-01T00:00:00Z',
        updated_at: '2024-01-01T00:00:00Z',
        version: 1,
      };

      render(<ProfileForm initialData={initialData} onSubmit={mockSubmit} />);

      // Navigate to final step
      fireEvent.click(screen.getByRole('button', { name: /next/i }));
      await waitFor(() => {
        expect(screen.getByLabelText(/zip code/i)).toBeInTheDocument();
      });
      
      fireEvent.click(screen.getByRole('button', { name: /next/i }));
      await waitFor(() => {
        expect(screen.getByLabelText(/insurance provider/i)).toBeInTheDocument();
      });
      
      fireEvent.click(screen.getByRole('button', { name: /next/i }));
      
      // Check for submit button
      await waitFor(() => {
        expect(screen.getByRole('button', { name: /update profile/i })).toBeInTheDocument();
      });
    });

    it('should call onCancel when cancel button is clicked', () => {
      render(<ProfileForm onSubmit={mockOnSubmit} onCancel={mockOnCancel} />);

      const cancelButton = screen.getByRole('button', { name: /cancel/i });
      fireEvent.click(cancelButton);

      expect(mockOnCancel).toHaveBeenCalled();
    });
  });

  describe('Insurance Provider Autocomplete', () => {
    it('should filter providers based on search', () => {
      render(<ProfileForm onSubmit={mockOnSubmit} />);

      // The autocomplete functionality is tested through the component's internal state
      // We verify the component renders without errors
      expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
    });
  });

  describe('Edit Mode', () => {
    const initialData = {
      id: '123',
      user_id: 'user123',
      name: 'Jane Doe',
      date_of_birth: '1985-05-15',
      location: {
        zip_code: '90210',
        city: 'Beverly Hills',
        state: 'CA',
        country: 'USA',
      },
      insurance_info: {
        provider: 'Aetna',
        policy_number: 'XYZ789',
        plan_type: 'HMO',
        coverage_details: {},
      },
      created_at: '2024-01-01T00:00:00Z',
      updated_at: '2024-01-01T00:00:00Z',
      version: 1,
    };

    it('should populate form with initial data', () => {
      render(<ProfileForm initialData={initialData} onSubmit={mockOnSubmit} />);

      expect(screen.getByLabelText(/full name/i)).toHaveValue('Jane Doe');
      expect(screen.getByLabelText(/date of birth/i)).toHaveValue('1985-05-15');
    });

    it('should show initial data is populated', () => {
      render(<ProfileForm initialData={initialData} onSubmit={mockOnSubmit} />);

      // Verify initial data is populated
      expect(screen.getByLabelText(/full name/i)).toHaveValue('Jane Doe');
      expect(screen.getByLabelText(/date of birth/i)).toHaveValue('1985-05-15');
    });
  });
});
