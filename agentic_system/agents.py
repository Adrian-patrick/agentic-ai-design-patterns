import os
from typing import Optional
from pydantic_ai import Agent
from .config import create_model
from .prompts import (
    gate_identifier_system_prompt,
    ui_presenter_system_prompt,
    feedback_learning_system_prompt,
    fatigue_monitor_system_prompt,
)
from .models import (
    GateType,
    DecisionType,
    QueueItem,
    HumanDecision,
    FeedbackLog,
)

# Check if Azure OpenAI API key is provided
IS_CONFIGURED = all(
    os.environ.get(var) for var in ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]
)

if not IS_CONFIGURED:
    print("[Info] Azure credentials not found. Falling back to local high-fidelity mock agents for showcase...")

class DecisionGateAgent:
    """Classifies incoming task queries into one of the four HITL Decision Gates."""
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=gate_identifier_system_prompt,
                retries=3,
            )

    async def run(self, query: str, scenario: str) -> GateType:
        if not IS_CONFIGURED:
            # High-fidelity mock gate selection based on scenario
            if scenario == "approve":
                return GateType.APPROVE
            elif scenario == "deny":
                return GateType.REVIEW
            elif scenario == "edit":
                return GateType.EDIT
            else:
                return GateType.COMPLEX

        result = await self.agent.run(f"Query: {query}\nScenario: {scenario}")
        content = result.output.strip()
        for gate in GateType:
            if gate.value.lower() in content.lower():
                return gate
        return GateType.APPROVE

class UIPresenterAgent:
    """Prepares detailed Review Queue items with SLA timers and original content context."""
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=ui_presenter_system_prompt,
                output_type=QueueItem,
                retries=3,
            )

    async def run(self, query: str, scenario: str) -> QueueItem:
        if not IS_CONFIGURED:
            # High-fidelity queue generation
            if scenario == "approve":
                return QueueItem(
                    urgency="Low",
                    content_draft="Blogging Draft: Agentic design patterns, such as Human-in-the-Loop systems, ensure safety and trust in production AI models.",
                    original_agent_output="Agentic design patterns, such as Human-in-the-Loop systems, ensure safety...",
                    sla_timer_sec=300,
                    context_summary="Marketing blog draft review"
                )
            elif scenario == "deny":
                return QueueItem(
                    urgency="Medium",
                    content_draft="Resume Summary - Candidate Name: Bob Rustacean, Tech Stack: Python, C++, Go. Recommendation: Recommend Hire for Rust Team.",
                    original_agent_output="Recommend Hire for Rust Team.",
                    sla_timer_sec=180,
                    context_summary="Resume Screening Gate - Tech Recruiter review"
                )
            elif scenario == "edit":
                return QueueItem(
                    urgency="Medium",
                    content_draft="Target Translation: French: Bonjour le monde (Original: Hello World)",
                    original_agent_output="Bonjour le monde",
                    sla_timer_sec=180,
                    context_summary="French Translation review gate"
                )
            else:
                return QueueItem(
                    urgency="High",
                    content_draft="Initiate bank wire transfer: $12,500.00 to account ACT-8812. Reason: Enterprise client refund.",
                    original_agent_output="Wire $12500 enterprise refund",
                    sla_timer_sec=60,
                    context_summary="Complex Case: Refund exceeds standard agent limit of $10,000"
                )

        prompt = (
            f"Query: {query}\n"
            f"Scenario: {scenario}\n"
            "Build the queue presentation."
        )
        result = await self.agent.run(prompt)
        return result.output

class FeedbackLearningAgent:
    """Synthesizes human reviews, edits, and rejections into structured guidelines to train the agent."""
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=feedback_learning_system_prompt,
                output_type=FeedbackLog,
                retries=3,
            )

    async def run(self, decision: HumanDecision) -> FeedbackLog:
        if not IS_CONFIGURED:
            # High-fidelity SRE training logs
            if decision.decision == DecisionType.APPROVE:
                return FeedbackLog(
                    action=DecisionType.APPROVE,
                    learning_points="Content draft was accurate, required no manual modifications.",
                    guidelines_updated="Continue applying matching voice and clarity rules."
                )
            elif decision.decision == DecisionType.DENY:
                return FeedbackLog(
                    action=DecisionType.DENY,
                    learning_points=f"Rejection: {decision.reviewer_feedback}. Candidate lacks critical Rust experience.",
                    guidelines_updated="Update filtering constraint: candidates for Rust team must explicitly list Rust, not just generic Go/Python."
                )
            elif decision.decision == DecisionType.EDIT:
                return FeedbackLog(
                    action=DecisionType.EDIT,
                    learning_points=f"Human Edit: Original draft '{decision.reviewer_feedback}' modified to '{decision.edited_content}'.",
                    guidelines_updated="Update translation engine prompts to prioritize colloquial phrasing ('Bonjour tout le monde') for audience-facing messages."
                )
            else:
                return FeedbackLog(
                    action=DecisionType.TAKEOVER,
                    learning_points=f"Takeover: {decision.takeover_reason}. Wire transfers >= $10,000 require senior financial clearance.",
                    guidelines_updated="System rules updated: block any automatic wire transfers >= $10,000. Force manual handoff at node start."
                )

        prompt = (
            f"Reviewer Decision: {decision.decision.value}\n"
            f"Feedback notes: {decision.reviewer_feedback}\n"
            f"Edited content: {decision.edited_content}\n"
            f"Takeover reason: {decision.takeover_reason}\n\n"
            "Synthesize this into a training feedback log."
        )
        result = await self.agent.run(prompt)
        return result.output

class FatigueMonitorAgent:
    """SRE Human Fatigue monitor assessing human queues and proposing load balancing adjustments."""
    async def evaluate(self, scenario: str) -> tuple[float, str]:
        print("   [Fatigue Monitor] Auditing reviewer key indicators (Queue length, SLA latency)...")
        if scenario == "takeover_fatigue":
            # Simulate high reviewer fatigue spike
            score = 0.85
            action = "REDUCE"
            print(f"   [Fatigue Monitor] ALERT: Reviewer Fatigue index = {score:.2f} (SPIKE)! Queue overload detected.")
        else:
            score = 0.22
            action = "MAINTAIN"
            print(f"   [Fatigue Monitor] Reviewer Fatigue index = {score:.2f} (Normal). Processing rate steady.")
        return score, action
