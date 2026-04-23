import pytest
from unittest.mock import AsyncMock, MagicMock
from app.services.gdpr import GDPRService


@pytest.mark.asyncio
async def test_opt_out_nonexistent_returns_false():
    svc = GDPRService()
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result
    result = await svc.opt_out_company(9999, db, actor_id=1)
    assert result is False


@pytest.mark.asyncio
async def test_delete_nonexistent_returns_not_found():
    svc = GDPRService()
    db = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    db.execute.return_value = mock_result
    result = await svc.delete_company_data(9999, db, actor_id=1)
    assert result["deleted"] is False
    assert result["reason"] == "not_found"
