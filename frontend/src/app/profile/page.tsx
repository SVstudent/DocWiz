'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { ProfileView } from '@/components/profile/ProfileView';
import { ProfileForm, ProfileFormData } from '@/components/profile/ProfileForm';
import { ProfileHistory } from '@/components/profile/ProfileHistory';
import { AppLayout } from '@/components/layout';
import { useProfileStore } from '@/store/profileStore';
import { useAuthStore } from '@/store/authStore';
import { apiClient, getErrorMessage } from '@/lib/api-client';
import { Button } from '@/components/ui/Button';
import { Card, CardContent } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { useToast } from '@/hooks/useToast';

type ViewMode = 'view' | 'edit' | 'create' | 'history';

interface ProfileVersion {
  id: string;
  profile_id: string;
  version: number;
  data: Record<string, unknown>;
  created_at: string;
}

export default function ProfilePage() {
  const router = useRouter();
  const { user } = useAuthStore();
  const { profile, setProfile, setLoading, setError } = useProfileStore();
  const toast = useToast();
  
  const [viewMode, setViewMode] = useState<ViewMode>('view');
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [versions, setVersions] = useState<ProfileVersion[]>([]);

  // Fetch profile on mount
  useEffect(() => {
    if (!user) {
      router.push('/login');
      return;
    }

    fetchProfile();
  }, [user]);

  const fetchProfile = async () => {
    try {
      setIsLoading(true);
      setLoading(true);
      
      // Try to get the user's profile
      const response = await apiClient.get(`/api/profiles/me`);
      
      if (response.data) {
        setProfile(response.data);
        setViewMode('view');
      }
    } catch (error: unknown) {
      const errorMessage = getErrorMessage(error);
      
      // If profile doesn't exist (404), show create form
      if (errorMessage.includes('404') || errorMessage.includes('not found')) {
        setViewMode('create');
      } else {
        setError(errorMessage);
        toast.error(errorMessage);
      }
    } finally {
      setIsLoading(false);
      setLoading(false);
    }
  };

  const fetchVersionHistory = async () => {
    if (!profile) return;

    try {
      const response = await apiClient.get(`/api/profiles/${profile.id}/history`);
      setVersions(response.data);
      setViewMode('history');
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(`Failed to load version history: ${errorMessage}`);
    }
  };

  const handleCreateProfile = async (data: ProfileFormData) => {
    try {
      setIsSaving(true);
      
      const response = await apiClient.post('/api/profiles', data);
      
      setProfile(response.data);
      setViewMode('view');
      
      toast.success('Profile created successfully');
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(`Failed to create profile: ${errorMessage}`);
      throw error;
    } finally {
      setIsSaving(false);
    }
  };

  const handleUpdateProfile = async (data: ProfileFormData) => {
    if (!profile) return;

    try {
      setIsSaving(true);
      
      const response = await apiClient.put(`/api/profiles/${profile.id}`, data);
      
      setProfile(response.data);
      setViewMode('view');
      
      toast.success('Profile updated successfully');
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(`Failed to update profile: ${errorMessage}`);
      throw error;
    } finally {
      setIsSaving(false);
    }
  };

  const handleRestoreVersion = async (version: ProfileVersion) => {
    if (!profile) return;

    try {
      setIsSaving(true);
      
      // Convert version data to ProfileFormData format
      const restoreData = version.data as unknown as ProfileFormData;
      
      const response = await apiClient.put(`/api/profiles/${profile.id}`, restoreData);
      
      setProfile(response.data);
      setViewMode('view');
      
      toast.success(`Profile restored to version ${version.version}`);
    } catch (error) {
      const errorMessage = getErrorMessage(error);
      toast.error(`Failed to restore version: ${errorMessage}`);
    } finally {
      setIsSaving(false);
    }
  };

  // Loading state
  if (isLoading) {
    return (
      <AppLayout showBreadcrumb>
        <div className="max-w-4xl mx-auto">
          <Card>
            <CardContent className="py-8">
              <div className="space-y-4">
                <Skeleton className="h-8 w-1/3" />
                <Skeleton className="h-4 w-1/4" />
                <div className="space-y-2 mt-6">
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-3/4" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout showBreadcrumb>
      <div className="max-w-4xl mx-auto">
      {viewMode === 'create' && (
        <ProfileForm
          onSubmit={handleCreateProfile}
          isLoading={isSaving}
        />
      )}

      {viewMode === 'edit' && profile && (
        <ProfileForm
          initialData={profile}
          onSubmit={handleUpdateProfile}
          onCancel={() => setViewMode('view')}
          isLoading={isSaving}
        />
      )}

      {viewMode === 'view' && profile && (
        <ProfileView
          profile={profile}
          onEdit={() => setViewMode('edit')}
          onViewHistory={fetchVersionHistory}
        />
      )}

      {viewMode === 'history' && (
        <ProfileHistory
          versions={versions}
          onClose={() => setViewMode('view')}
          onRestore={handleRestoreVersion}
        />
      )}

      {!profile && viewMode === 'view' && (
        <Card>
          <CardContent className="py-12 text-center">
            <h2 className="text-2xl font-bold text-surgical-gray-900 mb-4">
              No Profile Found
            </h2>
            <p className="text-surgical-gray-600 mb-6">
              Create your profile to get started with personalized surgical planning
            </p>
            <Button onClick={() => setViewMode('create')}>
              Create Profile
            </Button>
          </CardContent>
        </Card>
      )}
      </div>
    </AppLayout>
  );
}
