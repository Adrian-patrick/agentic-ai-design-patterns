from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field

class PriorityScoreCard(BaseModel):
    """Structured evaluation and scoring metrics for a task priority classification."""
    business_value: float = Field(description="Business value score from 1.0 to 10.0 (Premium customer tier has higher value).")
    risk_level: float = Field(description="Risk multiplier from 1.0 (Low) to 3.0 (Critical).")
    effort: float = Field(description="Estimated effort from 1.0 (Very Low) to 5.0 (Very High).")
    urgency: float = Field(description="Time sensitivity score from 1.0 (Low) to 5.0 (Critical).")
    explanation: str = Field(description="Reasoning details behind the score assignment.")

class SupportTicket(BaseModel):
    """Data structure representing a support ticket in our priority queue."""
    id: str = Field(description="Unique identifier of the ticket.")
    customer_tier: Literal["premium", "standard"] = Field(description="Customer service tier.")
    initial_urgency: Literal["critical", "high", "normal", "low"] = Field(description="Stated ticket urgency level.")
    description: str = Field(description="Details of the support request.")
    age_days: int = Field(description="Number of days the ticket has been waiting in the queue.")
    progress_pct: int = Field(default=0, description="Percentage of processing progress (0 to 100).")
    priority_score: float = Field(default=0.0, description="Calculated final priority score.")
    score_card: Optional[PriorityScoreCard] = Field(default=None, description="Detailed priority scorecard.")

class State(BaseModel):
    """Memory state for the Prioritization and Preemption pattern."""
    queue: List[SupportTicket] = Field(default_factory=list, description="The ordered priority queue of active tickets.")
    running_task: Optional[SupportTicket] = Field(default=None, description="The ticket currently executing.")
    completed_tasks: List[SupportTicket] = Field(default_factory=list, description="Tickets successfully resolved.")
    preemption_events: List[str] = Field(default_factory=list, description="Audit log of runtime preemption events.")
    new_ticket_event: Optional[SupportTicket] = Field(default=None, description="Simulated incoming high-priority ticket.")
    system_status: str = Field(default="Initializing", description="Current operations log detail.")

class Dependencies(BaseModel):
    """Injectable dependencies for the prioritization agents."""
    prioritizer_agent: Any
    worker_agent: Any
