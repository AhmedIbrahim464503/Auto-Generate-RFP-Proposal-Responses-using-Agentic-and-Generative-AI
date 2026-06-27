import time
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from sqlalchemy.orm import Session
from langgraph.graph import StateGraph, END

from backend.app.schemas.workflow import WorkflowGraphState
from backend.app.models.workflow import (
    WorkflowExecution,
    WorkflowCheckpoint,
    WorkflowEvent,
    WorkflowMetric,
    WorkflowApprovalGate
)
from backend.app.core.workflow.workflow_nodes import (
    DocumentProcessingNode,
    RequirementExtractionNode,
    DepartmentReviewNode,
    QualificationNode,
    QualificationApprovalGateNode,
    ProposalPlanningNode,
    KnowledgeRetrievalNode,
    ProposalGenerationNode,
    ReviewRefinementNode,
    ProposalAssemblyNode
)
from backend.app.core.logger import logger

class WorkflowOrchestratorService:
    def __init__(self):
        # Register nodes mapping
        self.nodes_map = {
            "document_processing": DocumentProcessingNode(),
            "requirement_extraction": RequirementExtractionNode(),
            "department_review": DepartmentReviewNode(),
            "qualification": QualificationNode(),
            "qualification_approval_gate": QualificationApprovalGateNode(),
            "proposal_planning": ProposalPlanningNode(),
            "knowledge_retrieval": KnowledgeRetrievalNode(),
            "proposal_generation": ProposalGenerationNode(),
            "review_refinement": ReviewRefinementNode(),
            "proposal_assembly": ProposalAssemblyNode()
        }
        self.compiled_graph = self._build_graph()

    def _build_graph(self):
        # Build LangGraph StateGraph
        workflow = StateGraph(Dict[str, Any])

        # Nodes define wrapper matching LangGraph expectations
        def make_node_fn(node_name: str):
            def node_fn(state: Dict[str, Any]) -> Dict[str, Any]:
                node_obj = self.nodes_map[node_name]
                # Prepare typed state
                typed_state = WorkflowGraphState(**state)
                # execute
                new_state = node_obj.execute(typed_state, None) # DB Session gets passed in real runs
                return new_state.model_dump()
            return node_fn

        for name in self.nodes_map:
            workflow.add_node(name, make_node_fn(name))

        # Define linear edges
        workflow.set_entry_point("document_processing")
        workflow.add_edge("document_processing", "requirement_extraction")
        workflow.add_edge("requirement_extraction", "department_review")
        workflow.add_edge("department_review", "qualification")
        workflow.add_edge("qualification", "qualification_approval_gate")
        
        # Conditional edge from gate
        def gate_routing(state: Dict[str, Any]) -> str:
            status = state.get("execution_status", "running")
            curr = state.get("current_node", "")
            if status == "paused":
                return END
            elif status == "failed":
                return END
            return "proposal_planning"

        workflow.add_conditional_edges("qualification_approval_gate", gate_routing, {
            END: END,
            "proposal_planning": "proposal_planning"
        })

        workflow.add_edge("proposal_planning", "knowledge_retrieval")
        workflow.add_edge("knowledge_retrieval", "proposal_generation")
        workflow.add_edge("proposal_generation", "review_refinement")
        workflow.add_edge("review_refinement", "proposal_assembly")
        workflow.add_edge("proposal_assembly", END)

        return workflow.compile()

    def start_execution(self, db: Session, workflow_name: str, proposal_id: str) -> WorkflowExecution:
        # Create execution
        initial_state = WorkflowGraphState(
            workflow_metadata={"workflow_name": workflow_name, "started_by": "system"},
            proposal_metadata={"proposal_id": proposal_id},
            current_node="init",
            execution_status="running"
        )
        
        db_exec = WorkflowExecution(
            workflow_name=workflow_name,
            proposal_id=proposal_id,
            status="running",
            current_node="init",
            state=initial_state.model_dump()
        )
        db.add(db_exec)
        db.commit()
        db.refresh(db_exec)

        self._log_event(db, db_exec.id, "WorkflowStarted", {"proposal_id": proposal_id})

        # Run starting
        return self._run_workflow_loop(db, db_exec)

    def resume_execution(self, db: Session, execution_id: str, decision_payload: Dict[str, Any]) -> WorkflowExecution:
        db_exec = db.query(WorkflowExecution).filter(WorkflowExecution.id == execution_id).first()
        if not db_exec:
            raise ValueError("Execution not found")

        state_data = WorkflowGraphState(**db_exec.state)
        current_node_name = db_exec.current_node

        node_obj = self.nodes_map.get(current_node_name)
        if not node_obj:
            raise ValueError(f"Invalid current node: {current_node_name}")

        self._log_event(db, db_exec.id, "HumanApprovalRequested", {"node": current_node_name, "payload": decision_payload})

        # Resume state
        updated_state = node_obj.resume(state_data, decision_payload, db)
        db_exec.state = updated_state.model_dump()
        db_exec.current_node = current_node_name
        db_exec.status = updated_state.execution_status
        db.commit()

        self._log_event(db, db_exec.id, "HumanApproved", {"node": current_node_name, "action": decision_payload.get("action")})

        if updated_state.execution_status == "running":
            # Continue running next nodes
            return self._run_workflow_loop(db, db_exec)
        else:
            db_exec.status = "failed"
            db.commit()
            self._log_event(db, db_exec.id, "WorkflowFailed", {"reason": "Rejected by human approval"})
            return db_exec

    def rollback_execution(self, db: Session, execution_id: str, target_node: str) -> WorkflowExecution:
        db_exec = db.query(WorkflowExecution).filter(WorkflowExecution.id == execution_id).first()
        if not db_exec:
            raise ValueError("Execution not found")

        # Find latest checkpoint matching target_node
        checkpoint = db.query(WorkflowCheckpoint).filter(
            WorkflowCheckpoint.execution_id == execution_id,
            WorkflowCheckpoint.node_name == target_node
        ).order_by(WorkflowCheckpoint.timestamp.desc()).first()

        if not checkpoint:
            raise ValueError(f"No checkpoint found for node {target_node}")

        # Restore state
        db_exec.state = checkpoint.state
        db_exec.current_node = target_node
        db_exec.status = "running"
        db_exec.error_message = None
        db.commit()

        self._log_event(db, db_exec.id, "CheckpointRestored", {"target_node": target_node})

        # Run loop from that node
        return self._run_workflow_loop(db, db_exec)

    def retry_node(self, db: Session, execution_id: str) -> WorkflowExecution:
        db_exec = db.query(WorkflowExecution).filter(WorkflowExecution.id == execution_id).first()
        if not db_exec:
            raise ValueError("Execution not found")

        db_exec.status = "running"
        db_exec.error_message = None
        db.commit()

        self._log_event(db, db_exec.id, "NodeStarted", {"node": db_exec.current_node, "retry": True})

        return self._run_workflow_loop(db, db_exec)

    def _run_workflow_loop(self, db: Session, db_exec: WorkflowExecution) -> WorkflowExecution:
        state_data = WorkflowGraphState(**db_exec.state)
        node_order = [
            "document_processing",
            "requirement_extraction",
            "department_review",
            "qualification",
            "qualification_approval_gate",
            "proposal_planning",
            "knowledge_retrieval",
            "proposal_generation",
            "review_refinement",
            "proposal_assembly"
        ]

        start_index = 0
        if db_exec.current_node != "init":
            try:
                start_index = node_order.index(db_exec.current_node)
            except ValueError:
                start_index = 0

        for i in range(start_index, len(node_order)):
            node_name = node_order[i]
            node_obj = self.nodes_map[node_name]
            
            db_exec.current_node = node_name
            db_exec.status = "running"
            db.commit()
            
            self._log_event(db, db_exec.id, "NodeStarted", {"node": node_name})
            
            start_time = time.time()
            try:
                state_data.current_node = node_name
                state_data = node_obj.execute(state_data, db)
                
                # Check status (e.g. paused)
                if state_data.execution_status == "paused":
                    db_exec.status = "paused"
                    db_exec.state = state_data.model_dump()
                    db.commit()
                    self._log_event(db, db_exec.id, "CheckpointSaved", {"node": node_name, "status": "paused"})
                    break
                elif state_data.execution_status == "failed":
                    db_exec.status = "failed"
                    db_exec.state = state_data.model_dump()
                    db.commit()
                    self._log_event(db, db_exec.id, "WorkflowFailed", {"node": node_name})
                    break
                
                duration = time.time() - start_time
                self._save_metric(db, db_exec.id, node_name, duration)
                
                # Save checkpoint
                checkpoint = WorkflowCheckpoint(
                    execution_id=db_exec.id,
                    node_name=node_name,
                    state=state_data.model_dump(),
                    timestamp=datetime.utcnow()
                )
                db.add(checkpoint)
                
                self._log_event(db, db_exec.id, "NodeCompleted", {"node": node_name})
                
            except Exception as e:
                logger.error(f"Error in node {node_name}: {str(e)}")
                db_exec.status = "failed"
                db_exec.error_message = str(e)
                state_data.errors.append(str(e))
                db_exec.state = state_data.model_dump()
                db.commit()
                self._log_event(db, db_exec.id, "NodeFailed", {"node": node_name, "error": str(e)})
                break
        else:
            # Loop finished completely
            db_exec.status = "completed"
            state_data.execution_status = "completed"
            db_exec.state = state_data.model_dump()
            db.commit()
            self._log_event(db, db_exec.id, "WorkflowCompleted", {})

        return db_exec

    def _log_event(self, db: Session, execution_id: str, event_type: str, payload: Dict[str, Any]) -> None:
        event = WorkflowEvent(
            execution_id=execution_id,
            event_type=event_type,
            payload=payload,
            timestamp=datetime.utcnow()
        )
        db.add(event)
        db.commit()

    def _save_metric(self, db: Session, execution_id: str, node_name: str, duration: float) -> None:
        metric = WorkflowMetric(
            execution_id=execution_id,
            node_name=node_name,
            duration_seconds=duration,
            tokens_used=100,  # Simulated standard token count per node
            cost=0.002,      # Simulated standard cost per node
            created_at=datetime.utcnow()
        )
        db.add(metric)
        db.commit()
