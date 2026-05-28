import asyncio
import sys
from agentic_system.graph import run_graph

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

async def main():
    """Main entry point running scientific exploration and discovery showcase."""
    print("="*60)
    print("STARTING SCIENTIFIC LITERARY EXPLORATION & DISCOVERY PIPELINE")
    print("="*60)
    
    goal = "Next-generation solid-state battery chemistries and solid-electrolyte interfaces beyond lithium-ion batteries"
    print(f"\nResearch Goal: \"{goal}\"")
    
    try:
        await run_graph(goal)
        print("\n" + "="*60)
        print("SHOWCASE GRAPH RUN SUCCESSFULLY COMPLETED")
        print("="*60)
    except Exception as e:
        print(f"Exploration Showcase failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
