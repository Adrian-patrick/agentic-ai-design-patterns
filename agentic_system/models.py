from typing import Any, Optional
from pydantic import BaseModel

class State(BaseModel):
    """The state of the agent."""
    query : str
    summarizer_response : Optional[str] = None
    critic_response : Any | None = None
    max_iterations : Optional[int] = 3
    
class Dependencies(BaseModel):
    """The dependencies of the graph."""
    summarizer : Any
    critic : Any

