import asyncio
from agentic_system.agents import agent

async def main():
    """Main entry point to run the agent."""
    result = await agent.run("What are you?")
    print(f"Agent response: {result.output}")

if __name__ == "__main__":
    asyncio.run(main())
