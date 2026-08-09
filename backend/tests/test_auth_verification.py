import pytest
from app.auth.jwt import get_password_hash, verify_password, create_access_token, decode_access_token

def test_password_hashing_and_verification():
    raw_pass = "SecurePass123!"
    hashed = get_password_hash(raw_pass)
    
    # 1. Hashed password must not equal plain text
    assert hashed != raw_pass
    
    # 2. Valid password verifies to True
    assert verify_password(raw_pass, hashed) is True
    
    # 3. Invalid password verifies to False
    assert verify_password("WrongPass123!", hashed) is False

def test_jwt_token_generation_and_decoding():
    user_email = "test.analyst@captrix.ai"
    role = "Analyst"
    
    token = create_access_token(data={"sub": user_email, "role": role})
    assert token is not None
    assert isinstance(token, str)
    
    payload = decode_access_token(token)
    assert payload is not None
    assert payload.get("sub") == user_email
    assert payload.get("role") == role
