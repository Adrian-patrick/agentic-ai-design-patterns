import os
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from .config import create_model
from .prompts import (
    router_system_prompt,
    low_cost_system_prompt,
    high_cost_system_prompt,
)

# Check if Azure OpenAI API key is provided
IS_CONFIGURED = all(
    os.environ.get(var) for var in ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]
)

if not IS_CONFIGURED:
    print("[Info] Azure credentials not found. Falling back to local high-fidelity mock agents for showcase...")

class ComplexityClassification(BaseModel):
    complexity: str = Field(description="Must be either 'simple' or 'complex'")
    reason: str = Field(description="Brief reason for classification")

class RouterAgent:
    """Specialized agent to classify task complexity and decide resource routing."""
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=router_system_prompt,
                output_type=ComplexityClassification,
                retries=3,
            )

    async def run(self, query: str) -> ComplexityClassification:
        if not IS_CONFIGURED:
            # High-fidelity mock complexity detection
            print("   [Router Agent] Simulating offline complexity classification...")
            # Detect based on keywords or length
            is_simple = any(kw in query.lower() for kw in ["calculate", "hello", "hi", "what is", "*", "+", "-", "/"]) or len(query) < 40
            if is_simple:
                return ComplexityClassification(
                    complexity="simple",
                    reason="Query is a brief factual, conversational, or mathematical request suitable for low-cost."
                )
            else:
                return ComplexityClassification(
                    complexity="complex",
                    reason="Query requires analytical, multi-perspective elaboration suitable for high-cost reasoning."
                )

        result = await self.agent.run(f"Task query to classify: {query}")
        return result.output

class ExecutionAgent:
    """Specialized agent to run the task using the optimized model tier persona."""
    def __init__(self):
        pass

    async def run(self, query: str, complexity: str) -> str:
        if not IS_CONFIGURED:
            print(f"   [Execution Agent] Simulating offline {complexity}-tier execution...")
            if complexity == "simple":
                # Concise 1-sentence answer
                return "The result of the calculation 5 * 12 + 10 is 70."
            else:
                # Thorough structured essay analysis
                return (
                    "PROS OF STANDARDIZING GLOBAL TAXATION:\n"
                    "1. Prevents Profit Shifting: Multi-national corporations cannot shift profits to tax havens.\n"
                    "2. Level Playing Field: Promotes fair competition across different sized nations.\n\n"
                    "CONS OF STANDARDIZING GLOBAL TAXATION:\n"
                    "1. Loss of Sovereign Autonomy: Individual nations lose the power to set competitive tax rates.\n"
                    "2. Barriers to Developing Nations: Small economies cannot use tax incentives to attract foreign direct investments.\n\n"
                    "ECONOMIC IMPACTS:\n"
                    "Standardization would redistribute global tax revenues, resulting in estimated gains of $150B annually for large consumer nations, but could lead to severe capital flight from small investment-driven economies."
                )

        # Dynamic agent creation to use the appropriate prompt based on model selection
        system_prompt = low_cost_system_prompt if complexity == "simple" else high_cost_system_prompt
        agent = Agent(
            model=create_model(),
            system_prompt=system_prompt,
            retries=3,
        )

        result = await agent.run(query)
        return result.output

