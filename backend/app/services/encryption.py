"""Encryption service for sensitive data."""
from cryptography.fernet import Fernet

from app.config import settings


class EncryptionService:
    """Service for encrypting and decrypting sensitive data."""

    def __init__(self):
        """Initialize encryption service with key from settings."""
        # Ensure the key is properly formatted (32 url-safe base64-encoded bytes)
        key = settings.encryption_key.encode()
        
        # If the key is not the right length, derive it properly
        if len(key) != 44:  # Fernet keys are 44 bytes when base64 encoded
            # For development, we'll pad/truncate to 32 bytes then encode
            key = key[:32].ljust(32, b'0')
            from base64 import urlsafe_b64encode
            key = urlsafe_b64encode(key)
        
        self.cipher = Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.
        
        Args:
            plaintext: The string to encrypt
            
        Returns:
            The encrypted string (base64 encoded)
        """
        if not plaintext:
            return ""
        
        encrypted_bytes = self.cipher.encrypt(plaintext.encode())
        return encrypted_bytes.decode()

    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a ciphertext string.
        
        Args:
            ciphertext: The encrypted string (base64 encoded)
            
        Returns:
            The decrypted plaintext string
        """
        if not ciphertext:
            return ""
        
        decrypted_bytes = self.cipher.decrypt(ciphertext.encode())
        return decrypted_bytes.decode()

    def encrypt_policy_number(self, policy_number: str) -> str:
        """
        Encrypt an insurance policy number.
        
        Args:
            policy_number: The policy number to encrypt
            
        Returns:
            The encrypted policy number
        """
        return self.encrypt(policy_number)

    def decrypt_policy_number(self, encrypted_policy_number: str) -> str:
        """
        Decrypt an insurance policy number.
        
        Args:
            encrypted_policy_number: The encrypted policy number
            
        Returns:
            The decrypted policy number
        """
        return self.decrypt(encrypted_policy_number)

    def encrypt_medical_history(self, medical_history: str) -> str:
        """
        Encrypt medical history text.
        
        Args:
            medical_history: The medical history to encrypt
            
        Returns:
            The encrypted medical history
        """
        return self.encrypt(medical_history)

    def decrypt_medical_history(self, encrypted_medical_history: str) -> str:
        """
        Decrypt medical history text.
        
        Args:
            encrypted_medical_history: The encrypted medical history
            
        Returns:
            The decrypted medical history
        """
        return self.decrypt(encrypted_medical_history)


# Global encryption service instance
encryption_service = EncryptionService()
