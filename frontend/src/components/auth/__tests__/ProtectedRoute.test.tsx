import { render, screen, waitFor } from '@testing-library/react';
import { useRouter, usePathname } from 'next/navigation';
import { ProtectedRoute, withAuth } from '../ProtectedRoute';
import { useAuthStore } from '@/store/authStore';

// Mock Next.js navigation
jest.mock('next/navigation', () => ({
  useRouter: jest.fn(),
  usePathname: jest.fn(),
}));

describe('ProtectedRoute', () => {
  const mockPush = jest.fn();
  const mockPathname = '/dashboard';

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    (usePathname as jest.Mock).mockReturnValue(mockPathname);
    // Reset auth store
    useAuthStore.setState({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  it('should render children when user is authenticated', () => {
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
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>
    );

    expect(screen.getByText('Protected Content')).toBeInTheDocument();
    expect(mockPush).not.toHaveBeenCalled();
  });

  it('should redirect to login when user is not authenticated', async () => {
    render(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith(
        `/login?returnUrl=${encodeURIComponent(mockPathname)}`
      );
    });

    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('should redirect to custom path when specified', async () => {
    render(
      <ProtectedRoute redirectTo="/custom-login">
        <div>Protected Content</div>
      </ProtectedRoute>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith(
        `/custom-login?returnUrl=${encodeURIComponent(mockPathname)}`
      );
    });
  });

  it('should show loading state while checking authentication', () => {
    // Set loading state
    useAuthStore.setState({ isLoading: true });

    render(
      <ProtectedRoute>
        <div>Protected Content</div>
      </ProtectedRoute>
    );

    // Should show loading spinner
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
    expect(screen.queryByText('Protected Content')).not.toBeInTheDocument();
  });

  it('should not redirect when on the redirect path', async () => {
    (usePathname as jest.Mock).mockReturnValue('/login');

    render(
      <ProtectedRoute redirectTo="/login">
        <div>Protected Content</div>
      </ProtectedRoute>
    );

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalledWith('/login?returnUrl=%2F');
    });
  });
});

describe('withAuth HOC', () => {
  const mockPush = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useRouter as jest.Mock).mockReturnValue({ push: mockPush });
    (usePathname as jest.Mock).mockReturnValue('/dashboard');
    useAuthStore.setState({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,
    });
  });

  it('should wrap component with ProtectedRoute', () => {
    const TestComponent = () => <div>Test Component</div>;
    const WrappedComponent = withAuth(TestComponent);

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

    render(<WrappedComponent />);

    expect(screen.getByText('Test Component')).toBeInTheDocument();
  });

  it('should pass props to wrapped component', () => {
    interface TestProps {
      message: string;
    }

    const TestComponent = ({ message }: TestProps) => <div>{message}</div>;
    const WrappedComponent = withAuth(TestComponent);

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

    render(<WrappedComponent message="Hello World" />);

    expect(screen.getByText('Hello World')).toBeInTheDocument();
  });

  it('should redirect when not authenticated', async () => {
    const TestComponent = () => <div>Test Component</div>;
    const WrappedComponent = withAuth(TestComponent);

    render(<WrappedComponent />);

    await waitFor(() => {
      expect(mockPush).toHaveBeenCalled();
    });

    expect(screen.queryByText('Test Component')).not.toBeInTheDocument();
  });
});
