from typing import Any, Optional, List
from pydantic import BaseModel

class PlannerOutput(BaseModel):
    is_complete: bool
    next_step: Optional[str] = None
    final_response: Optional[str] = None

class State(BaseModel):
    """The state of the agent."""
    query : str
    iteration: int = 0
    history: List[str] = []
    
class Dependencies(BaseModel):
    """The dependencies of the graph."""
    planner_agent : Any
    worker_agent : Any
