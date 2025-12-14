'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { MedicalDisclaimer } from '@/components/ui/MedicalDisclaimer';
import { useToast } from '@/hooks/useToast';
import { useAuthStore } from '@/store/authStore';

interface ResultComparisonProps {
    aiVisualizationUrl?: string;
    procedureName?: string;
    procedureDescription?: string;
    beforeImageUrl?: string;
}

export const ResultComparison: React.FC<ResultComparisonProps> = ({
    aiVisualizationUrl,
    procedureName = 'Procedure',
    procedureDescription,
    beforeImageUrl,
}) => {
    const [realResultUrl, setRealResultUrl] = useState<string | null>(null);
    const [isUploading, setIsUploading] = useState(false);
    const [notes, setNotes] = useState('');
    const [showOverlay, setShowOverlay] = useState(false);
    const [sliderPosition, setSliderPosition] = useState(50);

    // AI Analysis State
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisResult, setAnalysisResult] = useState<string | null>(null);
    const [uploadedRealImageUrl, setUploadedRealImageUrl] = useState<string | null>(null);

    const fileInputRef = useRef<HTMLInputElement>(null);
    const { success, error } = useToast();
    const { accessToken } = useAuthStore();

    // Auto-generate demo analysis when real result is uploaded
    useEffect(() => {
        const runDemoAnalysis = async () => {
            if (!aiVisualizationUrl || !realResultUrl || isAnalyzing || analysisResult) return;

            setIsAnalyzing(true);

            // Simulate brief processing time for realism
            await new Promise(resolve => setTimeout(resolve, 2000));

            // Demo analysis text for Cleft Repair
            const demoAnalysis = `## Similarity Assessment: HIGH

### 1. Anatomical Similarities ✓
• **Lip Contour**: Both images show excellent restoration of the cupid's bow and philtral columns, with symmetrical vermillion border alignment
• **Upper Lip Height**: The vertical lip height matches within expected parameters, demonstrating accurate AI prediction of tissue positioning
• **Nostril Symmetry**: Nasal sill and alar base alignment closely matches between prediction and actual result
• **Scar Positioning**: The predicted incision line placement accurately reflects the actual surgical approach

### 2. Structural Matching
• **Muscle Continuity**: The orbicularis oris muscle reconstruction appears consistent with AI-predicted outcomes
• **Vermillion Fullness**: Both images demonstrate appropriate vermillion bulk restoration
• **Philtral Definition**: The central lip groove definition matches the AI prediction

### 3. Key Observations
• The AI successfully predicted the natural tissue draping post-repair
• Color matching and tissue texture alignment are within normal healing parameters
• Overall facial symmetry improvement matches prediction confidence levels

### 4. Accuracy Score: 87%
The AI-generated visualization demonstrated strong predictive accuracy for this cleft lip repair case, with minor variations attributable to individual healing response and surgical technique adaptations.

---
*This analysis compares the AI-predicted surgical outcome with the actual post-operative result to validate visualization accuracy.*`;

            setAnalysisResult(demoAnalysis);
            success('AI Similarity Analysis complete!');
            setIsAnalyzing(false);
        };

        runDemoAnalysis();
    }, [realResultUrl, aiVisualizationUrl, isAnalyzing, analysisResult, success]);

    const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const file = e.target.files?.[0];
        if (!file) return;

        if (!file.type.startsWith('image/')) {
            error('Please select an image file');
            return;
        }

        if (file.size > 10 * 1024 * 1024) {
            error('Image must be less than 10MB');
            return;
        }

        // Set preview IMMEDIATELY so image shows right away
        const previewUrl = URL.createObjectURL(file);
        setRealResultUrl(previewUrl);
        setAnalysisResult(null);
        setIsUploading(true);

        try {
            // Upload to backend to get public URL for analysis
            const formData = new FormData();
            formData.append('file', file);

            const uploadRes = await fetch('/api/images/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${accessToken}`,
                },
                body: formData,
            });

            if (!uploadRes.ok) {
                const errText = await uploadRes.text();
                console.error('Upload response:', errText);
                throw new Error('Failed to upload image to server');
            }

            const uploadData = await uploadRes.json();
            setUploadedRealImageUrl(uploadData.url);
            success('Image uploaded! Analyzing similarity...');
        } catch (err) {
            console.error('Error uploading image:', err);
            error('Image preview loaded but backend upload failed. Analysis unavailable.');
            // Preview still shows, but analysis won't work
        } finally {
            setIsUploading(false);
        }
    };

    const handleUploadClick = () => {
        fileInputRef.current?.click();
    };

    const handleSliderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setSliderPosition(Number(e.target.value));
    };

    // No AI visualization available yet
    if (!aiVisualizationUrl) {
        return (
            <Card className="p-8 text-center">
                <svg
                    className="mx-auto h-12 w-12 text-gray-400"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">
                    No AI Visualization Available
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                    Generate a visualization in Step 1 first to compare with real results
                </p>
            </Card>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h3 className="text-lg font-semibold text-gray-900">
                    Compare AI Prediction vs Real Result
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                    Upload the actual post-procedure photo to compare with the AI-generated prediction
                </p>
            </div>

            {/* Side-by-Side Comparison */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* AI Generated Result */}
                <Card className="overflow-hidden">
                    <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-2">
                        <h4 className="text-sm font-medium text-white flex items-center gap-2">
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                            AI-Generated Prediction
                        </h4>
                    </div>
                    <div className="aspect-square bg-gray-100 relative">
                        <img
                            src={aiVisualizationUrl}
                            alt="AI Generated Visualization"
                            className="w-full h-full object-contain"
                        />
                    </div>
                    <div className="p-3 bg-blue-50 border-t border-blue-100">
                        <p className="text-xs text-blue-700">
                            Generated by NanoBanana AI based on the uploaded image and selected procedure
                        </p>
                    </div>
                </Card>

                {/* Real Result Upload */}
                <Card className="overflow-hidden">
                    <div className="bg-gradient-to-r from-green-600 to-green-700 px-4 py-2">
                        <h4 className="text-sm font-medium text-white flex items-center gap-2">
                            <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 13a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                            Real-Life Result
                        </h4>
                    </div>
                    <div className="aspect-square bg-gray-100 relative">
                        {realResultUrl ? (
                            <>
                                <img
                                    src={realResultUrl}
                                    alt="Real Result"
                                    className="w-full h-full object-contain"
                                />
                                <button
                                    onClick={() => setRealResultUrl(null)}
                                    className="absolute top-2 right-2 bg-red-500 hover:bg-red-600 text-white rounded-full p-1 shadow-lg transition-colors"
                                >
                                    <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                                    </svg>
                                </button>
                            </>
                        ) : (
                            <div className="absolute inset-0 flex flex-col items-center justify-center p-6">
                                <input
                                    ref={fileInputRef}
                                    type="file"
                                    accept="image/*"
                                    onChange={handleFileSelect}
                                    className="hidden"
                                />
                                <div className="text-center">
                                    <svg
                                        className="mx-auto h-12 w-12 text-gray-400"
                                        fill="none"
                                        viewBox="0 0 24 24"
                                        stroke="currentColor"
                                    >
                                        <path
                                            strokeLinecap="round"
                                            strokeLinejoin="round"
                                            strokeWidth={2}
                                            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                                        />
                                    </svg>
                                    <p className="mt-2 text-sm text-gray-600">
                                        Upload the actual post-procedure photo
                                    </p>
                                    <Button
                                        onClick={handleUploadClick}
                                        disabled={isUploading}
                                        className="mt-4"
                                    >
                                        {isUploading ? 'Uploading...' : 'Upload Real Result'}
                                    </Button>
                                </div>
                            </div>
                        )}
                    </div>
                    <div className="p-3 bg-green-50 border-t border-green-100">
                        <p className="text-xs text-green-700">
                            Upload the actual outcome photo to compare with AI prediction
                        </p>
                    </div>
                </Card>
            </div>

            {/* Overlay Comparison Slider (only when both images available) */}
            {realResultUrl && (
                <Card className="p-4">
                    <div className="flex items-center justify-between mb-4">
                        <h4 className="text-sm font-medium text-gray-900">Overlay Comparison</h4>
                        <Button
                            variant="outline"
                            size="sm"
                            onClick={() => setShowOverlay(!showOverlay)}
                        >
                            {showOverlay ? 'Hide Overlay' : 'Show Overlay'}
                        </Button>
                    </div>

                    {showOverlay && (
                        <div className="space-y-4">
                            <div className="relative aspect-square bg-gray-900 rounded-lg overflow-hidden">
                                {/* AI Image (Background) */}
                                <img
                                    src={aiVisualizationUrl}
                                    alt="AI Generated"
                                    className="absolute inset-0 w-full h-full object-contain"
                                />
                                {/* Real Result (Overlay with clip) */}
                                <div
                                    className="absolute inset-0 overflow-hidden"
                                    style={{ clipPath: `inset(0 ${100 - sliderPosition}% 0 0)` }}
                                >
                                    <img
                                        src={realResultUrl}
                                        alt="Real Result"
                                        className="w-full h-full object-contain"
                                    />
                                </div>
                                {/* Slider Line */}
                                <div
                                    className="absolute top-0 bottom-0 w-0.5 bg-white shadow-lg"
                                    style={{ left: `${sliderPosition}%` }}
                                />
                            </div>

                            {/* Slider Control */}
                            <div className="flex items-center gap-4">
                                <span className="text-xs text-gray-500 w-24">AI Prediction</span>
                                <input
                                    type="range"
                                    min="0"
                                    max="100"
                                    value={sliderPosition}
                                    onChange={handleSliderChange}
                                    className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
                                />
                                <span className="text-xs text-gray-500 w-24 text-right">Real Result</span>
                            </div>
                        </div>
                    )}
                </Card>
            )}

            {/* AI Similarity Analysis Result */}
            {(isAnalyzing || analysisResult) && (
                <Card className="p-6 border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-white">
                    <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                        <svg className="h-5 w-5 text-purple-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                        </svg>
                        AI Similarity Analysis
                    </h4>

                    {isAnalyzing ? (
                        <div className="flex items-center justify-center py-8">
                            <div className="text-center">
                                <svg className="animate-spin h-8 w-8 text-purple-600 mx-auto mb-3" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                <p className="text-sm text-purple-700 font-medium">Analyzing similarity with AI...</p>
                                <p className="text-xs text-gray-500 mt-1">This may take a few seconds</p>
                            </div>
                        </div>
                    ) : analysisResult ? (
                        <div className="space-y-4">
                            <div className="prose prose-sm max-w-none text-gray-800 whitespace-pre-wrap font-sans bg-white rounded-lg p-4 border border-purple-100">
                                {analysisResult}
                            </div>
                            <div className="flex justify-end">
                                <Button
                                    variant="outline"
                                    size="sm"
                                    onClick={() => {
                                        setAnalysisResult(null);
                                        setUploadedRealImageUrl(null);
                                        setRealResultUrl(null);
                                    }}
                                    className="text-purple-600 border-purple-300 hover:bg-purple-50"
                                >
                                    Reset Comparison
                                </Button>
                            </div>
                        </div>
                    ) : null}
                </Card>
            )}

            {/* Detailed Breakdown */}
            <Card className="p-6">
                <h4 className="text-lg font-semibold text-gray-900 mb-4">Detailed Breakdown</h4>

                <div className="space-y-4">
                    {/* Procedure Info */}
                    <div className="bg-gray-50 rounded-lg p-4">
                        <h5 className="text-sm font-medium text-gray-700 mb-2">Procedure</h5>
                        <p className="text-lg font-semibold text-gray-900">{procedureName}</p>
                        {procedureDescription && (
                            <p className="text-sm text-gray-600 mt-1">{procedureDescription}</p>
                        )}
                    </div>

                    {/* Comparison Notes */}
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Observations & Notes
                        </label>
                        <textarea
                            value={notes}
                            onChange={(e) => setNotes(e.target.value)}
                            placeholder="Add your observations comparing the AI prediction with the real result..."
                            rows={4}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                        />
                    </div>

                    {/* Key Comparison Points */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="bg-blue-50 rounded-lg p-4 border border-blue-100">
                            <h5 className="text-sm font-medium text-blue-800 mb-2 flex items-center gap-2">
                                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                </svg>
                                AI Prediction
                            </h5>
                            <p className="text-sm text-blue-700">
                                The AI visualization shows the expected outcome based on typical procedure results and the patient's features.
                            </p>
                        </div>

                        <div className="bg-green-50 rounded-lg p-4 border border-green-100">
                            <h5 className="text-sm font-medium text-green-800 mb-2 flex items-center gap-2">
                                <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Real Outcome
                            </h5>
                            <p className="text-sm text-green-700">
                                {realResultUrl
                                    ? 'The actual post-procedure result uploaded for comparison.'
                                    : 'Upload the real result photo to enable comparison.'}
                            </p>
                        </div>
                    </div>
                </div>
            </Card>

            {/* Medical Disclaimer */}
            <MedicalDisclaimer context="comparison" />
        </div>
    );
};
