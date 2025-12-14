'use client';

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';

interface ProfileVersion {
  id: string;
  profile_id: string;
  version: number;
  data: Record<string, unknown>;
  created_at: string;
}

interface ProfileHistoryProps {
  versions: ProfileVersion[];
  onClose: () => void;
  onRestore?: (version: ProfileVersion) => void;
}

export function ProfileHistory({ versions, onClose, onRestore }: ProfileHistoryProps) {
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getChangeSummary = (versionData: Record<string, unknown>): string[] => {
    const changes: string[] = [];
    
    if (versionData.name) changes.push('Name updated');
    if (versionData.date_of_birth) changes.push('Date of birth updated');
    if (versionData.location) changes.push('Location updated');
    if (versionData.insurance_info) changes.push('Insurance information updated');
    if (versionData.medical_history) changes.push('Medical history updated');
    
    return changes.length > 0 ? changes : ['Profile created'];
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-start">
        <div>
          <h2 className="text-2xl font-bold text-surgical-gray-900">Version History</h2>
          <p className="text-sm text-surgical-gray-600 mt-1">
            View all changes made to your profile
          </p>
        </div>
        <Button variant="outline" onClick={onClose}>
          Close
        </Button>
      </div>

      <div className="space-y-4">
        {versions.length === 0 ? (
          <Card>
            <CardContent className="py-8 text-center">
              <p className="text-surgical-gray-600">No version history available</p>
            </CardContent>
          </Card>
        ) : (
          versions.map((version, index) => {
            const changes = getChangeSummary(version.data);
            const isLatest = index === 0;

            return (
              <Card key={version.id} variant={isLatest ? 'outlined' : 'default'}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg flex items-center gap-2">
                        Version {version.version}
                        {isLatest && (
                          <span className="text-xs font-normal bg-surgical-blue-100 text-surgical-blue-700 px-2 py-1 rounded">
                            Current
                          </span>
                        )}
                      </CardTitle>
                      <CardDescription>{formatDate(version.created_at)}</CardDescription>
                    </div>
                    {!isLatest && onRestore && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => onRestore(version)}
                      >
                        Restore
                      </Button>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-surgical-gray-700">Changes:</p>
                    <ul className="list-disc list-inside space-y-1">
                      {changes.map((change, idx) => (
                        <li key={idx} className="text-sm text-surgical-gray-600">
                          {change}
                        </li>
                      ))}
                    </ul>
                  </div>
                </CardContent>
              </Card>
            );
          })
        )}
      </div>
    </div>
  );
}
