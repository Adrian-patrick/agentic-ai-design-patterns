import os
from pydantic_ai import Agent
from .config import create_model
from .prompts import (
    generator_system_prompt,
    corrector_system_prompt,
)

# Check if Azure OpenAI API key is provided
IS_CONFIGURED = all(
    os.environ.get(var) for var in ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]
)

if not IS_CONFIGURED:
    print("[Info] Azure credentials not found. Falling back to local high-fidelity mock agents for showcase...")

class CodeGeneratorAgent:
    """Specialized agent for initial code generation."""
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=generator_system_prompt,
                retries=3,
            )

    async def run(self, prompt: str, task_name: str) -> str:
        if not IS_CONFIGURED:
            print(f"   [Generator Agent] Simulating offline generation for task: '{task_name}'...")
            if task_name == "healthy_add":
                return "def add(a, b):\n    return a + b"
            else:
                # Buggy Fibonacci generation on first try (typo: subtract instead of add)
                return "def fibonacci(n):\n    if n <= 0: return 0\n    elif n == 1: return 1\n    return fibonacci(n - 1) - fibonacci(n - 2)"
        
        result = await self.agent.run(prompt)
        return result.output.strip()

class CodeCorrectorAgent:
    """Specialized agent for repairing code that fails quality gates."""
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=corrector_system_prompt,
                retries=3,
            )

    async def run(self, prompt: str, current_code: str, error_message: str) -> str:
        if not IS_CONFIGURED:
            print("   [Corrector Agent] Simulating offline code correction/patching...")
            # Returns fixed Fibonacci
            return "def fibonacci(n):\n    if n <= 0: return 0\n    elif n == 1: return 1\n    return fibonacci(n - 1) + fibonacci(n - 2)"

        input_prompt = (
            f"Original task: {prompt}\n\n"
            f"Failing Code:\n{current_code}\n\n"
            f"Error/Test failures:\n{error_message}"
        )
        result = await self.agent.run(input_prompt)
        return result.output.strip()
