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
