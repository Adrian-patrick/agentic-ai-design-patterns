import asyncio
import sys
from agentic_system.graph import run_graph, State

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

async def main():
    """Main entry point to run the Goal Setting & Monitoring showcases."""
    print("==================================================")
    print("STARTING SYSTEM SHOWCASE: GOAL SETTING & MONITORING")
    print("==================================================")
    
    # Define a complex goal setting query with rules and targets
    query = (
        "Configure and verify a supply chain inventory levels tracking service. "
        "Must have database read latency < 50ms and data accuracy >= 99.0% "
        "operating within a maximum limit of 3 turns and a budget of 150 credits."
    )
    
    # Initialize state
    state = State(query=query)
    
    try:
        # Run graph (handles full state machine, loops, monitor assessments, and adaptation nodes)
        report, state = await run_graph(query, state=state)
        
        print("\n\n>>>>>>>> SHOWCASE COMPLETED SUCCESSFULLY <<<<<<<<")
        print(f"Final State Success Flag: {state.is_achieved}")
        print(f"Total Steps Taken: {state.step_count}")
        print(f"Total Budget Consumed: {state.budget_spent} credits")
        if state.fix_action:
            print(f"Adaptations Triggered: {state.fix_action.fix_type} -> '{state.fix_action.value}'")
            
    except Exception as e:
        print(f"An error occurred during graph execution: {e}")

if __name__ == "__main__":
    asyncio.run(main())
