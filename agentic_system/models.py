from typing import Any, Optional, List
from pydantic import BaseModel

class ClassifierOutput(BaseModel):
    requires_summarizer: bool
    requires_pointer: bool

class OrchestratorInstructions(BaseModel):
    summarizer_instruction: Optional[str] = None
    pointer_instruction: Optional[str] = None

class State(BaseModel):
    """The state of the agent."""
    query : str
    content: str = ""
    requires_summarizer: bool = False
    requires_pointer: bool = False
    summarizer_instruction: Optional[str] = None
    pointer_instruction: Optional[str] = None
    summarizer_output: Optional[str] = None
    pointer_output: Optional[str] = None
    final_response: Optional[str] = None
    
class Dependencies(BaseModel):
    """The dependencies of the graph."""
    classifier_agent : Any
    orchestrator_agent : Any
    summarizer_agent : Any
    pointer_agent : Any
