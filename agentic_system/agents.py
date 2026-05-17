from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from .config import create_model
from .prompts import tool_agent_system_prompt, response_agent_system_prompt
    
class ToolAgent:
    def __init__(self):
        self.agent = Agent(
            model=create_model(),
            system_prompt=tool_agent_system_prompt,
            output_type=str,
        )
        
        @self.agent.tool
        def web_search(ctx: RunContext[str], query: str) -> str:
            """Search the web using DuckDuckGo."""
            try:
                from ddgs import DDGS
                with DDGS() as ddgs_client:
                    results = [r for r in ddgs_client.text(query, max_results=3)]
                if not results:
                    return "No results found for this query."
                return str(results)
            except Exception as e:
                return f"Search failed: {e}"
                
        @self.agent.tool
        def calculate(ctx: RunContext[str], expression: str) -> str:
            """Evaluate a mathematical expression."""
            try:
                return str(eval(expression))
            except Exception as e:
                return f"Calculation failed: {e}"

    async def run(self, query : str):
        result = await self.agent.run(query)
        return result.output

class ResponseAgent:
    def __init__(self):
        self.agent = Agent(
            model=create_model(),
            system_prompt=response_agent_system_prompt,
            output_type=str,
        )

    async def run(self, query: str, data: str):
        prompt = f"Original Query: {query}\n\nData gathered from tools:\n{data}"
        result = await self.agent.run(prompt)
        return result.output
