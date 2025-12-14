import { render, screen, waitFor } from '@testing-library/react';
import { useRouter, useSearchParams } from 'next/navigation';
import { PublicRoute } from '../PublicRoute';
import { useAuthStore } from '@/store/authStore';

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  useSearchParams: jest.fn(),
}));

describe('PublicRoute', () => {
  const mockPush = jest.fn();
  const mockGet = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    (useSearchParams as jest.Mock).mockReturnValue({ get: mockGet });
    mockGet.mockReturnValue(null);
    // Reset auth store
    useAuthStore.setState({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  it('should render children when user is not authenticated', () => {
    render(
      <PublicRoute>
        <div>Login Form</div>
      </PublicRoute>
    );

    expect(screen.getByText('Login Form')).toBeInTheDocument();
    expect(mockPush).not.toHaveBeenCalled();
  });

  it('should redirect to home when user is authenticated', async () => {
    // Set authenticated state
    useAuthStore.setState({
      user: {
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
      },
      accessToken: 'token',
      refreshToken: 'refresh',
      isAuthenticated: true,
      isLoading: false,
    });

    render(
      <PublicRoute>
        <div>Login Form</div>
      </PublicRoute>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/');
    });

    expect(screen.queryByText('Login Form')).not.toBeInTheDocument();
  });

  it('should redirect to custom path when specified', async () => {
    // Set authenticated state
    useAuthStore.setState({
      user: {
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
      },
      accessToken: 'token',
      refreshToken: 'refresh',
      isAuthenticated: true,
      isLoading: false,
    });

    render(
      <PublicRoute redirectTo="/dashboard">
        <div>Login Form</div>
      </PublicRoute>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('should redirect to returnUrl from query params when authenticated', async () => {
    // Set authenticated state
    useAuthStore.setState({
      user: {
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
      },
      accessToken: 'token',
      refreshToken: 'refresh',
      isAuthenticated: true,
      isLoading: false,
    });

    // Mock returnUrl in query params
    mockGet.mockReturnValue('/profile');

    render(
      <PublicRoute>
        <div>Login Form</div>
      </PublicRoute>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/profile');
    });
  });

  it('should show loading state while checking authentication', () => {
    // Set loading state
    useAuthStore.setState({ isLoading: true });

    render(
      <PublicRoute>
        <div>Login Form</div>
      </PublicRoute>
    );

    // Should show loading spinner
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
    expect(screen.queryByText('Login Form')).not.toBeInTheDocument();
  });

  it('should prioritize returnUrl over default redirectTo', async () => {
    // Set authenticated state
    useAuthStore.setState({
      user: {
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
      },
      accessToken: 'token',
      refreshToken: 'refresh',
      isAuthenticated: true,
      isLoading: false,
    });

    // Mock returnUrl in query params
    mockGet.mockReturnValue('/settings');

    render(
      <PublicRoute redirectTo="/dashboard">
        <div>Login Form</div>
      </PublicRoute>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/settings');
    });
  });
});
