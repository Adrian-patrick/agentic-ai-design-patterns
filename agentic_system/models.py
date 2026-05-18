from typing import Any, Optional, List
from pydantic import BaseModel

class MemoryItem(BaseModel):
    content: str
    category: str  # 'Short-Term', 'Episodic', 'Long-Term'
    tags: List[str] = []

class MemoryClassifierOutput(BaseModel):
    has_new_memories: bool
    memories: List[MemoryItem] = []

class State(BaseModel):
    """The state of the agent."""
    query : str
    response: Optional[str] = None
    loaded_memories: List[str] = []
    
    # Memory stores (normally in a database, here in state)
    short_term_buffer: List[str] = []  # Conversation buffer
    episodic_memory: List[MemoryItem] = []  # Experience event store
    long_term_memory: List[MemoryItem] = []  # Knowledge base

class Dependencies(BaseModel):
    """The dependencies of the graph."""
    responder_agent : Any
    memory_classifier_agent : Any
    compressor_agent: Any
