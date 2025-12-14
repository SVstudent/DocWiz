"""Property-based tests for sensitive data encryption.

Feature: docwiz-surgical-platform, Property 5: Sensitive data encryption
Validates: Requirements 2.3
"""
import pytest
from hypothesis import given, settings, strategies as st

from app.services.encryption import EncryptionService


@pytest.mark.property_test
@given(
    policy_number=st.text(min_size=1, max_size=100),
)
@settings(max_examples=100, deadline=None)
def test_policy_number_encryption_round_trip(policy_number):
    """
    Feature: docwiz-surgical-platform, Property 5: Sensitive data encryption
    
    For any patient profile save operation, all sensitive fields (policy number, 
    medical history) should be encrypted in storage such that raw values are not readable.
    
    This test verifies that policy numbers can be encrypted and decrypted correctly
    (round-trip property).
    """
    encryption_service = EncryptionService()
    
    # Encrypt the policy number
    encrypted = encryption_service.encrypt_policy_number(policy_number)
    
    # Verify encrypted value is different from original (unless empty)
    if policy_number:
        assert encrypted != policy_number, "Encrypted value should differ from plaintext"
    
    # Decrypt and verify round-trip
    decrypted = encryption_service.decrypt_policy_number(encrypted)
    assert decrypted == policy_number, "Decrypted value should match original"


@pytest.mark.property_test
@given(
    medical_history=st.text(min_size=0, max_size=1000),
)
@settings(max_examples=100, deadline=None)
def test_medical_history_encryption_round_trip(medical_history):
    """
    Feature: docwiz-surgical-platform, Property 5: Sensitive data encryption
    
    For any patient profile save operation, all sensitive fields (policy number, 
    medical history) should be encrypted in storage such that raw values are not readable.
    
    This test verifies that medical history can be encrypted and decrypted correctly
    (round-trip property).
    """
    encryption_service = EncryptionService()
    
    # Encrypt the medical history
    encrypted = encryption_service.encrypt_medical_history(medical_history)
    
    # Verify encrypted value is different from original (unless empty)
    if medical_history:
        assert encrypted != medical_history, "Encrypted value should differ from plaintext"
    
    # Decrypt and verify round-trip
    decrypted = encryption_service.decrypt_medical_history(encrypted)
    assert decrypted == medical_history, "Decrypted value should match original"


@pytest.mark.property_test
@given(
    plaintext=st.text(min_size=5, max_size=500),  # Use longer strings to avoid false positives
)
@settings(max_examples=100, deadline=None)
def test_encrypted_data_not_readable(plaintext):
    """
    Feature: docwiz-surgical-platform, Property 5: Sensitive data encryption
    
    For any patient profile save operation, all sensitive fields should be encrypted 
    in storage such that raw values are not readable.
    
    This test verifies that encrypted data does not contain the original plaintext
    as a recognizable substring (ensuring it's not readable). We use strings of length >= 5
    to avoid false positives from single characters appearing in base64 encoding.
    """
    encryption_service = EncryptionService()
    
    # Encrypt the data
    encrypted = encryption_service.encrypt(plaintext)
    
    # Verify the plaintext is not readable in the encrypted output
    # (plaintext should not appear as substring in ciphertext)
    assert plaintext not in encrypted, "Plaintext should not be readable in encrypted data"


@pytest.mark.property_test
@given(
    data1=st.text(min_size=1, max_size=100),
    data2=st.text(min_size=1, max_size=100),
)
@settings(max_examples=100, deadline=None)
def test_different_plaintexts_produce_different_ciphertexts(data1, data2):
    """
    Feature: docwiz-surgical-platform, Property 5: Sensitive data encryption
    
    For any two different sensitive data values, their encrypted forms should be different.
    This ensures the encryption is working properly and not producing collisions.
    """
    # Skip if data is the same
    if data1 == data2:
        return
    
    encryption_service = EncryptionService()
    
    # Encrypt both values
    encrypted1 = encryption_service.encrypt(data1)
    encrypted2 = encryption_service.encrypt(data2)
    
    # Verify different plaintexts produce different ciphertexts
    assert encrypted1 != encrypted2, "Different plaintexts should produce different ciphertexts"
