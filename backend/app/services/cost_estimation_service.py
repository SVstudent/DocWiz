"""Cost estimation service for calculating procedure costs.

This service provides methods to:
- Calculate comprehensive cost breakdowns
- Factor in geographic location
- Calculate insurance coverage
- Generate payment plan options
"""
import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any

from google.cloud.firestore_v1 import Client

from app.db.base import Collections
from app.db.seed_pricing import (
    get_base_pricing,
    get_region_from_zip,
    get_regional_multiplier,
    get_insurance_provider,
    is_procedure_covered,
    get_payment_plans,
    calculate_payment_plan_details,
)
from app.schemas.cost import (
    CostBreakdownResponse,
    InsuranceCoverage,
    PaymentPlan,
)
from app.schemas.profile import PatientProfileResponse


class CostEstimationService:
    """Service for calculating procedure costs and insurance coverage."""
    
    def __init__(self, db: Client):
        """Initialize cost estimation service.
        
        Args:
            db: Firestore client instance
        """
        self.db = db
        self.collection = Collections.COST_BREAKDOWNS
    
    async def calculate_cost_breakdown(
        self,
        procedure_id: str,
        patient_profile: PatientProfileResponse,
    ) -> CostBreakdownResponse:
        """Calculate comprehensive cost breakdown for a procedure.
        
        This method:
        1. Gets base pricing for the procedure
        2. Applies regional cost multiplier based on ZIP code
        3. Calculates insurance coverage if applicable
        4. Generates payment plan options
        5. Stores the breakdown in Firestore
        
        Args:
            procedure_id: Unique procedure identifier
            patient_profile: Patient profile with location and insurance info
        
        Returns:
            Complete cost breakdown with all calculations
        
        Raises:
            ValueError: If procedure pricing not found
        """
        # Get base pricing
        base_pricing = get_base_pricing(procedure_id)
        if not base_pricing:
            raise ValueError(f"Pricing not found for procedure: {procedure_id}")
        
        # Get geographic location and regional multiplier
        zip_code = patient_profile.location.zip_code
        region = get_region_from_zip(zip_code)
        multiplier = get_regional_multiplier(region)
        
        # Apply regional multiplier to all cost components
        surgeon_fee = (base_pricing["surgeon_fee"] * multiplier).quantize(Decimal("0.01"))
        facility_fee = (base_pricing["facility_fee"] * multiplier).quantize(Decimal("0.01"))
        anesthesia_fee = (base_pricing["anesthesia_fee"] * multiplier).quantize(Decimal("0.01"))
        post_op_care = (base_pricing["post_op_care"] * multiplier).quantize(Decimal("0.01"))
        
        # Calculate total cost
        total_cost = surgeon_fee + facility_fee + anesthesia_fee + post_op_care
        
        # Calculate insurance coverage
        insurance_coverage_result = await self.calculate_insurance_coverage(
            procedure_id=procedure_id,
            total_cost=total_cost,
            insurance_provider=patient_profile.insurance_info.provider,
        )
        
        # Generate payment plans
        payment_plans = self._generate_payment_plans(
            insurance_coverage_result.patient_responsibility
        )
        
        # Create cost breakdown ID
        breakdown_id = str(uuid.uuid4())
        
        # Data sources for transparency
        data_sources = [
            "National average procedure costs (2024)",
            f"Regional cost adjustment for {region} region",
        ]
        
        # Document insurance provider even if procedure not covered
        if patient_profile.insurance_info.provider and patient_profile.insurance_info.provider != "None":
            if insurance_coverage_result.is_covered:
                data_sources.append(
                    f"{patient_profile.insurance_info.provider} coverage policy"
                )
            else:
                data_sources.append(
                    f"{patient_profile.insurance_info.provider} policy (procedure not covered)"
                )
        
        # Create response
        breakdown = CostBreakdownResponse(
            id=breakdown_id,
            procedure_id=procedure_id,
            patient_id=patient_profile.id,
            surgeon_fee=surgeon_fee,
            facility_fee=facility_fee,
            anesthesia_fee=anesthesia_fee,
            post_op_care=post_op_care,
            total_cost=total_cost,
            insurance_coverage=insurance_coverage_result.estimated_coverage,
            patient_responsibility=insurance_coverage_result.patient_responsibility,
            deductible=insurance_coverage_result.deductible,
            copay=insurance_coverage_result.copay,
            out_of_pocket_max=insurance_coverage_result.out_of_pocket_max,
            payment_plans=payment_plans,
            calculated_at=datetime.utcnow(),
            data_sources=data_sources,
            region=region,
            insurance_provider=patient_profile.insurance_info.provider,
        )
        
        # Store in Firestore
        await self._store_cost_breakdown(breakdown)
        
        return breakdown
    
    async def calculate_insurance_coverage(
        self,
        procedure_id: str,
        total_cost: Decimal,
        insurance_provider: str,
    ) -> InsuranceCoverage:
        """Calculate insurance coverage for a procedure.
        
        Args:
            procedure_id: Procedure identifier
            total_cost: Total procedure cost
            insurance_provider: Insurance provider name
        
        Returns:
            Insurance coverage calculation
        """
        # Get insurance provider info
        provider_info = get_insurance_provider(insurance_provider)
        
        if not provider_info:
            # No insurance or unknown provider
            return InsuranceCoverage(
                is_covered=False,
                coverage_rate=Decimal("0.0"),
                estimated_coverage=Decimal("0.0"),
                deductible=Decimal("0.0"),
                copay=Decimal("0.0"),
                out_of_pocket_max=Decimal("0.0"),
                patient_responsibility=total_cost,
            )
        
        # Check if procedure is covered
        is_covered = is_procedure_covered(insurance_provider, procedure_id)
        
        out_of_pocket_max = provider_info["out_of_pocket_max"]
        
        if not is_covered:
            # Procedure not covered by this insurance
            # But patient responsibility is still capped at out-of-pocket max
            patient_responsibility = min(total_cost, out_of_pocket_max)
            estimated_coverage = total_cost - patient_responsibility
            
            return InsuranceCoverage(
                is_covered=False,
                coverage_rate=Decimal("0.0"),
                estimated_coverage=estimated_coverage,
                deductible=provider_info["deductible"],
                copay=Decimal("0.0"),
                out_of_pocket_max=out_of_pocket_max,
                patient_responsibility=patient_responsibility,
            )
        
        # Calculate coverage
        coverage_rate = Decimal(str(provider_info["coverage_rate"]))
        deductible = provider_info["deductible"]
        copay_rate = Decimal(str(provider_info["copay_rate"]))
        
        # Amount after deductible
        amount_after_deductible = max(Decimal("0.0"), total_cost - deductible)
        
        # Insurance covers percentage of amount after deductible
        estimated_coverage = (amount_after_deductible * coverage_rate).quantize(Decimal("0.01"))
        
        # Patient pays deductible + copay on remaining amount
        copay = (amount_after_deductible * copay_rate).quantize(Decimal("0.01"))
        patient_responsibility = (deductible + copay).quantize(Decimal("0.01"))
        
        # Cap at out-of-pocket maximum
        if patient_responsibility > out_of_pocket_max:
            patient_responsibility = out_of_pocket_max
            estimated_coverage = total_cost - patient_responsibility
        
        return InsuranceCoverage(
            is_covered=True,
            coverage_rate=coverage_rate,
            estimated_coverage=estimated_coverage,
            deductible=deductible,
            copay=copay,
            out_of_pocket_max=out_of_pocket_max,
            patient_responsibility=patient_responsibility,
        )
    
    def _generate_payment_plans(
        self,
        amount: Decimal
    ) -> List[PaymentPlan]:
        """Generate payment plan options for a given amount.
        
        Args:
            amount: Amount to finance
        
        Returns:
            List of available payment plans (always at least one)
        """
        # If amount is zero or very small, return a single "pay in full" plan
        if amount <= Decimal("100.00"):
            return [
                PaymentPlan(
                    name="Pay in Full",
                    monthly_payment=amount,
                    duration_months=1,
                    interest_rate=Decimal("0.00"),
                    total_paid=amount,
                )
            ]
        
        available_plans = get_payment_plans(amount)
        payment_plans = []
        
        for plan in available_plans:
            details = calculate_payment_plan_details(
                principal=amount,
                duration_months=plan["duration_months"],
                interest_rate=plan["interest_rate"],
            )
            
            payment_plans.append(
                PaymentPlan(
                    name=plan["name"],
                    monthly_payment=details["monthly_payment"],
                    duration_months=plan["duration_months"],
                    interest_rate=plan["interest_rate"],
                    total_paid=details["total_paid"],
                )
            )
        
        # Ensure at least one plan is always returned
        if not payment_plans:
            payment_plans.append(
                PaymentPlan(
                    name="Pay in Full",
                    monthly_payment=amount,
                    duration_months=1,
                    interest_rate=Decimal("0.00"),
                    total_paid=amount,
                )
            )
        
        return payment_plans
    
    async def _store_cost_breakdown(
        self,
        breakdown: CostBreakdownResponse
    ) -> None:
        """Store cost breakdown in Firestore.
        
        Args:
            breakdown: Cost breakdown to store
        """
        # Convert to dict for Firestore
        data = breakdown.model_dump(mode='json')
        
        # Store in Firestore
        self.db.collection(self.collection).document(breakdown.id).set(data)
    
    async def get_cost_breakdown(
        self,
        breakdown_id: str
    ) -> Optional[CostBreakdownResponse]:
        """Retrieve a cost breakdown by ID.
        
        Args:
            breakdown_id: Cost breakdown identifier
        
        Returns:
            Cost breakdown if found, None otherwise
        """
        doc = self.db.collection(self.collection).document(breakdown_id).get()
        
        if doc.exists:
            data = doc.to_dict()
            if data:
                return CostBreakdownResponse(**data)
        
        return None
    
    async def get_patient_cost_breakdowns(
        self,
        patient_id: str
    ) -> List[CostBreakdownResponse]:
        """Get all cost breakdowns for a patient.
        
        Args:
            patient_id: Patient identifier
        
        Returns:
            List of cost breakdowns
        """
        query = self.db.collection(self.collection).where("patient_id", "==", patient_id)
        docs = query.stream()
        
        breakdowns = []
        for doc in docs:
            data = doc.to_dict()
            if data:
                breakdowns.append(CostBreakdownResponse(**data))
        
        return breakdowns


def get_cost_estimation_service(db: Client) -> CostEstimationService:
    """Factory function to create cost estimation service instance.
    
    Args:
        db: Firestore client
    
    Returns:
        CostEstimationService instance
    """
    return CostEstimationService(db)
