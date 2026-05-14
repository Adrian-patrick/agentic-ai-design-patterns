from pydantic_ai import Agent
from pydantic import BaseModel
from .config import create_model
from .prompts import router_system_prompt, router_prompt, summarizer_system_prompt, summarizer_prompt, pointer_system_prompt, pointer_prompt

from typing import Literal

class Routes(BaseModel):
    route: Literal["summarizer", "pointer"]
    
class Router:

    def __init__(self, ):
        
        self.agent = Agent(
            model=create_model(),
            system_prompt=router_system_prompt,
            output_type=Routes,
        )

    async def route(self, query : str):

        return await self.agent.run(router_prompt.format(query=query))

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



