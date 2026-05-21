from typing import Any, Optional, List
from pydantic import BaseModel

class FeedbackSignal(BaseModel):
    user_correction: Optional[str] = None
    quality_rating: int  # 1 to 5
    automated_eval_score: float  # 0.0 to 1.0
    task_outcome: str  # 'success' or 'failure'

class FewShotExample(BaseModel):
    query: str
    preferred_response: str

class ValidationResult(BaseModel):
    is_adversarial: bool
    is_noisy: bool
    clean_feedback: Optional[str] = None

class AdaptationAction(BaseModel):
    action_type: str  # 'UpdatePrompts', 'AddExamples', 'UpdatePrefs'
    value: str  # The prompt update, preferred example, or new preference rule

class LearningReport(BaseModel):
    turns_operated: int
    improvements_deployed: List[str]
    failures_analyzed: List[str]
    system_status: str

class State(BaseModel):
    """The state of the learning & adaptation agent."""
    query: str
    response: Optional[str] = None
    
    # Feedback signals collected
    feedback: Optional[FeedbackSignal] = None
    
    # System settings (adapted dynamically)
    prompt_template: str = "Be a helpful assistant."
    few_shot_examples: List[FewShotExample] = []
    preference_rules: List[str] = []
    
    # Adaptation pipeline state
    is_malicious: bool = False
    validation_passed: bool = False
    adaptation_applied: Optional[str] = None
    monitor_status: str = "neutral"  # 'improvement', 'regression', 'neutral'
    learning_report: Optional[LearningReport] = None

class Dependencies(BaseModel):
    """The dependencies of the graph."""
    task_agent: Any
    feedback_validator_agent: Any
    learner_agent: Any
    evaluator_agent: Any
