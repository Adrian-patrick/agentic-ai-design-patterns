from pydantic import BaseModel
from pydantic_ai import Agent, RunContext
from .config import create_model
from .prompts import planner_agent_system_prompt, worker_agent_system_prompt
from .models import PlannerOutput
    
class PlannerAgent:
    def __init__(self):
        self.agent = Agent(
            model=create_model(),
            system_prompt=planner_agent_system_prompt,
            output_type=PlannerOutput,
        )

    async def run(self, query: str, history: list[str]):
        prompt = f"Original Query: {query}\n\nExecution History:\n" + "\n".join(history)
        result = await self.agent.run(prompt)
        return result.output

class WorkerAgent:
    def __init__(self):
        self.agent = Agent(
            model=create_model(),
            system_prompt=worker_agent_system_prompt,
            output_type=str,
        )
        
        @self.agent.tool
        def web_search(ctx: RunContext[str], query: str) -> str:
            """Search the web using DuckDuckGo."""
            print(f"   [Worker Tool] Running web search for query: '{query}'")
            try:
                from ddgs import DDGS
                with DDGS() as ddgs_client:
                    results = [r for r in ddgs_client.text(query, max_results=3)]
                if not results:
                    print(f"   [Worker Tool] No search results found.")
                    return "No results found for this query."
                print(f"   [Worker Tool] Search completed, found {len(results)} results.")
                return str(results)
            except Exception as e:
                print(f"   [Worker Tool] Search failed: {e}")
                return f"Search failed: {e}"
                
        @self.agent.tool
        def calculate(ctx: RunContext[str], expression: str) -> str:
            """Evaluate a mathematical expression."""
            print(f"   [Worker Tool] Calculating expression: '{expression}'")
            try:
                result = str(eval(expression))
                print(f"   [Worker Tool] Calculation successful: {result}")
                return result
            except Exception as e:
                print(f"   [Worker Tool] Calculation failed: {e}")
                return f"Calculation failed: {e}"

    async def run(self, step: str):
        prompt = f"Assigned Step: {step}"
        result = await self.agent.run(prompt)
        return result.output
