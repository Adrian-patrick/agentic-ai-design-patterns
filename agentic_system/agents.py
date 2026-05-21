import os
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from .config import create_model
from .prompts import (
    goal_creator_system_prompt,
    worker_system_prompt,
    monitor_system_prompt,
    adapter_system_prompt,
)
from .models import GoalSpec, ProgressSnapshot, FixAction

# Check if Azure OpenAI API key is provided
IS_CONFIGURED = all(
    os.environ.get(var) for var in ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]
)

if not IS_CONFIGURED:
    print("[Info] Azure credentials not found. Falling back to local high-fidelity mock agents for showcase...")

class GoalCreatorAgent:
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=goal_creator_system_prompt,
                output_type=GoalSpec,
                retries=3,
            )

    async def run(self, query: str) -> GoalSpec:
        if not IS_CONFIGURED:
            # Fallback high-fidelity GoalSpec
            return GoalSpec(
                specific="Configure and monitor a supply chain inventory tracking service.",
                measurable="Database read latency < 50ms, data accuracy >= 99.0%",
                achievable="Using Redis cache for hot reads and PostgreSQL storage.",
                relevant="Align inventory levels with customer demand dynamically.",
                deadline_turns=3,
                budget_limit=150,
                quality_standard="Latency SLA < 50ms, Accuracy SLA >= 99.0%"
            )
        result = await self.agent.run(query)
        return result.output

class WorkerAgent:
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=worker_system_prompt,
                output_type=str,
                retries=3,
            )

    async def run(self, goal_spec: GoalSpec, current_plan: str, current_turn: int) -> str:
        if not IS_CONFIGURED:
            # Fallback high-fidelity worker descriptions based on the turn
            if current_turn == 1:
                return "Completed initial supply chain inventory tracking pipeline. PostgreSQL tables populated with inventory levels."
            elif current_turn == 2:
                return "Implemented a Redis caching layer as per the adjusted plan to bypass PostgreSQL for hot reads and reduce latency."
            else:
                return "Finalized the supply chain system. All inventory calculations verified, caching layer fully integrated, ready for rollout."
                
        prompt = (
            f"Goal Spec: {goal_spec.model_dump_json()}\n"
            f"Current Execution Plan: {current_plan}\n"
            f"Current Turn: {current_turn}\n\n"
            "Please perform the necessary engineering tasks for this turn towards the goal."
        )
        result = await self.agent.run(prompt)
        return result.output

class MonitorAgent:
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=monitor_system_prompt,
                output_type=ProgressSnapshot,
                retries=3,
            )

    async def run(self, goal_spec: GoalSpec, worker_output: str, telemetry: dict) -> ProgressSnapshot:
        if not IS_CONFIGURED:
            # Fallback monitor snapshots
            latency = telemetry.get("database_latency_ms", 999)
            accuracy = telemetry.get("inventory_accuracy_pct", 0.0)
            cost = telemetry.get("credits_consumed", 0)
            
            if latency > 50:
                return ProgressSnapshot(
                    metrics_collected={"database_latency_ms": latency, "inventory_accuracy_pct": accuracy},
                    budget_spent_this_turn=cost,
                    current_status="off_track",
                    explanation="High database read latency of 120ms violates the SLA threshold of < 50ms."
                )
            else:
                accuracy_str = "achieved" if accuracy >= 100.0 else "on track"
                return ProgressSnapshot(
                    metrics_collected={"database_latency_ms": latency, "inventory_accuracy_pct": accuracy},
                    budget_spent_this_turn=cost,
                    current_status="on_track",
                    explanation=f"Telemetry metrics satisfied. Caching active (latency {latency}ms). Accuracy {accuracy_str} ({accuracy}%)."
                )

        prompt = (
            f"Goal Standards: {goal_spec.model_dump_json()}\n"
            f"Worker Output for this turn: {worker_output}\n"
            f"Raw Telemetry collected: {telemetry}\n\n"
            "Perform progress audit and return the snapshot metrics and status."
        )
        result = await self.agent.run(prompt)
        return result.output

class AdapterAgent:
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=adapter_system_prompt,
                output_type=FixAction,
                retries=3,
            )

    async def run(self, goal_spec: GoalSpec, worker_output: str, snapshot: ProgressSnapshot) -> FixAction:
        if not IS_CONFIGURED:
            # Fallback FixAction
            return FixAction(
                fix_type="ChangePlan",
                value="Implement a Redis caching layer for hot reads to bypass direct PostgreSQL table scanning and reduce query latency."
            )

        prompt = (
            f"Goal Spec: {goal_spec.model_dump_json()}\n"
            f"Worker Output: {worker_output}\n"
            f"Monitor Assessment: {snapshot.model_dump_json()}\n\n"
            "Recommend optimal adjustment path (fix_type and value)."
        )
        result = await self.agent.run(prompt)
        return result.output
