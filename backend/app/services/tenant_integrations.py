import base64
import hashlib
from copy import deepcopy
from typing import Any

from cryptography.fernet import Fernet, InvalidToken

from app.config import settings

SECRET_PATHS = {
    ("vapi", "api_key"),
    ("llm", "openai_api_key"),
    ("llm", "gemini_api_key"),
    ("llm", "deepseek_api_key"),
    ("leads", "google_places_api_key"),
    ("leads", "adzuna_app_id"),
    ("leads", "adzuna_app_key"),
}

MASK_KEYS = {
    "api_key",
    "openai_api_key",
    "gemini_api_key",
    "deepseek_api_key",
    "google_places_api_key",
    "adzuna_app_id",
    "adzuna_app_key",
}


def _derive_encryption_key() -> bytes:
    # If explicit key is missing, derive from SECRET_KEY for backward compatibility.
    raw = settings.settings_encryption_key or settings.secret_key
    digest = hashlib.sha256(raw.encode("utf-8")).digest()
    return base64.urlsafe_b64encode(digest)


_fernet = Fernet(_derive_encryption_key())


def _encrypt(value: str) -> str:
    if not value:
        return ""
    return "enc:" + _fernet.encrypt(value.encode("utf-8")).decode("utf-8")


def _decrypt(value: str) -> str:
    if not value:
        return ""
    if not value.startswith("enc:"):
        return value
    token = value[4:]
    try:
        return _fernet.decrypt(token.encode("utf-8")).decode("utf-8")
    except InvalidToken:
        return ""


def _deep_merge(base: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    out = deepcopy(base)
    for k, v in patch.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


class TenantIntegrationsService:
    @staticmethod
    def _normalize(payload: dict[str, Any]) -> dict[str, Any]:
        payload = payload or {}
        normalized = {
            "vapi": payload.get("vapi") or {},
            "llm": payload.get("llm") or {},
            "leads": payload.get("leads") or {},
        }
        return normalized

    def read_decrypted(self, tenant_settings: dict[str, Any] | None) -> dict[str, Any]:
        root = tenant_settings or {}
        integrations = self._normalize(root.get("integrations") or {})
        for section, key in SECRET_PATHS:
            current = integrations.get(section, {}).get(key)
            if isinstance(current, str):
                integrations[section][key] = _decrypt(current)
        return integrations

    def read_masked(self, tenant_settings: dict[str, Any] | None) -> dict[str, Any]:
        decrypted = self.read_decrypted(tenant_settings)
        masked = deepcopy(decrypted)
        for section in ("vapi", "llm", "leads"):
            data = masked.get(section, {})
            for key in list(data.keys()):
                if key in MASK_KEYS:
                    value = (data.get(key) or "").strip()
                    data[key] = {"configured": bool(value)}
        return masked

    def update(self, tenant_settings: dict[str, Any] | None, payload: dict[str, Any]) -> dict[str, Any]:
        root = deepcopy(tenant_settings or {})
        current_decrypted = self.read_decrypted(root)
        incoming = self._normalize(payload)

        merged = _deep_merge(current_decrypted, incoming)
        for section, key in SECRET_PATHS:
            value = (merged.get(section, {}).get(key) or "").strip()
            if value:
                merged[section][key] = _encrypt(value)
            else:
                merged[section][key] = ""

        root["integrations"] = merged
        return root

    def effective_credentials(self, tenant_settings: dict[str, Any] | None) -> dict[str, Any]:
        integrations = self.read_decrypted(tenant_settings)
        vapi = integrations.get("vapi", {})
        llm = integrations.get("llm", {})
        leads = integrations.get("leads", {})
        return {
            "vapi_api_key": (vapi.get("api_key") or settings.vapi_api_key or "").strip(),
            "vapi_voice_id": (vapi.get("voice_id") or settings.vapi_voice_id or "").strip(),
            "vapi_phone_number_id": (
                vapi.get("phone_number_id") or settings.vapi_phone_number_id or ""
            ).strip(),
            "openai_api_key": (llm.get("openai_api_key") or settings.openai_api_key or "").strip(),
            "gemini_api_key": (llm.get("gemini_api_key") or settings.gemini_api_key or "").strip(),
            "deepseek_api_key": (llm.get("deepseek_api_key") or settings.deepseek_api_key or "").strip(),
            "google_places_api_key": (
                leads.get("google_places_api_key") or settings.google_places_api_key or ""
            ).strip(),
            "adzuna_app_id": (leads.get("adzuna_app_id") or settings.adzuna_app_id or "").strip(),
            "adzuna_app_key": (leads.get("adzuna_app_key") or settings.adzuna_app_key or "").strip(),
            "adzuna_country": (leads.get("adzuna_country") or settings.adzuna_country or "gb").strip(),
        }
