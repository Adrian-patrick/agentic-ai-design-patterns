import asyncio
import sys
from agentic_system.graph import run_graph
from agentic_system.models import SupportTicket

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

async def main():
    """Main entry point running task prioritization and preemption showcase."""
    print("="*60)
    print("STARTING STATEFUL TASK PRIORITIZATION & DISPATCH PIPELINE")
    print("="*60)
    
    # 1. Setup Initial Task List
    t1 = SupportTicket(
        id="T1_Standard_Billing",
        customer_tier="standard",
        initial_urgency="normal",
        description="Routine billing query requesting copy of last month's invoice.",
        age_days=5
    )
    
    t2 = SupportTicket(
        id="T2_Starved_Data_Export",
        customer_tier="standard",
        initial_urgency="normal",
        description="Requesting historical CSV usage logs export for audit compliance.",
        age_days=45  # Old starving task: age > 30 days!
    )
    
    t3 = SupportTicket(
        id="T3_Premium_Latency",
        customer_tier="premium",
        initial_urgency="high",
        description="Experiencing 3-second latency spikes when updating profile dashboards.",
        age_days=2
    )
    
    initial_tickets = [t1, t2, t3]
    
    # 2. Setup Critical Inbound Preemption Event
    critical_event = SupportTicket(
        id="CRITICAL_DB_CRASH",
        customer_tier="premium",
        initial_urgency="critical",
        description="DATABASE OUTAGE: Primary transactional database crash, system completely offline!",
        age_days=0
    )
    
    print("\nInitial Queue Submitted:")
    for t in initial_tickets:
        print(f"  - [{t.id}] Tier: {t.customer_tier.upper()}, Urgency: {t.initial_urgency.upper()}, Age: {t.age_days} days")
    print(f"\nPreemption Trigger Inbound Event Configured:")
    print(f"  - [{critical_event.id}] Tier: {critical_event.customer_tier.upper()}, Urgency: {critical_event.initial_urgency.upper()}, Desc: '{critical_event.description}'")
    print("\n" + "="*50 + "\n")
    
    # Run the prioritization orchestration
    try:
        await run_graph(initial_tickets, new_ticket_trigger=critical_event)
        print("\n" + "="*60)
        print("SHOWCASE GRAPH RUN SUCCESSFULLY COMPLETED")
        print("="*60)
    except Exception as e:
        print(f"Prioritization Showcase failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
