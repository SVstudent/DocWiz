import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  setUser: (user: User) => void;
  setTokens: (accessToken: string, refreshToken: string) => void;
  logout: () => void;
  setLoading: (isLoading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      setUser: (user) => {
        console.log('AuthStore: setUser called with:', user);
        set({
          user,
          isAuthenticated: true,
        });
        // Log the state after setting
        setTimeout(() => {
          const state = get();
          console.log('AuthStore: State after setUser:', {
            user: state.user,
            isAuthenticated: state.isAuthenticated,
          });
        }, 0);
      },

      setTokens: (accessToken, refreshToken) => {
        console.log('AuthStore: setTokens called');
        set({
          accessToken,
          refreshToken,
        });
      },

      logout: () => {
        console.log('AuthStore: logout called');
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
        });
      },

      setLoading: (isLoading) =>
        set({
          isLoading,
        }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state) => {
        console.log('AuthStore: Rehydrated from localStorage:', state);
      },
    }
  )
);
