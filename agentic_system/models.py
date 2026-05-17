from typing import Any, Optional
from pydantic import BaseModel

class State(BaseModel):
    """The state of the agent."""
    query : str
    tool_agent_response : Optional[str] = None
    response_agent_response : Optional[str] = None
    
class Dependencies(BaseModel):
    """The dependencies of the graph."""
    tool_agent : Any
    response_agent : Any
