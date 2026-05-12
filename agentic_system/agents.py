from pydantic_ai import Agent
from .config import create_model
from .prompts import summarizer_system_prompt, summarizer_prompt, pointer_system_prompt, pointer_prompt, response_system_prompt, response_prompt


class Summarizer:

    def __init__(self, ):
        
        self.agent = Agent(
            model=create_model(),
            system_prompt=summarizer_system_prompt,
            output_type=str,
        )

    async def summarize(self, query : str):

        return await self.agent.run(summarizer_prompt.format(query=query))


class Pointer:
    def __init__(self,):

        self.agent = Agent(
            model=create_model(),
            system_prompt=pointer_system_prompt,
            output_type=str,
        )

    async def point(self, query : str):

        return await self.agent.run(pointer_prompt.format(query=query))

class Responder:
    def __init__(self,):

        self.agent = Agent(
            model=create_model(),
            system_prompt=response_system_prompt,
            output_type=str,
        )

    async def respond(self, query : str):

        return await self.agent.run(response_prompt.format(query=query))



