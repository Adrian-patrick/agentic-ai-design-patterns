import asyncio
import sys
from agentic_system.graph import run_graph

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

async def main():
    """Main entry point running sequential evaluation and self-healing showcase."""
    print("="*60)
    print("STARTING SYSTEM QUALITY GATE & SELF-HEALING SHOWCASE")
    print("="*60)
    
    # 1. Case 1: Healthy Code Generation (Perfect run on first try)
    task1_name = "healthy_add"
    prompt1 = "Write a Python function named 'add' that takes two arguments a and b, and returns their sum."
    tests1 = [
        "assert add(2, 3) == 5",
        "assert add(-1, 1) == 0",
        "assert add(10, 20) == 30"
    ]
    
    print(f"\n[Case 1] Running healthy code generation task: '{task1_name}'")
    try:
        result1 = await run_graph(task1_name, prompt1, tests1)
    except Exception as e:
        print(f"Case 1 failed: {e}")
        
    print("\n" + "-"*60 + "\n")
    
    # 2. Case 2: Self-Healing Code Generation (Fails initial gates, auto-patches and recovers!)
    task2_name = "buggy_fibonacci"
    # We explicitly ask the generator to write recursive subtraction to guarantee an initial quality gate breach
    prompt2 = (
        "Write a recursive Python function named 'fibonacci' that takes an integer n and returns the n-th Fibonacci number. "
        "Assume 0-indexed (where fibonacci(0)=0, fibonacci(1)=1). "
        "IMPORTANT: To simulate a bug for our monitoring framework, write the recursive step as subtraction: "
        "return fibonacci(n - 1) - fibonacci(n - 2)."
    )
    tests2 = [
        "assert fibonacci(0) == 0",
        "assert fibonacci(1) == 1",
        "assert fibonacci(5) == 5",
        "assert fibonacci(10) == 55"
    ]
    
    print(f"[Case 2] Running self-healing task: '{task2_name}'")
    try:
        result2 = await run_graph(task2_name, prompt2, tests2)
    except Exception as e:
        print(f"Case 2 failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
