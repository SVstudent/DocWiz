'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';

export default function ClearAuthPage() {
  const router = useRouter();
  const { logout } = useAuthStore();

  useEffect(() => {
    // Clear all auth data
    logout();
    
    // Also clear localStorage directly to be sure
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth-storage');
      localStorage.clear();
    }
    
    // Redirect to login after a short delay
    setTimeout(() => {
      router.push('/login');
    }, 1000);
  }, [logout, router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">
          Clearing Authentication Data...
        </h1>
        <p className="text-gray-600">
          You will be redirected to the login page.
        </p>
      </div>
    </div>
  );
}
