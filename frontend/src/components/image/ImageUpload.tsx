'use client';

import { useCallback, useState, useRef, ChangeEvent, DragEvent } from 'react';
import { cn } from '@/lib/utils';
import { Button } from '@/components/ui/Button';
import { apiClient, getErrorMessage } from '@/lib/api-client';
import { useImageStore } from '@/store/imageStore';

export interface ImageUploadProps {
  onUploadComplete: (imageId: string, imageUrl: string) => void;
  onUploadError?: (error: string) => void;
  maxSizeMB?: number;
  acceptedFormats?: string[];
  className?: string;
}

export interface UploadedImage {
  id: string;
  url: string;
  width: number;
  height: number;
  format: string;
  uploadedAt: Date;
}

const ACCEPTED_FORMATS = ['image/jpeg', 'image/png', 'image/webp'];
const MAX_SIZE_MB = 10;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

export function ImageUpload({
  onUploadComplete,
  onUploadError,
  maxSizeMB = MAX_SIZE_MB,
  acceptedFormats = ACCEPTED_FORMATS,
  className,
}: ImageUploadProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);
  const [uploadProgress, setUploadProgress] = useState<number>(0);
  const [isUploading, setIsUploading] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);
  const [shouldShowPreview, setShouldShowPreview] = useState(true);
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const { addUploadedImage } = useImageStore();

  const maxSizeBytes = maxSizeMB * 1024 * 1024;

  // Validate file before upload
  const validateFile = useCallback(
    (file: File): { valid: boolean; error?: string } => {
      // Check file type
      if (!acceptedFormats.includes(file.type)) {
        return {
          valid: false,
          error: `Invalid file format. Please upload ${acceptedFormats
            .map((f) => f.split('/')[1].toUpperCase())
            .join(', ')} files only.`,
        };
      }

      // Check file size
      if (file.size > maxSizeBytes) {
        return {
          valid: false,
          error: `File size exceeds ${maxSizeMB}MB limit. Please upload a smaller image.`,
        };
      }

      return { valid: true };
    },
    [acceptedFormats, maxSizeBytes, maxSizeMB]
  );

  // Upload file to backend
  const uploadFile = useCallback(
    async (file: File) => {
      setIsUploading(true);
      setUploadProgress(0);
      setShouldShowPreview(true);

      try {
        // Create form data
        const formData = new FormData();
        formData.append('file', file);

        // Upload with progress tracking
        const response = await apiClient.post<UploadedImage>(
          '/api/images/upload',
          formData,
          {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
            onUploadProgress: (progressEvent) => {
              if (progressEvent.total) {
                const percentCompleted = Math.round(
                  (progressEvent.loaded * 100) / progressEvent.total
                );
                setUploadProgress(percentCompleted);
              }
            },
          }
        );

        // Store uploaded image in state
        addUploadedImage(response.data);

        // Call success callback
        onUploadComplete(response.data.id, response.data.url);
      } catch (error) {
        const errorMessage = getErrorMessage(error);
        setValidationError(errorMessage);
        if (onUploadError) {
          onUploadError(errorMessage);
        }
        // Clear preview on error
        setShouldShowPreview(false);
        setPreview(null);
      } finally {
        setIsUploading(false);
      }
    },
    [onUploadComplete, onUploadError, addUploadedImage]
  );

  // Handle file selection
  const handleFileSelect = useCallback(
    async (file: File) => {
      setValidationError(null);
      setPreview(null);
      setShouldShowPreview(true);

      // Validate file
      const validation = validateFile(file);
      if (!validation.valid) {
        setValidationError(validation.error || 'Invalid file');
        if (onUploadError) {
          onUploadError(validation.error || 'Invalid file');
        }
        return;
      }

      // Create preview
      const reader = new FileReader();
      reader.onloadend = () => {
        // Only set preview if we should show it (upload didn't fail)
        setShouldShowPreview((shouldShow) => {
          if (shouldShow) {
            setPreview(reader.result as string);
          }
          return shouldShow;
        });
      };
      reader.readAsDataURL(file);

      // Upload file to backend
      await uploadFile(file);
    },
    [validateFile, onUploadError, uploadFile]
  );

  // Handle drag events
  const handleDragEnter = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback(
    (e: DragEvent<HTMLDivElement>) => {
      e.preventDefault();
      e.stopPropagation();
      setIsDragging(false);

      const files = e.dataTransfer.files;
      if (files && files.length > 0) {
        handleFileSelect(files[0]);
      }
    },
    [handleFileSelect]
  );

  // Handle file input change
  const handleFileInputChange = useCallback(
    (e: ChangeEvent<HTMLInputElement>) => {
      const files = e.target.files;
      if (files && files.length > 0) {
        handleFileSelect(files[0]);
      }
    },
    [handleFileSelect]
  );

  // Open file picker
  const handleClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  // Clear preview and reset
  const handleClear = useCallback(() => {
    setPreview(null);
    setValidationError(null);
    setUploadProgress(0);
    setShouldShowPreview(true);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, []);

  return (
    <div className={cn('w-full', className)}>
      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept={acceptedFormats.join(',')}
        onChange={handleFileInputChange}
        className="hidden"
        aria-label="Upload image file"
      />

      {/* Upload area */}
      {!preview ? (
        <div
          onDragEnter={handleDragEnter}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={handleClick}
          className={cn(
            'relative flex flex-col items-center justify-center',
            'rounded-lg border-2 border-dashed',
            'min-h-[300px] p-8',
            'cursor-pointer transition-colors',
            'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-surgical-blue-500 focus-visible:ring-offset-2',
            isDragging
              ? 'border-surgical-blue-500 bg-surgical-blue-50'
              : 'border-surgical-gray-300 hover:border-surgical-blue-400 hover:bg-surgical-gray-50',
            validationError && 'border-red-500 bg-red-50'
          )}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              handleClick();
            }
          }}
          aria-label="Click or drag and drop to upload image"
        >
          {/* Upload icon */}
          <svg
            className={cn(
              'mb-4 h-16 w-16',
              isDragging ? 'text-surgical-blue-500' : 'text-surgical-gray-400'
            )}
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
            />
          </svg>

          {/* Upload text */}
          <div className="text-center">
            <p className="mb-2 text-base font-medium text-surgical-gray-900">
              {isDragging ? 'Drop image here' : 'Drag and drop your image here'}
            </p>
            <p className="mb-4 text-sm text-surgical-gray-600">or</p>
            <Button
              type="button"
              variant="primary"
              size="md"
              onClick={(e) => {
                e.stopPropagation();
                handleClick();
              }}
            >
              Choose File
            </Button>
          </div>

          {/* Format and size info */}
          <p className="mt-4 text-xs text-surgical-gray-500">
            Supported formats: JPEG, PNG, WebP • Max size: {maxSizeMB}MB
          </p>

          {/* Validation error */}
          {validationError && (
            <div
              className="mt-4 rounded-md bg-red-100 p-3 text-sm text-red-800"
              role="alert"
              aria-live="polite"
            >
              {validationError}
            </div>
          )}
        </div>
      ) : (
        /* Preview area */
        <div className="space-y-4">
          {/* Image preview */}
          <div className="relative overflow-hidden rounded-lg border-2 border-surgical-gray-300">
            <img
              src={preview}
              alt="Upload preview"
              className="h-auto w-full object-contain"
              style={{ maxHeight: '500px' }}
            />
          </div>

          {/* Upload progress bar */}
          {isUploading && (
            <div className="space-y-2">
              <div className="flex items-center justify-between text-sm">
                <span className="text-surgical-gray-700">Uploading...</span>
                <span className="font-medium text-surgical-blue-600">
                  {uploadProgress}%
                </span>
              </div>
              <div className="h-2 w-full overflow-hidden rounded-full bg-surgical-gray-200">
                <div
                  className="h-full bg-surgical-blue-600 transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                  role="progressbar"
                  aria-valuenow={uploadProgress}
                  aria-valuemin={0}
                  aria-valuemax={100}
                />
              </div>
            </div>
          )}

          {/* Action buttons */}
          <div className="flex gap-3">
            <Button
              type="button"
              variant="outline"
              size="md"
              onClick={handleClear}
              disabled={isUploading}
              fullWidth
            >
              Clear
            </Button>
            <Button
              type="button"
              variant="primary"
              size="md"
              onClick={handleClick}
              disabled={isUploading}
              fullWidth
            >
              Choose Different Image
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
