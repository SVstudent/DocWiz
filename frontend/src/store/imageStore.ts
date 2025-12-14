import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export interface UploadedImage {
  id: string;
  url: string;
  width: number;
  height: number;
  format: string;
  uploadedAt: Date;
}

interface ImageState {
  currentImage: UploadedImage | null;
  uploadedImages: UploadedImage[];
  setCurrentImage: (image: UploadedImage | null) => void;
  addUploadedImage: (image: UploadedImage) => void;
  clearCurrentImage: () => void;
  clearAllImages: () => void;
}

export const useImageStore = create<ImageState>()(
  persist(
    (set) => ({
      currentImage: null,
      uploadedImages: [],

      setCurrentImage: (image) =>
        set({ currentImage: image }),

      addUploadedImage: (image) =>
        set((state) => ({
          currentImage: image,
          uploadedImages: [image, ...state.uploadedImages],
        })),

      clearCurrentImage: () =>
        set({ currentImage: null }),

      clearAllImages: () =>
        set({ currentImage: null, uploadedImages: [] }),
    }),
    {
      name: 'image-storage',
    }
  )
);
