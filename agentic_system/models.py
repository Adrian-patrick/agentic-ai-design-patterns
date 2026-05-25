from typing import Any, Optional
from pydantic import BaseModel, Field

class State(BaseModel):
    """Memory state for the direct Inter-Agent Communication (A2A) mesh."""
    query: str = Field(description="Original user task/query.")
    search_results: Optional[str] = Field(default=None, description="Gathers raw web search data.")
    synthesized_response: Optional[str] = Field(default=None, description="Compiled final summary and highlights.")
    system_status: str = Field(default="Initializing", description="Current operations log detail.")

class Dependencies(BaseModel):
    """Injectable dependencies for the direct peer agents."""
    search_agent: Any
    synthesis_agent: Any
