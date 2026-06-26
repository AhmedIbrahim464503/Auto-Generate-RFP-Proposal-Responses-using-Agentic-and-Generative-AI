import json
import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from backend.app.models.qualification import QualificationRule

logger = logging.getLogger("app")

DEFAULT_RULES = {
    "weights": {
        "strategic_fit": 0.15,
        "capability": 0.15,
        "financial": 0.15,
        "technical_readiness": 0.15,
        "compliance_readiness": 0.10,
        "risk": 0.10,
        "relationship": 0.10,
        "complexity": 0.10
    },
    "risk_thresholds": {
        "high_risk_veto": True,
        "escalation_score_cutoff": 65.0
      },
    "blockers": ["payment_terms_gt_NET60", "insurance_limit_gt_10M"],
    "veto_rules": {
        "legal_no_go_veto": True,
        "financial_no_go_veto": True
    }
}

class QualificationRulesService:
    @staticmethod
    def get_active_ruleset(db: Session, scope_key: str = "global") -> QualificationRule:
        """
        Retrieves the currently active ruleset. If none exists, seeds and returns a default.
        """
        ruleset = db.query(QualificationRule).filter(
            QualificationRule.is_active == True,
            QualificationRule.scope_key == scope_key
        ).first()

        if not ruleset:
            logger.info("No active ruleset found. Seeding default Standard Ruleset.")
            ruleset = QualificationRule(
                version="v1.0.0",
                name="SPS Enterprise Standard Ruleset",
                scope_key=scope_key,
                rules_payload=json.dumps(DEFAULT_RULES),
                is_active=True
            )
            db.add(ruleset)
            db.commit()
            db.refresh(ruleset)

        return ruleset

    @staticmethod
    def create_ruleset(db: Session, name: str, version: str, rules_payload: Dict[str, Any], scope_key: str = "global", make_active: bool = False) -> QualificationRule:
        """
        Creates a new ruleset. If make_active is True, deactivates the previously active ruleset.
        """
        if make_active:
            db.query(QualificationRule).filter(
                QualificationRule.scope_key == scope_key
            ).update({"is_active": False})

        new_rule = QualificationRule(
            version=version,
            name=name,
            scope_key=scope_key,
            rules_payload=json.dumps(rules_payload),
            is_active=make_active
        )
        db.add(new_rule)
        db.commit()
        db.refresh(new_rule)
        return new_rule

    @staticmethod
    def update_active_ruleset_payload(db: Session, new_payload: Dict[str, Any], scope_key: str = "global") -> QualificationRule:
        """
        Updates the payload configuration of the active ruleset.
        """
        ruleset = QualificationRulesService.get_active_ruleset(db, scope_key=scope_key)
        
        # Merge or overwrite payload
        current_data = json.loads(ruleset.rules_payload)
        current_data.update(new_payload)
        
        ruleset.rules_payload = json.dumps(current_data)
        db.commit()
        db.refresh(ruleset)
        return ruleset
