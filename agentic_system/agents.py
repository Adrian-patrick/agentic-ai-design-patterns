from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from .config import create_model
from .prompts import (
    classifier_system_prompt,
    orchestrator_system_prompt,
    summarizer_system_prompt,
    pointer_system_prompt,
)
from .models import ClassifierOutput, OrchestratorInstructions

class ClassifierAgent:
    def __init__(self):
        self.agent = Agent(
            model=create_model(),
            system_prompt=classifier_system_prompt,
            output_type=ClassifierOutput,
        )

    async def run(self, query: str) -> ClassifierOutput:
        result = await self.agent.run(query)
        return result.output

class OrchestratorAgent:
    def __init__(self):
        self.delegator_agent = Agent(
            model=create_model(),
            system_prompt=orchestrator_system_prompt,
            output_type=OrchestratorInstructions,
        )
        self.synthesizer_agent = Agent(
            model=create_model(),
            system_prompt=orchestrator_system_prompt,
            output_type=str,
        )

    async def delegate(self, query: str, requires_summarizer: bool, requires_pointer: bool) -> OrchestratorInstructions:
        prompt = (
            f"Original Query: {query}\n"
            f"Requires Summarizer: {requires_summarizer}\n"
            f"Requires Pointer: {requires_pointer}\n\n"
            "Please generate precise instructions for the required sub-agents."
        )
        result = await self.delegator_agent.run(prompt)
        return result.output

    async def synthesize(self, query: str, summarizer_output: str = None, pointer_output: str = None) -> str:
        prompt = (
            f"Original Query: {query}\n"
            f"Summarizer Output: {summarizer_output or 'N/A'}\n"
            f"Pointer Output: {pointer_output or 'N/A'}\n\n"
            "Please compile a final response to the original query."
        )
        result = await self.synthesizer_agent.run(prompt)
        return result.output

class SummarizerAgent:
    def __init__(self):
        self.agent = Agent(
            model=create_model(),
            system_prompt=summarizer_system_prompt,
            output_type=str,
        )

    async def run(self, content: str, instructions: str) -> str:
        prompt = f"Content to summarize:\n{content}\n\nInstructions from orchestrator:\n{instructions}"
        result = await self.agent.run(prompt)
        return result.output

class PointerAgent:
    def __init__(self):
        self.agent = Agent(
            model=create_model(),
            system_prompt=pointer_system_prompt,
            output_type=str,
        )

    async def run(self, content: str, instructions: str) -> str:
        prompt = f"Content to extract key points from:\n{content}\n\nInstructions from orchestrator:\n{instructions}"
        result = await self.agent.run(prompt)
        return result.output
