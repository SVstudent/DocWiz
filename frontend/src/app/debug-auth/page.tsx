'use client';

import { useAuthStore } from '@/store/authStore';
import { Card } from '@/components/ui/Card';
import { useEffect, useState } from 'react';

export default function DebugAuthPage() {
  const authState = useAuthStore();
  const [localStorageData, setLocalStorageData] = useState<string>('');
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    setHydrated(true);
    // Get localStorage data
    const data = localStorage.getItem('auth-storage');
    setLocalStorageData(data || 'No data found');
  }, []);

  const handleClearAuth = () => {
    localStorage.clear();
    authState.logout();
    window.location.reload();
  };

  if (!hydrated) {
    return <div>Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <Card className="max-w-4xl mx-auto p-8">
        <h1 className="text-3xl font-bold mb-6">Auth Debug Page</h1>
        
        <div className="space-y-6">
          <div>
            <h2 className="text-xl font-semibold mb-2">Zustand Store State:</h2>
            <pre className="bg-gray-100 p-4 rounded overflow-auto">
              {JSON.stringify({
                user: authState.user,
                isAuthenticated: authState.isAuthenticated,
                accessToken: authState.accessToken ? `${authState.accessToken.substring(0, 20)}...` : null,
                refreshToken: authState.refreshToken ? `${authState.refreshToken.substring(0, 20)}...` : null,
                isLoading: authState.isLoading,
              }, null, 2)}
            </pre>
          </div>

          <div>
            <h2 className="text-xl font-semibold mb-2">LocalStorage Data:</h2>
            <pre className="bg-gray-100 p-4 rounded overflow-auto">
              {localStorageData}
            </pre>
          </div>

          <div>
            <h2 className="text-xl font-semibold mb-2">Parsed LocalStorage:</h2>
            <pre className="bg-gray-100 p-4 rounded overflow-auto">
              {localStorageData !== 'No data found' 
                ? JSON.stringify(JSON.parse(localStorageData), null, 2)
                : 'No data to parse'}
            </pre>
          </div>

          <div className="flex gap-4">
            <button
              onClick={handleClearAuth}
              className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Clear Auth & Reload
            </button>
            <a
              href="/login"
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 inline-block"
            >
              Go to Login
            </a>
            <a
              href="/visualization"
              className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 inline-block"
            >
              Go to Visualization
            </a>
          </div>
        </div>
      </Card>
    </div>
  );
}
