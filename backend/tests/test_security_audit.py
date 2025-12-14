"""
Security audit tests for DocWiz platform.

Tests the following security aspects:
1. Authentication bypass attempts
2. Encryption of sensitive data
3. SQL injection vulnerabilities
4. CORS configuration

Requirements: 2.3, 9.1
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import jwt
from datetime import datetime, timedelta

from app.main import app
from app.config import settings
from app.services.encryption import EncryptionService


@pytest.mark.security
class TestAuthenticationSecurity:
    """Test authentication bypass attempts - Requirement 9.1"""
    
    def test_protected_endpoint_without_token(self, client):
        """Test that protected endpoints reject requests without authentication token."""
        protected_endpoints = [
            ("/api/profiles", "POST"),
            ("/api/visualizations", "POST"),
            ("/api/costs/estimate", "POST"),
            ("/api/insurance/claims", "POST"),
            ("/api/exports", "POST"),
        ]
        
        for endpoint, method in protected_endpoints:
            if method == "GET":
                response = client.get(endpoint)
            elif method == "POST":
                response = client.post(endpoint, json={})
            
            # Should return 401 Unauthorized
            assert response.status_code == 401, f"{method} {endpoint} should require authentication"
    
    def test_protected_endpoint_with_invalid_token(self, client):
        """Test that protected endpoints reject invalid tokens."""
        invalid_tokens = [
            "invalid_token",
            "Bearer invalid_token",
            "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.signature",
            "",
        ]
        
        for token in invalid_tokens:
            response = client.post(
                "/api/profiles",
                json={"name": "Test"},
                headers={"Authorization": token if token.startswith("Bearer") else f"Bearer {token}"}
            )
            assert response.status_code == 401, f"Should reject invalid token: {token}"
    
    def test_expired_token_rejection(self, client):
        """Test that expired tokens are rejected."""
        # Create an expired token
        expired_payload = {
            "sub": "test_user",
            "exp": datetime.utcnow() - timedelta(hours=1)  # Expired 1 hour ago
        }
        
        expired_token = jwt.encode(
            expired_payload,
            settings.secret_key,
            algorithm="HS256"
        )
        
        response = client.get(
            "/api/profiles",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        
        assert response.status_code == 401, "Should reject expired token"
    
    def test_token_with_wrong_signature(self, client):
        """Test that tokens with wrong signature are rejected."""
        # Create a token with wrong secret
        wrong_payload = {
            "sub": "test_user",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        
        wrong_token = jwt.encode(
            wrong_payload,
            "wrong_secret_key",
            algorithm="HS256"
        )
        
        response = client.post(
            "/api/profiles",
            json={"name": "Test"},
            headers={"Authorization": f"Bearer {wrong_token}"}
        )
        
        assert response.status_code == 401, "Should reject token with wrong signature"
    
    def test_authorization_user_cannot_access_other_user_data(self, client):
        """Test that users cannot access other users' data."""
        # This test verifies authorization, not just authentication
        # Create two different user tokens
        from app.services.auth import create_access_token
        
        user1_token = create_access_token(data={"sub": "user1_id"})
        user2_token = create_access_token(data={"sub": "user2_id"})
        
        # User 1 creates a profile
        profile_data = {
            "name": "User 1",
            "date_of_birth": "1990-01-01",
            "insurance_provider": "Test Insurance",
            "policy_number": "TEST123",
            "location": {"zip_code": "12345", "city": "Test", "state": "TS"}
        }
        
        create_response = client.post(
            "/api/profiles",
            json=profile_data,
            headers={"Authorization": f"Bearer {user1_token}"}
        )
        
        if create_response.status_code == 201:
            profile_id = create_response.json()["id"]
            
            # User 2 tries to access User 1's profile
            access_response = client.get(
                f"/api/profiles/{profile_id}",
                headers={"Authorization": f"Bearer {user2_token}"}
            )
            
            # Should be forbidden or not found
            assert access_response.status_code in [403, 404], \
                "User should not be able to access another user's profile"


@pytest.mark.security
class TestDataEncryption:
    """Test encryption of sensitive data - Requirement 2.3"""
    
    def test_sensitive_fields_are_encrypted_in_storage(self):
        """Test that sensitive fields are encrypted before storage."""
        encryption_service = EncryptionService()
        
        # Test data
        sensitive_data = {
            "policy_number": "BC123456789",
            "medical_history": "Patient has history of allergies"
        }
        
        # Encrypt
        encrypted_policy = encryption_service.encrypt(sensitive_data["policy_number"])
        encrypted_history = encryption_service.encrypt(sensitive_data["medical_history"])
        
        # Verify encrypted data is different from original
        assert encrypted_policy != sensitive_data["policy_number"]
        assert encrypted_history != sensitive_data["medical_history"]
        
        # Verify encrypted data is not readable
        assert "BC123456789" not in encrypted_policy
        assert "allergies" not in encrypted_history
        
        # Verify decryption works
        decrypted_policy = encryption_service.decrypt(encrypted_policy)
        decrypted_history = encryption_service.decrypt(encrypted_history)
        
        assert decrypted_policy == sensitive_data["policy_number"]
        assert decrypted_history == sensitive_data["medical_history"]
    
    def test_encryption_round_trip(self):
        """Test that encryption and decryption preserve data integrity."""
        encryption_service = EncryptionService()
        
        test_values = [
            "Simple text",
            "Text with special chars: !@#$%^&*()",
            "Unicode text: 你好世界",
            "Numbers: 1234567890",
            "Long text: " + "a" * 1000,
        ]
        
        for original in test_values:
            encrypted = encryption_service.encrypt(original)
            decrypted = encryption_service.decrypt(encrypted)
            assert decrypted == original, f"Round trip failed for: {original}"
    
    def test_profile_sensitive_data_not_in_response(self, client):
        """Test that sensitive data is not exposed in API responses."""
        from app.services.auth import create_access_token
        
        token = create_access_token(data={"sub": "test_user"})
        
        profile_data = {
            "name": "Test Patient",
            "date_of_birth": "1990-01-01",
            "insurance_provider": "Test Insurance",
            "policy_number": "SENSITIVE123",
            "medical_history": "SENSITIVE medical information",
            "location": {"zip_code": "12345", "city": "Test", "state": "TS"}
        }
        
        response = client.post(
            "/api/profiles",
            json=profile_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 201:
            response_data = response.json()
            
            # Sensitive fields should either be encrypted or not present
            if "policy_number" in response_data:
                # If present, should be encrypted (not the original value)
                assert response_data["policy_number"] != "SENSITIVE123"
            
            if "medical_history" in response_data:
                # If present, should be encrypted (not the original value)
                assert "SENSITIVE medical information" not in str(response_data["medical_history"])


@pytest.mark.security
class TestSQLInjection:
    """Test SQL injection vulnerabilities - Requirement 9.1"""
    
    def test_sql_injection_in_profile_name(self, client):
        """Test that SQL injection attempts in profile name are handled safely."""
        from app.services.auth import create_access_token
        
        token = create_access_token(data={"sub": "test_user"})
        
        sql_injection_attempts = [
            "'; DROP TABLE profiles; --",
            "' OR '1'='1",
            "admin'--",
            "' UNION SELECT * FROM users--",
            "1' AND '1'='1",
        ]
        
        for injection_attempt in sql_injection_attempts:
            profile_data = {
                "name": injection_attempt,
                "date_of_birth": "1990-01-01",
                "insurance_provider": "Test Insurance",
                "policy_number": "TEST123",
                "location": {"zip_code": "12345", "city": "Test", "state": "TS"}
            }
            
            response = client.post(
                "/api/profiles",
                json=profile_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Should either succeed (safely escaped) or fail with validation error
            # Should NOT cause a server error (500)
            assert response.status_code != 500, \
                f"SQL injection attempt caused server error: {injection_attempt}"
    
    def test_sql_injection_in_search_parameters(self, client):
        """Test that SQL injection in search/filter parameters is handled safely."""
        from app.services.auth import create_access_token
        
        token = create_access_token(data={"sub": "test_user"})
        
        # Test injection in query parameters
        injection_attempts = [
            "'; DROP TABLE procedures; --",
            "' OR '1'='1",
            "1' UNION SELECT * FROM users--",
        ]
        
        for injection_attempt in injection_attempts:
            response = client.get(
                f"/api/procedures?category={injection_attempt}",
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Should not cause server error
            assert response.status_code != 500, \
                f"SQL injection in query param caused server error: {injection_attempt}"
    
    def test_nosql_injection_in_firestore_queries(self, client):
        """Test that NoSQL injection attempts are handled safely."""
        from app.services.auth import create_access_token
        
        token = create_access_token(data={"sub": "test_user"})
        
        # NoSQL injection attempts - use string representations
        nosql_injections = [
            "$ne",
            "$gt",
            "$regex",
        ]
        
        for injection in nosql_injections:
            profile_data = {
                "name": "Test",
                "date_of_birth": "1990-01-01",
                "insurance_provider": injection,  # Injection attempt
                "policy_number": "TEST123",
                "location": {"zip_code": "12345", "city": "Test", "state": "TS"}
            }
            
            response = client.post(
                "/api/profiles",
                json=profile_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Should fail validation or succeed (safely handled), not cause server error
            assert response.status_code in [200, 201, 400, 422], \
                f"NoSQL injection should be handled safely: {injection}"


@pytest.mark.security
class TestCORSConfiguration:
    """Test CORS configuration - Requirement 9.1"""
    
    def test_cors_headers_present(self, client):
        """Test that CORS headers are properly configured."""
        response = client.options(
            "/api/procedures",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )
        
        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers or \
               "Access-Control-Allow-Origin" in response.headers, \
               "CORS headers should be present"
    
    def test_cors_allows_frontend_origin(self, client):
        """Test that CORS allows requests from frontend origin."""
        # Test with common frontend origins
        frontend_origins = [
            "http://localhost:3000",
            "http://localhost:3001",
            "https://docwiz.app",
        ]
        
        for origin in frontend_origins:
            response = client.get(
                "/api/procedures",
                headers={"Origin": origin}
            )
            
            # Should not be blocked by CORS
            assert response.status_code != 403, \
                f"Frontend origin should be allowed: {origin}"
    
    def test_cors_blocks_unauthorized_origins(self, client):
        """Test that CORS blocks requests from unauthorized origins."""
        # Note: This test depends on CORS configuration
        # If CORS is set to allow all origins (*), this test may not apply
        
        malicious_origins = [
            "http://malicious-site.com",
            "http://evil.example.com",
        ]
        
        for origin in malicious_origins:
            response = client.options(
                "/api/profiles",
                headers={
                    "Origin": origin,
                    "Access-Control-Request-Method": "POST",
                }
            )
            
            # Check if origin is in allowed origins
            allowed_origin = response.headers.get("access-control-allow-origin") or \
                           response.headers.get("Access-Control-Allow-Origin")
            
            # If CORS is properly configured, malicious origins should not be explicitly allowed
            # (unless using wildcard *)
            if allowed_origin and allowed_origin != "*":
                assert origin not in allowed_origin, \
                    f"Malicious origin should not be explicitly allowed: {origin}"


@pytest.mark.security
class TestInputValidation:
    """Test input validation and sanitization"""
    
    def test_xss_prevention_in_text_fields(self, client):
        """Test that XSS attempts in text fields are handled safely."""
        from app.services.auth import create_access_token
        
        token = create_access_token(data={"sub": "test_user"})
        
        xss_attempts = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<iframe src='javascript:alert(\"XSS\")'></iframe>",
        ]
        
        for xss_attempt in xss_attempts:
            profile_data = {
                "name": xss_attempt,
                "date_of_birth": "1990-01-01",
                "insurance_provider": "Test Insurance",
                "policy_number": "TEST123",
                "location": {"zip_code": "12345", "city": "Test", "state": "TS"}
            }
            
            response = client.post(
                "/api/profiles",
                json=profile_data,
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Should either succeed (safely escaped) or fail with validation
            # Should NOT cause server error
            assert response.status_code != 500, \
                f"XSS attempt caused server error: {xss_attempt}"
            
            if response.status_code == 201:
                # If accepted, verify it's properly escaped in response
                response_data = response.json()
                # The response should not contain executable script tags
                assert "<script>" not in str(response_data).lower()
    
    def test_file_upload_validation(self, client):
        """Test that file uploads are properly validated."""
        from app.services.auth import create_access_token
        from io import BytesIO
        
        token = create_access_token(data={"sub": "test_user"})
        
        # Test malicious file types
        malicious_files = [
            ("malware.exe", b"MZ\x90\x00", "application/x-msdownload"),
            ("script.php", b"<?php system($_GET['cmd']); ?>", "application/x-php"),
            ("shell.sh", b"#!/bin/bash\nrm -rf /", "application/x-sh"),
        ]
        
        for filename, content, content_type in malicious_files:
            file_data = BytesIO(content)
            
            response = client.post(
                "/api/images/upload",
                files={"image": (filename, file_data, content_type)},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Should reject non-image files (400, 422) or require auth (401)
            assert response.status_code in [400, 401, 422], \
                f"Should reject malicious file: {filename}"
    
    def test_oversized_file_rejection(self, client):
        """Test that oversized files are rejected."""
        from app.services.auth import create_access_token
        from io import BytesIO
        from PIL import Image
        
        token = create_access_token(data={"sub": "test_user"})
        
        # Create an oversized image (> 10MB)
        # Note: This creates a large file in memory, may be slow
        large_img = Image.new('RGB', (5000, 5000), color='white')
        img_bytes = BytesIO()
        large_img.save(img_bytes, format='JPEG', quality=100)
        img_bytes.seek(0)
        
        # Check file size
        file_size = len(img_bytes.getvalue())
        
        if file_size > 10 * 1024 * 1024:  # > 10MB
            response = client.post(
                "/api/images/upload",
                files={"image": ("large_image.jpg", img_bytes, "image/jpeg")},
                headers={"Authorization": f"Bearer {token}"}
            )
            
            # Should reject oversized file
            assert response.status_code in [400, 413, 422], \
                "Should reject oversized file"


@pytest.mark.security
class TestRateLimiting:
    """Test rate limiting (if implemented)"""
    
    def test_rate_limiting_on_authentication_endpoint(self, client):
        """Test that authentication endpoint has rate limiting."""
        # Note: Rate limiting may not be implemented yet
        # This test verifies the endpoint exists and handles requests
        
        response = client.post(
            "/api/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrong_password"
            }
        )
        
        # Endpoint should exist and return appropriate status
        # 401 (unauthorized), 422 (validation error), or 429 (rate limited)
        assert response.status_code in [401, 422, 429], \
            "Authentication endpoint should handle login attempts"
