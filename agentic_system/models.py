from typing import Any, List, Optional
from pydantic import BaseModel, Field

class LogicalCheck(BaseModel):
    side: str = Field(description="Either 'FOR' or 'AGAINST'")
    fallacy_or_weakness: str = Field(description="Specific logical weakness or fallacy identified, or 'None' if logical.")

class PointRating(BaseModel):
    point: str = Field(description="Summary of the argument/point.")
    side: str = Field(description="FOR or AGAINST")
    strength_rank: int = Field(description="Rank from 1 (strongest) to 5 (weakest)")

class Verdict(BaseModel):
    logical_checks: List[LogicalCheck] = Field(description="Logical evaluations for both sides.")
    point_ratings: List[PointRating] = Field(description="Ranked and rated arguments.")
    synthesis: str = Field(description="A thorough, balanced final verdict synthesis and compromise proposal.")

class State(BaseModel):
    """Memory state for the Debate Reasoning pattern."""
    topic: str = Field(description="The core thesis/topic to debate.")
    arguments_for: Optional[str] = Field(default=None, description="Arguments supporting the thesis.")
    arguments_against: Optional[str] = Field(default=None, description="Arguments opposing the thesis.")
    verdict: Optional[Verdict] = Field(default=None, description="The final synthesized structured verdict.")
    system_status: str = Field(default="Initializing", description="Current operations log detail.")

class Dependencies(BaseModel):
    """Injectable dependencies for the debate agents."""
    proponent_agent: Any
    opponent_agent: Any
    judge_agent: Any



