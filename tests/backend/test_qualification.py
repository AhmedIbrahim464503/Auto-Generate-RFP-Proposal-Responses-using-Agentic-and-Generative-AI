import pytest
import json
from datetime import datetime
from backend.app.models.opportunity import Opportunity
from backend.app.models.document import RFPDocument
from backend.app.models.review import FinancialReview, LegalReview, OperationsReview, TechnicalReview
from backend.app.models.qualification import QualificationDecision, QualificationRule, QualificationDecisionHistory
from backend.app.services.qualification_rules import QualificationRulesService
from backend.app.services.qualification_engine import qualification_engine_service

def test_ruleset_seeding_and_management(test_db):
    # Retrieve active ruleset (should auto-seed default standard ruleset)
    ruleset = QualificationRulesService.get_active_ruleset(test_db)
    assert ruleset is not None
    assert ruleset.is_active is True
    assert ruleset.version == "v1.0.0"
    
    payload = json.loads(ruleset.rules_payload)
    assert "weights" in payload
    assert payload["weights"]["strategic_fit"] == 0.15

    # Create new ruleset
    new_payload = {"weights": {"strategic_fit": 0.50}, "blockers": []}
    new_rule = QualificationRulesService.create_ruleset(
        test_db,
        name="Custom Ruleset",
        version="v2.0.0",
        rules_payload=new_payload,
        make_active=True
    )
    assert new_rule.is_active is True
    
    # Reload original ruleset to check it was deactivated
    test_db.refresh(ruleset)
    assert ruleset.is_active is False

    # Update active ruleset payload
    updated_rule = QualificationRulesService.update_active_ruleset_payload(test_db, {"blockers": ["payment_terms_gt_NET90"]})
    updated_payload = json.loads(updated_rule.rules_payload)
    assert "strategic_fit" in updated_payload["weights"]
    assert "payment_terms_gt_NET90" in updated_payload["blockers"]

def test_qualification_scoring_and_veto(test_db):
    # Seed default ruleset
    db_rule = test_db.query(QualificationRule).filter(QualificationRule.is_active == True).first()
    if db_rule:
        db_rule.is_active = False
    
    default_rule = QualificationRulesService.get_active_ruleset(test_db)

    # Seed opportunity
    opp = Opportunity(title="SPS Test Opportunity")
    test_db.add(opp)
    test_db.commit()

    # Seed department reviews
    fin = FinancialReview(opportunity_id=opp.id, decision="GO", confidence=0.9, reasoning="Net30 check okay", findings="['payment Net30 ok']")
    leg = LegalReview(opportunity_id=opp.id, decision="GO", confidence=0.8)
    ops = OperationsReview(opportunity_id=opp.id, decision="GO", confidence=0.85)
    tech = TechnicalReview(opportunity_id=opp.id, decision="GO", confidence=0.95)
    test_db.add_all([fin, leg, ops, tech])
    test_db.commit()

    # Run engine
    dec = qualification_engine_service.calculate_opportunity_score_and_run(test_db, opp.id)
    assert dec.recommendation == "GO"
    assert dec.opportunity_score > 70.0
    assert dec.estimated_win_probability == 80.0

    # Set Legal decision to NO_GO and test Veto rule
    leg.decision = "NO_GO"
    test_db.commit()

    dec2 = qualification_engine_service.calculate_opportunity_score_and_run(test_db, opp.id)
    assert dec2.recommendation == "NO_GO"

def test_qualification_endpoints_workflow(client, test_db):
    # Setup standard records
    opp = Opportunity(title="SPS API Opportunity")
    test_db.add(opp)
    test_db.commit()

    doc = RFPDocument(id="test-doc-qualification", opportunity_id=opp.id, file_name="sample.pdf", file_path="/tmp/sample.pdf")
    test_db.add(doc)
    test_db.commit()

    # Seed reviews
    fin = FinancialReview(opportunity_id=opp.id, decision="GO", confidence=0.9)
    leg = LegalReview(opportunity_id=opp.id, decision="GO", confidence=0.8)
    ops = OperationsReview(opportunity_id=opp.id, decision="GO", confidence=0.8)
    tech = TechnicalReview(opportunity_id=opp.id, decision="GO", confidence=0.9)
    test_db.add_all([fin, leg, ops, tech])
    test_db.commit()

    # 1. Run Qualification API
    resp = client.post(f"/api/v1/rfp/test-doc-qualification/qualification")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "DRAFT"
    assert data["recommendation"] == "GO"
    assert data["opportunity_score"] > 70.0
    assert data["estimated_win_probability"] == 80.0
    assert "strategic_fit" in [b["dimension"] for b in data["scoring_breakdowns"]]

    # 2. Get Qualification API
    resp = client.get(f"/api/v1/rfp/test-doc-qualification/qualification")
    assert resp.status_code == 200
    assert resp.json()["status"] == "DRAFT"

    # 3. Approve Decision API
    resp = client.post(
        f"/api/v1/rfp/test-doc-qualification/approve-decision",
        json={"reviewer": "John Doe", "comments": "Approved standard go-ahead."}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "APPROVED"
    assert data["final_decision"] == "GO"
    assert data["decision_by"] == "John Doe"

    # 4. Override Decision API
    resp = client.post(
        f"/api/v1/rfp/test-doc-qualification/override-decision",
        json={"new_decision": "NO_GO", "override_reason": "High strategic risk", "overridden_by": "VP of Capture"}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "OVERRIDDEN"
    assert data["final_decision"] == "NO_GO"
    assert data["decision_by"] == "VP of Capture"

    # 5. History API
    resp = client.get(f"/api/v1/rfp/test-doc-qualification/decision-history")
    assert resp.status_code == 200
    history = resp.json()
    assert len(history) >= 3
    actions = [h["action"] for h in history]
    assert "GENERATE" in actions
    assert "APPROVE" in actions
    assert "OVERRIDE" in actions

    # 6. Recalculate Weights API
    new_weights = {
        "strategic_fit": 0.30,
        "capability": 0.10,
        "financial": 0.10,
        "technical_readiness": 0.10,
        "compliance_readiness": 0.10,
        "risk": 0.10,
        "relationship": 0.10,
        "complexity": 0.10
    }
    resp = client.post(
        f"/api/v1/rfp/test-doc-qualification/recalculate",
        json={"weights": new_weights}
    )
    assert resp.status_code == 200
    # Opportunity score recalculation should reflect updated weights
    recalc_data = resp.json()
    assert len(recalc_data["scoring_breakdowns"]) == 8

    # 7. Rules Endpoint
    resp = client.get(f"/api/v1/rfp/rules/qualification")
    assert resp.status_code == 200
    rule_data = resp.json()
    assert rule_data["rules_payload"]["weights"]["strategic_fit"] == 0.30
