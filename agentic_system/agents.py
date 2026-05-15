from pydantic import BaseModel
from pydantic_ai import Agent
from .config import create_model
from .prompts import summarizer_with_feedback_prompt,summarizer_system_prompt, summarizer_prompt, critic_system_prompt, critic_prompt
    
class Summarizer:

    def __init__(self, ):
        
        self.agent = Agent(
            model=create_model(),
            system_prompt=summarizer_system_prompt,
            output_type=str,
        )

    async def summarize(self, query : str):

        result = await self.agent.run(summarizer_prompt.format(query=query))
        return result.output

    async def summarizewithfeedback(self, query : str, feedback:str):

        result = await self.agent.run(summarizer_with_feedback_prompt.format(query=query,feedback=feedback))
        return result.output

class CriticOutput(BaseModel):
    satisfied : bool 
    reason : str | None = None
    feedback : str | None = None

class Critic:
    def __init__(self,):

        self.agent = Agent(
            model=create_model(),
            system_prompt=critic_system_prompt,
            output_type=CriticOutput,
        )

    async def critics(self, query : str):

        result = await self.agent.run(critic_prompt.format(query=query))
        return result.output



