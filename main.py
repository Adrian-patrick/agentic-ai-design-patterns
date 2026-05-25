import asyncio
import sys
from agentic_system.graph import run_graph

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

async def main():
    """Main entry point running sequential resource-optimized showcase."""
    print("="*60)
    print("STARTING RESOURCE-AWARE ROUTING OPTIMIZATION SHOWCASE")
    print("="*60)
    
    # 1. Simple Task Case
    simple_query = "Please calculate 5 * 12 + 10."
    print(f"\n[Case 1] Running simple query: \"{simple_query}\"")
    try:
        simple_result = await run_graph(simple_query)
        print("\n" + "="*50)
        print("CASE 1 GRAPH OUTPUT REPORT:")
        print("="*50)
        print(simple_result)
        print("="*50)
    except Exception as e:
        print(f"Case 1 failed: {e}")
        
    print("\n" + "-"*60 + "\n")
    
    # 2. Complex Task Case
    complex_query = "Explain the pros, cons, and economic impacts of standardizing global corporate taxation."
    print(f"[Case 2] Running complex query: \"{complex_query}\"")
    try:
        complex_result = await run_graph(complex_query)
        print("\n" + "="*50)
        print("CASE 2 GRAPH OUTPUT REPORT:")
        print("="*50)
        print(complex_result)
        print("="*50)
    except Exception as e:
        print(f"Case 2 failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())

