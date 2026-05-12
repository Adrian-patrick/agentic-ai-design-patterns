from pydantic_ai import Agent
from .config import create_model

agent = Agent(
    model=create_model(),
    system_prompt="You are a helpful assistant that answers questions about yourself.",
    name="TestAgent",
    output_type=str,
)
