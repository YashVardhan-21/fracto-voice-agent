import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.services.pipeline import Pipeline


@pytest.mark.asyncio
async def test_process_company_returns_error_for_missing_company():
    pipeline = Pipeline()
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute = AsyncMock(return_value=mock_result)

    result = await pipeline.process_company(9999, db)
    assert result["success"] is False
    assert "not found" in result["error"].lower()


@pytest.mark.asyncio
async def test_process_company_creates_draft_agent_without_vapi_key(monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings, "vapi_api_key", None)

    pipeline = Pipeline()
    db = AsyncMock()
    db.flush = AsyncMock()

    mock_company = MagicMock()
    mock_company.id = 1
    mock_company.name = "Test Dental"
    mock_company.tenant_id = "fracto"
    mock_company.website = None
    mock_company.business_type = "dental"
    mock_company.services = ["Cleaning"]
    mock_company.phone = "555-1234"
    mock_company.status = "pending"

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_company
    db.execute = AsyncMock(return_value=mock_result)
    db.add = MagicMock()

    result = await pipeline.process_company(1, db)
    assert result["success"] is True
    assert result["status"] == "prompt_ready"
    assert "Test Dental" in result["prompt"]
    db.add.assert_called_once()
