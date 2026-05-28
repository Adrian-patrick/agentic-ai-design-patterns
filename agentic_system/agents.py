import os
from pydantic_ai import Agent
from .config import create_model
from .models import LogicalCheck, PointRating, Verdict
from .prompts import (
    proponent_system_prompt,
    opponent_system_prompt,
    judge_system_prompt,
)

# Check if Azure OpenAI API key is provided
IS_CONFIGURED = all(
    os.environ.get(var) for var in ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]
)

if not IS_CONFIGURED:
    print("[Info] Azure credentials not found. Falling back to local high-fidelity mock agents for showcase...")

class ProponentAgent:
    """Specialized agent arguing FOR the thesis/topic."""
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=proponent_system_prompt,
                retries=3,
            )

    async def run(self, topic: str) -> str:
        if not IS_CONFIGURED:
            print("   [Proponent Agent] Simulating offline FOR argument generation...")
            return (
                "1. Existential Risk: Artificial General Intelligence (AGI) possesses capabilities that, if unchecked, could lead to human extinction. Regulating early ensures safety boundaries.\n"
                "2. Alignment Problem: Ensuring AGI goals align with human values is an unsolved mathematical problem. Regulatory oversight forces mandatory safety alignment testing.\n"
                "3. Social Stability: Unregulated AGI will cause sudden, massive labor displacement and economic inequality that could collapse modern social security networks."
            )
        result = await self.agent.run(f"Construct arguments FOR this topic: {topic}")
        return result.output

class OpponentAgent:
    """Specialized agent arguing AGAINST the thesis/topic."""
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=opponent_system_prompt,
                retries=3,
            )

    async def run(self, topic: str) -> str:
        if not IS_CONFIGURED:
            print("   [Opponent Agent] Simulating offline AGAINST argument generation...")
            return (
                "1. Stifling Innovation: Heavy global regulation creates regulatory capture, leaving only massive corporations in control and halting open-source breakthroughs.\n"
                "2. Geopolitical Arbitrage: If democratic nations heavily regulate AGI, non-democratic states will ignore the rules, leading to a major strategic security deficit.\n"
                "3. Premature Rules: We do not yet understand AGI architectures. Setting hard rules today will regulate hypothetical science-fiction risks rather than actual near-term issues."
            )
        result = await self.agent.run(f"Construct arguments AGAINST this topic: {topic}")
        return result.output

class JudgeAgent:
    """Specialized agent analyzing, grading, ranking, and synthesizing the final verdict."""
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=judge_system_prompt,
                output_type=Verdict,
                retries=3,
            )

    async def run(self, topic: str, arguments_for: str, arguments_against: str) -> Verdict:
        if not IS_CONFIGURED:
            print("   [Judge Agent] Simulating offline verdict synthesis...")
            return Verdict(
                logical_checks=[
                    LogicalCheck(side="FOR", fallacy_or_weakness="Relies heavily on speculative future existential risk scenarios."),
                    LogicalCheck(side="AGAINST", fallacy_or_weakness="Assumes regulation necessarily halts innovation rather than shaping it safely.")
                ],
                point_ratings=[
                    PointRating(point="Geopolitical Arbitrage (Opponent)", side="AGAINST", strength_rank=1),
                    PointRating(point="Alignment Problem (Proponent)", side="FOR", strength_rank=2),
                    PointRating(point="Stifling Innovation (Opponent)", side="AGAINST", strength_rank=3),
                    PointRating(point="Existential Risk (Proponent)", side="FOR", strength_rank=4)
                ],
                synthesis=(
                    "A balanced synthesis recommends a 'Phased Safe Harbor' model: regulate the direct deployments of highly high-risk physical-world interfaces (like defense or power grids) while maintaining wide freedom, tax incentives, and lightweight sandbox environments for foundational research and open-source models."
                )
            )

        prompt = (
            f"Topic: {topic}\n\n"
            f"Arguments FOR:\n{arguments_for}\n\n"
            f"Arguments AGAINST:\n{arguments_against}"
        )
        result = await self.agent.run(prompt)
        return result.output
