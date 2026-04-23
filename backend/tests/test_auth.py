import pytest
from app.auth.service import AuthService, verify_password, create_access_token


def test_password_hash_and_verify():
    hashed = AuthService.hash_password("mypassword")
    assert verify_password("mypassword", hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_create_access_token_returns_string():
    token = create_access_token({"sub": "1", "email": "test@test.com"})
    assert isinstance(token, str)
    assert len(token) > 20
