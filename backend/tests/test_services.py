import pytest
from app.services.prompt_generator import PromptGenerator

def test_prompt_generator_dental():
    gen = PromptGenerator()
    prompt = gen.generate_local({"name": "Smile Clinic", "business_type": "dental", "services": ["Cleaning"], "phone": "555-1234"})
    assert "Smile Clinic" in prompt
    assert len(prompt) > 100

def test_prompt_generator_unknown_type():
    gen = PromptGenerator()
    prompt = gen.generate_local({"name": "Acme Co", "business_type": "xyz", "services": [], "phone": ""})
    assert "Acme Co" in prompt

def test_prompt_generator_formats_services_correctly():
    gen = PromptGenerator()
    prompt = gen.generate_local({"name": "Test Co", "business_type": "medical", "services": ["Checkup", "X-Ray"], "phone": "555-9999"})
    assert "Checkup" in prompt
    assert "555-9999" in prompt

def test_prompt_generator_handles_none_services():
    gen = PromptGenerator()
    prompt = gen.generate_local({"name": "Test Co", "business_type": "dental", "services": None, "phone": "555-0000"})
    assert "our services" in prompt

# Tests for WebsiteAnalyzer._local_analysis and _parse_json
def test_local_analysis_detects_dental():
    from app.services.website_analyzer import WebsiteAnalyzer
    analyzer = WebsiteAnalyzer()
    result = analyzer._local_analysis("We are a dental clinic offering teeth cleaning and dental implants.", "Smile Co")
    assert result["business_type"] == "dental"
    assert result["source"] == "local"
    assert result["confidence_score"] == 0.3

def test_parse_json_strips_code_fence():
    from app.services.website_analyzer import WebsiteAnalyzer
    analyzer = WebsiteAnalyzer()
    text = '```json\n{"business_type": "medical", "services": []}\n```'
    result = analyzer._parse_json(text)
    assert result is not None
    assert result["business_type"] == "medical"

def test_parse_json_handles_plain_json():
    from app.services.website_analyzer import WebsiteAnalyzer
    analyzer = WebsiteAnalyzer()
    result = analyzer._parse_json('{"business_type": "legal"}')
    assert result["business_type"] == "legal"

@pytest.mark.asyncio
async def test_vapi_make_call_raises_without_phone_number_id(monkeypatch):
    from app.services.vapi_client import VapiClient
    from app.config import settings
    monkeypatch.setattr(settings, "vapi_phone_number_id", None)
    client = VapiClient()
    with pytest.raises(ValueError, match="VAPI_PHONE_NUMBER_ID"):
        await client.make_call("agent-123", "+15550001111")

@pytest.mark.asyncio
async def test_scraper_returns_mock_data_on_failure():
    from app.services.scraper import JobScraper
    from unittest.mock import patch, AsyncMock
    import httpx
    scraper = JobScraper()
    with patch("httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get = AsyncMock(
            side_effect=httpx.ConnectError("connection refused")
        )
        results = await scraper.scrape_indeed("receptionist", "Dublin", 3)
    assert len(results) > 0
    assert results[0]["source"] == "mock"
