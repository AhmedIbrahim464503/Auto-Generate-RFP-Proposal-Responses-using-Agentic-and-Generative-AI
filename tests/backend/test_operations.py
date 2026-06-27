import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from backend.app.main import app
from backend.app.core.security.auth import create_access_token
from backend.app.models.proposal import ProposalPlan, ProposalSection

client = TestClient(app)

def test_auth_login_endpoint():
  # Admin credentials
  response = client.post("/api/v1/auth/login", json={"username": "admin", "password": "admin123"})
  assert response.status_code == 200
  data = response.json()
  assert "access_token" in data
  assert "refresh_token" in data
  assert data["role"] == "Admin"

  # Writer credentials
  response = client.post("/api/v1/auth/login", json={"username": "writer", "password": "writer123"})
  assert response.status_code == 200
  assert response.json()["role"] == "Writer"

  # Invalid credentials
  response = client.post("/api/v1/auth/login", json={"username": "bad", "password": "bad"})
  assert response.status_code == 401

def test_auth_refresh_endpoint():
  # Login first
  response = client.post("/api/v1/auth/login", json={"username": "writer", "password": "writer123"})
  refresh_token = response.json()["refresh_token"]

  # Refresh
  response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
  assert response.status_code == 200
  assert "access_token" in response.json()

def test_auth_me_endpoint():
  # Without credentials (Guest User default fallback)
  response = client.get("/api/v1/auth/me")
  assert response.status_code == 200
  assert response.json()["username"] == "guest_user"
  assert response.json()["role"] == "Guest"

  # With valid token
  token = create_access_token(data={"sub": "admin", "role": "Admin", "permissions": ["admin"]})
  headers = {"Authorization": f"Bearer {token}"}
  response = client.get("/api/v1/auth/me", headers=headers)
  assert response.status_code == 200
  assert response.json()["username"] == "admin"
  assert response.json()["role"] == "Admin"

def test_proposal_exporter(test_db: Session):
  from backend.app.models.opportunity import Opportunity
  opp = test_db.query(Opportunity).first()
  if not opp:
    opp = Opportunity(
        title="Test Opportunity",
        description="Desc",
    )
    test_db.add(opp)
    test_db.commit()

  # Setup dummy proposal
  proposal = ProposalPlan(opportunity_id=opp.id, title="Test Bid Package")
  test_db.add(proposal)
  test_db.commit()

  section1 = ProposalSection(proposal_plan_id=proposal.id, title="Section 1", content="This is content 1", status="approved")
  test_db.add(section1)
  test_db.commit()

  # Test docx download
  response = client.get(f"/api/v1/export/{proposal.id}/docx")
  assert response.status_code == 200
  assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

  # Test markdown export
  response = client.get(f"/api/v1/export/{proposal.id}/markdown")
  assert response.status_code == 200
  assert b"# Test Bid Package" in response.content

  # Test json export
  response = client.get(f"/api/v1/export/{proposal.id}/json")
  assert response.status_code == 200
  data = response.json()
  assert data["title"] == "Test Bid Package"
  assert len(data["sections"]) == 1
  assert data["sections"][0]["title"] == "Section 1"

  # Cleanup
  test_db.delete(section1)
  test_db.delete(proposal)
  test_db.commit()
