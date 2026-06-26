from typing import Any, Dict
from backend.app.schemas.agent import AgentOutput
from backend.app.core.logger import logger

class BaseAgent:
    def __init__(self, agent_id: str):
        self.agent_id = agent_id

    def initialize(self, input_data: Any, config: Dict[str, Any] = None) -> None:
        logger.info(f"Agent {self.agent_id}: Initializing")

    def validate_input(self, input_data: Any) -> bool:
        logger.info(f"Agent {self.agent_id}: Validating input")
        return True

    def prepare_context(self, input_data: Any, db: Any) -> Dict[str, Any]:
        logger.info(f"Agent {self.agent_id}: Preparing context")
        return {"input_data": input_data}

    def retrieve_tools(self, db: Any) -> list:
        logger.info(f"Agent {self.agent_id}: Retrieving tools")
        return []

    def execute(self, context: Dict[str, Any], tools: list) -> Any:
        logger.info(f"Agent {self.agent_id}: Executing logic")
        raise NotImplementedError("Subclasses must implement execute method")

    def validate_output(self, output: Any) -> bool:
        logger.info(f"Agent {self.agent_id}: Validating output")
        return True

    def persist(self, db: Any, output: Any) -> None:
        logger.info(f"Agent {self.agent_id}: Persisting execution records")

    def emit_events(self, event_type: str, payload: Dict[str, Any]) -> None:
        from backend.app.core.events.event_bus import event_bus
        event_bus.publish(event_type, payload)

    def cleanup(self) -> None:
        logger.info(f"Agent {self.agent_id}: Cleanup lifecycle")

    def run(self, db: Any, input_data: Any, config: Dict[str, Any] = None) -> AgentOutput:
        self.initialize(input_data, config)
        if not self.validate_input(input_data):
            raise ValueError(f"Agent {self.agent_id}: Input validation failed.")

        context = self.prepare_context(input_data, db)
        tools = self.retrieve_tools(db)
        
        self.emit_events("AgentStarted", {"agent_id": self.agent_id})

        output_raw = self.execute(context, tools)

        if not self.validate_output(output_raw):
            self.emit_events("ValidationFailed", {"agent_id": self.agent_id})
            raise ValueError(f"Agent {self.agent_id}: Output validation failed.")

        self.persist(db, output_raw)
        
        self.emit_events("AgentCompleted", {"agent_id": self.agent_id})
        self.cleanup()

        if isinstance(output_raw, AgentOutput):
            return output_raw
        
        return AgentOutput(
            decision="SUCCESS",
            confidence=0.9,
            reasoning=str(output_raw),
            evidence=[],
            risks=[],
            recommendations=[],
            processing_time_ms=0.0,
            metadata={}
        )
