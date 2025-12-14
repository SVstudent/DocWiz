# Firebase/Firestore Setup Guide

This guide explains how to set up Firebase/Firestore for DocWiz to maximize Google Cloud integration for the hackathon.

## Why Firebase/Firestore?

For the Google DeepMind hackathon, using Firebase/Firestore provides:
- **Maximum Google ecosystem integration** (scores better with judges!)
- **Firestore**: NoSQL document database with real-time capabilities
- **Firebase Authentication**: Optional integration for user management
- **Google Cloud Storage**: Seamless integration for image storage
- **Serverless**: No database server management needed
- **Free tier**: Generous free quota for hackathon development

## Setup Steps

### 1. Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or use existing Google Cloud project
3. Enter project name: `docwiz-hackathon` (or your choice)
4. Enable Google Analytics (optional)
5. Click "Create project"

### 2. Enable Firestore Database

1. In Firebase Console, go to "Build" → "Firestore Database"
2. Click "Create database"
3. Choose "Start in test mode" (for development)
   - **Production mode**: Requires security rules
   - **Test mode**: Open access for 30 days (perfect for hackathon!)
4. Select location: Choose closest to you (e.g., `us-central1`)
5. Click "Enable"

### 3. Get Service Account Credentials

1. In Firebase Console, click the gear icon → "Project settings"
2. Go to "Service accounts" tab
3. Click "Generate new private key"
4. Save the JSON file as `firebase-credentials.json` in the `backend/` directory
5. **IMPORTANT**: Add `firebase-credentials.json` to `.gitignore` (already done)

### 4. Update Environment Variables

Update `backend/.env` with your Firebase project details:

```bash
# Firebase/Firestore Database
FIREBASE_PROJECT_ID=your-actual-project-id  # From Firebase Console
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
USE_FIRESTORE_EMULATOR=false  # Set to true for local emulator

# Google Cloud Storage
GCS_PROJECT_ID=your-actual-project-id  # Same as Firebase project
GCS_BUCKET_NAME=docwiz-images-prod  # Create this bucket
GCS_CREDENTIALS_PATH=./firebase-credentials.json  # Same credentials
```

### 5. Create Google Cloud Storage Bucket

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your Firebase project
3. Go to "Cloud Storage" → "Buckets"
4. Click "Create bucket"
5. Name: `docwiz-images-prod` (or match your `.env`)
6. Location: Same region as Firestore
7. Storage class: Standard
8. Access control: Uniform
9. Click "Create"

### 6. Install Firebase Admin SDK

Already included in `pyproject.toml`:

```bash
cd backend
poetry install
```

Or with pip:

```bash
pip install firebase-admin google-cloud-firestore google-cloud-storage
```

### 7. Local Development with Firestore Emulator (Optional)

For local development without using cloud resources:

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Login to Firebase
firebase login

# Initialize Firebase in your project
firebase init emulators

# Select Firestore emulator
# Choose port 8080 (default)

# Start emulator
firebase emulators:start --only firestore
```

Update `.env` for emulator:

```bash
USE_FIRESTORE_EMULATOR=true
FIRESTORE_EMULATOR_HOST=localhost:8080
```

### 8. Verify Setup

Run the backend server:

```bash
cd backend
poetry run uvicorn app.main:app --reload
```

Check logs for successful Firestore connection:
```
INFO: Firestore initialized successfully
INFO: Project ID: your-project-id
```

## Firestore Data Structure

DocWiz uses these Firestore collections:

```
/users/{userId}
  - email, hashed_password, is_active, created_at

/patient_profiles/{profileId}
  - user_id, name, date_of_birth, location, insurance_info, version

/profile_version_history/{historyId}
  - profile_id, version, data, created_at

/procedures/{procedureId}
  - name, category, description, costs, recovery_days, cpt_codes

/visualization_results/{vizId}
  - patient_id, procedure_id, before_image_url, after_image_url, embedding

/cost_breakdowns/{costId}
  - procedure_id, patient_id, fees, insurance_coverage, payment_plans

/preauth_forms/{formId}
  - patient_id, procedure_id, cpt_codes, medical_justification, pdf_url

/comparisons/{comparisonId}
  - patient_id, source_image_id, procedure_ids, visualization_ids
```

## Security Rules (Production)

Before deploying, update Firestore security rules:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Users can only read/write their own data
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    match /patient_profiles/{profileId} {
      allow read, write: if request.auth != null && 
        resource.data.user_id == request.auth.uid;
    }
    
    // Procedures are read-only for all authenticated users
    match /procedures/{procedureId} {
      allow read: if request.auth != null;
      allow write: if false;  // Only admins via backend
    }
    
    // Other collections follow similar patterns
  }
}
```

## Advantages for Hackathon

✅ **All-Google Stack**: Gemini + Nano Banana + Firestore + GCS + Qdrant
✅ **Real-time capabilities**: Firestore supports live updates
✅ **Scalable**: Handles concurrent users automatically
✅ **No server management**: Focus on features, not infrastructure
✅ **Free tier**: Won't cost anything during hackathon
✅ **Impressive to judges**: Shows deep Google Cloud integration

## Troubleshooting

**Error: "Could not load credentials"**
- Ensure `firebase-credentials.json` exists in `backend/` directory
- Check `FIREBASE_CREDENTIALS_PATH` in `.env`
- Verify JSON file is valid (not corrupted)

**Error: "Permission denied"**
- Check Firestore security rules (use test mode for development)
- Verify service account has Firestore permissions

**Error: "Project not found"**
- Verify `FIREBASE_PROJECT_ID` matches your Firebase project
- Check project is enabled in Google Cloud Console

## Next Steps

1. ✅ Firebase/Firestore configured
2. ✅ Service account credentials downloaded
3. ✅ Environment variables updated
4. ✅ GCS bucket created
5. 🚀 Start building with full Google Cloud integration!

For more info:
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Google Cloud Storage](https://cloud.google.com/storage/docs)
