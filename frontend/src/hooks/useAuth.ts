import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient, getErrorMessage } from '@/lib/api-client';
import { useAuthStore } from '@/store/authStore';
import { useEffect } from 'react';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
  name: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    name: string;
    is_active: boolean;
  };
}

interface RefreshTokenResponse {
  access_token: string;
  refresh_token: string;
}

/**
 * Hook for user authentication state and actions
 */
export function useAuth() {
  const { user, isAuthenticated, accessToken, refreshToken } = useAuthStore();
  const loginMutation = useLogin();
  const registerMutation = useRegister();
  const logoutMutation = useLogout();
  const refreshMutation = useRefreshToken();

  return {
    user,
    isAuthenticated,
    accessToken,
    refreshToken,
    login: loginMutation.mutateAsync,
    register: registerMutation.mutateAsync,
    logout: logoutMutation.mutateAsync,
    refresh: refreshMutation.mutateAsync,
    isLoading:
      loginMutation.isPending ||
      registerMutation.isPending ||
      logoutMutation.isPending ||
      refreshMutation.isPending,
  };
}

export function useLogin() {
  const queryClient = useQueryClient();
  const { setUser, setTokens } = useAuthStore();

  return useMutation({
    mutationFn: async (credentials: LoginCredentials) => {
      const response = await apiClient.post<AuthResponse>(
        '/api/auth/login',
        credentials
      );
      return response.data;
    },
    onSuccess: (data) => {
      setUser(data.user);
      // For now, use access_token for both since we don't have refresh tokens yet
      setTokens(data.access_token, data.access_token);
      queryClient.invalidateQueries();
    },
    onError: (error) => {
      console.error('Login failed:', getErrorMessage(error));
    },
  });
}

export function useRegister() {
  const queryClient = useQueryClient();
  const { setUser, setTokens } = useAuthStore();

  return useMutation({
    mutationFn: async (data: RegisterData) => {
      const response = await apiClient.post<AuthResponse>(
        '/api/auth/register',
        data
      );
      return response.data;
    },
    onSuccess: (data) => {
      setUser(data.user);
      // For now, use access_token for both since we don't have refresh tokens yet
      setTokens(data.access_token, data.access_token);
      queryClient.invalidateQueries();
    },
    onError: (error) => {
      console.error('Registration failed:', getErrorMessage(error));
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  const { logout } = useAuthStore();

  return useMutation({
    mutationFn: async () => {
      await apiClient.post('/api/auth/logout');
    },
    onSuccess: () => {
      logout();
      queryClient.clear();
    },
    onError: (error) => {
      console.error('Logout failed:', getErrorMessage(error));
      // Logout locally even if API call fails
      logout();
      queryClient.clear();
    },
  });
}

export function useRefreshToken() {
  const { setTokens, logout } = useAuthStore();

  return useMutation({
    mutationFn: async (refreshToken: string) => {
      const response = await apiClient.post<RefreshTokenResponse>(
        '/api/auth/refresh',
        { refresh_token: refreshToken }
      );
      return response.data;
    },
    onSuccess: (data) => {
      setTokens(data.access_token, data.refresh_token);
    },
    onError: (error) => {
      console.error('Token refresh failed:', getErrorMessage(error));
      // Logout user if refresh fails
      logout();
    },
  });
}

/**
 * Hook to automatically refresh token before expiration
 * Call this in your root layout or app component
 */
export function useTokenRefresh() {
  const { accessToken, refreshToken, logout } = useAuthStore();
  const refreshMutation = useRefreshToken();

  useEffect(() => {
    if (!accessToken || !refreshToken) {
      return;
    }

    // Decode JWT to get expiration time
    try {
      const payload = JSON.parse(atob(accessToken.split('.')[1]));
      const expiresAt = payload.exp * 1000; // Convert to milliseconds
      const now = Date.now();
      const timeUntilExpiry = expiresAt - now;

      // If token is already expired, logout immediately
      if (timeUntilExpiry <= 0) {
        console.warn('Token expired, logging out');
        logout();
        return;
      }

      // Refresh token 5 minutes before expiration
      const refreshTime = timeUntilExpiry - 5 * 60 * 1000;

      if (refreshTime > 0) {
        const timeoutId = setTimeout(() => {
          refreshMutation.mutate(refreshToken);
        }, refreshTime);

        return () => clearTimeout(timeoutId);
      } else {
        // Token about to expire, refresh immediately
        refreshMutation.mutate(refreshToken);
      }
    } catch (error) {
      console.error('Failed to decode token:', error);
      // If we can't decode the token, it's invalid - logout
      logout();
    }
  }, [accessToken, refreshToken, refreshMutation, logout]);
}
