from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from .config import create_model
from .prompts import (
    task_system_prompt,
    feedback_validator_system_prompt,
    learner_system_prompt,
    evaluator_system_prompt,
)
from .models import ValidationResult, AdaptationAction

class TaskAgent:
    def __init__(self):
        self.agent = Agent(
            model=create_model(),
            system_prompt=task_system_prompt,
            output_type=str,
        )

    async def run(self, query: str, prompt_template: str, few_shot_examples: list, preference_rules: list[str]) -> str:
        # Dynamically inject configuration into system prompt
        self.agent.system_prompt = task_system_prompt.format(
            prompt_template=prompt_template,
            few_shot_examples=str(few_shot_examples),
            preference_rules=str(preference_rules)
        )
        result = await self.agent.run(query)
        return result.output

class FeedbackValidatorAgent:
    def __init__(self):
        self.agent = Agent(
            model=create_model(),
            system_prompt=feedback_validator_system_prompt,
            output_type=ValidationResult,
        )

    async def run(self, query: str, user_correction: str = None) -> ValidationResult:
        prompt = f"User Query: {query}\nFeedback Correction: {user_correction or 'None'}"
        result = await self.agent.run(prompt)
        return result.output

class LearnerAgent:
    def __init__(self):
        self.agent = Agent(
            model=create_model(),
            system_prompt=learner_system_prompt,
            output_type=AdaptationAction,
        )

    async def run(self, query: str, response: str, user_correction: str) -> AdaptationAction:
        prompt = (
            f"Original Query: {query}\n"
            f"Failed Response: {response}\n"
            f"User Correction: {user_correction}\n\n"
            "Please analyze the correction and decide on the best optimization step."
        )
        result = await self.agent.run(prompt)
        return result.output

class EvaluatorAgent:
    def __init__(self):
        self.agent = Agent(
            model=create_model(),
            system_prompt=evaluator_system_prompt,
            output_type=float,
        )

    async def run(self, query: str, failed_response: str, user_correction: str, proposed_action: str, proposed_value: str) -> float:
        prompt = (
            f"Query: {query}\n"
            f"Failed Response: {failed_response}\n"
            f"Correction: {user_correction}\n"
            f"Proposed Update Type: {proposed_action}\n"
            f"Proposed Update Value: {proposed_value}\n\n"
            "Will this update solve the issue and score high on criteria? Output score 0.0 to 1.0."
        )
        result = await self.agent.run(prompt)
        return result.output
