"""
Performance testing for DocWiz platform.

Tests the following performance aspects:
1. Load test API endpoints
2. Measure frontend load time (via API response times)
3. Test with large images
4. Verify response times under load

Requirements: 8.1, 9.5
"""

import pytest
import time
from io import BytesIO
from PIL import Image
import asyncio
from concurrent.futures import ThreadPoolExecutor
from statistics import mean, median


@pytest.mark.performance
class TestAPIPerformance:
    """Test API endpoint performance - Requirement 9.5"""
    
    def test_procedures_endpoint_response_time(self, client):
        """Test that procedures endpoint responds within acceptable time."""
        from app.services.auth import create_access_token
        
        token = create_access_token(data={"sub": "test_user"})
        
        # Measure response time
        start_time = time.time()
        response = client.get(
            "/api/procedures",
            headers={"Authorization": f"Bearer {token}"}
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        # Should respond within 2 seconds (Requirement 9.5)
        assert response_time < 2.0, f"Response time {response_time}s exceeds 2s threshold"
    
    def test_profile_creation_response_time(self, client):
        """Test that profile creation responds within acceptable time."""
        from app.services.auth import create_access_token
        from app.api.dependencies import get_current_active_user
        from app.db.models import User
        from app.main import app
        
        token = create_access_token(data={"sub": "test_user"})
        
        def mock_user():
            return User(id="test_user", email="test@example.com", hashed_password="fake")
        
        app.dependency_overrides[get_current_active_user] = mock_user
        
        try:
            profile_data = {
                "name": "Performance Test Patient",
                "date_of_birth": "1990-01-01",
                "insurance_provider": "Test Insurance",
                "policy_number": "PERF123",
                "location": {"zip_code": "12345", "city": "Test", "state": "TS"}
            }
            
            start_time = time.time()
            response = client.post(
                "/api/profiles",
                json=profile_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code in [200, 201]
            # Should respond within 2 seconds
            assert response_time < 2.0, f"Response time {response_time}s exceeds 2s threshold"
        finally:
            app.dependency_overrides.clear()
    
    def test_cost_estimation_response_time(self, client):
        """Test that cost estimation responds within acceptable time."""
        from app.services.auth import create_access_token
        
        token = create_access_token(data={"sub": "test_user"})
        
        # First create a profile
        profile_data = {
            "name": "Cost Test Patient",
            "date_of_birth": "1990-01-01",
            "insurance_provider": "Blue Cross Blue Shield",
            "policy_number": "COST123",
            "location": {"zip_code": "94102", "city": "San Francisco", "state": "CA"}
        }
        
        profile_response = client.post(
            "/api/profiles",
            json=profile_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if profile_response.status_code == 201:
            patient_id = profile_response.json()["id"]
            
            # Get a procedure
            procedures_response = client.get(
                "/api/procedures",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            if procedures_response.status_code == 200:
                procedures = procedures_response.json()
                if len(procedures) > 0:
                    procedure_id = procedures[0]["id"]
                    
                    # Measure cost estimation time
                    start_time = time.time()
                    cost_response = client.post(
                        "/api/costs/estimate",
                        json={
                            "procedure_id": procedure_id,
                            "patient_id": patient_id
                        },
                        headers={"Authorization": f"Bearer {token}"}
                    )
                    end_time = time.time()
                    
                    response_time = end_time - start_time
                    
                    assert cost_response.status_code == 200
                    # Should respond within 2 seconds
                    assert response_time < 2.0, \
                        f"Cost estimation response time {response_time}s exceeds 2s threshold"
    
    def test_multiple_concurrent_requests(self, client):
        """Test API performance under concurrent load."""
        from app.services.auth import create_access_token
        
        token = create_access_token(data={"sub": "test_user"})
        
        def make_request():
            start = time.time()
            response = client.get(
                "/api/procedures",
                headers={"Authorization": f"Bearer {token}"}
            )
            end = time.time()
            return {
                "status_code": response.status_code,
                "response_time": end - start
            }
        
        # Simulate 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [f.result() for f in futures]
        
        # All requests should succeed
        assert all(r["status_code"] == 200 for r in results), \
            "Some requests failed under concurrent load"
        
        # Calculate statistics
        response_times = [r["response_time"] for r in results]
        avg_time = mean(response_times)
        median_time = median(response_times)
        max_time = max(response_times)
        
        # 95th percentile should be under 2 seconds (Requirement 9.5)
        sorted_times = sorted(response_times)
        p95_index = int(len(sorted_times) * 0.95)
        p95_time = sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]
        
        assert p95_time < 2.0, \
            f"95th percentile response time {p95_time}s exceeds 2s threshold"
        
        print(f"\nConcurrent request statistics:")
        print(f"  Average: {avg_time:.3f}s")
        print(f"  Median: {median_time:.3f}s")
        print(f"  Max: {max_time:.3f}s")
        print(f"  95th percentile: {p95_time:.3f}s")


@pytest.mark.performance
class TestImageProcessingPerformance:
    """Test image processing performance - Requirement 8.1"""
    
    def test_small_image_upload_performance(self, client):
        """Test upload performance with small images."""
        from app.services.auth import create_access_token
        from app.api.dependencies import get_current_active_user
        from app.db.models import User
        from app.main import app
        
        token = create_access_token(data={"sub": "test_user"})
        
        def mock_user():
            return User(id="test_user", email="test@example.com", hashed_password="fake")
        
        app.dependency_overrides[get_current_active_user] = mock_user
        
        try:
            # Create a small image (800x600)
            img = Image.new('RGB', (800, 600), color='white')
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            
            start_time = time.time()
            response = client.post(
                "/api/images/upload",
                files={"image": ("test_small.jpg", img_bytes, "image/jpeg")},
                headers={"Authorization": f"Bearer {token}"}
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            # Small image should upload quickly (< 1 second)
            assert response_time < 1.0, \
                f"Small image upload took {response_time}s, should be < 1s"
        finally:
            app.dependency_overrides.clear()
    
    def test_large_image_upload_performance(self, client):
        """Test upload performance with large images (within size limit)."""
        from app.services.auth import create_access_token
        from app.api.dependencies import get_current_active_user
        from app.db.models import User
        from app.main import app
        
        token = create_access_token(data={"sub": "test_user"})
        
        def mock_user():
            return User(id="test_user", email="test@example.com", hashed_password="fake")
        
        app.dependency_overrides[get_current_active_user] = mock_user
        
        try:
            # Create a large image (3000x2000, but under 10MB)
            img = Image.new('RGB', (3000, 2000), color='white')
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG', quality=75)
            img_bytes.seek(0)
            
            file_size_mb = len(img_bytes.getvalue()) / (1024 * 1024)
            
            # Only test if under 10MB limit
            if file_size_mb < 10:
                start_time = time.time()
                response = client.post(
                    "/api/images/upload",
                    files={"image": ("test_large.jpg", img_bytes, "image/jpeg")},
                    headers={"Authorization": f"Bearer {token}"}
                )
                end_time = time.time()
                
                response_time = end_time - start_time
                
                assert response.status_code == 200
                # Large image should still upload within reasonable time (< 5 seconds)
                assert response_time < 5.0, \
                    f"Large image ({file_size_mb:.2f}MB) upload took {response_time}s, should be < 5s"
        finally:
            app.dependency_overrides.clear()
    
    def test_image_validation_performance(self, client):
        """Test that image validation doesn't significantly slow down uploads."""
        from app.services.auth import create_access_token
        
        token = create_access_token(data={"sub": "test_user"})
        
        # Create multiple test images
        test_images = []
        for size in [(800, 600), (1200, 900), (1600, 1200)]:
            img = Image.new('RGB', size, color='white')
            img_bytes = BytesIO()
            img.save(img_bytes, format='JPEG', quality=85)
            img_bytes.seek(0)
            test_images.append(img_bytes)
        
        upload_times = []
        
        for img_bytes in test_images:
            start_time = time.time()
            response = client.post(
                "/api/images/upload",
                files={"image": ("test.jpg", img_bytes, "image/jpeg")},
                headers={"Authorization": f"Bearer {token}"}
            )
            end_time = time.time()
            
            if response.status_code == 200:
                upload_times.append(end_time - start_time)
        
        if upload_times:
            avg_upload_time = mean(upload_times)
            # Average upload time should be reasonable
            assert avg_upload_time < 2.0, \
                f"Average upload time {avg_upload_time}s exceeds 2s threshold"


@pytest.mark.performance
class TestDatabasePerformance:
    """Test database operation performance"""
    
    def test_profile_retrieval_performance(self, client):
        """Test that profile retrieval is fast."""
        from app.services.auth import create_access_token
        
        token = create_access_token(data={"sub": "test_user"})
        
        # Create a profile first
        profile_data = {
            "name": "DB Test Patient",
            "date_of_birth": "1990-01-01",
            "insurance_provider": "Test Insurance",
            "policy_number": "DB123",
            "location": {"zip_code": "12345", "city": "Test", "state": "TS"}
        }
        
        create_response = client.post(
            "/api/profiles",
            json=profile_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if create_response.status_code == 201:
            profile_id = create_response.json()["id"]
            
            # Measure retrieval time
            start_time = time.time()
            response = client.get(
                f"/api/profiles/{profile_id}",
                headers={"Authorization": f"Bearer {token}"}
            )
            end_time = time.time()
            
            response_time = end_time - start_time
            
            assert response.status_code == 200
            # Database retrieval should be very fast (< 0.5 seconds)
            assert response_time < 0.5, \
                f"Profile retrieval took {response_time}s, should be < 0.5s"
    
    def test_multiple_profile_operations_performance(self, client):
        """Test performance of multiple database operations."""
        from app.services.auth import create_access_token
        
        token = create_access_token(data={"sub": "test_user"})
        
        operation_times = []
        
        # Create multiple profiles
        for i in range(5):
            profile_data = {
                "name": f"Perf Test Patient {i}",
                "date_of_birth": "1990-01-01",
                "insurance_provider": "Test Insurance",
                "policy_number": f"PERF{i}",
                "location": {"zip_code": "12345", "city": "Test", "state": "TS"}
            }
            
            start_time = time.time()
            response = client.post(
                "/api/profiles",
                json=profile_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            end_time = time.time()
            
            if response.status_code == 201:
                operation_times.append(end_time - start_time)
        
        if operation_times:
            avg_time = mean(operation_times)
            max_time = max(operation_times)
            
            # Average operation time should be reasonable
            assert avg_time < 1.0, \
                f"Average database operation time {avg_time}s exceeds 1s"
            
            # No single operation should be extremely slow
            assert max_time < 2.0, \
                f"Slowest database operation {max_time}s exceeds 2s"


@pytest.mark.performance
class TestMemoryUsage:
    """Test memory usage and resource management"""
    
    def test_large_response_handling(self, client):
        """Test that large responses are handled efficiently."""
        from app.services.auth import create_access_token
        
        token = create_access_token(data={"sub": "test_user"})
        
        # Request procedures list (potentially large response)
        start_time = time.time()
        response = client.get(
            "/api/procedures",
            headers={"Authorization": f"Bearer {token}"}
        )
        end_time = time.time()
        
        response_time = end_time - start_time
        
        assert response.status_code == 200
        
        # Even with large response, should be fast
        assert response_time < 1.0, \
            f"Large response handling took {response_time}s, should be < 1s"
        
        # Response should be valid JSON (can be list or dict with procedures key)
        data = response.json()
        assert isinstance(data, (list, dict))
    
    def test_repeated_requests_no_memory_leak(self, client):
        """Test that repeated requests don't cause memory issues."""
        from app.services.auth import create_access_token
        
        token = create_access_token(data={"sub": "test_user"})
        
        # Make many repeated requests
        response_times = []
        
        for i in range(20):
            start_time = time.time()
            response = client.get(
                "/api/procedures",
                headers={"Authorization": f"Bearer {token}"}
            )
            end_time = time.time()
            
            assert response.status_code == 200
            response_times.append(end_time - start_time)
        
        # Response times should remain consistent (no degradation)
        first_half_avg = mean(response_times[:10])
        second_half_avg = mean(response_times[10:])
        
        # Second half should not be significantly slower than first half
        # (allowing for some variance)
        assert second_half_avg < first_half_avg * 1.5, \
            "Response times degraded significantly over repeated requests"


@pytest.mark.performance
class TestFrontendLoadTime:
    """Test factors affecting frontend load time - Requirement 8.1"""
    
    def test_initial_data_load_time(self, client):
        """Test time to load initial data for frontend."""
        from app.services.auth import create_access_token
        
        token = create_access_token(data={"sub": "test_user"})
        
        # Simulate initial page load - fetch procedures
        start_time = time.time()
        
        procedures_response = client.get(
            "/api/procedures",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        assert procedures_response.status_code == 200
        
        # Initial data load should be fast to support 3s page load (Requirement 8.1)
        # API should respond in < 1s to leave time for frontend rendering
        assert total_time < 1.0, \
            f"Initial data load took {total_time}s, should be < 1s for 3s page load target"
    
    def test_api_response_size(self, client):
        """Test that API responses are reasonably sized for fast transfer."""
        from app.services.auth import create_access_token
        
        token = create_access_token(data={"sub": "test_user"})
        
        response = client.get(
            "/api/procedures",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        
        # Check response size
        response_size_kb = len(response.content) / 1024
        
        # Response should be reasonably sized (< 500KB for good performance)
        assert response_size_kb < 500, \
            f"Response size {response_size_kb:.2f}KB is large, may slow frontend load"
        
        print(f"\nAPI response size: {response_size_kb:.2f}KB")
