"""Insurance documentation routes."""
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from app.api.dependencies import get_current_active_user, get_db
from app.db.models import User
from app.services.insurance_doc_service import InsuranceDocService
from app.services.nano_banana_client import NanoBananaClient
from app.services.profile_service import ProfileService
from app.schemas.insurance import (
    PreAuthFormCreate,
    PreAuthFormResponse,
    InsuranceValidationRequest,
    InsuranceValidationResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/insurance", tags=["insurance"])


@router.post("/validate", response_model=InsuranceValidationResponse)
async def validate_insurance(
    request: InsuranceValidationRequest,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db)
) -> InsuranceValidationResponse:
    """
    Validate insurance information.
    
    Validates that the insurance provider is supported and the policy
    information is in the correct format.
    """
    logger.info(f"Validating insurance for user {current_user.id}")
    
    # Create profile service
    profile_service = ProfileService(db=db)
    
    # Validate insurance provider
    is_valid = await profile_service.validate_insurance_provider(request.provider)
    
    if is_valid:
        return InsuranceValidationResponse(
            is_valid=True,
            provider=request.provider,
            message=f"Insurance provider {request.provider} is supported",
            supported_procedures=None  # Could be expanded to list supported procedures
        )
    else:
        return InsuranceValidationResponse(
            is_valid=False,
            provider=request.provider,
            message=f"Insurance provider {request.provider} is not currently supported"
        )


@router.post("/claims", response_model=PreAuthFormResponse)
async def generate_claim(
    request: PreAuthFormCreate,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db)
) -> PreAuthFormResponse:
    """
    Generate insurance claim documentation.
    
    Creates a pre-authorization form with medical justification,
    procedure codes, and cost breakdown.
    """
    logger.info(
        f"Generating claim for user {current_user.id}, "
        f"procedure {request.procedure_id}, patient {request.patient_id}"
    )
    
    # Create insurance documentation service
    nano_banana = NanoBananaClient()
    insurance_service = InsuranceDocService(db=db, nano_banana_client=nano_banana)
    
    try:
        # Generate pre-auth form
        provider_info_dict = None
        if request.provider_info:
            provider_info_dict = request.provider_info.model_dump()
        
        form = await insurance_service.generate_preauth_form(
            procedure_id=request.procedure_id,
            patient_id=request.patient_id,
            cost_breakdown_id=request.cost_breakdown_id,
            provider_info=provider_info_dict
        )
        
        # Convert to response model
        # Convert ProviderInfoModel to ProviderInfo schema
        from app.schemas.insurance import ProviderInfo
        provider_info_response = ProviderInfo(
            name=form.provider_info.name,
            npi=form.provider_info.npi,
            address=form.provider_info.address,
            phone=form.provider_info.phone,
            specialty=form.provider_info.specialty
        )
        
        return PreAuthFormResponse(
            id=form.id,
            patient_id=form.patient_id,
            procedure_id=form.procedure_id,
            cost_breakdown_id=form.cost_breakdown_id,
            cpt_codes=form.cpt_codes,
            icd10_codes=form.icd10_codes,
            medical_justification=form.medical_justification,
            provider_info=provider_info_response,
            pdf_url=form.pdf_url,
            structured_data=form.structured_data,
            generated_at=form.generated_at
        )
        
    except ValueError as e:
        logger.error(f"Validation error generating claim: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating claim: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate claim")


@router.get("/claims/{claim_id}/pdf")
async def download_claim_pdf(
    claim_id: str,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db)
) -> Response:
    """
    Download claim as PDF.
    
    Exports the pre-authorization form as a PDF document.
    """
    logger.info(f"Downloading PDF for claim {claim_id}, user {current_user.id}")
    
    # Create insurance documentation service
    nano_banana = NanoBananaClient()
    insurance_service = InsuranceDocService(db=db, nano_banana_client=nano_banana)
    
    try:
        # Export as PDF
        pdf_bytes = await insurance_service.export_preauth_form_pdf(claim_id)
        
        # Return PDF response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=preauth_form_{claim_id}.pdf"
            }
        )
        
    except ValueError as e:
        logger.error(f"Claim not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate PDF")


@router.get("/claims/{claim_id}/json")
async def download_claim_json(
    claim_id: str,
    current_user: User = Depends(get_current_active_user),
    db=Depends(get_db)
) -> Response:
    """
    Download claim as JSON.
    
    Exports the pre-authorization form as structured JSON data
    for insurance system integration.
    """
    logger.info(f"Downloading JSON for claim {claim_id}, user {current_user.id}")
    
    # Create insurance documentation service
    nano_banana = NanoBananaClient()
    insurance_service = InsuranceDocService(db=db, nano_banana_client=nano_banana)
    
    try:
        # Export as JSON
        json_str = await insurance_service.export_preauth_form_json(claim_id)
        
        # Return JSON response
        return Response(
            content=json_str,
            media_type="application/json",
            headers={
                "Content-Disposition": f"attachment; filename=preauth_form_{claim_id}.json"
            }
        )
        
    except ValueError as e:
        logger.error(f"Claim not found: {e}")
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating JSON: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate JSON")
