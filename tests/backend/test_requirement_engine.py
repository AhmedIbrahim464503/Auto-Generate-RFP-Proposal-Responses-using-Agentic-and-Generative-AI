import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from backend.app.db.base import Base
from backend.app.db.session import get_db
from backend.app.main import app
from backend.app.models.opportunity import Opportunity
from backend.app.models.document import RFPDocument
from backend.app.services.requirement_engine import PROMPT_REGISTRY, requirement_engine_service
from backend.app.schemas.requirement_intelligence import RequirementIntelligenceOutput, RequirementExtractionOutput

# Setup in-memory SQLite using StaticPool to keep the connection persistent
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables in the test database
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Apply the override to the FastAPI app
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def test_prompt_registry_keys():
    assert "v1.0" in PROMPT_REGISTRY
    v1 = PROMPT_REGISTRY["v1.0"]
    assert "system_instruction" in v1
    assert "extraction_prompt" in v1


def test_requirement_extraction_schema():
    data = {
        "confidence": 0.95,
        "evidence": "The contractor shall provide a backup server.",
        "reasoning": "Identified a functional requirement.",
        "validation_status": "VALIDATED",
        "temp_id": "REQ-001",
        "title": "Backup Server Requirement",
        "text_content": "Deploy backup nodes.",
        "category": "Technical",
        "priority": "High",
        "req_type": "Functional",
        "mandatory": True,
        "source_section": "Sec 1",
        "source_page": 2,
        "temp_parent_id": None,
        "assigned_departments": ["Technical"]
    }
    req = RequirementExtractionOutput(**data)
    assert req.temp_id == "REQ-001"
    assert req.priority == "High"
    assert req.mandatory is True


def test_service_mock_fallback():
    output = requirement_engine_service.extract_requirement_intelligence("some doc context")
    assert isinstance(output, RequirementIntelligenceOutput)
    assert len(output.requirements) > 0
    assert output.requirements[0].temp_id == "REQ-001"


def test_e2e_extraction_and_retrieval(client: TestClient, test_db):
    # 1. Setup mock Opportunity and RFPDocument
    opp = Opportunity(title="SPS AI Opportunity")
    test_db.add(opp)
    test_db.commit()

    doc = RFPDocument(opportunity_id=opp.id, file_name="sps_ai_rfp.pdf", file_path="/fake/path")
    test_db.add(doc)
    test_db.commit()

    doc_id = str(doc.id)

    # 2. Trigger Extraction API
    extract_res = client.post(f"/api/v1/rfp/{doc_id}/requirements/extract")
    assert extract_res.status_code == 200
    extract_data = extract_res.json()
    assert len(extract_data["requirements"]) > 0

    # 3. Retrieve Requirements
    reqs_res = client.get(f"/api/v1/rfp/{doc_id}/requirements")
    assert reqs_res.status_code == 200
    reqs_data = reqs_res.json()
    assert len(reqs_data) > 0
    assert reqs_data[0]["title"] == "SPS Core Platform Deployment"

    # 4. Retrieve Deliverables
    dels_res = client.get(f"/api/v1/rfp/{doc_id}/deliverables")
    assert dels_res.status_code == 200
    dels_data = dels_res.json()
    assert len(dels_data) > 0

    # 5. Retrieve Risks
    risks_res = client.get(f"/api/v1/rfp/{doc_id}/risks")
    assert risks_res.status_code == 200
    assert len(risks_res.json()) > 0

    # 6. Retrieve Knowledge Graph
    graph_res = client.get(f"/api/v1/rfp/{doc_id}/knowledge-graph")
    assert graph_res.status_code == 200
    graph_data = graph_res.json()
    assert "nodes" in graph_data
    assert "edges" in graph_data
