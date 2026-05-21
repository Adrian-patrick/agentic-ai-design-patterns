from typing import Any, Optional, List, Dict
from pydantic import BaseModel, Field

class GoalSpec(BaseModel):
    """Specific, Measurable, Achievable, Relevant, Timebound objectives & rules."""
    specific: str = Field(description="Clear statement of the goal and objectives.")
    measurable: str = Field(description="The concrete, measurable success criteria.")
    achievable: str = Field(description="Feasibility and resources check description.")
    relevant: str = Field(description="Business value and alignment reasoning.")
    deadline_turns: int = Field(description="Maximum execution turns limit (e.g. 3).")
    budget_limit: int = Field(description="Maximum credit budget limit (e.g. 150).")
    quality_standard: str = Field(description="Quality constraints and SLAs (e.g. database_latency_ms < 50ms, data accuracy >= 99%).")

class TelemetryMetrics(BaseModel):
    """Telemetry metrics collected from system monitors."""
    database_latency_ms: float = Field(description="Simulated or measured database read latency in milliseconds.")
    inventory_accuracy_pct: float = Field(description="Calculated database inventory accuracy vs ground truth source as a percentage.")

    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self, key, default)

    def items(self):
        return self.model_dump().items()

class ProgressSnapshot(BaseModel):
    """Telemetry/metrics collected during work execution."""
    metrics_collected: TelemetryMetrics = Field(description="Key metrics parsed from telemetry. Must contain database_latency_ms and inventory_accuracy_pct.")
    budget_spent_this_turn: int = Field(description="Credits/cost spent during this turn.")
    current_status: str = Field(description="Current status assessment. Must be one of: 'on_track', 'off_track', or 'blocked'.")
    explanation: str = Field(description="Detailed reasoning for the status assessment.")

class FixAction(BaseModel):
    """Adaptation action proposed by the adapter agent."""
    fix_type: str = Field(description="Type of adaptation: 'ChangePlan', 'GetMoreResources', or 'ChangeGoal'.")
    value: str = Field(description="Detailed explanation/value of the fix action.")

class State(BaseModel):
    """State for the Goal Setting & Monitoring orchestrator."""
    query: str
    goal_spec: Optional[GoalSpec] = None
    current_plan: str = "None"
    last_worker_output: str = ""
    step_count: int = 0
    budget_spent: int = 0
    status_history: List[ProgressSnapshot] = []
    
    # Execution states
    is_achieved: bool = False
    is_blocked: bool = False
    fix_action: Optional[FixAction] = None
    final_report: Optional[str] = None

class Dependencies(BaseModel):
    """Injectable agent dependencies."""
    goal_creator_agent: Any
    worker_agent: Any
    monitor_agent: Any
    adapter_agent: Any
