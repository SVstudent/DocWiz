# Implementation Plan

- [ ] 1. Set up project structure and development environment
  - Initialize monorepo with frontend and backend directories
  - Create Docker Compose configuration for local development (PostgreSQL, Qdrant, Redis)
  - Set up environment variable management (.env files)
  - Configure linting and formatting (ESLint, Prettier, Black, Flake8)
  - Initialize Git repository with .gitignore
  - _Requirements: 8.1, 9.1_

- [x] 2. Implement backend core infrastructure
  - [x] 2.1 Set up FastAPI application with project structure
    - Create main FastAPI app with CORS middleware
    - Set up routing structure (auth, profiles, images, procedures, visualizations, costs, insurance, exports)
    - Configure Pydantic settings management
    - Add health check endpoint
    - _Requirements: 9.1, 9.5_

  - [x] 2.2 Implement database models and migrations
    - Create SQLAlchemy models for PatientProfile, Procedure, VisualizationResult, CostBreakdown, PreAuthForm
    - Set up Alembic for database migrations
    - Create initial migration with all tables
    - Add indexes for common queries
    - _Requirements: 2.1, 2.3, 2.4_

  - [x] 2.3 Set up authentication and authorization
    - Implement JWT token generation and validation
    - Create user registration endpoint
    - Create login endpoint with password hashing
    - Add authentication middleware for protected routes
    - Implement token refresh mechanism
    - _Requirements: 9.1_

  - [x] 2.4 Write property test for authentication enforcement
    - **Property 26: Authentication enforcement**
    - **Validates: Requirements 9.1**

  - [x] 2.5 Implement encryption service for sensitive data
    - Create encryption utility using Fernet (symmetric encryption)
    - Add methods for encrypting/decrypting policy numbers and medical history
    - Configure encryption key management
    - _Requirements: 2.3_

  - [x] 2.6 Write property test for sensitive data encryption
    - **Property 5: Sensitive data encryption**
    - **Validates: Requirements 2.3**

- [x] 3. Implement AI service integrations
  - [x] 3.1 Create Gemini API client
    - Implement GeminiClient class with image generation method
    - Add retry logic with exponential backoff
    - Handle API errors gracefully
    - Add request/response logging
    - _Requirements: 1.3, 9.2_

  - [x] 3.2 Create Nano Banana API client
    - Implement NanoBananaClient class for text generation
    - Add methods for medical justification generation
    - Implement error handling and retries
    - _Requirements: 7.3, 9.2_

  - [x] 3.3 Create Freepik API client
    - Implement FreepikClient class for image/video generation
    - Add methods for cost infographic generation
    - Handle API authentication
    - _Requirements: 3.4, 9.3_

  - [x] 3.4 Write property test for AI service orchestration
    - **Property 27: AI service orchestration**
    - **Validates: Requirements 9.2**

  - [x] 3.5 Write property test for Freepik integration
    - **Property 28: Freepik integration**
    - **Validates: Requirements 9.3**

- [x] 4. Implement Qdrant vector database integration
  - [x] 4.1 Set up Qdrant client and collection
    - Initialize Qdrant client with connection configuration
    - Create collection for image embeddings with appropriate vector size
    - Define payload schema for metadata (procedure_type, age_range, outcome_rating)
    - _Requirements: 5.1, 9.4_

  - [x] 4.2 Implement embedding generation and storage
    - Create method to generate embeddings from images
    - Implement upsert operation for storing embeddings with metadata
    - Add error handling for Qdrant operations
    - _Requirements: 5.1_

  - [x] 4.3 Write property test for embedding generation
    - **Property 16: Embedding generation**
    - **Validates: Requirements 5.1**

  - [x] 4.4 Implement similarity search functionality
    - Create search method with filtering by procedure type, age range, outcome quality
    - Implement result ranking and scoring
    - Add pagination support
    - _Requirements: 5.2, 5.5_

  - [x] 4.5 Write property test for similar case filtering
    - **Property 17: Similar case filtering**
    - **Validates: Requirements 5.2**

  - [x] 4.6 Write property test for multi-filter application
    - **Property 20: Multi-filter application**
    - **Validates: Requirements 5.5**

  - [x] 4.7 Write property test for Qdrant vector operations
    - **Property 29: Qdrant vector operations**
    - **Validates: Requirements 9.4**

- [x] 5. Implement patient profile management
  - [x] 5.1 Create profile service with CRUD operations
    - Implement create_profile method with validation
    - Implement get_profile, update_profile, delete_profile methods
    - Add version history tracking on updates
    - Encrypt sensitive fields before storage
    - _Requirements: 2.1, 2.3, 2.4_

  - [x] 5.2 Write property test for profile field completeness
    - **Property 3: Profile field completeness**
    - **Validates: Requirements 2.1**

  - [x] 5.3 Write property test for version history preservation
    - **Property 6: Version history preservation**
    - **Validates: Requirements 2.4**

  - [x] 5.4 Implement profile validation
    - Create validation function to check required fields
    - Implement insurance provider validation against database
    - Add location validation (zip code format)
    - _Requirements: 2.2, 2.5_

  - [x] 5.5 Write property test for incomplete profile detection
    - **Property 7: Incomplete profile detection**
    - **Validates: Requirements 2.5**

  - [x] 5.6 Write property test for insurance validation
    - **Property 4: Insurance validation**
    - **Validates: Requirements 2.2**

  - [x] 5.7 Create profile API endpoints
    - POST /api/profiles (create profile)
    - GET /api/profiles/:id (get profile)
    - PUT /api/profiles/:id (update profile)
    - GET /api/profiles/:id/history (get version history)
    - _Requirements: 2.1, 2.4_

- [x] 6. Implement image upload and storage
  - [x] 6.1 Set up object storage client (S3/R2)
    - Configure boto3 or equivalent client
    - Set up bucket with appropriate permissions
    - Implement upload method with unique file naming
    - _Requirements: 1.1_

  - [x] 6.2 Create image validation service
    - Implement format validation (JPEG, PNG, WebP)
    - Add file size validation (max 10MB)
    - Check image dimensions and quality
    - Validate for malicious content
    - _Requirements: 1.1_

  - [x] 6.3 Write property test for image validation consistency
    - **Property 1: Image validation consistency**
    - **Validates: Requirements 1.1**

  - [x] 6.4 Create image upload API endpoint
    - POST /api/images/upload with multipart form data
    - Return image ID and URL
    - Handle upload errors gracefully
    - _Requirements: 1.1_

- [x] 7. Implement procedure management
  - [x] 7.1 Create procedure database seed data
    - Define common procedures (rhinoplasty, breast augmentation, cleft lip repair, etc.)
    - Include CPT codes, ICD-10 codes, descriptions, recovery times, risk levels
    - Create prompt templates for each procedure
    - _Requirements: 1.2_

  - [x] 7.2 Implement procedure service
    - Create methods to fetch all procedures
    - Add filtering by category
    - Implement procedure detail retrieval
    - _Requirements: 1.2_

  - [x] 7.3 Write property test for procedure display completeness
    - **Property 2: Procedure display completeness**
    - **Validates: Requirements 1.2**

  - [x] 7.4 Create procedure API endpoints
    - GET /api/procedures (list all procedures)
    - GET /api/procedures/:id (get procedure details)
    - GET /api/procedures/categories (list categories)
    - _Requirements: 1.2_

- [x] 8. Implement surgical visualization service
  - [x] 8.1 Create visualization service core logic
    - Implement generate_surgical_preview method
    - Build procedure-specific prompts from templates
    - Integrate with Gemini API for image generation
    - Store before/after images in object storage
    - Generate and store embeddings in Qdrant
    - _Requirements: 1.3, 1.5, 5.1_

  - [x] 8.2 Implement similar cases search
    - Create find_similar_cases method using Qdrant
    - Apply filters for procedure type, age range, outcome quality
    - Format results with anonymized data
    - _Requirements: 5.2, 5.3, 5.4, 5.5_

  - [x] 8.3 Write property test for search result completeness
    - **Property 18: Search result completeness**
    - **Validates: Requirements 5.3**

  - [x] 8.4 Write property test for similarity information display
    - **Property 19: Similarity information display**
    - **Validates: Requirements 5.4**

  - [x] 8.3 Create visualization API endpoints
    - POST /api/visualizations (generate visualization)
    - GET /api/visualizations/:id (get visualization)
    - GET /api/visualizations/:id/similar (find similar cases)
    - _Requirements: 1.3, 5.2_

- [-] 9. Implement comparison functionality
  - [x] 9.1 Create comparison service
    - Implement multi-procedure comparison generation
    - Ensure all visualizations use same source image
    - Calculate cost, recovery time, and risk differences
    - Store comparison sets with metadata
    - _Requirements: 4.1, 4.3, 4.4_

  - [x] 9.2 Write property test for comparison source consistency
    - **Property 13: Comparison source consistency**
    - **Validates: Requirements 4.1**

  - [x] 9.3 Write property test for comparison data completeness
    - **Property 14: Comparison data completeness**
    - **Validates: Requirements 4.3**

  - [x] 9.4 Write property test for comparison persistence round-trip
    - **Property 15: Comparison persistence round-trip**
    - **Validates: Requirements 4.4**

  - [x] 9.5 Create comparison API endpoint
    - POST /api/visualizations/compare (create comparison)
    - GET /api/comparisons/:id (retrieve comparison)
    - _Requirements: 4.1, 4.4_

- [x] 10. Implement cost estimation service
  - [x] 10.1 Create pricing database and seed data
    - Define base costs for procedures by region
    - Include surgeon fees, facility fees, anesthesia, post-op care
    - Add insurance coverage rates by provider
    - _Requirements: 3.1, 3.2_

  - [x] 10.2 Implement cost calculation logic
    - Create calculate_cost_breakdown method
    - Factor in geographic location (zip code to region mapping)
    - Calculate insurance coverage, deductibles, copays, out-of-pocket
    - Generate payment plan options
    - _Requirements: 3.1, 3.2, 3.3, 3.5_

  - [x] 10.3 Write property test for cost breakdown completeness
    - **Property 8: Cost breakdown completeness**
    - **Validates: Requirements 3.1**

  - [x] 10.4 Write property test for geographic cost variation
    - **Property 9: Geographic cost variation**
    - **Validates: Requirements 3.2**

  - [x] 10.5 Write property test for insurance calculation completeness
    - **Property 10: Insurance calculation completeness**
    - **Validates: Requirements 3.3**

  - [x] 10.6 Write property test for payment plan inclusion
    - **Property 12: Payment plan inclusion**
    - **Validates: Requirements 3.5**

  - [x] 10.7 Implement cost infographic generation
    - Use Freepik API to generate visual cost breakdown
    - Create chart showing cost components
    - Include insurance coverage visualization
    - Support PNG and JPEG formats
    - _Requirements: 3.4_

  - [x] 10.8 Write property test for dual format cost output
    - **Property 11: Dual format cost output**
    - **Validates: Requirements 3.4**

  - [x] 10.9 Write property test for cost estimate transparency
    - **Property 21: Cost estimate transparency**
    - **Validates: Requirements 6.4**

  - [x] 10.10 Create cost estimation API endpoints
    - POST /api/costs/estimate (calculate cost)
    - GET /api/costs/:id (get cost breakdown)
    - GET /api/costs/:id/infographic (get visual breakdown)
    - _Requirements: 3.1, 3.4_

- [x] 11. Implement insurance documentation service
  - [x] 11.1 Create insurance claim generation logic
    - Implement generate_preauth_form method
    - Include CPT codes, ICD-10 codes from procedure
    - Use Nano Banana to generate medical necessity justification
    - Add cost breakdown and provider information
    - _Requirements: 7.1, 7.3, 7.4_

  - [x] 11.2 Write property test for claim documentation completeness
    - **Property 23: Claim documentation completeness**
    - **Validates: Requirements 7.1**

  - [x] 11.3 Write property test for claim information completeness
    - **Property 25: Claim information completeness**
    - **Validates: Requirements 7.4**

  - [x] 11.4 Implement PDF and JSON export for claims
    - Generate PDF using ReportLab or WeasyPrint
    - Create structured JSON output for insurance systems
    - Ensure HIPAA compliance in formatting
    - _Requirements: 7.2, 7.5_

  - [x] 11.5 Write property test for dual format claim output
    - **Property 24: Dual format claim output**
    - **Validates: Requirements 7.2**

  - [x] 11.6 Create insurance API endpoints
    - POST /api/insurance/validate (validate insurance info)
    - POST /api/insurance/claims (generate claim)
    - GET /api/insurance/claims/:id/pdf (download PDF)
    - _Requirements: 2.2, 7.1, 7.2_

- [x] 12. Implement export service
  - [x] 12.1 Create comprehensive report generation
    - Implement export_comprehensive_report method
    - Gather all visualizations, cost estimates, comparisons for patient
    - Generate report with medical disclaimers
    - Support PDF, PNG, JPEG, JSON formats
    - _Requirements: 10.1, 10.2, 6.5_

  - [x] 12.2 Write property test for export report completeness
    - **Property 30: Export report completeness**
    - **Validates: Requirements 10.1**

  - [x] 12.3 Write property test for multi-format export support
    - **Property 31: Multi-format export support**
    - **Validates: Requirements 10.2**

  - [x] 12.4 Write property test for export metadata inclusion
    - **Property 32: Export metadata inclusion**
    - **Validates: Requirements 10.3**

  - [x] 12.5 Implement shareable export with data sanitization
    - Create export_shareable_version method
    - Remove sensitive fields (policy number, medical history)
    - Maintain all visualizations and cost summaries
    - _Requirements: 10.5_

  - [x] 12.6 Write property test for shareable export sanitization
    - **Property 33: Shareable export sanitization**
    - **Validates: Requirements 10.5**

  - [x] 12.7 Write property test for medical disclaimer inclusion
    - **Property 22: Medical disclaimer inclusion**
    - **Validates: Requirements 6.5**

  - [x] 12.8 Create export API endpoints
    - POST /api/exports (create export)
    - GET /api/exports/:id (get export metadata)
    - GET /api/exports/:id/download (download file)
    - _Requirements: 10.1, 10.2_

- [ ] 13. Set up Celery for async task processing
  - Configure Celery with Redis as broker
  - Create tasks for long-running operations (visualization generation, export creation)
  - Implement task status tracking
  - Add WebSocket support for real-time progress updates
  - _Requirements: 9.5_

- [x] 14. Checkpoint - Ensure all backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 15. Initialize frontend Next.js application
  - [x] 15.1 Create Next.js project with TypeScript
    - Initialize Next.js 14 with App Router
    - Configure TypeScript with strict mode
    - Set up Tailwind CSS with custom theme
    - Configure path aliases (@/components, @/lib, etc.)
    - _Requirements: 8.1, 8.5_

  - [x] 15.2 Set up state management with Zustand
    - Create stores for auth, profile, visualizations, costs
    - Implement persistence for auth tokens
    - Add TypeScript types for all stores
    - _Requirements: 8.2_

  - [x] 15.3 Configure React Query for server state
    - Set up QueryClient with default options
    - Create API client with axios
    - Implement request/response interceptors for auth
    - Add error handling
    - _Requirements: 8.4, 9.1_

  - [x] 15.4 Create design system components
    - Implement Button, Input, Card, Modal, Toast components
    - Use Tailwind with "surgically effective" theme (surgical blue, clean layouts)
    - Add loading states (skeleton screens)
    - Ensure WCAG AAA accessibility
    - _Requirements: 8.1, 8.3_

- [x] 16. Implement frontend authentication
  - [x] 16.1 Create authentication pages
    - Build login page with form validation
    - Build registration page with password strength indicator
    - Implement password reset flow
    - _Requirements: 9.1_

  - [x] 16.2 Implement auth context and hooks
    - Create useAuth hook for authentication state
    - Implement login, logout, register functions
    - Add token refresh logic
    - Create protected route wrapper
    - _Requirements: 9.1_

  - [x] 16.3 Write unit tests for auth flows
    - Test login success and failure
    - Test registration validation
    - Test token refresh
    - Test protected route access
    - _Requirements: 9.1_

- [x] 17. Implement patient profile UI
  - [x] 17.1 Create profile form component
    - Build multi-step form for profile creation
    - Add real-time validation with error messages
    - Implement insurance provider autocomplete
    - Add location lookup by zip code
    - _Requirements: 2.1, 2.2, 2.5_

  - [x] 17.2 Create profile display and edit pages
    - Build profile view page showing all information
    - Implement edit mode with inline editing
    - Add version history viewer
    - Show encrypted fields indicator
    - _Requirements: 2.1, 2.4_

  - [x] 17.3 Write unit tests for profile components
    - Test form validation
    - Test profile update
    - Test version history display
    - _Requirements: 2.1, 2.5_

- [x] 18. Implement image upload component
  - [x] 18.1 Create ImageUpload component
    - Implement drag-and-drop file upload
    - Add file picker fallback
    - Show upload progress bar
    - Display image preview after upload
    - Validate format and size client-side
    - _Requirements: 1.1, 8.3_

  - [x] 18.2 Integrate with backend upload API
    - Call POST /api/images/upload
    - Handle upload errors with user-friendly messages
    - Store uploaded image ID in state
    - _Requirements: 1.1, 8.4_

  - [x] 18.3 Write unit tests for image upload
    - Test file validation
    - Test upload success
    - Test upload error handling
    - _Requirements: 1.1_

- [x] 19. Implement procedure selection UI
  - [x] 19.1 Create ProcedureSelector component
    - Build searchable procedure list with categories
    - Implement category filtering
    - Add procedure cards with details (description, recovery time, risk level)
    - Support single and multi-select modes
    - _Requirements: 1.2, 4.1_

  - [x] 19.2 Create procedure detail modal
    - Show full procedure information
    - Display typical costs and recovery timeline
    - Include risk factors and considerations
    - Add "Select Procedure" action button
    - _Requirements: 1.2_

  - [x] 19.3 Write unit tests for procedure selection
    - Test search functionality
    - Test category filtering
    - Test selection state
    - _Requirements: 1.2_

- [x] 20. Implement visualization viewer UI
  - [x] 20.1 Create VisualizationViewer component
    - Build side-by-side before/after view
    - Implement slider comparison tool
    - Add synchronized zoom and pan controls
    - Show loading state during generation
    - _Requirements: 1.3, 4.2, 8.3_

  - [x] 20.2 Integrate with visualization API
    - Call POST /api/visualizations to generate preview
    - Poll or use WebSocket for progress updates
    - Display generated images
    - Handle generation errors
    - _Requirements: 1.3, 8.4_

  - [x] 20.3 Add save and regenerate actions
    - Implement save to profile functionality
    - Add regenerate button with confirmation
    - Show saved visualizations in profile
    - _Requirements: 1.3_

  - [x] 20.4 Write unit tests for visualization viewer
    - Test image display
    - Test comparison slider
    - Test save functionality
    - _Requirements: 1.3_

- [x] 21. Implement comparison tool UI
  - [x] 21.1 Create ComparisonTool component
    - Build multi-procedure selection interface
    - Display all visualizations in grid layout
    - Show cost, recovery, and risk comparisons
    - Implement synchronized zoom across all images
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 21.2 Integrate with comparison API
    - Call POST /api/visualizations/compare
    - Display comparison results
    - Allow saving comparison sets
    - _Requirements: 4.1, 4.4_

  - [x] 21.3 Write unit tests for comparison tool
    - Test multi-procedure selection
    - Test comparison display
    - Test save functionality
    - _Requirements: 4.1, 4.3_

- [x] 22. Implement cost dashboard UI
  - [x] 22.1 Create CostDashboard component
    - Build visual cost breakdown with chart (pie or bar chart)
    - Display insurance coverage calculator
    - Show payment plan options in expandable cards
    - Add data source citations
    - _Requirements: 3.1, 3.3, 3.5, 6.4_

  - [x] 22.2 Implement cost infographic display
    - Fetch and display PNG/JPEG infographic from API
    - Add download button for infographic
    - Show loading state during generation
    - _Requirements: 3.4_

  - [x] 22.3 Add export functionality
    - Implement export buttons for PDF, PNG, JSON
    - Call export API endpoints
    - Trigger file download
    - _Requirements: 10.2_

  - [x] 22.4 Write unit tests for cost dashboard
    - Test cost display
    - Test payment plan calculations
    - Test export functionality
    - _Requirements: 3.1, 3.5_

- [x] 23. Implement similar cases search UI
  - [x] 23.1 Create SimilarCases component
    - Display similar cases in grid layout
    - Show before/after images with similarity scores
    - Add sidebar filters (procedure type, outcome quality, recency)
    - Display outcome ratings and satisfaction scores
    - _Requirements: 5.2, 5.3, 5.4, 5.5_

  - [x] 23.2 Integrate with similar cases API
    - Call GET /api/visualizations/:id/similar
    - Apply filters and update results
    - Handle empty results gracefully
    - _Requirements: 5.2, 5.5_

  - [x] 23.3 Write unit tests for similar cases
    - Test filter application
    - Test result display
    - Test empty state
    - _Requirements: 5.2, 5.5_

- [x] 24. Implement insurance claim UI
  - [x] 24.1 Create InsuranceClaim component
    - Build claim generation form
    - Display generated pre-authorization form
    - Show medical necessity justification
    - Add download buttons for PDF and JSON
    - _Requirements: 7.1, 7.2, 7.3_

  - [x] 24.2 Integrate with insurance API
    - Call POST /api/insurance/claims
    - Display generated claim document
    - Handle PDF download
    - _Requirements: 7.1, 7.2_

  - [x] 24.3 Write unit tests for insurance claim
    - Test claim generation
    - Test PDF download
    - Test error handling
    - _Requirements: 7.1, 7.2_

- [x] 25. Implement export and sharing UI
  - [x] 25.1 Create ExportReport component
    - Build export options selector (format, shareable toggle)
    - Show export preview
    - Display download button
    - Add share link generation
    - _Requirements: 10.1, 10.2, 10.5_

  - [x] 25.2 Integrate with export API
    - Call POST /api/exports
    - Poll for export completion
    - Trigger file download
    - _Requirements: 10.1, 10.2_

  - [x] 25.3 Write unit tests for export
    - Test format selection
    - Test shareable toggle
    - Test download
    - _Requirements: 10.2, 10.5_

- [x] 26. Implement main application layout and navigation
  - [x] 26.1 Create app layout with navigation
    - Build responsive header with logo and nav links
    - Implement sticky navigation
    - Add user menu with profile and logout
    - Create breadcrumb navigation for complex flows
    - _Requirements: 8.1, 8.2, 8.5_

  - [x] 26.2 Create dashboard/home page
    - Display recent visualizations
    - Show saved comparisons
    - Add quick action buttons (new visualization, view profile)
    - _Requirements: 8.1_

  - [x] 26.3 Implement responsive design
    - Ensure all components work on mobile, tablet, desktop
    - Use Tailwind responsive utilities
    - Test on different screen sizes
    - _Requirements: 8.5_

- [x] 27. Add error handling and loading states
  - [x] 27.1 Create error boundary component
    - Implement React error boundary
    - Display user-friendly error messages
    - Add error reporting to Sentry (optional)
    - _Requirements: 8.4_

  - [x] 27.2 Implement global loading states
    - Create loading spinner component
    - Add skeleton screens for content loading
    - Implement progress bars for long operations
    - _Requirements: 8.3_

  - [x] 27.3 Add toast notifications
    - Implement toast system for success/error messages
    - Add notifications for async operations
    - Auto-dismiss after timeout
    - _Requirements: 8.3, 8.4_

- [ ] 28. Implement medical disclaimers throughout UI
  - Add disclaimer text to all medical information displays
  - Include disclaimers in visualizations, cost estimates, and exports
  - Make disclaimers prominent but not intrusive
  - _Requirements: 6.5_

- [x] 29. Checkpoint - Ensure all frontend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 30. Create comprehensive documentation
  - [x] 30.1 Write API documentation
    - Document all endpoints with request/response examples
    - Include authentication requirements
    - Add error code reference
    - _Requirements: 9.1_

  - [x] 30.2 Write deployment guide
    - Document Docker setup
    - Include environment variable configuration
    - Add production deployment steps
    - _Requirements: 8.1, 9.5_

  - [x] 30.3 Create user guide
    - Document main user flows with screenshots
    - Include troubleshooting section
    - Add FAQ
    - _Requirements: 8.1_

- [x] 31. Final integration testing and polish
  - [x] 31.1 Test complete user workflows end-to-end
    - Test full visualization workflow (upload → select → generate → view → save)
    - Test cost estimation workflow (profile → procedure → estimate → export)
    - Test comparison workflow (select multiple → compare → save)
    - Test insurance claim workflow (generate → download)
    - _Requirements: 1.1, 1.2, 1.3, 3.1, 4.1, 7.1_

  - [x] 31.2 Perform security audit
    - Test authentication bypass attempts
    - Verify encryption of sensitive data
    - Check for SQL injection vulnerabilities
    - Test CORS configuration
    - _Requirements: 2.3, 9.1_

  - [x] 31.3 Perform performance testing
    - Load test API endpoints
    - Measure frontend load time
    - Test with large images
    - Verify response times under load
    - _Requirements: 8.1, 9.5_

  - [x] 31.4 UI/UX polish
    - Review all pages for "surgically effective" design consistency
    - Fix any visual bugs or inconsistencies
    - Ensure smooth transitions and animations
    - Test accessibility (keyboard navigation, screen readers)
    - _Requirements: 8.1, 8.2, 8.5_

- [ ] 32. Final checkpoint - Complete system verification
  - Ensure all tests pass, ask the user if questions arise.
