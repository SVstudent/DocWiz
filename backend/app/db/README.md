# Database Layer - Firebase/Firestore

This directory contains the database layer for DocWiz using Google Firebase/Firestore.

## Files

- `base.py`: Firestore client initialization and connection management
- `firestore_models.py`: Pydantic models and CRUD helper functions for Firestore
- `models.py`: Legacy SQLAlchemy models (kept for reference, not used)

## Why Firestore?

For the Google DeepMind hackathon, we're using Firestore to maximize Google Cloud integration:

✅ **NoSQL Document Database**: Flexible schema, perfect for rapid development
✅ **Real-time Capabilities**: Live updates for surgical visualizations
✅ **Serverless**: No database server management needed
✅ **Scalable**: Automatically handles concurrent users
✅ **Google Ecosystem**: Seamless integration with Gemini, GCS, and other Google services
✅ **Free Tier**: Generous quota for hackathon development

## Collections Structure

```
/users
  - Authentication and user management
  
/patient_profiles
  - Patient information with encrypted sensitive data
  
/profile_version_history
  - Version tracking for profile changes
  
/procedures
  - Surgical procedure definitions and templates
  
/visualization_results
  - AI-generated before/after surgical previews
  
/cost_breakdowns
  - Cost estimates with insurance calculations
  
/preauth_forms
  - Insurance pre-authorization documents
  
/comparisons
  - Multi-procedure comparison sets
```

## Usage Examples

### Creating a Document

```python
from app.db.base import get_db, Collections
from app.db.firestore_models import PatientProfileModel, create_document

db = get_db()

profile = PatientProfileModel(
    user_id="user123",
    name="John Doe",
    date_of_birth=datetime(1990, 1, 1),
    location=LocationModel(zip_code="94102", city="San Francisco", state="CA"),
    insurance_info=InsuranceInfoModel(
        provider="Blue Cross",
        encrypted_policy_number="encrypted_value"
    )
)

profile_id = await create_document(db, Collections.PATIENT_PROFILES, profile)
```

### Querying Documents

```python
from app.db.firestore_models import query_documents

# Get all procedures in a category
procedures = await query_documents(
    db,
    Collections.PROCEDURES,
    filters=[("category", "==", "facial")],
    order_by="name",
    limit=10
)
```

### Updating a Document

```python
from app.db.firestore_models import update_document

await update_document(
    db,
    Collections.PATIENT_PROFILES,
    profile_id,
    {"name": "John Smith", "version": 2}
)
```

## Migration from PostgreSQL

The original design used PostgreSQL with SQLAlchemy. We've migrated to Firestore for better Google Cloud integration. Key changes:

1. **No ORM**: Direct Firestore API calls instead of SQLAlchemy
2. **Document-based**: JSON documents instead of relational tables
3. **No migrations**: Schema-less, no Alembic needed
4. **Async-first**: All operations are async by default
5. **Subcollections**: Can nest related data (e.g., version history under profiles)

## Local Development

Use the Firestore emulator for local development:

```bash
# Install Firebase CLI
npm install -g firebase-tools

# Start emulator
firebase emulators:start --only firestore

# Update .env
USE_FIRESTORE_EMULATOR=true
FIRESTORE_EMULATOR_HOST=localhost:8080
```

## Production Deployment

1. Create Firebase project in console
2. Enable Firestore database
3. Download service account credentials
4. Set environment variables:
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_CREDENTIALS_PATH`
5. Deploy with credentials file

See `FIREBASE_SETUP.md` in project root for detailed setup instructions.

## Security

- Sensitive data (policy numbers, medical history) is encrypted before storage
- Firestore security rules control access in production
- Service account credentials required for backend access
- Never commit `firebase-credentials.json` to version control

## Performance Tips

1. **Indexing**: Firestore auto-indexes single fields, create composite indexes for complex queries
2. **Batch Operations**: Use batch writes for multiple documents
3. **Caching**: Use Redis for frequently accessed data
4. **Pagination**: Always use `limit()` and pagination for large result sets
5. **Denormalization**: Duplicate data when needed for query performance

## Resources

- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Best Practices](https://firebase.google.com/docs/firestore/best-practices)
