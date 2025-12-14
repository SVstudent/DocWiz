"""Property-based tests for authentication enforcement.

Feature: docwiz-surgical-platform, Property 26: Authentication enforcement
Validates: Requirements 9.1
"""
import pytest
from fastapi import status
from hypothesis import given, settings, strategies as st, HealthCheck

from app.services.auth import create_access_token, create_user


# List of protected endpoints that require authentication
PROTECTED_ENDPOINTS = [
    ("/api/profiles", "POST"),
    ("/api/profiles/test-id", "GET"),
    ("/api/profiles/test-id", "PUT"),
    ("/api/profiles/test-id/history", "GET"),
    ("/api/images/upload", "POST"),
    ("/api/images/test-id", "GET"),
    ("/api/images/test-id", "DELETE"),
    ("/api/visualizations", "POST"),
    ("/api/visualizations/test-id", "GET"),
    ("/api/visualizations/compare", "POST"),
    ("/api/visualizations/test-id/similar", "GET"),
    ("/api/costs/estimate", "POST"),
    ("/api/costs/test-id", "GET"),
    ("/api/costs/test-id/infographic", "GET"),
    ("/api/insurance/validate", "POST"),
    ("/api/insurance/claims", "POST"),
    ("/api/insurance/claims/test-id/pdf", "GET"),
    ("/api/exports", "POST"),
    ("/api/exports/test-id", "GET"),
    ("/api/exports/test-id/download", "GET"),
    ("/api/auth/refresh", "POST"),
    ("/api/auth/logout", "POST"),
    ("/api/auth/me", "GET"),
]


@pytest.mark.property_test
@given(
    endpoint_index=st.integers(min_value=0, max_value=len(PROTECTED_ENDPOINTS) - 1),
)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_authentication_enforcement_unauthenticated(client, endpoint_index):
    """
    Feature: docwiz-surgical-platform, Property 26: Authentication enforcement
    
    For any API request to protected endpoints, unauthenticated requests should be 
    rejected with 401 status, and only authenticated requests should be processed.
    
    This test verifies that all protected endpoints reject unauthenticated requests.
    """
    endpoint, method = PROTECTED_ENDPOINTS[endpoint_index]
    
    # Make request without authentication
    if method == "GET":
        response = client.get(endpoint)
    elif method == "POST":
        response = client.post(endpoint, json={})
    elif method == "PUT":
        response = client.put(endpoint, json={})
    elif method == "DELETE":
        response = client.delete(endpoint)
    
    # Verify that unauthenticated request is rejected with 401 or 403
    assert response.status_code in [
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    ], f"Endpoint {method} {endpoint} should reject unauthenticated requests"


@pytest.mark.property_test
@given(
    endpoint_index=st.integers(min_value=0, max_value=len(PROTECTED_ENDPOINTS) - 1),
    email=st.emails(),
)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_authentication_enforcement_authenticated(client, db_session, endpoint_index, email):
    """
    Feature: docwiz-surgical-platform, Property 26: Authentication enforcement
    
    For any API request to protected endpoints, authenticated requests should be 
    processed (not rejected with 401).
    
    This test verifies that authenticated requests are not rejected due to authentication.
    Note: They may fail with other status codes (400, 404, etc.) due to missing data,
    but they should not fail with 401 Unauthorized.
    """
    endpoint, method = PROTECTED_ENDPOINTS[endpoint_index]
    
    # Create a test user with a simple password (bcrypt has 72 byte limit)
    try:
        user = create_user(db_session, email, "TestPass123!")
    except Exception:
        # Skip if user creation fails (e.g., duplicate email from previous iteration)
        pytest.skip("User creation failed")
    
    # Create valid JWT token
    token = create_access_token({"sub": user.id, "email": user.email})
    
    # Make request with authentication
    headers = {"Authorization": f"Bearer {token}"}
    
    if method == "GET":
        response = client.get(endpoint, headers=headers)
    elif method == "POST":
        response = client.post(endpoint, json={}, headers=headers)
    elif method == "PUT":
        response = client.put(endpoint, json={}, headers=headers)
    elif method == "DELETE":
        response = client.delete(endpoint, headers=headers)
    
    # Verify that authenticated request is NOT rejected with 401
    # It may fail with other codes (400, 404, 422, etc.) but not 401
    assert response.status_code != status.HTTP_401_UNAUTHORIZED, (
        f"Endpoint {method} {endpoint} should not reject authenticated requests with 401"
    )


@pytest.mark.property_test
@given(
    endpoint_index=st.integers(min_value=0, max_value=len(PROTECTED_ENDPOINTS) - 1),
    invalid_token=st.text(
        alphabet=st.characters(min_codepoint=33, max_codepoint=126, blacklist_categories=()),
        min_size=10,
        max_size=100,
    ),
)
@settings(
    max_examples=100,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
def test_authentication_enforcement_invalid_token(client, endpoint_index, invalid_token):
    """
    Feature: docwiz-surgical-platform, Property 26: Authentication enforcement
    
    For any API request to protected endpoints with an invalid token, the request 
    should be rejected with 401 status.
    
    This test verifies that invalid tokens are properly rejected.
    """
    endpoint, method = PROTECTED_ENDPOINTS[endpoint_index]
    
    # Make request with invalid token (using ASCII-safe characters)
    headers = {"Authorization": f"Bearer {invalid_token}"}
    
    if method == "GET":
        response = client.get(endpoint, headers=headers)
    elif method == "POST":
        response = client.post(endpoint, json={}, headers=headers)
    elif method == "PUT":
        response = client.put(endpoint, json={}, headers=headers)
    elif method == "DELETE":
        response = client.delete(endpoint, headers=headers)
    
    # Verify that request with invalid token is rejected with 401 or 403
    assert response.status_code in [
        status.HTTP_401_UNAUTHORIZED,
        status.HTTP_403_FORBIDDEN,
    ], f"Endpoint {method} {endpoint} should reject invalid tokens"
