import os
from pydantic_ai import Agent, RunContext
from .config import create_model
from .prompts import (
    search_agent_system_prompt,
    synthesis_agent_system_prompt,
)

# Check if Azure OpenAI API key is provided
IS_CONFIGURED = all(
    os.environ.get(var) for var in ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]
)

if not IS_CONFIGURED:
    print("[Info] Azure credentials not found. Falling back to local high-fidelity mock agents for showcase...")

class SearchAgent:
    """Specialized agent to search the web and compile raw context."""
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=search_agent_system_prompt,
                retries=3,
            )
            
            @self.agent.tool
            def web_search(ctx: RunContext[str], query: str) -> str:
                """Search the web using DuckDuckGo."""
                print(f"   [Search Tool] Running web search for query: '{query}'")
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

    async def run(self, query: str) -> str:
        if not IS_CONFIGURED:
            # High-fidelity mock search results
            print("   [Search Tool] Simulating offline search results...")
            return "Mock Search Results: Google announces new Gemini model updates, OpenAI releases GPT-5-mini, and Apple integrates on-device AI across models."

        result = await self.agent.run(f"Search query: {query}")
        return result.output

class SynthesisAgent:
    """Specialized agent to write narrative summaries and extract highlight points."""
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=synthesis_agent_system_prompt,
                retries=3,
            )

    async def run(self, search_context: str) -> str:
        if not IS_CONFIGURED:
            # High-fidelity mock synthesis
            print("   [Synthesis Agent] Simulating offline response synthesis...")
            return (
                "Synthesis: We successfully compiled the latest artificial intelligence developments:\n\n"
                "Summary:\n"
                "Recent breakthroughs in artificial intelligence feature substantial upgrades across major tech platforms. "
                "Google unveiled new Gemini models, OpenAI introduced the efficient GPT-5-mini model, and Apple expanded "
                "on-device intelligence across its entire ecosystem.\n\n"
                "Key Highlights:\n"
                "- Google announces new Gemini model updates.\n"
                "- OpenAI releases GPT-5-mini.\n"
                "- Apple integrates on-device AI."
            )

        result = await self.agent.run(f"Raw Search Context:\n{search_context}")
        return result.output
