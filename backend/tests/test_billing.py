from app.services.billing import PLANS

def test_plans_exist():
    assert "starter" in PLANS
    assert "pro" in PLANS
    assert "agency" in PLANS

def test_plan_structure():
    for name, plan in PLANS.items():
        assert "price" in plan
        assert "agents" in plan
        assert "campaigns" in plan

def test_invalid_plan_detection():
    valid = ["starter", "pro", "agency"]
    assert "enterprise" not in valid
