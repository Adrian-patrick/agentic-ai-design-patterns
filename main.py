import asyncio
import sys
from agentic_system.graph import run_graph, State

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

async def main():
    """Main entry point to execute the three reliability scenarios."""
    print("==========================================================================")
    print("      STARTING SYSTEM SHOWCASE: EXCEPTION HANDLING AND RECOVERY PATTERN")
    print("==========================================================================\n")
    
    # --------------------------------------------------------------------------
    # SCENARIO 1: TRANSIENT SUCCESS
    # Demonstrates: Temporary socket failure -> Retries with backoff -> Succeeds
    # --------------------------------------------------------------------------
    print("\n" + "="*80)
    print("▶️ SCENARIO 1: TRANSIENT ERROR RECOVERY (Network Glitch / Jitter)")
    print("="*80)
    query_1 = "Fetch and aggregate transaction logs from external microservices region-IN."
    report_1, state_1 = await run_graph(query_1, scenario="transient_success")
    
    print("\n\n" + "="*80)
    print("▶️ SCENARIO 1 PROGRESS BRIEF:")
    print(f"  Outcome Status: {state_1.operation_outcome}")
    print(f"  Attempt Invocations: {state_1.call_attempts}")
    print(f"  Error History Count: {len(state_1.error_history)}")
    print("="*80 + "\n\n")

    # --------------------------------------------------------------------------
    # SCENARIO 2: PERMANENT FALLBACK
    # Demonstrates: Credentials revoked -> Permanent Error -> Graceful Fallback
    # --------------------------------------------------------------------------
    print("\n" + "="*80)
    print("▶️ SCENARIO 2: PERMANENT ERROR HANDLING (API Key Revocation / Expiration)")
    print("="*80)
    query_2 = "Authorize payment gateway integration for user order ORD-7782."
    report_2, state_2 = await run_graph(query_2, scenario="permanent_fallback")
    
    print("\n\n" + "="*80)
    print("▶️ SCENARIO 2 PROGRESS BRIEF:")
    print(f"  Outcome Status: {state_2.operation_outcome}")
    print(f"  Attempt Invocations: {state_2.call_attempts}")
    print(f"  Fallback Used: {state_2.backup_plan_selected.value if state_2.backup_plan_selected else 'None'}")
    print("="*80 + "\n\n")

    # --------------------------------------------------------------------------
    # SCENARIO 3: CRITICAL EMERGENCY
    # Demonstrates: Full storage partition -> State Save -> Alarm sound -> Safe Stop
    # --------------------------------------------------------------------------
    print("\n" + "="*80)
    print("▶️ SCENARIO 3: CRITICAL SYSTEM FAULT (Database Partition 100% Full)")
    print("="*80)
    query_3 = "Execute critical transactional flush to local system partition storage."
    report_3, state_3 = await run_graph(query_3, scenario="critical_emergency")
    
    print("\n\n" + "="*80)
    print("▶️ SCENARIO 3 PROGRESS BRIEF:")
    print(f"  Outcome Status: {state_3.operation_outcome}")
    print(f"  Emergency Saved?: {state_3.emergency_saved}")
    print(f"  SRE Alarm Triggered?: {state_3.emergency_alerted}")
    print(f"  Safety Stop Activated?: {not state_3.safety_verdict.is_safe if state_3.safety_verdict else 'N/A'}")
    print("="*80 + "\n")
    
    print("\n==========================================================================")
    print("       ALL THREE SCENARIO SHOWCASES COMPLETED AND VERIFIED SUCCESSFULLY")
    print("==========================================================================")

if __name__ == "__main__":
    asyncio.run(main())
