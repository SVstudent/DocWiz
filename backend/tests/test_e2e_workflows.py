"""
End-to-end integration tests for complete user workflows.

Tests the following workflows:
1. Full visualization workflow (upload → select → generate → view → save)
2. Cost estimation workflow (profile → procedure → estimate → export)
3. Comparison workflow (select multiple → compare → save)
4. Insurance claim workflow (generate → download)

Requirements: 1.1, 1.2, 1.3, 3.1, 4.1, 7.1
"""

import pytest
from httpx import AsyncClient
from io import BytesIO
from PIL import Image
import json


@pytest.mark.asyncio
@pytest.mark.integration
class TestVisualizationWorkflow:
    """Test full visualization workflow: upload → select → generate → view → save"""
    
    async def test_complete_visualization_workflow(
        self,
        async_client: AsyncClient,
        test_user_token: str,
        test_patient_profile: dict
    ):
        """
        Test the complete visualization workflow from image upload to saving results.
        Requirements: 1.1, 1.2, 1.3
        """
        # Override auth dependency for this test
        from app.api.dependencies import get_current_active_user
        from app.db.models import User
        from app.main import app
        
        def mock_user():
            return User(id="test_user_id", email="test@example.com", hashed_password="fake")
        
        app.dependency_overrides[get_current_active_user] = mock_user
        
        try:
            # Step 1: Upload image
            # Create a test image
            img = Image.new('RGB', (800, 600), color='white')
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            upload_response = await async_client.post(
                "/api/images/upload",
                files={"image": ("test_image.jpg", img_bytes, "image/jpeg")},
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert upload_response.status_code == 200
            upload_data = upload_response.json()
            assert "id" in upload_data
            assert "url" in upload_data
            image_id = upload_data["id"]
            
            # Step 2: Select a surgical procedure
            procedures_response = await async_client.get(
                "/api/procedures",
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert procedures_response.status_code == 200
            procedures = procedures_response.json()
            assert len(procedures) > 0
            selected_procedure = procedures[0]
            
            # Verify procedure has required details
            assert "description" in selected_procedure
            assert "recovery_days" in selected_procedure
            assert "risk_level" in selected_procedure
            
            # Step 3: Generate surgical preview
            viz_request = {
                "image_id": image_id,
                "procedure_id": selected_procedure["id"],
                "patient_id": test_patient_profile["id"]
            }
            
            viz_response = await async_client.post(
                "/api/visualizations",
                json=viz_request,
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert viz_response.status_code == 200
            viz_data = viz_response.json()
            
            # Step 4: View the generated visualization
            assert "id" in viz_data
            assert "before_image_url" in viz_data
            assert "after_image_url" in viz_data
            assert "procedure_id" in viz_data
            viz_id = viz_data["id"]
            
            # Retrieve the visualization
            get_viz_response = await async_client.get(
                f"/api/visualizations/{viz_id}",
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert get_viz_response.status_code == 200
            retrieved_viz = get_viz_response.json()
            assert retrieved_viz["id"] == viz_id
            
            # Step 5: Save to profile (verify it's persisted)
            # The visualization should already be saved, verify it appears in profile
            profile_response = await async_client.get(
                f"/api/profiles/{test_patient_profile['id']}",
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert profile_response.status_code == 200
        finally:
            app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
class TestCostEstimationWorkflow:
    """Test cost estimation workflow: profile → procedure → estimate → export"""
    
    async def test_complete_cost_estimation_workflow(
        self,
        async_client: AsyncClient,
        test_user_token: str,
        test_patient_profile: dict
    ):
        """
        Test the complete cost estimation workflow.
        Requirements: 3.1
        """
        # Override auth dependency
        from app.api.dependencies import get_current_active_user
        from app.db.models import User
        from app.main import app
        
        def mock_user():
            return User(id="test_user_id", email="test@example.com", hashed_password="fake")
        
        app.dependency_overrides[get_current_active_user] = mock_user
        
        try:
            # Step 1: Verify profile exists with required information
            profile_response = await async_client.get(
                f"/api/profiles/{test_patient_profile['id']}",
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert profile_response.status_code == 200
            profile = profile_response.json()
            assert "insurance_provider" in profile
            assert "location" in profile
            
            # Step 2: Select a procedure
            procedures_response = await async_client.get(
                "/api/procedures",
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert procedures_response.status_code == 200
            procedures = procedures_response.json()
            assert len(procedures) > 0
            selected_procedure = procedures[0]
            
            # Step 3: Request cost estimate
            cost_request = {
                "procedure_id": selected_procedure["id"],
                "patient_id": test_patient_profile["id"]
            }
            
            cost_response = await async_client.post(
                "/api/costs/estimate",
                json=cost_request,
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert cost_response.status_code == 200
            cost_data = cost_response.json()
            
            # Verify cost breakdown completeness (Property 8)
            assert "surgeon_fee" in cost_data
            assert "facility_fee" in cost_data
            assert "anesthesia_fee" in cost_data
            assert "post_op_care" in cost_data
            assert "total_cost" in cost_data
            
            # Verify insurance calculations (Property 10)
            assert "insurance_coverage" in cost_data
            assert "deductible" in cost_data
            assert "copay" in cost_data
            assert "out_of_pocket_max" in cost_data
            
            # Verify payment plans (Property 12)
            assert "payment_plans" in cost_data
            assert len(cost_data["payment_plans"]) > 0
            
            cost_id = cost_data["id"]
            
            # Step 4: Export the cost estimate
            export_request = {
                "cost_ids": [cost_id],
                "format": "pdf"
            }
            
            export_response = await async_client.post(
                "/api/exports",
                json=export_request,
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert export_response.status_code == 200
            export_data = export_response.json()
            assert "id" in export_data
            
            # Verify export can be downloaded
            download_response = await async_client.get(
                f"/api/exports/{export_data['id']}/download",
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert download_response.status_code == 200
        finally:
            app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
class TestComparisonWorkflow:
    """Test comparison workflow: select multiple → compare → save"""
    
    async def test_complete_comparison_workflow(
        self,
        async_client: AsyncClient,
        test_user_token: str,
        test_patient_profile: dict
    ):
        """
        Test the complete comparison workflow.
        Requirements: 4.1
        """
        # Override auth dependency
        from app.api.dependencies import get_current_active_user
        from app.db.models import User
        from app.main import app
        
        def mock_user():
            return User(id="test_user_id", email="test@example.com", hashed_password="fake")
        
        app.dependency_overrides[get_current_active_user] = mock_user
        
        try:
            # Step 1: Upload source image
            img = Image.new('RGB', (800, 600), color='white')
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            upload_response = await async_client.post(
                "/api/images/upload",
                files={"image": ("test_image.jpg", img_bytes, "image/jpeg")},
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert upload_response.status_code == 200
            image_id = upload_response.json()["id"]
            
            # Step 2: Select multiple procedures
            procedures_response = await async_client.get(
                "/api/procedures",
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert procedures_response.status_code == 200
            procedures = procedures_response.json()
            assert len(procedures) >= 2
            
            # Select at least 2 procedures for comparison
            selected_procedures = procedures[:2]
            procedure_ids = [p["id"] for p in selected_procedures]
            
            # Step 3: Generate comparison
            comparison_request = {
                "image_id": image_id,
                "procedure_ids": procedure_ids,
                "patient_id": test_patient_profile["id"]
            }
            
            comparison_response = await async_client.post(
                "/api/visualizations/compare",
                json=comparison_request,
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert comparison_response.status_code == 200
            comparison_data = comparison_response.json()
            
            # Verify comparison source consistency (Property 13)
            assert "visualizations" in comparison_data
            visualizations = comparison_data["visualizations"]
            assert len(visualizations) == len(procedure_ids)
            
            # All visualizations should use the same source image
            source_images = set(v["before_image_url"] for v in visualizations)
            assert len(source_images) == 1
            
            # Verify comparison data completeness (Property 14)
            assert "cost_comparison" in comparison_data
            assert "recovery_comparison" in comparison_data
            assert "risk_comparison" in comparison_data
            
            comparison_id = comparison_data["id"]
            
            # Step 4: Save the comparison (verify persistence)
            # Retrieve the saved comparison
            get_comparison_response = await async_client.get(
                f"/api/comparisons/{comparison_id}",
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert get_comparison_response.status_code == 200
            retrieved_comparison = get_comparison_response.json()
            
            # Verify comparison persistence (Property 15)
            assert retrieved_comparison["id"] == comparison_id
            assert len(retrieved_comparison["visualizations"]) == len(procedure_ids)
        finally:
            app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
class TestInsuranceClaimWorkflow:
    """Test insurance claim workflow: generate → download"""
    
    async def test_complete_insurance_claim_workflow(
        self,
        async_client: AsyncClient,
        test_user_token: str,
        test_patient_profile: dict
    ):
        """
        Test the complete insurance claim workflow.
        Requirements: 7.1
        """
        # Override auth dependency
        from app.api.dependencies import get_current_active_user
        from app.db.models import User
        from app.main import app
        
        def mock_user():
            return User(id="test_user_id", email="test@example.com", hashed_password="fake")
        
        app.dependency_overrides[get_current_active_user] = mock_user
        
        try:
            # Step 1: Get a procedure
            procedures_response = await async_client.get(
                "/api/procedures",
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert procedures_response.status_code == 200
            procedures_data = procedures_response.json()
            # Handle both list and dict responses
            procedures = procedures_data if isinstance(procedures_data, list) else procedures_data.get("procedures", [])
            assert len(procedures) > 0
            selected_procedure = procedures[0]
            
            # Step 2: Generate cost estimate (needed for claim)
            cost_request = {
                "procedure_id": selected_procedure["id"],
                "patient_id": test_patient_profile["id"]
            }
            
            cost_response = await async_client.post(
                "/api/costs/estimate",
                json=cost_request,
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert cost_response.status_code == 200
            cost_data = cost_response.json()
            
            # Step 3: Generate insurance claim
            claim_request = {
                "procedure_id": selected_procedure["id"],
                "patient_id": test_patient_profile["id"],
                "cost_breakdown_id": cost_data["id"]
            }
            
            claim_response = await async_client.post(
                "/api/insurance/claims",
                json=claim_request,
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert claim_response.status_code == 200
            claim_data = claim_response.json()
            
            # Verify claim documentation completeness (Property 23)
            assert "cpt_codes" in claim_data
            assert "medical_justification" in claim_data
            assert "cost_breakdown" in claim_data or "cost_breakdown_id" in claim_data
            
            # Verify claim information completeness (Property 25)
            assert "patient_info" in claim_data or "patient_id" in claim_data
            assert "provider_info" in claim_data or "procedure_id" in claim_data
            
            claim_id = claim_data["id"]
            
            # Step 4: Download PDF
            pdf_response = await async_client.get(
                f"/api/insurance/claims/{claim_id}/pdf",
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert pdf_response.status_code == 200
            assert pdf_response.headers["content-type"] == "application/pdf"
            
            # Verify dual format output (Property 24)
            # The claim_data itself is JSON format
            assert isinstance(claim_data, dict)
            # PDF was successfully downloaded
            assert len(pdf_response.content) > 0
        finally:
            app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.integration
class TestCrossWorkflowIntegration:
    """Test integration across multiple workflows"""
    
    async def test_full_patient_journey(
        self,
        async_client: AsyncClient,
        test_user_token: str
    ):
        """
        Test a complete patient journey through the system.
        This simulates a real user going through all major features.
        """
        # Override auth dependency
        from app.api.dependencies import get_current_active_user
        from app.db.models import User
        from app.main import app
        
        def mock_user():
            return User(id="test_user_id", email="test@example.com", hashed_password="fake")
        
        app.dependency_overrides[get_current_active_user] = mock_user
        
        try:
            # 1. Create patient profile
            profile_data = {
                "name": "Integration Test Patient",
                "date_of_birth": "1990-01-01",
                "insurance_provider": "Blue Cross Blue Shield",
                "policy_number": "BC123456789",
                "location": {
                    "zip_code": "94102",
                    "city": "San Francisco",
                    "state": "CA"
                }
            }
            
            profile_response = await async_client.post(
                "/api/profiles",
                json=profile_data,
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert profile_response.status_code == 201
            profile = profile_response.json()
            patient_id = profile["id"]
            
            # 2. Upload image
            img = Image.new('RGB', (800, 600), color='white')
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            
            upload_response = await async_client.post(
                "/api/images/upload",
                files={"image": ("patient_photo.jpg", img_bytes, "image/jpeg")},
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert upload_response.status_code == 200
            image_id = upload_response.json()["id"]
            
            # 3. Browse procedures
            procedures_response = await async_client.get(
                "/api/procedures",
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert procedures_response.status_code == 200
            procedures = procedures_response.json()
            
            # 4. Generate visualization for first procedure
            viz_response = await async_client.post(
                "/api/visualizations",
                json={
                    "image_id": image_id,
                    "procedure_id": procedures[0]["id"],
                    "patient_id": patient_id
                },
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert viz_response.status_code == 200
            
            # 5. Get cost estimate
            cost_response = await async_client.post(
                "/api/costs/estimate",
                json={
                    "procedure_id": procedures[0]["id"],
                    "patient_id": patient_id
                },
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert cost_response.status_code == 200
            
            # 6. Compare multiple procedures
            if len(procedures) >= 2:
                comparison_response = await async_client.post(
                    "/api/visualizations/compare",
                    json={
                        "image_id": image_id,
                        "procedure_ids": [p["id"] for p in procedures[:2]],
                        "patient_id": patient_id
                    },
                    headers={"Authorization": f"Bearer {test_user_token}"}
                )
                assert comparison_response.status_code == 200
            
            # 7. Generate insurance claim
            claim_response = await async_client.post(
                "/api/insurance/claims",
                json={
                    "procedure_id": procedures[0]["id"],
                    "patient_id": patient_id,
                    "cost_breakdown_id": cost_response.json()["id"]
                },
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert claim_response.status_code == 200
            
            # 8. Export comprehensive report
            export_response = await async_client.post(
                "/api/exports",
                json={
                    "patient_id": patient_id,
                    "format": "pdf"
                },
                headers={"Authorization": f"Bearer {test_user_token}"}
            )
            assert export_response.status_code == 200
        finally:
            app.dependency_overrides.clear()
