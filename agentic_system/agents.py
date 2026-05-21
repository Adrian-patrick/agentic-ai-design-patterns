from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from .config import create_model
from .prompts import (
    responder_system_prompt,
    memory_classifier_system_prompt,
    compressor_system_prompt,
)
from .models import MemoryClassifierOutput

class ResponderAgent:
    def __init__(self):
        self.agent = Agent(
            model=create_model(),
            system_prompt=responder_system_prompt,
            output_type=str,
        )

    async def run(self, query: str, loaded_memories: list[str], short_term_buffer: list[str]) -> str:
        prompt = (
            f"User Query: {query}\n\n"
            f"Loaded Memories:\n" + "\n".join(loaded_memories) + "\n\n"
            f"Short-Term Buffer:\n" + "\n".join(short_term_buffer)
        )
        result = await self.agent.run(prompt)
        return result.output

class MemoryClassifierAgent:
    def __init__(self):
        self.agent = Agent(
            model=create_model(),
            system_prompt=memory_classifier_system_prompt,
            output_type=MemoryClassifierOutput,
        )

    async def run(self, query: str, response: str) -> MemoryClassifierOutput:
        prompt = (
            f"User Query: {query}\n"
            f"Agent Response: {response}"
        )
        result = await self.agent.run(prompt)
        return result.output

class CompressorAgent:
    def __init__(self):
        self.agent = Agent(
            model=create_model(),
            system_prompt=compressor_system_prompt,
            output_type=str,
        )

    async def run(self, buffer_turns: list[str]) -> str:
        prompt = "Turns to summarize and compress:\n" + "\n".join(buffer_turns)
        result = await self.agent.run(prompt)
        return result.output
