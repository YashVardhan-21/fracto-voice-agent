def test_tenant_model_fields():
    from app.models.tenant import Tenant
    t = Tenant(id="tenant_abc", name="Test Co", slug="tenant_abc", plan="starter", is_active=True)
    assert t.id == "tenant_abc"
    assert t.plan == "starter"
    assert t.is_active == True
