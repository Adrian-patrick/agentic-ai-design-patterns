from typing import Any, Optional, List, Dict
from enum import Enum
from pydantic import BaseModel, Field

class ExceptionCategory(str, Enum):
    TEMPORARY = "Temporary"
    PERMANENT = "Permanent"
    CRITICAL = "Critical"

class BackupOption(str, Enum):
    SIMPLE_METHOD = "Simple Method"
    SAVED_DATA = "Saved Data"
    DEFAULT_ANSWER = "Default Answer"
    HUMAN_HELP = "Get Human Help"

class ErrorTriageResult(BaseModel):
    """Result of classifying and triaging an exception."""
    category: ExceptionCategory = Field(description="The classified type of the error (Temporary, Permanent, Critical).")
    severity: str = Field(description="Severity of the error (e.g., 'Low', 'Medium', 'High').")
    reasoning: str = Field(description="Detailed reasoning for the classification.")
    recommended_action: str = Field(description="Recommended recovery or handling strategy.")

class SafetyVerdict(BaseModel):
    """Verdict of the safety review after a critical exception."""
    is_safe: bool = Field(description="Whether it is safe to resume or continue the operation.")
    reasoning: str = Field(description="Detailed assessment of system hazards or limits.")
    next_action: str = Field(description="Next structural node to trigger: 'RESUME' or 'STOP'.")

class ErrorRecord(BaseModel):
    """Record of an error occurrence, captured for telemetry and learning."""
    attempt: int = Field(description="The attempt number during which the error occurred.")
    error_msg: str = Field(description="The exception or error message text.")
    category: str = Field(description="The triage category assigned to this error.")
    action_taken: str = Field(description="The action executed to handle or mitigate the error.")

class State(BaseModel):
    """State for the Exception Handling & Recovery orchestrator."""
    query: str = Field(description="The overall task or query description.")
    scenario: str = Field(default="transient_success", description="Active test scenario: 'transient_success', 'permanent_fallback', or 'critical_emergency'.")
    
    # Pre-execution checks
    safety_checked: bool = False
    
    # Execution metrics and attempt tracking
    call_attempts: int = 0
    max_retries: int = 3
    current_wait_sec: float = 0.0
    
    # Exception handling & telemetry
    error_history: List[ErrorRecord] = []
    last_error: Optional[str] = None
    backup_plan_selected: Optional[BackupOption] = None
    
    # Emergency state tracking
    emergency_saved: bool = False
    emergency_alerted: bool = False
    safety_verdict: Optional[SafetyVerdict] = None
    
    # Final resolution outcome
    operation_outcome: str = "PENDING"  # SUCCESS, RECOVERED, EMERGENCY_STOP
    learned_patterns: str = ""
    final_report: Optional[str] = None

class Dependencies(BaseModel):
    """Injectable agent dependencies."""
    safety_agent: Any
    service_agent: Any
    triage_agent: Any
    recovery_agent: Any
    learning_agent: Any
