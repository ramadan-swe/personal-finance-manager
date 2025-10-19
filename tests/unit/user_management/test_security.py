# tests/unit/user_management/test_security.py
import pytest
from src.utils.security import generate_salt, hash_pin, verify_pin

def test_generate_salt():
    salt1 = generate_salt()
    salt2 = generate_salt()
    assert isinstance(salt1, bytes)
    assert len(salt1) == 16  # Default length
    assert salt1 != salt2  # Salts should be random

def test_hash_pin():
    pin = "1234"
    salt = generate_salt()
    hashed_pin = hash_pin(pin, salt)
    assert isinstance(hashed_pin, str)
    assert len(hashed_pin) > 0
    # Hashing same PIN with different salt should produce different hash
    hashed_pin2 = hash_pin(pin, generate_salt())
    assert hashed_pin != hashed_pin2

def test_verify_pin():
    pin = "1234"
    salt = generate_salt()
    hashed_pin = hash_pin(pin, salt)

    assert verify_pin(pin, hashed_pin, salt) is True
    assert verify_pin("wrong_pin", hashed_pin, salt) is False
    assert verify_pin(pin, "wrong_hash", salt) is False
    assert verify_pin(pin, hashed_pin, generate_salt()) is False # Different salt
