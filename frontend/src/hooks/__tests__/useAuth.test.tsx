import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ReactNode } from 'react';
import { useLogin, useRegister, useLogout, useRefreshToken, useAuth } from '../useAuth';
import { useAuthStore } from '@/store/authStore';
import { apiClient } from '@/lib/api-client';

// Mock the API client
jest.mock('@/lib/api-client', () => ({
  apiClient: {
    post: jest.fn(),
  },
  getErrorMessage: jest.fn((error) => error.message || 'An error occurred'),
}));

// Create a wrapper with QueryClient
const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  const Wrapper = ({ children }: { children: ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
  
  return Wrapper;
};

describe('useAuth hooks', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    // Reset auth store
    useAuthStore.getState().logout();
  });

  describe('useLogin', () => {
    it('should successfully login and update auth state', async () => {
      const mockResponse = {
        data: {
          access_token: 'mock-access-token',
          refresh_token: 'mock-refresh-token',
          user: {
            id: '123',
            email: 'test@example.com',
            name: 'Test User',
          },
        },
      };

      (apiClient.post as jest.Mock).mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useLogin(), {
        wrapper: createWrapper(),
      });

      const credentials = {
        email: 'test@example.com',
        password: 'password123',
      };

      await waitFor(() => {
        result.current.mutate(credentials);
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // Verify API was called correctly
      expect(apiClient.post).toHaveBeenCalledWith('/api/auth/login', credentials);

      // Verify auth store was updated
      const authState = useAuthStore.getState();
      expect(authState.user).toEqual(mockResponse.data.user);
      expect(authState.accessToken).toBe(mockResponse.data.access_token);
      expect(authState.refreshToken).toBe(mockResponse.data.refresh_token);
      expect(authState.isAuthenticated).toBe(true);
    });

    it('should handle login failure', async () => {
      const mockError = new Error('Invalid credentials');
      (apiClient.post as jest.Mock).mockRejectedValueOnce(mockError);

      const { result } = renderHook(() => useLogin(), {
        wrapper: createWrapper(),
      });

      const credentials = {
        email: 'test@example.com',
        password: 'wrongpassword',
      };

      await waitFor(() => {
        result.current.mutate(credentials);
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      // Verify auth store was not updated
      const authState = useAuthStore.getState();
      expect(authState.user).toBeNull();
      expect(authState.isAuthenticated).toBe(false);
    });
  });

  describe('useRegister', () => {
    it('should successfully register and update auth state', async () => {
      const mockResponse = {
        data: {
          access_token: 'mock-access-token',
          refresh_token: 'mock-refresh-token',
          user: {
            id: '456',
            email: 'newuser@example.com',
            name: 'New User',
          },
        },
      };

      (apiClient.post as jest.Mock).mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useRegister(), {
        wrapper: createWrapper(),
      });

      const registerData = {
        name: 'New User',
        email: 'newuser@example.com',
        password: 'password123',
      };

      await waitFor(() => {
        result.current.mutate(registerData);
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // Verify API was called correctly
      expect(apiClient.post).toHaveBeenCalledWith('/api/auth/register', registerData);

      // Verify auth store was updated
      const authState = useAuthStore.getState();
      expect(authState.user).toEqual(mockResponse.data.user);
      expect(authState.accessToken).toBe(mockResponse.data.access_token);
      expect(authState.isAuthenticated).toBe(true);
    });

    it('should handle registration validation errors', async () => {
      const mockError = new Error('Email already exists');
      (apiClient.post as jest.Mock).mockRejectedValueOnce(mockError);

      const { result } = renderHook(() => useRegister(), {
        wrapper: createWrapper(),
      });

      const registerData = {
        name: 'Test User',
        email: 'existing@example.com',
        password: 'password123',
      };

      await waitFor(() => {
        result.current.mutate(registerData);
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      // Verify auth store was not updated
      const authState = useAuthStore.getState();
      expect(authState.user).toBeNull();
      expect(authState.isAuthenticated).toBe(false);
    });
  });

  describe('useLogout', () => {
    it('should successfully logout and clear auth state', async () => {
      // Set up authenticated state
      useAuthStore.getState().setUser({
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
      });
      useAuthStore.getState().setTokens('access-token', 'refresh-token');

      (apiClient.post as jest.Mock).mockResolvedValueOnce({});

      const { result } = renderHook(() => useLogout(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        result.current.mutate();
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // Verify API was called
      expect(apiClient.post).toHaveBeenCalledWith('/api/auth/logout');

      // Verify auth store was cleared
      const authState = useAuthStore.getState();
      expect(authState.user).toBeNull();
      expect(authState.accessToken).toBeNull();
      expect(authState.refreshToken).toBeNull();
      expect(authState.isAuthenticated).toBe(false);
    });

    it('should clear auth state even if API call fails', async () => {
      // Set up authenticated state
      useAuthStore.getState().setUser({
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
      });
      useAuthStore.getState().setTokens('access-token', 'refresh-token');

      const mockError = new Error('Network error');
      (apiClient.post as jest.Mock).mockRejectedValueOnce(mockError);

      const { result } = renderHook(() => useLogout(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        result.current.mutate();
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      // Verify auth store was still cleared
      const authState = useAuthStore.getState();
      expect(authState.user).toBeNull();
      expect(authState.isAuthenticated).toBe(false);
    });
  });

  describe('useRefreshToken', () => {
    it('should successfully refresh tokens', async () => {
      const mockResponse = {
        data: {
          access_token: 'new-access-token',
          refresh_token: 'new-refresh-token',
        },
      };

      (apiClient.post as jest.Mock).mockResolvedValueOnce(mockResponse);

      const { result } = renderHook(() => useRefreshToken(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        result.current.mutate('old-refresh-token');
      });

      await waitFor(() => {
        expect(result.current.isSuccess).toBe(true);
      });

      // Verify API was called correctly
      expect(apiClient.post).toHaveBeenCalledWith('/api/auth/refresh', {
        refresh_token: 'old-refresh-token',
      });

      // Verify tokens were updated
      const authState = useAuthStore.getState();
      expect(authState.accessToken).toBe('new-access-token');
      expect(authState.refreshToken).toBe('new-refresh-token');
    });

    it('should logout user if token refresh fails', async () => {
      // Set up authenticated state
      useAuthStore.getState().setUser({
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
      });
      useAuthStore.getState().setTokens('access-token', 'refresh-token');

      const mockError = new Error('Invalid refresh token');
      (apiClient.post as jest.Mock).mockRejectedValueOnce(mockError);

      const { result } = renderHook(() => useRefreshToken(), {
        wrapper: createWrapper(),
      });

      await waitFor(() => {
        result.current.mutate('invalid-refresh-token');
      });

      await waitFor(() => {
        expect(result.current.isError).toBe(true);
      });

      // Verify user was logged out
      const authState = useAuthStore.getState();
      expect(authState.user).toBeNull();
      expect(authState.isAuthenticated).toBe(false);
    });
  });

  describe('useAuth', () => {
    it('should provide auth state and methods', () => {
      // Set up authenticated state
      const mockUser = {
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
      };
      useAuthStore.getState().setUser(mockUser);
      useAuthStore.getState().setTokens('access-token', 'refresh-token');

      const { result } = renderHook(() => useAuth(), {
        wrapper: createWrapper(),
      });

      expect(result.current.user).toEqual(mockUser);
      expect(result.current.isAuthenticated).toBe(true);
      expect(result.current.accessToken).toBe('access-token');
      expect(result.current.refreshToken).toBe('refresh-token');
      expect(typeof result.current.login).toBe('function');
      expect(typeof result.current.register).toBe('function');
      expect(typeof result.current.logout).toBe('function');
      expect(typeof result.current.refresh).toBe('function');
    });
  });
});
