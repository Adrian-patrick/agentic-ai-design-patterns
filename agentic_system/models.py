from typing import Any, Optional
from pydantic import BaseModel

class State(BaseModel):
    """The state of the agent."""
    query : str
    summarizer_response : Optional[str] = None
    pointer_response : Optional[str] = None
    responder_response : Optional[str] = None

class Dependencies(BaseModel):
    """The dependencies of the agent."""
    summarizer : Any
    pointer : Any
    responder : Any

