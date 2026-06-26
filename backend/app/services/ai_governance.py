import re
from typing import Dict, Any

class AIGovernanceService:
    def redact_pii(self, text: str) -> str:
        email_pattern = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'
        phone_pattern = r'\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b'
        
        redacted = re.sub(email_pattern, "[REDACTED_EMAIL]", text)
        redacted = re.sub(phone_pattern, "[REDACTED_PHONE]", redacted)
        return redacted

    def detect_prompt_injection(self, text: str) -> bool:
        injection_triggers = [
            "ignore previous",
            "system override",
            "you are now",
            "forget the instructions",
            "bypass safety",
            "new rules"
        ]
        text_lower = text.lower()
        for trigger in injection_triggers:
            if trigger in text_lower:
                return True
        return False

    def validate_content_safety(self, text: str) -> bool:
        restricted_terms = ["malware", "bypass", "exploit", "compromise"]
        text_lower = text.lower()
        for term in restricted_terms:
            if term in text_lower:
                return False
        return True

    def run_guardrails(self, text: str) -> Dict[str, Any]:
        pii_cleaned = self.redact_pii(text)
        is_safe = self.validate_content_safety(pii_cleaned)
        
        return {
            "passed": is_safe,
            "cleaned_text": pii_cleaned,
            "blocked_reasons": [] if is_safe else ["Failed safety policy validation"]
        }

# Global governance service instance
ai_governance_service = AIGovernanceService()
