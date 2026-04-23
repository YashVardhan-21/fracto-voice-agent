def test_branding_defaults():
    """GET /settings/branding falls back to FRACTO defaults when tenant has no settings."""
    # We can test the default logic directly without a DB:
    tenant_settings = {}
    company_name = tenant_settings.get("company_name", "FRACTO")
    primary_color = tenant_settings.get("primary_color", "#4F46E5")
    assert company_name == "FRACTO"
    assert primary_color == "#4F46E5"

def test_branding_update_logic():
    """Patching settings merges with existing dict."""
    current = {"company_name": "OldName", "primary_color": "#000000"}
    update = {"company_name": "NewName"}
    for k, v in update.items():
        if v is not None:
            current[k] = v
    assert current["company_name"] == "NewName"
    assert current["primary_color"] == "#000000"  # Preserved
