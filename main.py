import asyncio
import sys
from agentic_system.prompts import queries
from agentic_system.graph import run_graph, State

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

async def main():
    """Main entry point to run the multi-turn agentic system graph with memory."""
    print("==================================================")
    print("STARTING MULTI-TURN AGENTIC SYSTEM WITH MEMORY")
    print("==================================================")
    
    # Initialize a persistent state
    state = State(query="")
    
    for i, q in enumerate(queries, 1):
        print(f"\n\n>>>>>>>> TURN {i} <<<<<<<<")
        print(f"User Query: '{q}'")
        try:
            # Run graph, which updates the state in-place
            response, state = await run_graph(q, state=state)
            
            print("\n--------------------------------------------------")
            print(f"TURN {i} RESPONSE:")
            print(response)
            print("--------------------------------------------------")
            
            # Print current state database contents
            print("\n[Current Memory Database Snapshot]")
            print(f"  - Short-Term Buffer: {len(state.short_term_buffer)} items")
            print(f"  - Episodic Memory: {len(state.episodic_memory)} items")
            print(f"  - Long-Term Memory: {len(state.long_term_memory)} items")
            for item in state.long_term_memory:
                print(f"    * [Long-Term] {item.content}")
                
        except Exception as e:
            print(f"An error occurred during turn {i}: {e}")
            break

if __name__ == "__main__":
    asyncio.run(main())
