import asyncio
from agentic_system.graph import run_graph
from test_transcript import transcript

async def main():
    """Main entry point to run the agentic system graph with the test transcript."""
    query = transcript
    print(f"Running graph with query (length: {len(query)} characters)...")
    
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
