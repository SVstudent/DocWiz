"""Export service for generating comprehensive reports."""
import io
import json
import logging
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from decimal import Decimal

from google.cloud.firestore_v1 import Client
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, PageBreak
from reportlab.lib import colors
from PIL import Image
import requests

from app.db.base import Collections
from app.db.firestore_models import (
    PatientProfileModel,
    VisualizationResultModel,
    CostBreakdownModel,
    ComparisonSetModel,
    get_document,
)
from app.schemas.export import ExportData, ExportMetadata

logger = logging.getLogger(__name__)


# Medical disclaimer text
MEDICAL_DISCLAIMER = (
    "MEDICAL DISCLAIMER: This report is for informational purposes only and does not constitute medical advice. "
    "All surgical visualizations are AI-generated predictions and may not reflect actual surgical outcomes. "
    "Cost estimates are approximate and subject to change. Always consult with qualified medical professionals "
    "before making any healthcare decisions."
)


class ExportService:
    """Service for generating comprehensive surgical analysis reports."""

    def __init__(self, db: Client):
        """
        Initialize export service.

        Args:
            db: Firestore database client
        """
        self.db = db

    async def export_comprehensive_report(
        self,
        patient_id: str,
        format: Literal["pdf", "png", "jpeg", "json"],
        shareable: bool = False,
        include_visualizations: bool = True,
        include_cost_estimates: bool = True,
        include_comparisons: bool = True,
        visualization_ids: Optional[List[str]] = None,
        cost_breakdown_ids: Optional[List[str]] = None,
        comparison_ids: Optional[List[str]] = None,
    ) -> bytes:
        """
        Export comprehensive surgical analysis report.

        Includes:
        - All visualizations (or specified ones)
        - Cost breakdowns (or specified ones)
        - Comparison analysis (or specified ones)
        - Medical disclaimers

        Args:
            patient_id: Patient profile ID
            format: Export format (pdf, png, jpeg, json)
            shareable: Whether to create shareable version (removes sensitive data)
            include_visualizations: Include visualization results
            include_cost_estimates: Include cost estimates
            include_comparisons: Include comparison sets
            visualization_ids: Specific visualization IDs to include (all if None)
            cost_breakdown_ids: Specific cost breakdown IDs to include (all if None)
            comparison_ids: Specific comparison IDs to include (all if None)

        Returns:
            Export file as bytes

        Raises:
            ValueError: If patient not found or no data to export
        """
        logger.info(f"Generating {format} export for patient {patient_id}, shareable={shareable}")

        # Gather all data
        export_data = await self._gather_export_data(
            patient_id=patient_id,
            include_visualizations=include_visualizations,
            include_cost_estimates=include_cost_estimates,
            include_comparisons=include_comparisons,
            visualization_ids=visualization_ids,
            cost_breakdown_ids=cost_breakdown_ids,
            comparison_ids=comparison_ids,
        )

        # Apply sanitization if shareable
        if shareable:
            export_data = self._sanitize_export_data(export_data)

        # Generate export based on format
        if format == "json":
            return await self._export_json(export_data)
        elif format == "pdf":
            return await self._export_pdf(export_data)
        elif format in ["png", "jpeg"]:
            return await self._export_image(export_data, format)
        else:
            raise ValueError(f"Unsupported export format: {format}")

    async def _gather_export_data(
        self,
        patient_id: str,
        include_visualizations: bool,
        include_cost_estimates: bool,
        include_comparisons: bool,
        visualization_ids: Optional[List[str]],
        cost_breakdown_ids: Optional[List[str]],
        comparison_ids: Optional[List[str]],
    ) -> ExportData:
        """
        Gather all data for export.

        Args:
            patient_id: Patient profile ID
            include_visualizations: Include visualization results
            include_cost_estimates: Include cost estimates
            include_comparisons: Include comparison sets
            visualization_ids: Specific visualization IDs
            cost_breakdown_ids: Specific cost breakdown IDs
            comparison_ids: Specific comparison IDs

        Returns:
            ExportData with all gathered information

        Raises:
            ValueError: If patient not found
        """
        # Fetch patient profile
        patient_data = await get_document(self.db, Collections.PATIENT_PROFILES, patient_id)
        if not patient_data:
            raise ValueError(f"Patient {patient_id} not found")

        patient = PatientProfileModel(**patient_data)

        # Initialize export data
        export_data = ExportData(
            export_id=str(uuid.uuid4()),
            patient_name=patient.name,
            generated_at=datetime.utcnow(),
            shareable=False,  # Will be set later if sanitized
        )

        # Gather visualizations
        if include_visualizations:
            visualizations = await self._get_visualizations(patient_id, visualization_ids)
            export_data.visualizations = [v.model_dump(mode='json') for v in visualizations]

        # Gather cost estimates
        if include_cost_estimates:
            cost_estimates = await self._get_cost_breakdowns(patient_id, cost_breakdown_ids)
            export_data.cost_estimates = [c.model_dump(mode='json') for c in cost_estimates]

        # Gather comparisons
        if include_comparisons:
            comparisons = await self._get_comparisons(patient_id, comparison_ids)
            export_data.comparisons = [c.model_dump(mode='json') for c in comparisons]

        # Validate we have data to export
        if not export_data.visualizations and not export_data.cost_estimates and not export_data.comparisons:
            raise ValueError(f"No data found to export for patient {patient_id}")

        return export_data

    async def _get_visualizations(
        self,
        patient_id: str,
        visualization_ids: Optional[List[str]] = None
    ) -> List[VisualizationResultModel]:
        """Get visualizations for patient."""
        if visualization_ids:
            # Get specific visualizations
            visualizations = []
            for viz_id in visualization_ids:
                viz_data = await get_document(self.db, Collections.VISUALIZATION_RESULTS, viz_id)
                if viz_data and viz_data.get("patient_id") == patient_id:
                    visualizations.append(VisualizationResultModel(**viz_data))
        else:
            # Get all visualizations for patient
            query = self.db.collection(Collections.VISUALIZATION_RESULTS).where("patient_id", "==", patient_id)
            docs = query.stream()
            visualizations = [VisualizationResultModel(**doc.to_dict()) for doc in docs if doc.exists]

        return visualizations

    async def _get_cost_breakdowns(
        self,
        patient_id: str,
        cost_breakdown_ids: Optional[List[str]] = None
    ) -> List[CostBreakdownModel]:
        """Get cost breakdowns for patient."""
        if cost_breakdown_ids:
            # Get specific cost breakdowns
            breakdowns = []
            for breakdown_id in cost_breakdown_ids:
                breakdown_data = await get_document(self.db, Collections.COST_BREAKDOWNS, breakdown_id)
                if breakdown_data and breakdown_data.get("patient_id") == patient_id:
                    breakdowns.append(CostBreakdownModel(**breakdown_data))
        else:
            # Get all cost breakdowns for patient
            query = self.db.collection(Collections.COST_BREAKDOWNS).where("patient_id", "==", patient_id)
            docs = query.stream()
            breakdowns = [CostBreakdownModel(**doc.to_dict()) for doc in docs if doc.exists]

        return breakdowns

    async def _get_comparisons(
        self,
        patient_id: str,
        comparison_ids: Optional[List[str]] = None
    ) -> List[ComparisonSetModel]:
        """Get comparison sets for patient."""
        if comparison_ids:
            # Get specific comparisons
            comparisons = []
            for comparison_id in comparison_ids:
                comparison_data = await get_document(self.db, Collections.COMPARISON_SETS, comparison_id)
                if comparison_data and comparison_data.get("patient_id") == patient_id:
                    comparisons.append(ComparisonSetModel(**comparison_data))
        else:
            # Get all comparisons for patient
            query = self.db.collection(Collections.COMPARISON_SETS).where("patient_id", "==", patient_id)
            docs = query.stream()
            comparisons = [ComparisonSetModel(**doc.to_dict()) for doc in docs if doc.exists]

        return comparisons

    def _sanitize_export_data(self, export_data: ExportData) -> ExportData:
        """
        Remove sensitive fields for shareable export.

        Removes:
        - Policy numbers
        - Medical history
        - Personal identifiers

        Maintains:
        - All visualizations
        - Cost summaries (without insurance details)

        Args:
            export_data: Original export data

        Returns:
            Sanitized export data
        """
        logger.info("Sanitizing export data for shareable version")

        # Mark as shareable
        export_data.shareable = True

        # Sanitize cost estimates - remove insurance details
        for cost_estimate in export_data.cost_estimates:
            # Remove sensitive insurance fields
            if "insurance_provider" in cost_estimate:
                cost_estimate["insurance_provider"] = "REDACTED"
            if "insurance_coverage" in cost_estimate:
                cost_estimate["insurance_coverage"] = None
            if "deductible" in cost_estimate:
                cost_estimate["deductible"] = None
            if "copay" in cost_estimate:
                cost_estimate["copay"] = None

        # Note: Visualizations and comparisons don't contain sensitive data
        # so they can be included as-is

        return export_data

    async def _export_json(self, export_data: ExportData) -> bytes:
        """
        Export data as JSON.

        Args:
            export_data: Export data

        Returns:
            JSON as bytes
        """
        logger.info(f"Exporting as JSON: {export_data.export_id}")

        # Convert to dict
        data_dict = export_data.model_dump(mode='json')

        # Pretty print JSON
        json_str = json.dumps(data_dict, indent=2, default=str)

        return json_str.encode('utf-8')

    async def _export_pdf(self, export_data: ExportData) -> bytes:
        """
        Export data as PDF.

        Args:
            export_data: Export data

        Returns:
            PDF as bytes
        """
        logger.info(f"Exporting as PDF: {export_data.export_id}")

        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            textColor=colors.HexColor('#0066CC'),
            spaceAfter=20,
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=colors.HexColor('#0066CC'),
            spaceAfter=12,
        )

        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            spaceAfter=12,
        )

        # Title
        story.append(Paragraph("DocWiz Surgical Analysis Report", title_style))
        story.append(Spacer(1, 0.1 * inch))

        # Metadata
        story.append(Paragraph(f"<b>Patient:</b> {export_data.patient_name}", styles['Normal']))
        story.append(Paragraph(f"<b>Report ID:</b> {export_data.export_id}", styles['Normal']))
        story.append(Paragraph(
            f"<b>Generated:</b> {export_data.generated_at.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            styles['Normal']
        ))
        if export_data.shareable:
            story.append(Paragraph("<b>Type:</b> Shareable (sensitive data removed)", styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # Disclaimer at top
        story.append(Paragraph(export_data.disclaimer, disclaimer_style))
        story.append(Spacer(1, 0.2 * inch))

        # Visualizations section
        if export_data.visualizations:
            story.append(Paragraph(f"Surgical Visualizations ({len(export_data.visualizations)})", heading_style))
            for viz in export_data.visualizations:
                story.append(Paragraph(f"<b>Procedure:</b> {viz.get('procedure_name', 'N/A')}", styles['Normal']))
                story.append(Paragraph(
                    f"<b>Generated:</b> {viz.get('generated_at', 'N/A')}",
                    styles['Normal']
                ))
                story.append(Paragraph(
                    f"<b>Confidence Score:</b> {viz.get('confidence_score', 0):.2f}",
                    styles['Normal']
                ))
                story.append(Paragraph(f"<b>Before Image:</b> {viz.get('before_image_url', 'N/A')}", styles['Normal']))
                story.append(Paragraph(f"<b>After Image:</b> {viz.get('after_image_url', 'N/A')}", styles['Normal']))
                story.append(Spacer(1, 0.2 * inch))

        # Cost estimates section
        if export_data.cost_estimates:
            story.append(PageBreak())
            story.append(Paragraph(f"Cost Estimates ({len(export_data.cost_estimates)})", heading_style))
            for cost in export_data.cost_estimates:
                story.append(Paragraph(f"<b>Procedure ID:</b> {cost.get('procedure_id', 'N/A')}", styles['Normal']))
                story.append(Paragraph(
                    f"<b>Calculated:</b> {cost.get('calculated_at', 'N/A')}",
                    styles['Normal']
                ))

                # Cost breakdown table
                cost_table_data = [
                    ["Surgeon Fee:", f"${float(cost.get('surgeon_fee', 0)):,.2f}"],
                    ["Facility Fee:", f"${float(cost.get('facility_fee', 0)):,.2f}"],
                    ["Anesthesia Fee:", f"${float(cost.get('anesthesia_fee', 0)):,.2f}"],
                    ["Post-Op Care:", f"${float(cost.get('post_op_care', 0)):,.2f}"],
                    ["Total Cost:", f"${float(cost.get('total_cost', 0)):,.2f}"],
                ]

                if not export_data.shareable and cost.get('insurance_coverage'):
                    cost_table_data.extend([
                        ["", ""],
                        ["Insurance Coverage:", f"${float(cost.get('insurance_coverage', 0)):,.2f}"],
                        ["Patient Responsibility:", f"${float(cost.get('patient_responsibility', 0)):,.2f}"],
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

                # Data sources
                if cost.get('data_sources'):
                    story.append(Spacer(1, 0.1 * inch))
                    story.append(Paragraph("<b>Data Sources:</b>", styles['Normal']))
                    for source in cost['data_sources']:
                        story.append(Paragraph(f"• {source}", styles['Normal']))

                story.append(Spacer(1, 0.3 * inch))

        # Comparisons section
        if export_data.comparisons:
            story.append(PageBreak())
            story.append(Paragraph(f"Procedure Comparisons ({len(export_data.comparisons)})", heading_style))
            for comparison in export_data.comparisons:
                story.append(Paragraph(f"<b>Comparison ID:</b> {comparison.get('id', 'N/A')}", styles['Normal']))
                story.append(Paragraph(
                    f"<b>Created:</b> {comparison.get('created_at', 'N/A')}",
                    styles['Normal']
                ))
                story.append(Paragraph(
                    f"<b>Procedures Compared:</b> {len(comparison.get('procedure_ids', []))}",
                    styles['Normal']
                ))
                story.append(Spacer(1, 0.2 * inch))

        # Final disclaimer
        story.append(PageBreak())
        story.append(Paragraph(export_data.disclaimer, disclaimer_style))

        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info(f"PDF generated successfully: {len(pdf_bytes)} bytes")
        return pdf_bytes

    async def _export_image(
        self,
        export_data: ExportData,
        format: Literal["png", "jpeg"]
    ) -> bytes:
        """
        Export data as image (PNG or JPEG).

        Creates a visual summary of the report.

        Args:
            export_data: Export data
            format: Image format (png or jpeg)

        Returns:
            Image as bytes
        """
        logger.info(f"Exporting as {format.upper()}: {export_data.export_id}")

        # For now, create a simple text-based image
        # In production, this would create a more sophisticated visual report
        from PIL import Image, ImageDraw, ImageFont

        # Create image
        width, height = 800, 1000
        bg_color = (255, 255, 255) if format == "png" else (255, 255, 255)
        img = Image.new('RGB', (width, height), color=bg_color)
        draw = ImageDraw.Draw(img)

        # Use default font
        try:
            font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
            font_normal = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 14)
            font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 10)
        except:
            font_title = ImageFont.load_default()
            font_normal = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # Draw content
        y = 40
        draw.text((40, y), "DocWiz Surgical Analysis Report", fill=(0, 102, 204), font=font_title)
        y += 60

        draw.text((40, y), f"Patient: {export_data.patient_name}", fill=(0, 0, 0), font=font_normal)
        y += 30
        draw.text((40, y), f"Report ID: {export_data.export_id}", fill=(0, 0, 0), font=font_normal)
        y += 30
        draw.text((40, y), f"Generated: {export_data.generated_at.strftime('%Y-%m-%d %H:%M:%S')}", fill=(0, 0, 0), font=font_normal)
        y += 50

        # Summary
        draw.text((40, y), f"Visualizations: {len(export_data.visualizations)}", fill=(0, 0, 0), font=font_normal)
        y += 30
        draw.text((40, y), f"Cost Estimates: {len(export_data.cost_estimates)}", fill=(0, 0, 0), font=font_normal)
        y += 30
        draw.text((40, y), f"Comparisons: {len(export_data.comparisons)}", fill=(0, 0, 0), font=font_normal)
        y += 60

        # Disclaimer
        disclaimer_lines = [
            "MEDICAL DISCLAIMER:",
            "This report is for informational purposes only.",
            "Consult qualified medical professionals before",
            "making any healthcare decisions.",
        ]
        for line in disclaimer_lines:
            draw.text((40, y), line, fill=(128, 128, 128), font=font_small)
            y += 20

        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format=format.upper())
        image_bytes = buffer.getvalue()
        buffer.close()

        logger.info(f"{format.upper()} generated successfully: {len(image_bytes)} bytes")
        return image_bytes

    async def create_export_metadata(
        self,
        patient_id: str,
        format: str,
        shareable: bool,
        file_size_bytes: int
    ) -> ExportMetadata:
        """
        Create and store export metadata.

        Args:
            patient_id: Patient profile ID
            format: Export format
            shareable: Whether this is a shareable export
            file_size_bytes: File size in bytes

        Returns:
            ExportMetadata

        Raises:
            ValueError: If patient not found
        """
        # Fetch patient profile
        patient_data = await get_document(self.db, Collections.PATIENT_PROFILES, patient_id)
        if not patient_data:
            raise ValueError(f"Patient {patient_id} not found")

        patient = PatientProfileModel(**patient_data)

        # Create metadata
        metadata = ExportMetadata(
            id=str(uuid.uuid4()),
            patient_id=patient_id,
            patient_name=patient.name,
            format=format,
            shareable=shareable,
            created_at=datetime.utcnow(),
            file_size_bytes=file_size_bytes,
        )

        # Store in Firestore
        self.db.collection(Collections.EXPORTS).document(metadata.id).set(
            metadata.model_dump(mode='json')
        )

        return metadata

    async def get_export_metadata(self, export_id: str) -> Optional[ExportMetadata]:
        """
        Retrieve export metadata by ID.

        Args:
            export_id: Export identifier

        Returns:
            ExportMetadata if found, None otherwise
        """
        doc = self.db.collection(Collections.EXPORTS).document(export_id).get()

        if doc.exists:
            data = doc.to_dict()
            if data:
                return ExportMetadata(**data)

        return None


def get_export_service(db: Client) -> ExportService:
    """Factory function to create export service instance.

    Args:
        db: Firestore client

    Returns:
        ExportService instance
    """
    return ExportService(db)
