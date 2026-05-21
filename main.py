import asyncio
import sys
from agentic_system.prompts import query
from agentic_system.graph import run_graph

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

async def main():
    """Main entry point to run the agentic system graph."""
    print(f"Running graph with query: {query}")
    
    try:
        result = await run_graph(query)
        print("\n" + "="*50)
        print("FINAL RESPONSE:")
        print("="*50)
        print(result)
        print("="*50)
    except Exception as e:
        print(f"An error occurred during graph execution: {e}")

if __name__ == "__main__":
    asyncio.run(main())
