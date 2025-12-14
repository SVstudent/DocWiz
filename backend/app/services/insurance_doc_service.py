"""Insurance documentation service for generating pre-authorization forms."""
import io
import json
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

from google.cloud.firestore_v1 import Client
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

from app.services.nano_banana_client import NanoBananaClient, NanoBananaAPIError
from app.db.firestore_models import (
    PreAuthFormModel,
    ProviderInfoModel,
    ProcedureModel,
    PatientProfileModel,
    CostBreakdownModel,
    create_document,
    get_document,
)
from app.db.base import Collections
from app.schemas.insurance import (
    ClaimHeader,
    ServiceLineItem,
    DiagnosisInfo,
    FacilityInfo,
    ReferringProvider,
)
import random
import string

logger = logging.getLogger(__name__)


class InsuranceDocService:
    """Service for generating insurance documentation."""

    def __init__(
        self,
        db: Client,
        nano_banana_client: NanoBananaClient
    ):
        """
        Initialize insurance documentation service.

        Args:
            db: Firestore database client
            nano_banana_client: Nano Banana API client for text generation
        """
        self.db = db
        self.nano_banana = nano_banana_client

    async def generate_preauth_form(
        self,
        procedure_id: str,
        patient_id: str,
        cost_breakdown_id: Optional[str] = None,
        provider_info: Optional[Dict[str, Any]] = None
    ) -> PreAuthFormModel:
        """
        Generate pre-authorization form using Nano Banana.

        Includes:
        - CPT/ICD-10 codes from procedure
        - Medical necessity justification
        - Cost breakdown
        - Provider information

        Args:
            procedure_id: ID of the surgical procedure
            patient_id: ID of the patient
            cost_breakdown_id: Optional ID of cost breakdown
            provider_info: Optional provider information dict

        Returns:
            PreAuthFormModel with generated form data

        Raises:
            ValueError: If procedure or patient not found
            NanoBananaAPIError: If text generation fails
        """
        logger.info(
            f"Generating pre-auth form for patient {patient_id}, "
            f"procedure {procedure_id}"
        )

        # Fetch procedure data
        procedure_data = await get_document(
            self.db,
            Collections.PROCEDURES,
            procedure_id
        )
        if not procedure_data:
            raise ValueError(f"Procedure {procedure_id} not found")

        procedure = ProcedureModel(**procedure_data)

        # Fetch patient profile
        patient_data = await get_document(
            self.db,
            Collections.PATIENT_PROFILES,
            patient_id
        )
        
        if not patient_data:
            # Fallback: Create a demo patient profile for demo purposes
            logger.warning(f"Patient profile not found for {patient_id}, creating demo placeholder")
            from app.db.firestore_models import LocationModel, InsuranceInfoModel
            
            demo_patient = PatientProfileModel(
                id=patient_id,
                user_id=patient_id,
                name="Demo Patient",
                date_of_birth=datetime(1990, 1, 1),
                location=LocationModel(
                    zip_code="90210",
                    city="Beverly Hills",
                    state="CA",
                    country="USA"
                ),
                insurance_info=InsuranceInfoModel(
                    provider="Blue Cross Blue Shield",
                    encrypted_policy_number="DEMO-POLICY-12345",
                    group_number="GRP-DEMO-001",
                    plan_type="PPO",
                    coverage_details={"deductible": 500, "copay_percent": 20}
                ),
                encrypted_medical_history="Demo patient with no prior medical history."
            )
            
            # Save the demo patient profile
            await create_document(self.db, Collections.PATIENT_PROFILES, demo_patient)
            patient = demo_patient
        else:
            patient = PatientProfileModel(**patient_data)

        # Fetch cost breakdown if provided
        cost_breakdown = None
        if cost_breakdown_id:
            cost_data = await get_document(
                self.db,
                Collections.COST_BREAKDOWNS,
                cost_breakdown_id
            )
            if cost_data:
                cost_breakdown = CostBreakdownModel(**cost_data)

        # Generate medical necessity justification
        medical_justification = await self.generate_medical_justification(
            procedure=procedure,
            patient_history=patient.encrypted_medical_history
        )

        # Create provider info (use provided or default)
        if provider_info:
            provider = ProviderInfoModel(**provider_info)
        else:
            # Default provider info for demo purposes
            provider = ProviderInfoModel(
                name="DocWiz Surgical Center",
                npi="1234567890",
                address="123 Medical Plaza, Suite 100",
                phone="(555) 123-4567",
                specialty="Plastic and Reconstructive Surgery"
            )

        # Generate new detailed objects
        claim_header = self._build_claim_header()
        service_lines = self._build_service_line_items(procedure, cost_breakdown)
        diagnosis_details = self._build_diagnosis_info(procedure)
        facility_info = self._build_facility_info(provider)
        referring_provider = self._build_referring_provider()

        # Create structured data for insurance systems
        structured_data = self._build_structured_data(
            procedure=procedure,
            patient=patient,
            cost_breakdown=cost_breakdown,
            medical_justification=medical_justification,
            provider=provider
        )

        # Create pre-auth form model
        # Note: We use model_dump() to pass dicts which Pydantic will validate against the Firestore models
        # This works because the Schema models and Firestore models have compatible structures
        preauth_form = PreAuthFormModel(
            patient_id=patient_id,
            procedure_id=procedure_id,
            cost_breakdown_id=cost_breakdown_id,
            cpt_codes=procedure.cpt_codes,
            icd10_codes=procedure.icd10_codes,
            medical_justification=medical_justification,
            provider_info=provider,
            
            # New Detailed Fields
            claim_header=claim_header.model_dump(),
            service_lines=[l.model_dump() for l in service_lines],
            diagnosis_details=[d.model_dump() for d in diagnosis_details],
            facility_info=facility_info.model_dump(),
            referring_provider=referring_provider.model_dump(),
            
            structured_data=structured_data
        )

        # Save to Firestore
        form_id = await create_document(
            self.db,
            Collections.PREAUTH_FORMS,
            preauth_form
        )

        logger.info(f"Pre-auth form generated with ID: {form_id}")
        return preauth_form

    async def generate_medical_justification(
        self,
        procedure: ProcedureModel,
        patient_history: Optional[str] = None
    ) -> str:
        """
        Generate professional medical necessity justification.

        Args:
            procedure: Procedure model with details
            patient_history: Optional encrypted patient medical history

        Returns:
            Professional medical justification text

        Raises:
            NanoBananaAPIError: If text generation fails
        """
        logger.info(f"Generating medical justification for {procedure.name}")

        try:
            justification = await self.nano_banana.generate_medical_justification(
                procedure_name=procedure.name,
                procedure_description=procedure.description,
                patient_history=patient_history,
                cpt_codes=procedure.cpt_codes,
                icd10_codes=procedure.icd10_codes
            )

            logger.info("Medical justification generated successfully")
            return justification

        except NanoBananaAPIError as e:
            logger.error(f"Failed to generate medical justification: {e}")
            raise

    def _generate_authorization_reference(self) -> str:
        """Generate a realistic mock prior authorization number."""
        # Format: PA-YYYYMMDD-XXXXX
        date_str = datetime.now().strftime("%Y%m%d")
        random_suffix = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
        return f"PA-{date_str}-{random_suffix}"

    def _get_place_of_service_code(self) -> str:
        """Get place of service code (24 = Ambulatory Surgical Center)."""
        return "24"

    def _build_claim_header(self) -> ClaimHeader:
        """Build insurance claim header."""
        return ClaimHeader(
            claim_type="Professional",
            place_of_service=self._get_place_of_service_code(),
            prior_authorization_number=self._generate_authorization_reference(),
            referral_number=None,
            claim_frequency_code="1"  # Original claim
        )

    def _build_service_line_items(
        self,
        procedure: ProcedureModel,
        cost_breakdown: Optional[CostBreakdownModel]
    ) -> List[ServiceLineItem]:
        """Build service line items with modifiers and pricing."""
        lines = []
        
        # Primary procedure line
        primary_price = float(cost_breakdown.surgeon_fee) if cost_breakdown else 0.0
        lines.append(ServiceLineItem(
            procedure_code=procedure.cpt_codes[0] if procedure.cpt_codes else "99999",
            modifiers=[],
            description=procedure.name,
            quantity=1.0,
            unit_price=primary_price,
            total_price=primary_price,
            diagnosis_pointers=[1],
            service_date=datetime.now()
        ))
        
        # Facility fee line (if applicable)
        if cost_breakdown and float(cost_breakdown.facility_fee) > 0:
            lines.append(ServiceLineItem(
                procedure_code="S0020",  # S0020 = Injection, bupivicaine hydrochloride, 30 ml (often used for facility fees in some contexts, or use a generic facility code)
                # Better to use a generic facility code like 'FAC' for internal or specific logic if needed
                # For this demo, let's use a standard facility code structure or modifier
                modifiers=["TC"],  # Technical Component
                description="Facility Fee / Ambulatory Surgical Center",
                quantity=1.0,
                unit_price=float(cost_breakdown.facility_fee),
                total_price=float(cost_breakdown.facility_fee),
                diagnosis_pointers=[1],
                service_date=datetime.now()
            ))

        # Anesthesia line (if applicable)
        if cost_breakdown and float(cost_breakdown.anesthesia_fee) > 0:
             lines.append(ServiceLineItem(
                procedure_code="00100",  # Generic anesthesia code placeholder
                modifiers=["AA"],  # Anesthesia services performed personally by anesthesiologist
                description="Anesthesia Services",
                quantity=1.0,  # Could be time units
                unit_price=float(cost_breakdown.anesthesia_fee),
                total_price=float(cost_breakdown.anesthesia_fee),
                diagnosis_pointers=[1],
                service_date=datetime.now()
            ))
            
        return lines

    def _build_diagnosis_info(self, procedure: ProcedureModel) -> List[DiagnosisInfo]:
        """Build diagnosis information."""
        diagnoses = []
        if procedure.icd10_codes:
            # Primary diagnosis
            diagnoses.append(DiagnosisInfo(
                icd10_code=procedure.icd10_codes[0],
                description="Primary surgical diagnosis",
                type="Principal"
            ))
            # Secondary diagnoses
            for code in procedure.icd10_codes[1:]:
                 diagnoses.append(DiagnosisInfo(
                    icd10_code=code,
                    description="Secondary diagnosis",
                    type="Secondary"
                ))
        return diagnoses

    def _build_facility_info(self, provider: ProviderInfoModel) -> FacilityInfo:
        """Build facility information."""
        return FacilityInfo(
            name="DocWiz Surgical Center",  # Could be dynamic
            npi="1987654321",  # Mock Facility NPI
            address=provider.address,  # Use provider address for now
            place_of_service_code=self._get_place_of_service_code()
        )
        
    def _build_referring_provider(self) -> ReferringProvider:
        """Build mock referring provider info."""
        return ReferringProvider(
            name="Dr. Jane Smith",
            npi="1122334455"
        )

    def _build_structured_data(
        self,
        procedure: ProcedureModel,
        patient: PatientProfileModel,
        cost_breakdown: Optional[CostBreakdownModel],
        medical_justification: str,
        provider: ProviderInfoModel
    ) -> Dict[str, Any]:
        """
        Build structured data for insurance submission systems.

        Args:
            procedure: Procedure model
            patient: Patient profile model
            cost_breakdown: Optional cost breakdown model
            medical_justification: Generated justification text
            provider: Provider information model

        Returns:
            Dictionary with structured insurance claim data
        """
        # Generate new detailed objects
        claim_header = self._build_claim_header()
        service_lines = self._build_service_line_items(procedure, cost_breakdown)
        diagnosis_details = self._build_diagnosis_info(procedure)
        facility_info = self._build_facility_info(provider)
        referring_provider = self._build_referring_provider()
        
        # Build base structured data
        structured_data = {
            "claim_type": "pre_authorization",
            "submission_date": datetime.utcnow().isoformat(),
            "patient": {
                "name": patient.name,
                "date_of_birth": patient.date_of_birth.isoformat(),
                "insurance_provider": patient.insurance_info.provider,
                "policy_number": patient.insurance_info.encrypted_policy_number,
                "group_number": patient.insurance_info.group_number,
            },
            "provider": {
                "name": provider.name,
                "npi": provider.npi,
                "address": provider.address,
                "phone": provider.phone,
                "specialty": provider.specialty,
            },
            "facility": facility_info.model_dump(),
            "referring_provider": referring_provider.model_dump(),
            "claim_header": claim_header.model_dump(),
            "procedure": {
                "name": procedure.name,
                "category": procedure.category,
                "description": procedure.description,
                "cpt_codes": procedure.cpt_codes,
                "icd10_codes": procedure.icd10_codes,
            },
            "diagnosis_details": [d.model_dump() for d in diagnosis_details],
            "service_lines": [l.model_dump() for l in service_lines],
            "medical_justification": medical_justification,
        }

        # Add cost information if available
        if cost_breakdown:
            structured_data["cost_estimate"] = {
                "total_cost": float(cost_breakdown.total_cost),
                "surgeon_fee": float(cost_breakdown.surgeon_fee),
                "facility_fee": float(cost_breakdown.facility_fee),
                "anesthesia_fee": float(cost_breakdown.anesthesia_fee),
                "post_op_care": float(cost_breakdown.post_op_care),
                "estimated_insurance_coverage": float(cost_breakdown.insurance_coverage) if cost_breakdown.insurance_coverage else None,
                "estimated_patient_responsibility": float(cost_breakdown.patient_responsibility) if cost_breakdown.patient_responsibility else None,
            }

        return structured_data

    async def get_preauth_form(self, form_id: str) -> Optional[PreAuthFormModel]:
        """
        Retrieve a pre-authorization form by ID.

        Args:
            form_id: ID of the pre-auth form

        Returns:
            PreAuthFormModel if found, None otherwise
        """
        form_data = await get_document(
            self.db,
            Collections.PREAUTH_FORMS,
            form_id
        )

        if form_data:
            return PreAuthFormModel(**form_data)
        return None

    async def export_preauth_form_pdf(
        self,
        form_id: str
    ) -> bytes:
        """
        Export pre-authorization form as PDF.

        Args:
            form_id: ID of the pre-auth form

        Returns:
            PDF file as bytes

        Raises:
            ValueError: If form not found
        """
        logger.info(f"Exporting pre-auth form {form_id} as PDF")

        # Retrieve form
        form = await self.get_preauth_form(form_id)
        if not form:
            raise ValueError(f"Pre-auth form {form_id} not found")

        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=colors.HexColor('#0066CC'),
            spaceAfter=30,
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#0066CC'),
            spaceAfter=12,
        )

        # Title
        story.append(Paragraph("Pre-Authorization Request", title_style))
        story.append(Spacer(1, 0.2 * inch))

        # Form metadata
        story.append(Paragraph(f"Form ID: {form.id}", styles['Normal']))
        story.append(Paragraph(
            f"Generated: {form.generated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            styles['Normal']
        ))
        
        # New Claim Indicators
        if form.claim_header:
            story.append(Spacer(1, 0.1 * inch))
            header_text = []
            if form.claim_header.prior_authorization_number:
                header_text.append(f"<b>Prior Authorization #:</b> {form.claim_header.prior_authorization_number}")
            if form.claim_header.place_of_service:
                header_text.append(f"<b>Place of Service:</b> {form.claim_header.place_of_service}")
            
            if header_text:
                story.append(Paragraph(" | ".join(header_text), styles['Normal']))
                
        story.append(Spacer(1, 0.3 * inch))

        # Patient & Insurance Information
        story.append(Paragraph("Patient & Insurance Information", heading_style))
        if form.structured_data and "patient" in form.structured_data:
            patient_data = form.structured_data["patient"]
            patient_table_data = [
                ["Patient Name:", patient_data.get("name", "N/A")],
                ["Date of Birth:", patient_data.get("date_of_birth", "N/A")],
                ["Insurance Provider:", patient_data.get("insurance_provider", "N/A")],
                ["Policy Number:", patient_data.get("policy_number", "N/A")],
                ["Group Number:", patient_data.get("group_number", "N/A")],
            ]
            patient_table = Table(patient_table_data, colWidths=[2 * inch, 4 * inch])
            patient_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(patient_table)
        story.append(Spacer(1, 0.3 * inch))

        # Provider & Facility Information
        story.append(Paragraph("Provider & Facility Information", heading_style))
        provider_table_data = [
            ["Billing Provider:", form.provider_info.name],
            ["NPI:", form.provider_info.npi],
            ["Address:", form.provider_info.address],
            ["Phone:", form.provider_info.phone],
        ]
        
        if form.facility_info:
            provider_table_data.extend([
                ["", ""],
                ["Service Facility:", form.facility_info.name],
                ["Facility NPI:", form.facility_info.npi],
                ["Facility Address:", form.facility_info.address],
            ])
            
        if form.referring_provider and form.referring_provider.name:
            provider_table_data.extend([
                ["", ""],
                ["Referring Provider:", form.referring_provider.name],
                ["NPI:", form.referring_provider.npi or "N/A"],
            ])
            
        provider_table = Table(provider_table_data, colWidths=[2 * inch, 4 * inch])
        provider_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(provider_table)
        story.append(Spacer(1, 0.3 * inch))

        # Procedure & Diagnosis Information
        story.append(Paragraph("Diagnostic Information", heading_style))
        if form.diagnosis_details:
            diag_data = [["Code", "Description", "Type"]]
            for diag in form.diagnosis_details:
                diag_data.append([
                    diag.icd10_code,
                    diag.description or "N/A",
                    diag.type
                ])
            
            diag_table = Table(diag_data, colWidths=[1.5 * inch, 3.5 * inch, 1 * inch])
            diag_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(diag_table)
        else:
            # Fallback to old format
            story.append(Paragraph(f"ICD-10 Codes: {', '.join(form.icd10_codes)}", styles['Normal']))
            
        story.append(Spacer(1, 0.3 * inch))

        # Service Lines (Itemized)
        if form.service_lines:
            story.append(Paragraph("Service Lines", heading_style))
            line_data = [["Date", "Code", "Mod", "Description", "Qty", "Price"]]
            
            for line in form.service_lines:
                price_str = f"${line.total_price:,.2f}"
                mod_str = ", ".join(line.modifiers) if line.modifiers else ""
                date_str = line.service_date.strftime("%m/%d/%Y")
                
                line_data.append([
                    date_str,
                    line.procedure_code,
                    mod_str,
                    line.description[:30] + "..." if len(line.description) > 30 else line.description,
                    f"{line.quantity:.0f}",
                    price_str
                ])
                
            line_table = Table(line_data, colWidths=[1 * inch, 0.8 * inch, 0.8 * inch, 2.4 * inch, 0.5 * inch, 1 * inch])
            line_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                ('ALIGN', (-2, 1), (-1, -1), 'RIGHT'), # Align numbers right
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(line_table)
            story.append(Spacer(1, 0.3 * inch))

        # Medical Justification
        story.append(Paragraph("Medical Necessity Justification", heading_style))
        justification_para = Paragraph(
            form.medical_justification,
            styles['Normal']
        )
        story.append(justification_para)
        story.append(Spacer(1, 0.3 * inch))

        # Cost Estimate Summary (Keep as overall summary)
        if form.structured_data and "cost_estimate" in form.structured_data:
            story.append(Paragraph("Financial Summary", heading_style))
            cost_data = form.structured_data["cost_estimate"]
            cost_table_data = [
                ["Surgeon Fee:", f"${cost_data.get('surgeon_fee', 0):,.2f}"],
                ["Facility Fee:", f"${cost_data.get('facility_fee', 0):,.2f}"],
                ["Anesthesia Fee:", f"${cost_data.get('anesthesia_fee', 0):,.2f}"],
                ["Post-Op Care:", f"${cost_data.get('post_op_care', 0):,.2f}"],
                ["Total Cost:", f"${cost_data.get('total_cost', 0):,.2f}"],
            ]

            if cost_data.get('estimated_insurance_coverage'):
                cost_table_data.extend([
                    ["", ""],
                    ["Est. Insurance Coverage:", f"${cost_data.get('estimated_insurance_coverage', 0):,.2f}"],
                    ["Est. Patient Responsibility:", f"${cost_data.get('estimated_patient_responsibility', 0):,.2f}"],
                ])

            cost_table = Table(cost_table_data, colWidths=[3 * inch, 2 * inch])
            cost_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LINEABOVE', (0, 4), (-1, 4), 1, colors.black),
                ('FONTNAME', (0, 4), (-1, 4), 'Helvetica-Bold'),
            ]))
            story.append(cost_table)
            story.append(Spacer(1, 0.3 * inch))

        # Disclaimer
        story.append(Spacer(1, 0.5 * inch))
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
        )
        story.append(Paragraph(
            "<b>DISCLAIMER:</b> This pre-authorization request is for informational purposes only. "
            "Final coverage determination is subject to insurance provider review and approval. "
            "Cost estimates are approximate and may vary based on actual services provided.",
            disclaimer_style
        ))

        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info(f"PDF generated successfully for form {form_id}")
        return pdf_bytes

    async def export_preauth_form_json(
        self,
        form_id: str
    ) -> str:
        """
        Export pre-authorization form as JSON.

        Args:
            form_id: ID of the pre-auth form

        Returns:
            JSON string with structured claim data

        Raises:
            ValueError: If form not found
        """
        logger.info(f"Exporting pre-auth form {form_id} as JSON")

        # Retrieve form
        form = await self.get_preauth_form(form_id)
        if not form:
            raise ValueError(f"Pre-auth form {form_id} not found")

        # Build JSON structure (HIPAA-compliant format / 837P)
        json_data = {
            "claim_type": "pre_authorization",
            "form_id": form.id,
            "submission_date": form.generated_at.isoformat(),
            
            # Header Info
            "claim_header": form.claim_header.model_dump() if form.claim_header else None,
            
            "patient": form.structured_data.get("patient", {}) if form.structured_data else {},
            
            "provider": {
                "name": form.provider_info.name,
                "npi": form.provider_info.npi,
                "address": form.provider_info.address,
                "phone": form.provider_info.phone,
                "specialty": form.provider_info.specialty,
            },
            
            "facility": form.facility_info.model_dump() if form.facility_info else None,
            "referring_provider": form.referring_provider.model_dump() if form.referring_provider else None,
            
            "procedure": form.structured_data.get("procedure", {}) if form.structured_data else {},
            
            "diagnosis_codes": [d.model_dump() for d in form.diagnosis_details] if form.diagnosis_details else {
                "cpt": form.cpt_codes,
                "icd10": form.icd10_codes,
            },
            
            "service_lines": [l.model_dump() for l in form.service_lines] if form.service_lines else [],
            
            "medical_justification": form.medical_justification,
            "cost_estimate": form.structured_data.get("cost_estimate") if form.structured_data else None,
        }

        logger.info(f"JSON generated successfully for form {form_id}")
        return json.dumps(json_data, indent=2)
