import asyncio
import sys
from agentic_system.graph import run_graph
from agentic_system.prompts import default_topic

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

async def main():
    """Main entry point running dialectical debate showcase."""
    print("="*60)
    print("STARTING DIALECTICAL DEBATE REASONING SYSTEM")
    print("="*60)
    
    topic = default_topic
    print(f"\nDebate Topic: \"{topic}\"")
    
    try:
        verdict = await run_graph(topic)
        print("\n" + "="*60)
        print("SHOWCASE GRAPH RUN SUCCESSFULLY COMPLETED")
        print("="*60)
    except Exception as e:
        print(f"Showcase failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
