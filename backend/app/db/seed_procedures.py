"""Seed data for surgical procedures.

This module contains comprehensive procedure definitions including:
- Common cosmetic and reconstructive procedures
- CPT and ICD-10 codes
- Prompt templates for AI visualization
- Cost ranges, recovery times, and risk levels
"""
from typing import List, Dict, Any


# Procedure categories
class ProcedureCategory:
    FACIAL = "facial"
    BODY = "body"
    RECONSTRUCTIVE = "reconstructive"
    COSMETIC = "cosmetic"


# Seed data for procedures
PROCEDURES_SEED_DATA: List[Dict[str, Any]] = [
    {
        "id": "rhinoplasty-001",
        "name": "Rhinoplasty (Nose Reshaping)",
        "category": ProcedureCategory.FACIAL,
        "description": "Surgical procedure to reshape the nose by modifying bone, cartilage, or both. Can address cosmetic concerns or breathing issues. Common modifications include reducing nose size, changing nose shape, narrowing nostrils, or changing the angle between nose and upper lip.",
        "typical_cost_min": 5000.0,
        "typical_cost_max": 15000.0,
        "recovery_days": 14,
        "risk_level": "medium",
        "cpt_codes": ["30400", "30410", "30420"],
        "icd10_codes": ["J34.89", "M95.0", "Q30.0"],
        "prompt_template": "Professional medical photography, 8K resolution, ultra-realistic. Show the healed result of a rhinoplasty using dorsal hump reduction and tip refinement techniques. The nose structure should be {modification_type}. The nasal bridge should be smooth and straight, and the tip refined and natural. Maintain natural pores and skin texture. Soft studio lighting with realistic shadows. Preserve all other facial features exactly. Avoid artificial or plastic appearance. Anatomically accurate."
    },
    {
        "id": "breast-augmentation-001",
        "name": "Breast Augmentation",
        "category": ProcedureCategory.BODY,
        "description": "Surgical procedure to increase breast size using implants or fat transfer. Can restore breast volume lost after weight reduction or pregnancy, achieve a more rounded breast shape, or improve natural breast size asymmetry.",
        "typical_cost_min": 6000.0,
        "typical_cost_max": 12000.0,
        "recovery_days": 21,
        "risk_level": "medium",
        "cpt_codes": ["19325", "19340", "19342"],
        "icd10_codes": ["N64.82", "N62", "Q83.8"],
        "prompt_template": "Professional medical photography, 8K resolution, ultra-realistic. Show the result of breast augmentation to {size_preference}. The breasts should appear naturally full with a teardrop shape and smooth upper pole transition. Maintain natural skin texture, symmetry, and anatomically accurate positioning. Soft diffused lighting to highlight natural contours. Keep all other body features identical. Avoid exaggerated or spherical implant look."
    },
    {
        "id": "cleft-lip-repair-001",
        "name": "Cleft Lip Repair",
        "category": ProcedureCategory.RECONSTRUCTIVE,
        "description": "Reconstructive surgery to repair a cleft lip, a birth defect where the upper lip doesn't form completely. The procedure closes the separation in the lip, restores normal lip function, and improves facial appearance. Typically performed in infancy but can be done at any age.",
        "typical_cost_min": 5000.0,
        "typical_cost_max": 10000.0,
        "recovery_days": 10,
        "risk_level": "medium",
        "cpt_codes": ["40700", "40701", "40702"],
        "icd10_codes": ["Q36.0", "Q36.1", "Q36.9"],
        "prompt_template": "Professional medical photography, 8K resolution, ultra-realistic. Show the healed result of a cleft lip repair using the Millard rotation-advancement technique. The upper lip should appear fully reconstructed with a continuous vermilion border, symmetrical philtral columns, and natural Cupid's bow formation. Include subtle surgical scar along the philtral column that appears healed and fading. Maintain natural skin texture with visible pores, realistic lip color with natural moisture, and soft studio lighting with accurate shadows. Preserve all other facial features exactly. Avoid artificial or plastic appearance."
    },
    {
        "id": "facelift-001",
        "name": "Facelift (Rhytidectomy)",
        "category": ProcedureCategory.FACIAL,
        "description": "Surgical procedure to reduce visible signs of aging in the face and neck. Removes excess skin, tightens underlying tissues, and repositions facial fat. Addresses sagging skin, deep creases, jowls, and loss of muscle tone in the lower face and neck.",
        "typical_cost_min": 7000.0,
        "typical_cost_max": 20000.0,
        "recovery_days": 21,
        "risk_level": "high",
        "cpt_codes": ["15824", "15825", "15826"],
        "icd10_codes": ["L57.4", "L98.8"],
        "prompt_template": "Professional medical photography, 8K resolution, ultra-realistic. Show the result of a deep plane facelift. The facial tissues should be repositioned to a more youthful elevation, defining the jawline and smoothing the nasolabial folds. No pulled or windblown look. Natural skin texture with fine lines appropriate for age preserved. Soft, flattering lighting. Maintain natural expression and features. Anatomically accurate rejuvenation."
    },
    {
        "id": "liposuction-001",
        "name": "Liposuction",
        "category": ProcedureCategory.BODY,
        "description": "Surgical procedure to remove excess fat deposits from specific areas of the body. Uses suction technique to remove fat from areas such as abdomen, hips, thighs, buttocks, arms, or neck. Improves body contours and proportion.",
        "typical_cost_min": 3000.0,
        "typical_cost_max": 10000.0,
        "recovery_days": 14,
        "risk_level": "medium",
        "cpt_codes": ["15876", "15877", "15878", "15879"],
        "icd10_codes": ["E66.9", "E66.01"],
        "prompt_template": "Professional medical photography, 8K resolution, ultra-realistic. Show the result of liposuction in the {target_area}. The contours should be smooth and refined, reducing subcutaneous fat while preserving muscle definition. Natural skin retraction without irregularities or dimpling. Realistic skin texture and tone. Soft lighting emphasizing the new body contour. Anatomically accurate physique."
    },
    {
        "id": "blepharoplasty-001",
        "name": "Blepharoplasty (Eyelid Surgery)",
        "category": ProcedureCategory.FACIAL,
        "description": "Surgical procedure to improve the appearance of the eyelids. Can be performed on upper lids, lower lids, or both. Removes excess skin, muscle, and fat. Addresses drooping upper lids and puffy bags below the eyes.",
        "typical_cost_min": 4000.0,
        "typical_cost_max": 8000.0,
        "recovery_days": 10,
        "risk_level": "low",
        "cpt_codes": ["15820", "15821", "15822", "15823"],
        "icd10_codes": ["H02.31", "H02.32", "H02.33"],
        "prompt_template": "Professional medical photography, 8K resolution, ultra-realistic. Show the result of blepharoplasty on {eyelid_location} eyelids. The eyes should appear refreshed and alert with excess skin and fat pads removed. Crisp, natural eyelid crease. No hollowed-out look. Maintain natural eye shape and expression. Realistic skin texture with fine lines. Soft, focused lighting on the eyes. Anatomically accurate."
    },
    {
        "id": "tummy-tuck-001",
        "name": "Abdominoplasty (Tummy Tuck)",
        "category": ProcedureCategory.BODY,
        "description": "Surgical procedure to remove excess skin and fat from the abdomen and tighten abdominal muscles. Addresses loose, sagging skin and weakened muscles often resulting from pregnancy, significant weight loss, or aging. Creates a firmer, flatter abdominal profile.",
        "typical_cost_min": 8000.0,
        "typical_cost_max": 15000.0,
        "recovery_days": 28,
        "risk_level": "high",
        "cpt_codes": ["15830", "15847"],
        "icd10_codes": ["L98.7", "M62.81"],
        "prompt_template": "Professional medical photography, 8K resolution, ultra-realistic. Show the result of abdominoplasty (tummy tuck). The abdomen should be flat and firm with tightened rectus muscles. Well-defined waistline. A fine, linear surgical scar placed low on the abdomen, appearing healed. Natural looking umbilicus (belly button) reconstruction. Realistic skin texture and tone. Soft studio lighting. Anatomically accurate."
    },
    {
        "id": "otoplasty-001",
        "name": "Otoplasty (Ear Surgery)",
        "category": ProcedureCategory.FACIAL,
        "description": "Surgical procedure to change the shape, position, or size of the ears. Can correct ears that stick out too far from the head, reduce large ears, or reshape ears after injury. Often performed on children but can be done at any age.",
        "typical_cost_min": 3000.0,
        "typical_cost_max": 7000.0,
        "recovery_days": 7,
        "risk_level": "low",
        "cpt_codes": ["69300", "69320"],
        "icd10_codes": ["Q17.5", "H61.19"],
        "prompt_template": "Professional medical photography, 8K resolution, ultra-realistic. Show the result of otoplasty (ear pinning). The ears should be positioned closer to the head with a natural antihelical fold. Symmetrical and balanced appearance. No 'pinned back' artificial look. Maintain natural ear cartilage detail and skin texture. Soft lighting. Preserve all other facial features exactly. Anatomically accurate."
    },
    {
        "id": "chin-augmentation-001",
        "name": "Chin Augmentation (Mentoplasty)",
        "category": ProcedureCategory.FACIAL,
        "description": "Surgical procedure to enhance the chin using implants or bone advancement. Improves facial balance and profile by increasing chin projection. Often performed in conjunction with rhinoplasty to achieve optimal facial proportions.",
        "typical_cost_min": 4000.0,
        "typical_cost_max": 8000.0,
        "recovery_days": 14,
        "risk_level": "medium",
        "cpt_codes": ["21120", "21121", "21123"],
        "icd10_codes": ["M26.09", "Q67.4"],
        "prompt_template": "Professional medical photography, 8K resolution, ultra-realistic. Show the result of chin augmentation to {augmentation_level} projection. The chin should have increased definition and forward projection that balances the facial profile. Natural transition to the jawline. No visible implant edges. Realistic skin texture and pores. Soft studio lighting. Preserve all other facial features exactly. Anatomically accurate."
    },
    {
        "id": "breast-reduction-001",
        "name": "Breast Reduction (Reduction Mammoplasty)",
        "category": ProcedureCategory.BODY,
        "description": "Surgical procedure to reduce breast size by removing excess breast tissue, fat, and skin. Addresses physical discomfort from overly large breasts including back pain, neck pain, and skin irritation. Creates smaller, lighter, and better-shaped breasts.",
        "typical_cost_min": 7000.0,
        "typical_cost_max": 12000.0,
        "recovery_days": 21,
        "risk_level": "medium",
        "cpt_codes": ["19318", "19316"],
        "icd10_codes": ["N62", "N64.82"],
        "prompt_template": "Professional medical photography, 8K resolution, ultra-realistic. Show the result of breast reduction to {target_size}. The breasts should be lifted and proportionate to the body frame with a natural teardrop shape. Include characteristic anchor or lollipop scar pattern that appears healed. Natural skin texture and nipple position. Soft diffused lighting. Keep all other body features identical. Anatomically accurate."
    },
    {
        "id": "brow-lift-001",
        "name": "Brow Lift (Forehead Lift)",
        "category": ProcedureCategory.FACIAL,
        "description": "Surgical procedure to raise drooping eyebrows and smooth forehead wrinkles. Addresses sagging brows, deep horizontal forehead lines, and frown lines between eyebrows. Creates a more youthful, refreshed appearance.",
        "typical_cost_min": 5000.0,
        "typical_cost_max": 10000.0,
        "recovery_days": 14,
        "risk_level": "medium",
        "cpt_codes": ["15839", "67900"],
        "icd10_codes": ["H02.31", "L57.4"],
        "prompt_template": "Professional medical photography, 8K resolution, ultra-realistic. Show the result of a brow lift. The eyebrows should be elevated to a natural, youthful position above the orbital rim. Forehead lines smoothed but not frozen. Open and alert eyes. No 'surprised' look. Realistic skin texture with natural fine lines. Soft lighting. Preserve all other facial features exactly. Anatomically accurate."
    },
    {
        "id": "lip-augmentation-001",
        "name": "Lip Augmentation",
        "category": ProcedureCategory.FACIAL,
        "description": "Procedure to enhance lip fullness and shape using dermal fillers or implants. Addresses thin lips, asymmetry, or age-related volume loss. Creates fuller, more defined lips with improved contours.",
        "typical_cost_min": 500.0,
        "typical_cost_max": 2000.0,
        "recovery_days": 3,
        "risk_level": "low",
        "cpt_codes": ["40530", "11950", "11951"],
        "icd10_codes": ["Q38.0", "L98.8"],
        "prompt_template": "Professional medical photography, 8K resolution, ultra-realistic. Show the result of lip augmentation to {volume_level}. The lips should appear naturally plump and hydrated with defined vermilion border. Cupid's bow enhanced but natural. No 'duck lip' appearance. Realistic lip texture details. Soft studio lighting. Preserve all other facial features exactly. Anatomically accurate."
    }
]


def get_all_procedures() -> List[Dict[str, Any]]:
    """Get all procedure seed data."""
    return PROCEDURES_SEED_DATA


def get_procedure_by_id(procedure_id: str) -> Dict[str, Any] | None:
    """Get a specific procedure by ID."""
    for procedure in PROCEDURES_SEED_DATA:
        if procedure["id"] == procedure_id:
            return procedure
    return None


def get_procedures_by_category(category: str) -> List[Dict[str, Any]]:
    """Get all procedures in a specific category."""
    return [p for p in PROCEDURES_SEED_DATA if p["category"] == category]


def get_all_categories() -> List[str]:
    """Get all unique procedure categories."""
    return list(set(p["category"] for p in PROCEDURES_SEED_DATA))
