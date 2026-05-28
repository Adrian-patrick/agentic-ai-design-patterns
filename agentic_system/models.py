from typing import Any, List, Optional
from pydantic import BaseModel, Field

class MetricSummary(BaseModel):
    """Execution and evaluation metrics for a single code generation iteration."""
    iteration: int = Field(description="The generation/patch iteration number.")
    compilation_success: bool = Field(description="True if the code compiled without syntax errors.")
    syntax_error: Optional[str] = Field(default=None, description="The compilation error message if any.")
    test_pass_rate: float = Field(description="The percentage of unit tests that passed (0.0 to 1.0).")
    test_failure_details: Optional[str] = Field(default=None, description="Detailed test failures if any.")
    latency_ms: float = Field(description="Time taken to generate and test the code in milliseconds.")
    estimated_cost: float = Field(description="Calculated token/run cost in USD.")

class AlertInfo(BaseModel):
    """Details about a quality gate threshold breach."""
    gate_name: str = Field(description="The name of the gate (e.g. 'Syntax Check', 'Unit Tests', 'Latency SLA').")
    severity: str = Field(description="Severity: WARNING or CRITICAL.")
    message: str = Field(description="Detailed alert message.")

class State(BaseModel):
    """Memory state for the Evaluation & Monitoring pattern."""
    task_name: str = Field(description="Short identifier of the coding task.")
    prompt: str = Field(description="Instructions describing the function to write.")
    unit_tests: List[str] = Field(description="List of Python assertion statements to run against the code.")
    generated_code: Optional[str] = Field(default=None, description="The current generated code solution.")
    metrics_history: List[MetricSummary] = Field(default_factory=list, description="Historical record of iteration metrics.")
    active_alerts: List[AlertInfo] = Field(default_factory=list, description="List of generated alerts.")
    recovered: bool = Field(default=False, description="True if a previous gate breach was successfully resolved.")
    system_status: str = Field(default="Initializing", description="Current operations log detail.")

class Dependencies(BaseModel):
    """Injectable dependencies for the evaluation agents."""
    generator_agent: Any
    corrector_agent: Any
