import asyncio
import sys
from agentic_system.prompts import turns
from agentic_system.graph import run_graph, State
from agentic_system.models import FeedbackSignal

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

async def main():
    """Main entry point to run the multi-turn learning and adaptation system showcase."""
    print("==================================================")
    print("STARTING SYSTEM SHOWCASE: LEARNING & ADAPTATION")
    print("==================================================")
    
    # Initialize a persistent state for system configuration
    state = State(query="")
    
    for i, turn in enumerate(turns, 1):
        print(f"\n\n>>>>>>>> TURN {i} <<<<<<<<")
        q = turn["query"]
        fb_dict = turn["feedback"]
        
        fb = FeedbackSignal(
            user_correction=fb_dict["user_correction"],
            quality_rating=fb_dict["quality_rating"],
            automated_eval_score=fb_dict["automated_eval_score"],
            task_outcome=fb_dict["task_outcome"]
        )
        
        try:
            # Run graph, which updates the state (prompt templates, rules, and few-shots)
            response, state = await run_graph(q, feedback=fb, state=state)
            
            # Print current state database contents
            print("\n[Current Persistent Configuration Snapshot]")
            print(f"  - Core Prompt: '{state.prompt_template}'")
            print(f"  - Few-Shot Examples Count: {len(state.few_shot_examples)}")
            print(f"  - Preference Rules: {state.preference_rules}")
            if state.learning_report:
                report = state.learning_report
                print(f"  - Deployed Optimizations: {report.improvements_deployed}")
                print(f"  - Tracked/Blocked Incidents: {report.failures_analyzed}")
                print(f"  - Learning Report System Status: {report.system_status}")
                
        except Exception as e:
            print(f"An error occurred during turn {i}: {e}")
            break

if __name__ == "__main__":
    asyncio.run(main())
