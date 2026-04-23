import pytest
from app.models.company import Company
from app.models.user import User

def test_company_has_tenant_id():
    cols = [c.name for c in Company.__table__.columns]
    assert "tenant_id" in cols

def test_user_model_fields():
    cols = [c.name for c in User.__table__.columns]
    assert "email" in cols
    assert "hashed_password" in cols
    assert "is_active" in cols
