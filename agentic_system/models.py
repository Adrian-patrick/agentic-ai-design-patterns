from typing import Any, Optional
from pydantic import BaseModel, Field

class State(BaseModel):
    """Memory state for the Resource-Aware Optimization pattern."""
    query: str = Field(description="Original user query/task.")
    complexity: Optional[str] = Field(default=None, description="Classified complexity (simple or complex).")
    selected_model: Optional[str] = Field(default=None, description="Selected model tier (Low-Cost Model or High-Cost Model).")
    execution_response: Optional[str] = Field(default=None, description="Final response content.")
    estimated_cost: float = Field(default=0.0, description="Estimated execution cost in USD.")
    estimated_savings: float = Field(default=0.0, description="Estimated savings in USD.")
    system_status: str = Field(default="Initializing", description="Current operations log detail.")

class Dependencies(BaseModel):
    """Injectable dependencies for the optimization agents."""
    router_agent: Any
    execution_agent: Any

