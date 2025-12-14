"""Patient profile service."""
from datetime import datetime
from typing import Dict, List, Optional

from google.cloud.firestore_v1 import Client

from app.db.base import Collections
from app.db.firestore_models import (
    InsuranceInfoModel,
    LocationModel,
    PatientProfileModel,
    ProfileVersionHistoryModel,
)
from app.schemas.profile import (
    InsuranceInfoCreate,
    LocationCreate,
    PatientProfileCreate,
    PatientProfileUpdate,
    ProfileValidationResult,
)
from app.services.encryption import encryption_service


class ProfileService:
    """Service for managing patient profiles."""

    def __init__(self, db: Client):
        """Initialize profile service.
        
        Args:
            db: Firestore client
        """
        self.db = db
        self.encryption_service = encryption_service

    async def create_profile(
        self,
        user_id: str,
        profile_data: PatientProfileCreate
    ) -> PatientProfileModel:
        """Create a new patient profile with encrypted sensitive data.
        
        Args:
            user_id: ID of the user creating the profile
            profile_data: Profile data to create
            
        Returns:
            Created patient profile
        """
        # Encrypt sensitive fields
        encrypted_policy_number = self.encryption_service.encrypt_policy_number(
            profile_data.insurance_info.policy_number
        )
        
        encrypted_medical_history = None
        if profile_data.medical_history:
            encrypted_medical_history = self.encryption_service.encrypt_medical_history(
                profile_data.medical_history
            )
        
        # Create location model
        location = LocationModel(
            zip_code=profile_data.location.zip_code,
            city=profile_data.location.city,
            state=profile_data.location.state,
            country=profile_data.location.country
        )
        
        # Create insurance info model with encrypted policy number
        insurance_info = InsuranceInfoModel(
            provider=profile_data.insurance_info.provider,
            encrypted_policy_number=encrypted_policy_number,
            group_number=profile_data.insurance_info.group_number,
            plan_type=profile_data.insurance_info.plan_type,
            coverage_details=profile_data.insurance_info.coverage_details
        )
        
        # Create profile model
        profile = PatientProfileModel(
            user_id=user_id,
            name=profile_data.name,
            date_of_birth=datetime.combine(profile_data.date_of_birth, datetime.min.time()),
            location=location,
            insurance_info=insurance_info,
            encrypted_medical_history=encrypted_medical_history,
            version=1
        )
        
        # Save to Firestore
        profile_dict = profile.model_dump(mode='json')
        self.db.collection(Collections.PATIENT_PROFILES).document(profile.id).set(profile_dict)
        
        return profile

    async def get_profile(self, profile_id: str) -> Optional[PatientProfileModel]:
        """Get a patient profile by ID.
        
        Args:
            profile_id: ID of the profile to retrieve
            
        Returns:
            Patient profile if found, None otherwise
        """
        doc_ref = self.db.collection(Collections.PATIENT_PROFILES).document(profile_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return None
        
        data = doc.to_dict()
        return PatientProfileModel(**data)

    async def get_profile_by_user_id(self, user_id: str) -> Optional[PatientProfileModel]:
        """Get a patient profile by user ID.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Patient profile if found, None otherwise
        """
        query = (
            self.db.collection(Collections.PATIENT_PROFILES)
            .where('user_id', '==', user_id)
            .limit(1)
        )
        
        docs = list(query.stream())
        
        if not docs:
            return None
        
        data = docs[0].to_dict()
        return PatientProfileModel(**data)

    async def update_profile(
        self,
        profile_id: str,
        updates: PatientProfileUpdate
    ) -> Optional[PatientProfileModel]:
        """Update a patient profile with version history tracking.
        
        Args:
            profile_id: ID of the profile to update
            updates: Profile updates to apply
            
        Returns:
            Updated patient profile if found, None otherwise
        """
        # Get existing profile
        existing_profile = await self.get_profile(profile_id)
        if not existing_profile:
            return None
        
        # Save current version to history
        await self._save_version_history(existing_profile)
        
        # Prepare update data
        update_data: Dict[str, any] = {}
        
        if updates.name is not None:
            update_data['name'] = updates.name
        
        if updates.date_of_birth is not None:
            update_data['date_of_birth'] = datetime.combine(
                updates.date_of_birth,
                datetime.min.time()
            )
        
        if updates.location is not None:
            location = LocationModel(
                zip_code=updates.location.zip_code,
                city=updates.location.city,
                state=updates.location.state,
                country=updates.location.country
            )
            update_data['location'] = location.model_dump()
        
        if updates.insurance_info is not None:
            # Encrypt policy number
            encrypted_policy_number = self.encryption_service.encrypt_policy_number(
                updates.insurance_info.policy_number
            )
            
            insurance_info = InsuranceInfoModel(
                provider=updates.insurance_info.provider,
                encrypted_policy_number=encrypted_policy_number,
                group_number=updates.insurance_info.group_number,
                plan_type=updates.insurance_info.plan_type,
                coverage_details=updates.insurance_info.coverage_details
            )
            update_data['insurance_info'] = insurance_info.model_dump()
        
        if updates.medical_history is not None:
            encrypted_medical_history = self.encryption_service.encrypt_medical_history(
                updates.medical_history
            )
            update_data['encrypted_medical_history'] = encrypted_medical_history
        
        # Increment version and update timestamp
        update_data['version'] = existing_profile.version + 1
        update_data['updated_at'] = datetime.utcnow()
        
        # Update in Firestore
        self.db.collection(Collections.PATIENT_PROFILES).document(profile_id).update(update_data)
        
        # Get and return updated profile
        return await self.get_profile(profile_id)

    async def delete_profile(self, profile_id: str) -> bool:
        """Delete a patient profile.
        
        Args:
            profile_id: ID of the profile to delete
            
        Returns:
            True if deleted, False if not found
        """
        doc_ref = self.db.collection(Collections.PATIENT_PROFILES).document(profile_id)
        doc = doc_ref.get()
        
        if not doc.exists:
            return False
        
        doc_ref.delete()
        return True

    async def get_profile_history(
        self,
        profile_id: str
    ) -> List[ProfileVersionHistoryModel]:
        """Get version history for a profile.
        
        Args:
            profile_id: ID of the profile
            
        Returns:
            List of version history records, ordered by version descending
        """
        query = (
            self.db.collection(Collections.PROFILE_VERSION_HISTORY)
            .where('profile_id', '==', profile_id)
            .order_by('version', direction='DESCENDING')
        )
        
        docs = query.stream()
        history = []
        
        for doc in docs:
            data = doc.to_dict()
            history.append(ProfileVersionHistoryModel(**data))
        
        return history

    async def _save_version_history(self, profile: PatientProfileModel) -> None:
        """Save current profile state to version history.
        
        Args:
            profile: Profile to save to history
        """
        history = ProfileVersionHistoryModel(
            profile_id=profile.id,
            version=profile.version,
            data=profile.model_dump(mode='json')
        )
        
        history_dict = history.model_dump(mode='json')
        self.db.collection(Collections.PROFILE_VERSION_HISTORY).document(history.id).set(history_dict)

    def decrypt_profile_for_response(self, profile: PatientProfileModel) -> Dict:
        """Decrypt sensitive fields in profile for API response.
        
        Args:
            profile: Profile with encrypted fields
            
        Returns:
            Profile dict with decrypted sensitive fields
        """
        profile_dict = profile.model_dump(mode='json')
        
        # Decrypt policy number
        if profile.insurance_info.encrypted_policy_number:
            profile_dict['insurance_info']['policy_number'] = (
                self.encryption_service.decrypt_policy_number(
                    profile.insurance_info.encrypted_policy_number
                )
            )
            # Remove encrypted field from response
            del profile_dict['insurance_info']['encrypted_policy_number']
        
        # Decrypt medical history
        if profile.encrypted_medical_history:
            profile_dict['medical_history'] = (
                self.encryption_service.decrypt_medical_history(
                    profile.encrypted_medical_history
                )
            )
            # Remove encrypted field from response
            del profile_dict['encrypted_medical_history']
        
        return profile_dict

    async def validate_profile(
        self,
        profile_data: PatientProfileCreate
    ) -> ProfileValidationResult:
        """Validate profile data for completeness and correctness.
        
        Args:
            profile_data: Profile data to validate
            
        Returns:
            Validation result with missing/invalid fields
        """
        missing_fields = []
        invalid_fields = {}
        
        # Check required fields
        if not profile_data.name or not profile_data.name.strip():
            missing_fields.append('name')
        
        if not profile_data.date_of_birth:
            missing_fields.append('date_of_birth')
        
        if not profile_data.location:
            missing_fields.append('location')
        elif not profile_data.location.zip_code:
            missing_fields.append('location.zip_code')
        
        if not profile_data.insurance_info:
            missing_fields.append('insurance_info')
        else:
            if not profile_data.insurance_info.provider:
                missing_fields.append('insurance_info.provider')
            if not profile_data.insurance_info.policy_number:
                missing_fields.append('insurance_info.policy_number')
        
        # Validate insurance provider (check against supported providers)
        if profile_data.insurance_info and profile_data.insurance_info.provider:
            is_valid = await self.validate_insurance_provider(
                profile_data.insurance_info.provider
            )
            if not is_valid:
                invalid_fields['insurance_info.provider'] = (
                    'Insurance provider not in supported database'
                )
        
        is_valid = len(missing_fields) == 0 and len(invalid_fields) == 0
        
        return ProfileValidationResult(
            is_valid=is_valid,
            missing_fields=missing_fields,
            invalid_fields=invalid_fields
        )

    async def validate_insurance_provider(self, provider: str) -> bool:
        """Validate insurance provider against database of supported providers.
        
        Args:
            provider: Insurance provider name
            
        Returns:
            True if provider is supported, False otherwise
        """
        # Check for empty or whitespace-only provider
        if not provider or not provider.strip():
            return False
        
        # For now, use a hardcoded list of common providers
        # In production, this would query a database
        supported_providers = {
            'Blue Cross Blue Shield',
            'Aetna',
            'UnitedHealthcare',
            'Cigna',
            'Humana',
            'Kaiser Permanente',
            'Anthem',
            'Medicare',
            'Medicaid',
        }
        
        # Common abbreviations and variations
        abbreviations = {
            'bcbs': 'Blue Cross Blue Shield',
            'blue cross': 'Blue Cross Blue Shield',
            'blue shield': 'Blue Cross Blue Shield',
            'united healthcare': 'UnitedHealthcare',
            'united': 'UnitedHealthcare',
            'kaiser': 'Kaiser Permanente',
        }
        
        # Case-insensitive partial match
        provider_lower = provider.lower().strip()
        
        # Check abbreviations first
        if provider_lower in abbreviations:
            return True
        
        # Check partial matches with supported providers
        for supported in supported_providers:
            if provider_lower in supported.lower() or supported.lower() in provider_lower:
                return True
        
        return False
