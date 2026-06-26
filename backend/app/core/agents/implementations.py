from typing import Any, Dict, List
import time
import uuid
from sqlalchemy.orm import Session
from backend.app.core.agents.base import BaseAgent
from backend.app.schemas.agent import AgentOutput
from backend.app.services.ai_platform import ai_platform_service
from backend.app.services.ai_governance import ai_governance_service
from backend.app.core.events.event_bus import event_bus

class StandardAgentExecutor:
    @staticmethod
    def execute(db: Session, agent_id: str, input_data: Any, logic_func: Any, config: Dict[str, Any] = None) -> AgentOutput:
        execution_id = str(uuid.uuid4())
        event_bus.publish("AgentStarted", {"agent_id": agent_id, "execution_id": execution_id})
        
        # Governance - Prompt injection check
        input_str = str(input_data)
        if ai_governance_service.detect_prompt_injection(input_str):
            output = AgentOutput(
                decision="REJECTED_INPUT_SAFETY",
                confidence=0.0,
                reasoning="Input contains patterns matching prompt injection triggers.",
                evidence=[],
                risks=["Security risk: Prompt injection attempt detected."],
                recommendations=["Flag input for administrative review."],
                processing_time_ms=0.0,
                metadata={"safety_violation": True}
            )
            event_bus.publish("AgentFinished", {"agent_id": agent_id, "execution_id": execution_id, "status": "failed"})
            return output

        t0 = time.time()
        try:
            result = logic_func(db, input_data, config)
            latency_ms = (time.time() - t0) * 1000

            if isinstance(result, AgentOutput):
                output = result
            else:
                output = AgentOutput(
                    decision=getattr(result, "decision", "SUCCESS"),
                    confidence=getattr(result, "confidence", 0.9),
                    reasoning=getattr(result, "reasoning", "Execution completed successfully."),
                    evidence=getattr(result, "evidence", []),
                    risks=getattr(result, "risks", []),
                    recommendations=getattr(result, "recommendations", []),
                    processing_time_ms=latency_ms,
                    metadata=getattr(result, "metadata", {})
                )

            # Governance - Output guardrails
            gov_res = ai_governance_service.run_guardrails(output.reasoning)
            if not gov_res["passed"]:
                output.decision = "BLOCKED_OUTPUT_SAFETY"
                output.reasoning = "Output blocked due to content safety policy violation."
                output.metadata["blocked_reasons"] = gov_res["blocked_reasons"]

            # Log metrics
            ai_platform_service.log_agent_execution(
                db=db,
                agent_id=agent_id,
                execution_id=execution_id,
                latency_ms=latency_ms,
                input_tokens=len(input_str) // 4,
                output_tokens=len(output.reasoning) // 4,
                cost=0.0,
                status="success" if gov_res["passed"] else "blocked"
            )
            
            # Log explainability
            ai_platform_service.log_explainability(
                db=db,
                execution_id=execution_id,
                inputs={"input": input_str[:1000]},
                retrieved_evidence={"evidence": output.evidence},
                rules_used={},
                prompt_version="1.0",
                model_version="gemini-2.5-flash",
                confidence=output.confidence,
                reasoning=output.reasoning,
                output_schema=None
            )

            event_bus.publish("AgentFinished", {"agent_id": agent_id, "execution_id": execution_id, "status": "success"})
            return output
            
        except Exception as e:
            latency_ms = (time.time() - t0) * 1000
            ai_platform_service.log_agent_execution(
                db=db,
                agent_id=agent_id,
                execution_id=execution_id,
                latency_ms=latency_ms,
                input_tokens=len(input_str) // 4,
                output_tokens=0,
                cost=0.0,
                status="failed"
            )
            event_bus.publish("AgentFinished", {"agent_id": agent_id, "execution_id": execution_id, "status": "failed"})
            raise e

class QualificationAgent(BaseAgent):
    def __init__(self):
        super().__init__("qualification")

    def run(self, db: Session, opportunity_id: str, config: Dict[str, Any] = None) -> AgentOutput:
        from backend.app.services.qualification_engine import qualification_engine_service
        def logic(db_session, opt_id, cfg):
            res = qualification_engine_service.calculate_opportunity_score_and_run(db_session, opt_id)
            return AgentOutput(
                decision=res.recommendation,
                confidence=(res.win_probability if hasattr(res, 'win_probability') else (getattr(res, 'estimated_win_probability', 70.0))) / 100.0,
                reasoning=res.reasoning or "Scored and analyzed proposal feasibility.",
                evidence=[],
                risks=[],
                recommendations=[],
                processing_time_ms=0.0,
                metadata={}
            )

        return StandardAgentExecutor.execute(db, self.agent_id, opportunity_id, logic, config)


class PlanningAgent(BaseAgent):
    def __init__(self):
        super().__init__("planning")

    def run(self, db: Session, opportunity_id: str, config: Dict[str, Any] = None) -> AgentOutput:
        from backend.app.services.planning_engine import proposal_planning_service
        def logic(db_session, opt_id, cfg):
            res = proposal_planning_service.create_proposal_planning_package(db_session, opt_id)
            return AgentOutput(
                decision="PLAN_GENERATED",
                confidence=0.95,
                reasoning=f"Proposal plan generated successfully with {len(res.sections)} sections.",
                evidence=[],
                risks=[],
                recommendations=[],
                processing_time_ms=0.0,
                metadata={}
            )
        return StandardAgentExecutor.execute(db, self.agent_id, opportunity_id, logic, config)

class LegalReviewAgent(BaseAgent):
    def __init__(self):
        super().__init__("legal_review")

    def run(self, db: Session, opportunity_id: str, config: Dict[str, Any] = None) -> AgentOutput:
        from backend.app.services.review_engine import review_engine_service
        def logic(db_session, opt_id, cfg):
            res = review_engine_service.run_legal_review(db_session, opt_id)
            return AgentOutput(
                decision=res.decision,
                confidence=res.confidence,
                reasoning=res.reasoning,
                evidence=[res.evidence] if res.evidence else [],
                risks=res.risks,
                recommendations=res.recommendations,
                processing_time_ms=0.0,
                metadata={}
            )
        return StandardAgentExecutor.execute(db, self.agent_id, opportunity_id, logic, config)

class FinancialReviewAgent(BaseAgent):
    def __init__(self):
        super().__init__("financial_review")

    def run(self, db: Session, opportunity_id: str, config: Dict[str, Any] = None) -> AgentOutput:
        from backend.app.services.review_engine import review_engine_service
        def logic(db_session, opt_id, cfg):
            res = review_engine_service.run_financial_review(db_session, opt_id)
            return AgentOutput(
                decision=res.decision,
                confidence=res.confidence,
                reasoning=res.reasoning,
                evidence=[res.evidence] if res.evidence else [],
                risks=res.risks,
                recommendations=res.recommendations,
                processing_time_ms=0.0,
                metadata={}
            )
        return StandardAgentExecutor.execute(db, self.agent_id, opportunity_id, logic, config)

class TechnicalReviewAgent(BaseAgent):
    def __init__(self):
        super().__init__("technical_review")

    def run(self, db: Session, opportunity_id: str, config: Dict[str, Any] = None) -> AgentOutput:
        from backend.app.services.review_engine import review_engine_service
        def logic(db_session, opt_id, cfg):
            res = review_engine_service.run_technical_review(db_session, opt_id)
            return AgentOutput(
                decision=res.decision,
                confidence=res.confidence,
                reasoning=res.reasoning,
                evidence=[res.evidence] if res.evidence else [],
                risks=res.risks,
                recommendations=res.recommendations,
                processing_time_ms=0.0,
                metadata={}
            )
        return StandardAgentExecutor.execute(db, self.agent_id, opportunity_id, logic, config)

class OperationsReviewAgent(BaseAgent):
    def __init__(self):
        super().__init__("operations_review")

    def run(self, db: Session, opportunity_id: str, config: Dict[str, Any] = None) -> AgentOutput:
        from backend.app.services.review_engine import review_engine_service
        def logic(db_session, opt_id, cfg):
            res = review_engine_service.run_operations_review(db_session, opt_id)
            return AgentOutput(
                decision=res.decision,
                confidence=res.confidence,
                reasoning=res.reasoning,
                evidence=[res.evidence] if res.evidence else [],
                risks=res.risks,
                recommendations=res.recommendations,
                processing_time_ms=0.0,
                metadata={}
            )
        return StandardAgentExecutor.execute(db, self.agent_id, opportunity_id, logic, config)

class WriterAgent(BaseAgent):
    def __init__(self):
        super().__init__("writer")

    def run(self, db: Session, section_data: Dict[str, Any], config: Dict[str, Any] = None) -> AgentOutput:
        from backend.app.services.proposal_generator import proposal_generator_service
        def logic(db_session, sdata, cfg):
            proposal_plan_id = sdata.get("proposal_plan_id")
            section_id = sdata.get("section_id")
            tone_style = sdata.get("tone_style", "Professional")
            actor = sdata.get("actor", "Proposal Writer")
            context_override = sdata.get("additional_context")
            
            res = proposal_generator_service.generate_single_section(
                db=db_session,
                proposal_plan_id=proposal_plan_id,
                section_id=section_id,
                tone_style=tone_style,
                actor=actor,
                additional_context=context_override
            )
            return AgentOutput(
                decision="SECTION_DRAFTED",
                confidence=res.confidence,
                reasoning=f"Generated draft for section using tone: {res.tone_style}",
                evidence=[],
                risks=[],
                recommendations=[],
                processing_time_ms=0.0,
                metadata={}
            )
        return StandardAgentExecutor.execute(db, self.agent_id, section_data, logic, config)
