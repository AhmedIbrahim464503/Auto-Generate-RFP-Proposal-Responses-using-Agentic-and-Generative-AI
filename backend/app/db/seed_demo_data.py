import sys
import os
from sqlalchemy.orm import Session

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..")))

from backend.app.db.session import SessionLocal, engine
from backend.app.db.base_class import Base
from backend.app.models.opportunity import Opportunity
from backend.app.models.proposal import ProposalPlan, ProposalSection
from backend.app.models.document import RFPDocument
from backend.app.core.config import settings

def seed_database():
  # Zero-config support: if we are using SQLite or if tables do not exist, create them
  db_url = settings.get_database_url()
  print(f"Target Database: {db_url}")
  
  if "sqlite" in db_url or not engine.dialect.has_table(engine.connect(), "opportunity"):
    print("Creating tables in database schema...")
    Base.metadata.create_all(bind=engine)

  db: Session = SessionLocal()
  try:
    print("Seeding database opportunity records...")
    
    # Check if opportunity already exists to prevent duplicate seeds
    existing_opp = db.query(Opportunity).filter(Opportunity.title == "US Department of Defense Cloud Migration RFP").first()
    if existing_opp:
      print("Database already seeded with demo data.")
      return

    # 1. Opportunity
    opp = Opportunity(
        title="US Department of Defense Cloud Migration RFP",
        description="Multi-year infrastructure upgrade proposal requiring zero-trust cloud transition frameworks."
    )
    db.add(opp)
    db.commit()
    db.refresh(opp)

    # 2. RFP Document
    doc = RFPDocument(
        opportunity_id=opp.id,
        file_name="dod_cloud_migration_solicitation.pdf",
        file_path="/storage/dod_cloud_migration_solicitation.pdf",
        status="PROCESSED"
    )
    db.add(doc)
    db.commit()

    # 3. Proposal Plan
    plan = ProposalPlan(
        opportunity_id=opp.id,
        title="Tactical Security Cloud Solution Proposal",
        client="US Department of Defense",
        rfp_name="DOD-CLOUD-2026",
        proposal_type="Technical & Financial Bid Package",
        complexity="High",
        priority="High",
        status="APPROVED"
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)

    # 4. Proposal Sections
    sec1 = ProposalSection(
        proposal_plan_id=plan.id,
        title="Executive Summary",
        content="This proposal outlines the deployment architecture of the Tactical Security Cloud Solution. Our framework leverages zero-trust identity checks and high-availability endpoints configured across global edge nodes.",
        status="REVIEWED",
        owner="Lead Solutions Architect"
    )
    sec2 = ProposalSection(
        proposal_plan_id=plan.id,
        title="Compliance & Zero-Trust Architecture",
        content="Zero-Trust frameworks verify every request at network boundaries. Data flows are encrypted in-transit and at-rest using FIPS 140-3 cryptography algorithms.",
        status="COMPLETED",
        owner="Chief Security Officer"
    )
    db.add(sec1)
    db.add(sec2)
    db.commit()

    print("Database seeding completed successfully.")
  except Exception as e:
    db.rollback()
    print(f"Error seeding database: {e}")
  finally:
    db.close()

if __name__ == "__main__":
  seed_database()
