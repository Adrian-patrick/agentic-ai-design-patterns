from pydantic_ai import Agent
from .config import create_model
from .prompts import responder_system_prompt, responder_prompt, summarizer_system_prompt, summarizer_prompt, pointer_system_prompt, pointer_prompt
    
class Responder:

    def __init__(self, ):
        
        self.agent = Agent(
            model=create_model(),
            system_prompt=responder_system_prompt,
            output_type=str,
        )

    async def respond(self, pointer_output : str, summarizer_output : str, query : str):

        return await self.agent.run(responder_prompt.format(pointer_output=pointer_output, summarizer_output=summarizer_output, query=query))

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



