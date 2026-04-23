import re


def _slugify(name: str, suffix: str) -> str:
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40]
    return f"{base}-{suffix}"


def test_tenant_model_fields():
    from app.models.tenant import Tenant
    t = Tenant(id="tenant_abc", name="Test Co", slug="test-co-abc", plan="starter", is_active=True)
    assert t.id == "tenant_abc"
    assert t.plan == "starter"
    assert t.is_active == True


def test_slug_generation():
    assert _slugify("Acme Corp", "abc12345") == "acme-corp-abc12345"
    assert len(_slugify("A" * 100, "suffix")) <= 48  # 40 + 1 + 6 chars


def test_make_slug_special_chars():
    slug = _slugify("My Company (Ltd.)", "xyz00000")
    assert "my-company" in slug
    assert slug.endswith("-xyz00000")
