import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ImageUpload } from '../ImageUpload';
import { apiClient } from '@/lib/api-client';
import { useImageStore } from '@/store/imageStore';

// Mock the API client
jest.mock('@/lib/api-client', () => ({
  apiClient: {
    post: jest.fn(),
  },
  getErrorMessage: jest.fn((error: any) => error.message || 'An error occurred'),
}));

// Mock the image store
jest.mock('@/store/imageStore', () => ({
  useImageStore: jest.fn(),
}));

describe('ImageUpload', () => {
  const mockOnUploadComplete = jest.fn();
  const mockOnUploadError = jest.fn();
  const mockAddUploadedImage = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    (useImageStore as jest.Mock).mockReturnValue({
      addUploadedImage: mockAddUploadedImage,
    });
  });

  describe('File Validation', () => {
    it('should accept valid JPEG file', async () => {
      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
        />
      );

      const file = new File(['image content'], 'test.jpg', { type: 'image/jpeg' });
      const input = screen.getByLabelText(/upload image file/i);

      // Mock successful upload
      (apiClient.post as jest.Mock).mockResolvedValue({
        data: {
          id: 'img-123',
          url: 'https://example.com/image.jpg',
          width: 800,
          height: 600,
          format: 'JPEG',
          uploadedAt: new Date(),
        },
      });

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(mockOnUploadComplete).toHaveBeenCalledWith(
          'img-123',
          'https://example.com/image.jpg'
        );
      });
    });

    it('should accept valid PNG file', async () => {
      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
        />
      );

      const file = new File(['image content'], 'test.png', { type: 'image/png' });
      const input = screen.getByLabelText(/upload image file/i);

      (apiClient.post as jest.Mock).mockResolvedValue({
        data: {
          id: 'img-456',
          url: 'https://example.com/image.png',
          width: 1024,
          height: 768,
          format: 'PNG',
          uploadedAt: new Date(),
        },
      });

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(mockOnUploadComplete).toHaveBeenCalled();
      });
    });

    it('should accept valid WebP file', async () => {
      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
        />
      );

      const file = new File(['image content'], 'test.webp', { type: 'image/webp' });
      const input = screen.getByLabelText(/upload image file/i);

      (apiClient.post as jest.Mock).mockResolvedValue({
        data: {
          id: 'img-789',
          url: 'https://example.com/image.webp',
          width: 1920,
          height: 1080,
          format: 'WEBP',
          uploadedAt: new Date(),
        },
      });

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(mockOnUploadComplete).toHaveBeenCalled();
      });
    });

    it('should reject invalid file format', async () => {
      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
        />
      );

      const file = new File(['image content'], 'test.gif', { type: 'image/gif' });
      const input = screen.getByLabelText(/upload image file/i) as HTMLInputElement;

      // Manually trigger the change event with the file
      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      });
      fireEvent.change(input);

      await waitFor(() => {
        expect(screen.getByText(/invalid file format/i)).toBeInTheDocument();
      });

      expect(mockOnUploadError).toHaveBeenCalled();
      expect(mockOnUploadComplete).not.toHaveBeenCalled();
    });

    it('should reject file exceeding size limit', async () => {
      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
          maxSizeMB={10}
        />
      );

      // Create a file larger than 10MB (using a more realistic size for testing)
      const largeContent = 'a'.repeat(11 * 1024 * 1024);
      const file = new File([largeContent], 'large.jpg', { type: 'image/jpeg' });
      const input = screen.getByLabelText(/upload image file/i) as HTMLInputElement;

      // Manually trigger the change event with the file
      Object.defineProperty(input, 'files', {
        value: [file],
        writable: false,
      });
      fireEvent.change(input);

      await waitFor(() => {
        expect(screen.getByText(/file size exceeds 10mb limit/i)).toBeInTheDocument();
      });

      expect(mockOnUploadError).toHaveBeenCalled();
      expect(mockOnUploadComplete).not.toHaveBeenCalled();
    }, 10000);

    it('should accept file within size limit', async () => {
      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
          maxSizeMB={10}
        />
      );

      // Create a file smaller than 10MB
      const content = new Array(5 * 1024 * 1024).fill('a').join('');
      const file = new File([content], 'valid.jpg', { type: 'image/jpeg' });
      const input = screen.getByLabelText(/upload image file/i);

      (apiClient.post as jest.Mock).mockResolvedValue({
        data: {
          id: 'img-valid',
          url: 'https://example.com/valid.jpg',
          width: 800,
          height: 600,
          format: 'JPEG',
          uploadedAt: new Date(),
        },
      });

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(mockOnUploadComplete).toHaveBeenCalled();
      });
    });
  });

  describe('Upload Success', () => {
    it('should call onUploadComplete with correct data on successful upload', async () => {
      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
        />
      );

      const file = new File(['image content'], 'test.jpg', { type: 'image/jpeg' });
      const input = screen.getByLabelText(/upload image file/i);

      const mockResponse = {
        data: {
          id: 'img-success',
          url: 'https://example.com/success.jpg',
          width: 1024,
          height: 768,
          format: 'JPEG',
          size_bytes: 102400,
          uploadedAt: new Date('2024-01-01T00:00:00Z'),
        },
      };

      (apiClient.post as jest.Mock).mockResolvedValue(mockResponse);

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(mockOnUploadComplete).toHaveBeenCalledWith(
          'img-success',
          'https://example.com/success.jpg'
        );
      });
    });

    it('should store uploaded image in state', async () => {
      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
        />
      );

      const file = new File(['image content'], 'test.jpg', { type: 'image/jpeg' });
      const input = screen.getByLabelText(/upload image file/i);

      const mockResponse = {
        data: {
          id: 'img-store',
          url: 'https://example.com/store.jpg',
          width: 800,
          height: 600,
          format: 'JPEG',
          size_bytes: 51200,
          uploadedAt: new Date(),
        },
      };

      (apiClient.post as jest.Mock).mockResolvedValue(mockResponse);

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(mockAddUploadedImage).toHaveBeenCalledWith(mockResponse.data);
      });
    });

    it('should display image preview after selection', async () => {
      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
        />
      );

      const file = new File(['image content'], 'test.jpg', { type: 'image/jpeg' });
      const input = screen.getByLabelText(/upload image file/i);

      (apiClient.post as jest.Mock).mockResolvedValue({
        data: {
          id: 'img-preview',
          url: 'https://example.com/preview.jpg',
          width: 800,
          height: 600,
          format: 'JPEG',
          uploadedAt: new Date(),
        },
      });

      await userEvent.upload(input, file);

      await waitFor(() => {
        const preview = screen.getByAltText(/upload preview/i);
        expect(preview).toBeInTheDocument();
      });
    });

    it('should show upload progress during upload', async () => {
      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
        />
      );

      const file = new File(['image content'], 'test.jpg', { type: 'image/jpeg' });
      const input = screen.getByLabelText(/upload image file/i);

      let progressCallback: ((event: any) => void) | undefined;

      (apiClient.post as jest.Mock).mockImplementationOnce((url, data, config) => {
        progressCallback = config?.onUploadProgress;
        return new Promise((resolve) => {
          setTimeout(() => {
            if (progressCallback) {
              progressCallback({ loaded: 50, total: 100 });
            }
            resolve({
              data: {
                id: 'img-progress',
                url: 'https://example.com/progress.jpg',
                width: 800,
                height: 600,
                format: 'JPEG',
                uploadedAt: new Date(),
              },
            });
          }, 100);
        });
      });

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(screen.getByText(/uploading/i)).toBeInTheDocument();
      });
    });
  });

  describe('Upload Error Handling', () => {
    beforeEach(() => {
      // Clear all mocks before each test in this suite
      jest.clearAllMocks();
      (useImageStore as jest.Mock).mockReturnValue({
        addUploadedImage: mockAddUploadedImage,
      });
      // Reset the mock implementation to default rejected state
      (apiClient.post as jest.Mock).mockReset();
    });

    it('should call onUploadError on upload failure', async () => {
      // Explicitly mock rejection for this test
      (apiClient.post as jest.Mock).mockRejectedValueOnce(new Error('Upload failed'));

      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
        />
      );

      const file = new File(['image content'], 'test.jpg', { type: 'image/jpeg' });
      const input = screen.getByLabelText(/upload image file/i);

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(mockOnUploadError).toHaveBeenCalled();
        expect(mockOnUploadComplete).not.toHaveBeenCalled();
      });
    });

    it('should display error message on upload failure', async () => {
      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
        />
      );

      const file = new File(['image content'], 'test.jpg', { type: 'image/jpeg' });
      const input = screen.getByLabelText(/upload image file/i);

      (apiClient.post as jest.Mock).mockRejectedValue(new Error('Network error'));

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(screen.getByText(/network error/i)).toBeInTheDocument();
      });
    });

    it('should clear preview on upload error', async () => {
      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
        />
      );

      const file = new File(['image content'], 'test.jpg', { type: 'image/jpeg' });
      const input = screen.getByLabelText(/upload image file/i);

      (apiClient.post as jest.Mock).mockRejectedValue(new Error('Upload failed'));

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(screen.queryByAltText(/upload preview/i)).not.toBeInTheDocument();
      });
    });
  });

  describe('Drag and Drop', () => {
    it('should handle drag enter event', () => {
      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
        />
      );

      const dropzone = screen.getByRole('button', {
        name: /click or drag and drop to upload image/i,
      });

      fireEvent.dragEnter(dropzone);

      expect(screen.getByText(/drop image here/i)).toBeInTheDocument();
    });

    it('should handle drag leave event', () => {
      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
        />
      );

      const dropzone = screen.getByRole('button', {
        name: /click or drag and drop to upload image/i,
      });

      fireEvent.dragEnter(dropzone);
      expect(screen.getByText(/drop image here/i)).toBeInTheDocument();

      fireEvent.dragLeave(dropzone);
      expect(screen.getByText(/drag and drop your image here/i)).toBeInTheDocument();
    });

    it('should handle file drop', async () => {
      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
        />
      );

      const file = new File(['image content'], 'dropped.jpg', { type: 'image/jpeg' });
      const dropzone = screen.getByRole('button', {
        name: /click or drag and drop to upload image/i,
      });

      (apiClient.post as jest.Mock).mockResolvedValue({
        data: {
          id: 'img-dropped',
          url: 'https://example.com/dropped.jpg',
          width: 800,
          height: 600,
          format: 'JPEG',
          uploadedAt: new Date(),
        },
      });

      fireEvent.drop(dropzone, {
        dataTransfer: {
          files: [file],
        },
      });

      await waitFor(() => {
        expect(mockOnUploadComplete).toHaveBeenCalled();
      });
    });
  });

  describe('Clear Functionality', () => {
    it('should clear preview when clear button is clicked', async () => {
      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
        />
      );

      const file = new File(['image content'], 'test.jpg', { type: 'image/jpeg' });
      const input = screen.getByLabelText(/upload image file/i);

      (apiClient.post as jest.Mock).mockResolvedValue({
        data: {
          id: 'img-clear',
          url: 'https://example.com/clear.jpg',
          width: 800,
          height: 600,
          format: 'JPEG',
          uploadedAt: new Date(),
        },
      });

      await userEvent.upload(input, file);

      await waitFor(() => {
        expect(screen.getByAltText(/upload preview/i)).toBeInTheDocument();
      });

      const clearButton = screen.getByRole('button', { name: /clear/i });
      fireEvent.click(clearButton);

      await waitFor(() => {
        expect(screen.queryByAltText(/upload preview/i)).not.toBeInTheDocument();
        expect(screen.getByText(/drag and drop your image here/i)).toBeInTheDocument();
      });
    });
  });

  describe('File Picker Fallback', () => {
    it('should open file picker when choose file button is clicked', () => {
      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
        />
      );

      const chooseFileButton = screen.getByRole('button', { name: /choose file/i });
      const fileInput = screen.getByLabelText(/upload image file/i) as HTMLInputElement;

      // Mock the click method
      const clickSpy = jest.spyOn(fileInput, 'click');

      fireEvent.click(chooseFileButton);

      expect(clickSpy).toHaveBeenCalled();
    });

    it('should open file picker when dropzone is clicked', () => {
      render(
        <ImageUpload
          onUploadComplete={mockOnUploadComplete}
          onUploadError={mockOnUploadError}
        />
      );

      const dropzone = screen.getByRole('button', {
        name: /click or drag and drop to upload image/i,
      });
      const fileInput = screen.getByLabelText(/upload image file/i) as HTMLInputElement;

      const clickSpy = jest.spyOn(fileInput, 'click');

      fireEvent.click(dropzone);

      expect(clickSpy).toHaveBeenCalled();
    });
  });
});
