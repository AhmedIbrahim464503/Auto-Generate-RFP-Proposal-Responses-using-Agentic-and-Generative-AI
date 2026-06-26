from typing import Callable, Dict, List, Any
from backend.app.core.logger import logger

class AIEventBus:
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, listener: Callable[[Dict[str, Any]], None]):
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(listener)

    def publish(self, event_type: str, payload: Dict[str, Any]):
        logger.info(f"AIEventBus: Publishing event {event_type}")
        if event_type in self._listeners:
            for listener in self._listeners[event_type]:
                try:
                    listener(payload)
                except Exception as e:
                    logger.error(f"AIEventBus listener failed for event {event_type}: {str(e)}")

# Global event bus instance
event_bus = AIEventBus()
