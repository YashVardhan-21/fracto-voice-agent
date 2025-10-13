"""
Free LLM Integration Client
Supports: Google Gemini, Deepseek, Perplexity API
With intelligent fallback and rate limiting
"""

import httpx
import os
import time
import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv

class FreeLLMClient:
    def __init__(self):
        # Load variables from .env if present (no-op if missing)
        load_dotenv()
        # API Keys
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.deepseek_key = os.getenv("DEEPSEEK_API_KEY")
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")
        
        # Rate limiting
        self.gemini_last_request = 0
        self.deepseek_requests_today = 0
        self.deepseek_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        # Usage tracking
        self.usage_stats = {
            "gemini": {"requests": 0, "tokens": 0},
            "deepseek": {"requests": 0, "tokens": 0},
            "perplexity": {"requests": 0, "tokens": 0}
        }
    
    async def analyze_website(self, content: str, company_name: str) -> Dict:
        """Analyze website content using free APIs with fallback"""
        
        # Try Gemini first (free tier)
        if self.gemini_key and self._can_use_gemini():
            try:
                result = await self._analyze_with_gemini(content, company_name)
                if result.get("success"):
                    return result
            except Exception as e:
                print(f"Gemini failed: {e}")
        
        # Try Deepseek (free tier)
        if self.deepseek_key and self._can_use_deepseek():
            try:
                result = await self._analyze_with_deepseek(content, company_name)
                if result.get("success"):
                    return result
            except Exception as e:
                print(f"Deepseek failed: {e}")
        
        # Try Perplexity (your $5 credit)
        if self.perplexity_key:
            try:
                result = await self._analyze_with_perplexity(content, company_name)
                if result.get("success"):
                    return result
            except Exception as e:
                print(f"Perplexity failed: {e}")
        
        # Fallback to local analysis
        return self._local_analysis(content, company_name)
    
    async def generate_prompt(self, company_data: Dict) -> str:
        """Generate voice agent prompt using free APIs"""
        
        # Try Gemini first
        if self.gemini_key and self._can_use_gemini():
            try:
                prompt = await self._generate_prompt_with_gemini(company_data)
                if prompt:
                    return prompt
            except Exception as e:
                print(f"Gemini prompt generation failed: {e}")
        
        # Try Deepseek
        if self.deepseek_key and self._can_use_deepseek():
            try:
                prompt = await self._generate_prompt_with_deepseek(company_data)
                if prompt:
                    return prompt
            except Exception as e:
                print(f"Deepseek prompt generation failed: {e}")
        
        # Fallback to local templates
        return self._generate_local_prompt(company_data)
    
    def _can_use_gemini(self) -> bool:
        """Check if Gemini can be used (rate limit: 15/min)"""
        now = time.time()
        if now - self.gemini_last_request < 4:  # 4 seconds between requests
            return False
        return True
    
    def _can_use_deepseek(self) -> bool:
        """Check if Deepseek can be used (rate limit: 100/day)"""
        # Reset daily counter
        if datetime.now() >= self.deepseek_reset_time:
            self.deepseek_requests_today = 0
            self.deepseek_reset_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
        
        return self.deepseek_requests_today < 100
    
    async def _analyze_with_gemini(self, content: str, company_name: str) -> Dict:
        """Analyze website using Google Gemini"""
        self.gemini_last_request = time.time()
        
        prompt = f"""Analyze this company website and extract structured information.

Company: {company_name}
Content: {content[:2000]}  # Limit content for free tier

Extract:
1. Business type (dental, medical, legal, retail, restaurant, salon, spa, gym, other)
2. Services offered (list 3-5 main services)
3. Contact phone (if found)
4. Contact email (if found)
5. Confidence score (0.0-1.0)

Return ONLY valid JSON:
{{
    "business_type": "dental",
    "services": ["General Dentistry", "Cosmetic Dentistry"],
    "contact_phone": "+1-555-1234",
    "contact_email": "info@example.com",
    "confidence_score": 0.85
}}"""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_key}",
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result["candidates"][0]["content"]["parts"][0]["text"]
                
                # Extract JSON from response
                try:
                    if "```json" in text:
                        json_text = text.split("```json")[1].split("```")[0].strip()
                    else:
                        json_text = text.strip()
                    
                    analysis = json.loads(json_text)
                    analysis["success"] = True
                    analysis["source"] = "gemini"
                    
                    self.usage_stats["gemini"]["requests"] += 1
                    return analysis
                except json.JSONDecodeError:
                    pass
        
        return {"success": False}
    
    async def _analyze_with_deepseek(self, content: str, company_name: str) -> Dict:
        """Analyze website using Deepseek"""
        self.deepseek_requests_today += 1
        
        prompt = f"""Analyze this company website and extract business information.

Company: {company_name}
Content: {content[:1500]}

Extract business type, services, contact info, and confidence score.
Return valid JSON only."""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.deepseek_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "You are a business analyst. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result["choices"][0]["message"]["content"]
                
                try:
                    if "```json" in text:
                        json_text = text.split("```json")[1].split("```")[0].strip()
                    else:
                        json_text = text.strip()
                    
                    analysis = json.loads(json_text)
                    analysis["success"] = True
                    analysis["source"] = "deepseek"
                    
                    self.usage_stats["deepseek"]["requests"] += 1
                    return analysis
                except json.JSONDecodeError:
                    pass
        
        return {"success": False}
    
    async def _analyze_with_perplexity(self, content: str, company_name: str) -> Dict:
        """Analyze website using Perplexity API (your $5 credit)"""
        
        prompt = f"""Research and analyze this company: {company_name}
Website content: {content[:1000]}

Provide detailed business analysis including:
- Business type and industry
- Main services offered
- Contact information
- Business confidence score

Return as JSON format."""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.perplexity_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.1-sonar-small-128k-online",
                    "messages": [
                        {"role": "system", "content": "You are a business research analyst. Return only valid JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                text = result["choices"][0]["message"]["content"]
                
                try:
                    if "```json" in text:
                        json_text = text.split("```json")[1].split("```")[0].strip()
                    else:
                        json_text = text.strip()
                    
                    analysis = json.loads(json_text)
                    analysis["success"] = True
                    analysis["source"] = "perplexity"
                    
                    self.usage_stats["perplexity"]["requests"] += 1
                    return analysis
                except json.JSONDecodeError:
                    pass
        
        return {"success": False}
    
    def _local_analysis(self, content: str, company_name: str) -> Dict:
        """Fallback local analysis using keyword matching"""
        
        # Simple keyword-based business type detection
        content_lower = content.lower()
        
        business_type = "other"
        if any(word in content_lower for word in ["dental", "dentist", "teeth", "oral"]):
            business_type = "dental"
        elif any(word in content_lower for word in ["medical", "doctor", "clinic", "health"]):
            business_type = "medical"
        elif any(word in content_lower for word in ["legal", "law", "attorney", "lawyer"]):
            business_type = "legal"
        elif any(word in content_lower for word in ["restaurant", "food", "dining", "cafe"]):
            business_type = "restaurant"
        elif any(word in content_lower for word in ["salon", "hair", "beauty", "spa"]):
            business_type = "salon"
        
        # Extract phone and email using regex
        import re
        phone_match = re.search(r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})', content)
        email_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', content)
        
        return {
            "success": True,
            "business_type": business_type,
            "services": ["General Services"],
            "contact_phone": phone_match.group(0) if phone_match else "",
            "contact_email": email_match.group(0) if email_match else "",
            "confidence_score": 0.3,  # Low confidence for local analysis
            "source": "local"
        }
    
    async def _generate_prompt_with_gemini(self, company_data: Dict) -> Optional[str]:
        """Generate prompt using Gemini"""
        if not self._can_use_gemini():
            return None
        
        self.gemini_last_request = time.time()
        
        prompt = f"""Create a professional voice agent prompt for {company_data.get('name')}.

Business Type: {company_data.get('business_type')}
Services: {company_data.get('services')}
Contact: {company_data.get('contact_phone')}

Create a warm, professional prompt for a voice assistant that:
- Answers questions about services
- Schedules appointments
- Provides contact information
- Handles inquiries professionally

Keep it under 400 words."""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.gemini_key}",
                json={
                    "contents": [{
                        "parts": [{"text": prompt}]
                    }]
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["candidates"][0]["content"]["parts"][0]["text"]
        
        return None
    
    async def _generate_prompt_with_deepseek(self, company_data: Dict) -> Optional[str]:
        """Generate prompt using Deepseek"""
        if not self._can_use_deepseek():
            return None
        
        self.deepseek_requests_today += 1
        
        prompt = f"""Create a voice agent prompt for {company_data.get('name')}, a {company_data.get('business_type')} business.

Services: {company_data.get('services')}
Contact: {company_data.get('contact_phone')}

Make it professional and helpful."""

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.deepseek_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": "You are an expert at creating voice agent prompts."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                },
                timeout=30.0
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["choices"][0]["message"]["content"]
        
        return None
    
    def _generate_local_prompt(self, company_data: Dict) -> str:
        """Generate prompt using local templates"""
        
        templates = {
            "dental": f"""You are a friendly receptionist for {company_data.get('name')}, a dental practice.

Your role:
- Answer questions about our dental services: {company_data.get('services')}
- Schedule appointments for new and existing patients
- Provide information about dental procedures
- Handle insurance inquiries

Contact: {company_data.get('contact_phone')}

Always be warm, professional, and reassuring. Many patients are nervous about dental visits.""",
            
            "medical": f"""You are a professional medical receptionist for {company_data.get('name')}.

Your responsibilities:
- Schedule patient appointments
- Answer questions about our services: {company_data.get('services')}
- Provide general medical information (not medical advice)
- Handle insurance inquiries

Contact: {company_data.get('contact_phone')}

Be professional, empathetic, and efficient.""",
            
            "legal": f"""You are an experienced legal assistant for {company_data.get('name')}.

Your duties:
- Schedule consultations with attorneys
- Provide information about our practice areas: {company_data.get('services')}
- Collect basic case information
- Answer general questions about legal processes

Contact: {company_data.get('contact_phone')}

Be professional, discrete, and detail-oriented.""",
            
            "default": f"""You are a helpful assistant for {company_data.get('name')}.

Your role:
- Answer questions about our business
- Provide information about our services: {company_data.get('services')}
- Schedule appointments or consultations
- Connect callers with the right department

Contact: {company_data.get('contact_phone')}

Always be friendly, professional, and helpful."""
        }
        
        business_type = company_data.get("business_type", "default")
        return templates.get(business_type, templates["default"])
    
    def get_usage_stats(self) -> Dict:
        """Get API usage statistics"""
        return {
            "usage": self.usage_stats,
            "rate_limits": {
                "gemini": {
                    "requests_per_minute": 15,
                    "last_request": self.gemini_last_request
                },
                "deepseek": {
                    "requests_today": self.deepseek_requests_today,
                    "daily_limit": 100,
                    "reset_time": self.deepseek_reset_time.isoformat()
                }
            }
        }
