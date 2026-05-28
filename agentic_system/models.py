from typing import Any, List, Literal, Optional
from pydantic import BaseModel, Field

class ScoutedSource(BaseModel):
    """Represents a piece of raw information collected during broad scouting."""
    title: str = Field(description="Title of the paper, patent, or resource.")
    author: str = Field(description="Author, inventor, or origin details.")
    source_type: Literal["Academic Paper", "Patent", "Expert Interview", "Web Resource"] = Field(description="Origin source classification.")
    summary: str = Field(description="Summary of key findings, data points, or ideas.")

class ClusteredTheme(BaseModel):
    """Represents a conceptual theme emerged by clustering scouted knowledge."""
    name: str = Field(description="Short descriptive name of the conceptual theme.")
    description: str = Field(description="Detailed description mapping the research area.")
    associated_source_titles: List[str] = Field(description="List of scouted source titles grouped under this theme.")

class ThemeEvaluation(BaseModel):
    """Structured evaluation of an emerging theme against selection criteria."""
    theme_name: str = Field(description="The conceptual theme under evaluation.")
    novelty_score: float = Field(description="Novelty rating from 1.0 (highly saturated) to 10.0 (groundbreaking).")
    potential_impact: float = Field(description="Potential impact score from 1.0 (niche) to 10.0 (transformational).")
    feasibility: float = Field(description="Technical or operational feasibility from 1.0 (hypothetical) to 10.0 (near-term ready).")
    knowledge_gaps: float = Field(description="Knowledge gap score from 1.0 (fully understood) to 10.0 (completely unexplored).")
    justification: str = Field(description="Justification reasoning behind the scores assigned.")

class DeepDiveArtifacts(BaseModel):
    """Structured research artifacts extracted during deep target investigation."""
    notes: str = Field(description="Comprehensive research and conceptual modeling notes.")
    bibliography: List[str] = Field(description="Curated references, key papers, or citations.")
    hypotheses: List[str] = Field(description="List of testable scientific hypotheses generated for experimental validation.")

class State(BaseModel):
    """Memory state for the Exploration & Discovery pattern."""
    goal: str = Field(description="The primary research goal or technology scouting topic.")
    sources: List[ScoutedSource] = Field(default_factory=list, description="List of scouted sources gathered.")
    themes: List[ClusteredTheme] = Field(default_factory=list, description="Emerged clustered conceptual themes.")
    theme_evaluations: List[ThemeEvaluation] = Field(default_factory=list, description="Score cards for all themes.")
    selected_target: Optional[ClusteredTheme] = Field(default=None, description="The conceptual theme chosen for deep dive.")
    artifacts: Optional[DeepDiveArtifacts] = Field(default=None, description="Extracted deep dive conceptual artifacts.")
    system_status: str = Field(default="Initializing", description="Current operations log detail.")

class Dependencies(BaseModel):
    """Injectable dependencies for the discovery agents."""
    scout_agent: Any
    clustering_agent: Any
    target_selector_agent: Any
    deep_dive_agent: Any
