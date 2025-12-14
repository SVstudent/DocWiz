"""Seed data for procedure pricing and insurance coverage.

This module contains comprehensive pricing data including:
- Base costs for procedures by region
- Surgeon fees, facility fees, anesthesia, post-op care
- Insurance coverage rates by provider
- Regional cost multipliers
"""
from typing import List, Dict, Any
from decimal import Decimal


# US Regions for cost variation
class Region:
    NORTHEAST = "northeast"
    SOUTHEAST = "southeast"
    MIDWEST = "midwest"
    SOUTHWEST = "southwest"
    WEST = "west"


# Regional cost multipliers (base = 1.0)
REGIONAL_MULTIPLIERS = {
    Region.NORTHEAST: 1.25,  # Higher costs in NYC, Boston
    Region.SOUTHEAST: 0.90,  # Lower costs in most areas
    Region.MIDWEST: 0.95,    # Moderate costs
    Region.SOUTHWEST: 1.00,  # Base costs
    Region.WEST: 1.30,       # Highest costs in SF, LA
}


# ZIP code to region mapping (sample - would be comprehensive in production)
ZIP_TO_REGION = {
    # Northeast
    "10001": Region.NORTHEAST,  # NYC
    "02101": Region.NORTHEAST,  # Boston
    "19101": Region.NORTHEAST,  # Philadelphia
    "20001": Region.NORTHEAST,  # DC
    
    # Southeast
    "30301": Region.SOUTHEAST,  # Atlanta
    "33101": Region.SOUTHEAST,  # Miami
    "28201": Region.SOUTHEAST,  # Charlotte
    "37201": Region.SOUTHEAST,  # Nashville
    
    # Midwest
    "60601": Region.MIDWEST,    # Chicago
    "48201": Region.MIDWEST,    # Detroit
    "55401": Region.MIDWEST,    # Minneapolis
    "63101": Region.MIDWEST,    # St. Louis
    
    # Southwest
    "75201": Region.SOUTHWEST,  # Dallas
    "77001": Region.SOUTHWEST,  # Houston
    "85001": Region.SOUTHWEST,  # Phoenix
    "73101": Region.SOUTHWEST,  # Oklahoma City
    
    # West
    "94101": Region.WEST,       # San Francisco
    "90001": Region.WEST,       # Los Angeles
    "98101": Region.WEST,       # Seattle
    "97201": Region.WEST,       # Portland
}


# Base pricing for procedures (in USD)
# Format: procedure_id -> cost breakdown
PROCEDURE_BASE_PRICING: Dict[str, Dict[str, Decimal]] = {
    "rhinoplasty-001": {
        "surgeon_fee": Decimal("5000.00"),
        "facility_fee": Decimal("2000.00"),
        "anesthesia_fee": Decimal("1000.00"),
        "post_op_care": Decimal("500.00"),
    },
    "breast-augmentation-001": {
        "surgeon_fee": Decimal("6000.00"),
        "facility_fee": Decimal("2500.00"),
        "anesthesia_fee": Decimal("1200.00"),
        "post_op_care": Decimal("800.00"),
    },
    "cleft-lip-repair-001": {
        "surgeon_fee": Decimal("4000.00"),
        "facility_fee": Decimal("2000.00"),
        "anesthesia_fee": Decimal("800.00"),
        "post_op_care": Decimal("500.00"),
    },
    "facelift-001": {
        "surgeon_fee": Decimal("8000.00"),
        "facility_fee": Decimal("3000.00"),
        "anesthesia_fee": Decimal("1500.00"),
        "post_op_care": Decimal("1000.00"),
    },
    "liposuction-001": {
        "surgeon_fee": Decimal("3500.00"),
        "facility_fee": Decimal("1500.00"),
        "anesthesia_fee": Decimal("800.00"),
        "post_op_care": Decimal("400.00"),
    },
    "blepharoplasty-001": {
        "surgeon_fee": Decimal("3500.00"),
        "facility_fee": Decimal("1500.00"),
        "anesthesia_fee": Decimal("700.00"),
        "post_op_care": Decimal("300.00"),
    },
    "tummy-tuck-001": {
        "surgeon_fee": Decimal("7000.00"),
        "facility_fee": Decimal("3000.00"),
        "anesthesia_fee": Decimal("1500.00"),
        "post_op_care": Decimal("1000.00"),
    },
    "otoplasty-001": {
        "surgeon_fee": Decimal("2500.00"),
        "facility_fee": Decimal("1200.00"),
        "anesthesia_fee": Decimal("600.00"),
        "post_op_care": Decimal("300.00"),
    },
    "chin-augmentation-001": {
        "surgeon_fee": Decimal("3500.00"),
        "facility_fee": Decimal("1500.00"),
        "anesthesia_fee": Decimal("800.00"),
        "post_op_care": Decimal("400.00"),
    },
    "breast-reduction-001": {
        "surgeon_fee": Decimal("6500.00"),
        "facility_fee": Decimal("2500.00"),
        "anesthesia_fee": Decimal("1200.00"),
        "post_op_care": Decimal("800.00"),
    },
    "brow-lift-001": {
        "surgeon_fee": Decimal("4500.00"),
        "facility_fee": Decimal("2000.00"),
        "anesthesia_fee": Decimal("900.00"),
        "post_op_care": Decimal("600.00"),
    },
    "lip-augmentation-001": {
        "surgeon_fee": Decimal("800.00"),
        "facility_fee": Decimal("300.00"),
        "anesthesia_fee": Decimal("200.00"),
        "post_op_care": Decimal("100.00"),
    },
}


# Insurance providers and their coverage policies
INSURANCE_PROVIDERS = {
    "Blue Cross Blue Shield": {
        "id": "bcbs",
        "coverage_rate": 0.80,  # 80% coverage for covered procedures
        "deductible": Decimal("1500.00"),
        "out_of_pocket_max": Decimal("6000.00"),
        "copay_rate": 0.20,  # 20% copay after deductible
        "covered_procedures": [
            "cleft-lip-repair-001",  # Reconstructive
            "breast-reduction-001",  # If medically necessary
            "blepharoplasty-001",    # If vision impairment
        ],
    },
    "Aetna": {
        "id": "aetna",
        "coverage_rate": 0.75,
        "deductible": Decimal("2000.00"),
        "out_of_pocket_max": Decimal("7000.00"),
        "copay_rate": 0.25,
        "covered_procedures": [
            "cleft-lip-repair-001",
            "breast-reduction-001",
            "rhinoplasty-001",  # If breathing issues
        ],
    },
    "UnitedHealthcare": {
        "id": "uhc",
        "coverage_rate": 0.80,
        "deductible": Decimal("1000.00"),
        "out_of_pocket_max": Decimal("5000.00"),
        "copay_rate": 0.20,
        "covered_procedures": [
            "cleft-lip-repair-001",
            "breast-reduction-001",
            "tummy-tuck-001",  # If post-bariatric
        ],
    },
    "Cigna": {
        "id": "cigna",
        "coverage_rate": 0.70,
        "deductible": Decimal("2500.00"),
        "out_of_pocket_max": Decimal("8000.00"),
        "copay_rate": 0.30,
        "covered_procedures": [
            "cleft-lip-repair-001",
            "otoplasty-001",  # If congenital
        ],
    },
    "Kaiser Permanente": {
        "id": "kaiser",
        "coverage_rate": 0.85,
        "deductible": Decimal("1200.00"),
        "out_of_pocket_max": Decimal("4500.00"),
        "copay_rate": 0.15,
        "covered_procedures": [
            "cleft-lip-repair-001",
            "breast-reduction-001",
            "blepharoplasty-001",
        ],
    },
    "Humana": {
        "id": "humana",
        "coverage_rate": 0.75,
        "deductible": Decimal("1800.00"),
        "out_of_pocket_max": Decimal("6500.00"),
        "copay_rate": 0.25,
        "covered_procedures": [
            "cleft-lip-repair-001",
        ],
    },
    "None": {
        "id": "none",
        "coverage_rate": 0.0,
        "deductible": Decimal("0.00"),
        "out_of_pocket_max": Decimal("0.00"),
        "copay_rate": 1.0,
        "covered_procedures": [],
    },
}


# Payment plan options
PAYMENT_PLAN_OPTIONS = [
    {
        "name": "6-Month Plan",
        "duration_months": 6,
        "interest_rate": Decimal("0.00"),  # Interest-free
        "min_amount": Decimal("1000.00"),
    },
    {
        "name": "12-Month Plan",
        "duration_months": 12,
        "interest_rate": Decimal("0.05"),  # 5% APR
        "min_amount": Decimal("2000.00"),
    },
    {
        "name": "24-Month Plan",
        "duration_months": 24,
        "interest_rate": Decimal("0.08"),  # 8% APR
        "min_amount": Decimal("5000.00"),
    },
    {
        "name": "36-Month Plan",
        "duration_months": 36,
        "interest_rate": Decimal("0.10"),  # 10% APR
        "min_amount": Decimal("10000.00"),
    },
]


def get_region_from_zip(zip_code: str) -> str:
    """Get region from ZIP code.
    
    Args:
        zip_code: 5-digit ZIP code
    
    Returns:
        Region identifier (defaults to SOUTHWEST if not found)
    """
    # Extract first 5 digits
    zip_prefix = zip_code[:5]
    
    # Direct lookup
    if zip_prefix in ZIP_TO_REGION:
        return ZIP_TO_REGION[zip_prefix]
    
    # Fallback to ZIP code ranges
    zip_int = int(zip_prefix)
    
    if 10000 <= zip_int <= 19999:
        return Region.NORTHEAST
    elif 20000 <= zip_int <= 39999:
        return Region.SOUTHEAST
    elif 40000 <= zip_int <= 59999:
        return Region.MIDWEST
    elif 60000 <= zip_int <= 79999:
        return Region.SOUTHWEST
    elif 80000 <= zip_int <= 99999:
        return Region.WEST
    
    # Default
    return Region.SOUTHWEST


def get_regional_multiplier(region: str) -> Decimal:
    """Get cost multiplier for a region.
    
    Args:
        region: Region identifier
    
    Returns:
        Cost multiplier as Decimal
    """
    return Decimal(str(REGIONAL_MULTIPLIERS.get(region, 1.0)))


def get_base_pricing(procedure_id: str) -> Dict[str, Decimal] | None:
    """Get base pricing for a procedure.
    
    Args:
        procedure_id: Unique procedure identifier
    
    Returns:
        Dictionary with cost breakdown or None if not found
    """
    return PROCEDURE_BASE_PRICING.get(procedure_id)


def get_insurance_provider(provider_name: str) -> Dict[str, Any] | None:
    """Get insurance provider information.
    
    Args:
        provider_name: Insurance provider name
    
    Returns:
        Provider information dictionary or None if not found
    """
    return INSURANCE_PROVIDERS.get(provider_name)


def get_all_insurance_providers() -> List[str]:
    """Get list of all supported insurance providers.
    
    Returns:
        List of provider names
    """
    return list(INSURANCE_PROVIDERS.keys())


def is_procedure_covered(provider_name: str, procedure_id: str) -> bool:
    """Check if a procedure is covered by an insurance provider.
    
    Args:
        provider_name: Insurance provider name
        procedure_id: Procedure identifier
    
    Returns:
        True if covered, False otherwise
    """
    provider = get_insurance_provider(provider_name)
    if not provider:
        return False
    
    return procedure_id in provider["covered_procedures"]


def get_payment_plans(min_amount: Decimal) -> List[Dict[str, Any]]:
    """Get available payment plans for a given amount.
    
    Args:
        min_amount: Minimum amount to finance
    
    Returns:
        List of applicable payment plan options
    """
    return [
        plan for plan in PAYMENT_PLAN_OPTIONS
        if min_amount >= plan["min_amount"]
    ]


def calculate_payment_plan_details(
    principal: Decimal,
    duration_months: int,
    interest_rate: Decimal
) -> Dict[str, Decimal]:
    """Calculate payment plan details.
    
    Args:
        principal: Amount to finance
        duration_months: Loan duration in months
        interest_rate: Annual interest rate (e.g., 0.05 for 5%)
    
    Returns:
        Dictionary with monthly_payment and total_paid
    """
    if interest_rate == 0:
        # Interest-free
        monthly_payment = principal / Decimal(str(duration_months))
        total_paid = principal
    else:
        # Calculate with interest (simple interest for simplicity)
        monthly_rate = interest_rate / Decimal("12")
        total_interest = principal * interest_rate * (Decimal(str(duration_months)) / Decimal("12"))
        total_paid = principal + total_interest
        monthly_payment = total_paid / Decimal(str(duration_months))
    
    return {
        "monthly_payment": monthly_payment.quantize(Decimal("0.01")),
        "total_paid": total_paid.quantize(Decimal("0.01")),
    }
