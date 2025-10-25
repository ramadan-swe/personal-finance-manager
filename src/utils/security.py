# src/utils/security.py
import hashlib
import secrets

# Security constants
PBKDF2_ITERATIONS = 100000

def generate_salt(length=16):
    return secrets.token_bytes(length)

def hash_pin(pin, salt):
    # Using PBKDF2 as a strong hashing algorithm
    # It's important to use a sufficient number of iterations
    iterations = PBKDF2_ITERATIONS
    hashed_pin = hashlib.pbkdf2_hmac(
        'sha256',  # The hash algorithm to use
        pin.encode('utf-8'),  # Convert the PIN to bytes
        salt,  # Provide the salt
        iterations  # It's recommended to use at least 100,000 iterations
    )
    return hashed_pin.hex()

def verify_pin(pin, hashed_pin, salt):
    return hash_pin(pin, salt) == hashed_pin
