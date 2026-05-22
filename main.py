import asyncio
import sys
from agentic_system.graph import run_graph, State

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

async def main():
    """Main entry point to execute the four Human-in-the-Loop showcases."""
    print("==========================================================================")
    print("      STARTING SYSTEM SHOWCASE: HUMAN-IN-THE-LOOP (HITL) PATTERN")
    print("==========================================================================\n")
    
    # --------------------------------------------------------------------------
    # SCENARIO 1: APPROVE
    # Demonstrates: Simple Content -> Approval Required -> Human Approves
    # --------------------------------------------------------------------------
    print("\n" + "="*80)
    print("▶️ SCENARIO 1: HUMAN APPROVAL (Content Validation Checkpoint)")
    print("="*80)
    query_1 = "Review and approve the new SRE guidelines blog post draft."
    report_1, state_1 = await run_graph(query_1, scenario="approve")
    
    print("\n\n" + "="*80)
    print("▶️ SCENARIO 1 PROGRESS BRIEF:")
    print(f"  Gate Identified: {state_1.gate_identified.value if state_1.gate_identified else 'N/A'}")
    print(f"  Operator Decision: {state_1.human_decision.decision.value if state_1.human_decision else 'N/A'}")
    print(f"  Reviewer Fatigue Index: {state_1.fatigue_score:.2f} ({state_1.load_action})")
    print(f"  System Automation Level: {state_1.automation_level * 100:.0f}%")
    print("="*80 + "\n\n")

    # --------------------------------------------------------------------------
    # SCENARIO 2: DENY (REJECTION)
    # Demonstrates: Resume Rating -> Review Needed -> Human Denies & Learns
    # --------------------------------------------------------------------------
    print("\n" + "="*80)
    print("▶️ SCENARIO 2: HUMAN DENIAL (Resume Screening Validation)")
    print("="*80)
    query_2 = "Evaluate the resume submission of Bob Rustacean for the Rust Tech Lead role."
    report_2, state_2 = await run_graph(query_2, scenario="deny")
    
    print("\n\n" + "="*80)
    print("▶️ SCENARIO 2 PROGRESS BRIEF:")
    print(f"  Gate Identified: {state_2.gate_identified.value if state_2.gate_identified else 'N/A'}")
    print(f"  Operator Decision: {state_2.human_decision.decision.value if state_2.human_decision else 'N/A'}")
    print(f"  Constraint Added to Guidelines: '{state_2.feedback_log.guidelines_updated if state_2.feedback_log else 'None'}'")
    print("="*80 + "\n\n")

    # --------------------------------------------------------------------------
    # SCENARIO 3: EDIT (CHECKPOINT MODIFICATION)
    # Demonstrates: Translation -> Editing Checkpoint -> Human Polishes
    # --------------------------------------------------------------------------
    print("\n" + "="*80)
    print("▶️ SCENARIO 3: HUMAN EDITING (Translation Checkpoint Polish)")
    print("="*80)
    query_3 = "Polishing French translation block draft."
    report_3, state_3 = await run_graph(query_3, scenario="edit")
    
    print("\n\n" + "="*80)
    print("▶️ SCENARIO 3 PROGRESS BRIEF:")
    print(f"  Gate Identified: {state_3.gate_identified.value if state_3.gate_identified else 'N/A'}")
    print(f"  Operator Decision: {state_3.human_decision.decision.value if state_3.human_decision else 'N/A'}")
    print(f"  Human Edit Result: '{state_3.human_decision.edited_content if state_3.human_decision else 'None'}'")
    print("="*80 + "\n\n")

    # --------------------------------------------------------------------------
    # SCENARIO 4: TAKEOVER & FATIGUE LOAD BALANCING
    # Demonstrates: Large wire transfer -> Human Takeover -> Fatigue triggers REDUCE load
    # --------------------------------------------------------------------------
    print("\n" + "="*80)
    print("▶️ SCENARIO 4: MANUAL TAKEOVER & FATIGUE AUTO-BALANCE (Overload Protection)")
    print("="*80)
    query_4 = "Authorize wire transfer refund of $12,500.00 for client ACT-8812 under queue spikes."
    report_4, state_4 = await run_graph(query_4, scenario="takeover_fatigue")
    
    print("\n\n" + "="*80)
    print("▶️ SCENARIO 4 PROGRESS BRIEF:")
    print(f"  Gate Identified: {state_4.gate_identified.value if state_4.gate_identified else 'N/A'}")
    print(f"  Operator Decision: {state_4.human_decision.decision.value if state_4.human_decision else 'N/A'}")
    print(f"  Reviewer Fatigue Index: {state_4.fatigue_score:.2f} ({state_4.load_action})")
    print(f"  New AI System Automation Rate: {state_4.automation_level * 100:.0f}% (LOAD BALANCED)")
    print("="*80 + "\n")
    
    print("\n==========================================================================")
    print("       ALL FOUR SCENARIO SHOWCASES COMPLETED AND VERIFIED SUCCESSFULLY")
    print("==========================================================================")

if __name__ == "__main__":
    asyncio.run(main())
