from typing import Any, Literal, Optional
from pydantic import BaseModel, Field

class InputEvaluation(BaseModel):
    """Structured evaluation of user input for safety and confidentiality."""
    risk_level: Literal["low", "medium", "very_high"] = Field(description="Assessed risk level.")
    pii_detected: bool = Field(description="True if PII like email, phone, credit card, etc., is detected.")
    injection_detected: bool = Field(description="True if prompt injection or system hijacking is detected.")
    redacted_input: str = Field(description="Input with PII redacted/masked, or original input if low risk.")
    reason: str = Field(description="Explanation for the risk assessment and redacts.")

class OutputEvaluation(BaseModel):
    """Structured evaluation of assistant output against compliance policies."""
    safe: bool = Field(description="True if the response complies with ethics, values, and legal rules.")
    policy_violation: Optional[str] = Field(default=None, description="Detailed policy violation if unsafe.")
    synthesis_decision: Literal["allow", "block", "edit"] = Field(description="Final action to take for the output.")

class State(BaseModel):
    """Memory state for the Guardrails/Safety pattern."""
    original_input: str = Field(description="Original user prompt.")
    cleaned_input: Optional[str] = Field(default=None, description="Cleaned or redacted input.")
    risk_level: str = Field(default="low", description="Evaluated input risk level.")
    worker_output: Optional[str] = Field(default=None, description="Output from the executor agent.")
    output_evaluation: Optional[OutputEvaluation] = Field(default=None, description="Evaluated output compliance report.")
    final_decision: str = Field(default="allow", description="Final decision: allow, block, edit.")
    rejection_reason: Optional[str] = Field(default=None, description="Reason for rejection if blocked.")
    system_status: str = Field(default="Initializing", description="Current operations log detail.")

class Dependencies(BaseModel):
    """Injectable dependencies for safety agents."""
    input_guardrail_agent: Any
    execution_agent: Any
    output_guardrail_agent: Any
