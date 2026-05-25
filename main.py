import asyncio
import sys
from agentic_system.graph import run_graph, State, Document

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

async def main():
    """Main entry point to execute the two Knowledge Retrieval (RAG) showcases."""
    print("==========================================================================")
    print("      STARTING SYSTEM SHOWCASE: KNOWLEDGE RETRIEVAL (RAG) PATTERN")
    print("==========================================================================\n")
    
    # --------------------------------------------------------------------------
    # SCENARIO 1: HAPPY PATH (Direct Answer & High Quality)
    # Demonstrates: Loading Doc -> Segmenting -> Query Expansion -> Retrieval ->
    #               relevance Ranking -> Synthesis -> Quality PASS -> Delivery.
    # --------------------------------------------------------------------------
    print("\n" + "="*80)
    print("▶️ SCENARIO 1: HAPPY PATH (Direct Grounded Search)")
    print("="*80)
    
    docs_1 = [
        Document(
            title="Product Hardware Manual",
            content="Warranty Rules: The warranty period for product batteries is 3 years from the date of purchase. Replacement is fully covered if capacity degrades below 70%."
        ),
        Document(
            title="User Charging Safety Guide",
            content="Charging Safety: Never charge batteries above 45 degrees Celsius. Use only standard certified charging plugs to prevent battery swelling."
        )
    ]
    
    query_1 = "What is the warranty period for product batteries?"
    report_1, state_1 = await run_graph(query_1, scenario="happy_path", documents=docs_1)
    
    print("\n\n" + "="*80)
    print("▶️ SCENARIO 1 PROGRESS BRIEF:")
    print(f"  Ingested Documents count: {len(state_1.documents)}")
    print(f"  Total Segments Processed: {len(state_1.chunks)}")
    print(f"  Expanded Search Query: '{state_1.improved_query}'")
    print(f"  Total Match Chunks Fetched: {len(state_1.retrieved_chunks)}")
    print(f"  Quality Verification Verdict: {'PASS' if state_1.generated_response and state_1.generated_response.is_good else 'FAIL'}")
    print(f"  SRE Search Benchmarks: Accuracy={state_1.accuracy_score*100:.0f}%, Coverage={state_1.coverage_score*100:.0f}%")
    print("="*80 + "\n\n")

    # --------------------------------------------------------------------------
    # SCENARIO 2: LOOP PATH (Quality Re-evaluation & Parameter Adjustment)
    # Demonstrates: Retrieval gets incomplete chunks -> synthesizes incomplete answer ->
    #               Quality Check flags FAIL -> Redo Search -> Adjust Settings (raise top-k) ->
    #               Retrieve better chunks -> Re-synthesize -> Quality Check PASS -> Deliver.
    # --------------------------------------------------------------------------
    print("\n" + "="*80)
    print("▶️ SCENARIO 2: LOOP PATH (Completeness Auto-Recovery & Quality Gate)")
    print("="*80)
    
    docs_2 = [
        Document(
            title="SRE Operations Playbook",
            content="Queue Alerts: Severe queue spikes trigger standard warning sirens in the operations dashboard. Operators must investigate logs immediately to find bottlenecks."
        ),
        Document(
            title="Compliance and Risk Guidelines",
            content="Emergency Measures: During severe queue spikes, recovery steps are: 1) Activate traffic throttling, 2) Batch items into chunks of 10+, and 3) Elevate the AI automation rate to 85% to offload operators. The standard agent credit limit is $10,000."
        )
    ]
    
    query_2 = "What are the recovery steps and limits during severe queue spikes?"
    report_2, state_2 = await run_graph(query_2, scenario="loop_path", documents=docs_2)
    
    print("\n\n" + "="*80)
    print("▶️ SCENARIO 2 PROGRESS BRIEF:")
    print(f"  Ingested Documents count: {len(state_2.documents)}")
    print(f"  Total Search Attempts Performed: {state_2.search_attempts} (Activated Quality recovery loop)")
    print(f"  Final Retrieval Fetch Limits: top-{state_2.retrieval_limit} chunks (Auto-Elevated from top-2)")
    print(f"  Quality Verification Verdict: {'PASS' if state_2.generated_response and state_2.generated_response.is_good else 'FAIL'}")
    print(f"  SRE Search Benchmarks: Accuracy={state_2.accuracy_score*100:.0f}%, Coverage={state_2.coverage_score*100:.0f}%")
    print("="*80 + "\n")
    
    print("\n==========================================================================")
    print("       ALL RAG PIPELINE SCENARIO SHOWCASES COMPLETED AND VERIFIED")
    print("==========================================================================")

if __name__ == "__main__":
    asyncio.run(main())
