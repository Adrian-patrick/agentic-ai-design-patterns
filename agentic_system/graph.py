from typing import Optional
from .agents import PrioritizerAgent, SupportWorkerAgent
from .models import State, Dependencies, SupportTicket, PriorityScoreCard
from pydantic_graph import BaseNode, End, GraphRunContext, Graph

class StartNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "PrioritizeNode":
        print(f"\n--- [Start Node] Deploying Task Prioritization & Scheduling Pipeline ---")
        ctx.state.system_status = "Pipeline initialized"
        return PrioritizeNode()

class PrioritizeNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "DispatchNode":
        print("\n--- [Prioritize Node] Evaluating Scoring Factors & Starvation Prevention ---")
        ctx.state.system_status = "Scoring active queue tasks"
        
        prioritizer = ctx.deps.prioritizer_agent
        
        # 1. Score each ticket if not already scored
        for ticket in ctx.state.queue:
            if not ticket.score_card:
                score_card = await prioritizer.run(
                    id=ticket.id,
                    customer_tier=ticket.customer_tier,
                    initial_urgency=ticket.initial_urgency,
                    description=ticket.description
                )
                ticket.score_card = score_card
                
                # Apply priority formula: Priority = (Value/Effort) * Urgency * Risk
                raw_score = (score_card.business_value / score_card.effort) * score_card.urgency * score_card.risk_level
                ticket.priority_score = raw_score
                
                # 2. Scheduling Strategy - Task Aging (Starvation Prevention)
                # Boost priority score of old tasks (waiting > 30 days) to prevent starvation
                if ticket.age_days > 30:
                    age_boost = 15.0  # Significant priority boost
                    ticket.priority_score += age_boost
                    print(f"    [Task Aging] Boosted starved ticket '{ticket.id}' (+{age_boost:.1f} score, Age: {ticket.age_days} days)")

        # 3. Sort queue in descending order of priority score
        ctx.state.queue.sort(key=lambda x: x.priority_score, reverse=True)
        
        print("\n    CURRENT PRIORITY QUEUE:")
        for rank, ticket in enumerate(ctx.state.queue, 1):
            boost_indicator = " ⭐ [Aging Boosted]" if ticket.age_days > 30 else ""
            print(f"      {rank}. [{ticket.id} - Score: {ticket.priority_score:.2f}]{boost_indicator} "
                  f"Tier: {ticket.customer_tier.upper()}, Urgency: {ticket.initial_urgency.upper()}, Desc: '{ticket.description[:35]}...'")
        print()
        
        return DispatchNode()

class DispatchNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "MonitorNode | EndNode":
        print("--- [Dispatch Node] Selecting Top Priority Task ---")
        
        if not ctx.state.queue:
            print("    All active queue tasks completed successfully.")
            return EndNode()
            
        # Take the top prioritized task
        next_task = ctx.state.queue.pop(0)
        ctx.state.running_task = next_task
        ctx.state.system_status = f"Executing ticket {next_task.id}"
        
        print(f"    Selected Ticket: '{next_task.id}' (Priority Score: {next_task.priority_score:.2f})")
        return MonitorNode()

class MonitorNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "PrioritizeNode | ExecuteNode":
        print("\n--- [Monitor Node] Checking for New Critical Events ---")
        
        running_task = ctx.state.running_task
        if not running_task:
            return ExecuteNode()
            
        new_event = ctx.state.new_ticket_event
        if new_event:
            print("    [ALERT] A new incoming task event has arrived!")
            ctx.state.system_status = f"Evaluating preemption for incoming ticket: {new_event.id}"
            
            # Prioritize the incoming event immediately
            prioritizer = ctx.deps.prioritizer_agent
            score_card = await prioritizer.run(
                id=new_event.id,
                customer_tier=new_event.customer_tier,
                initial_urgency=new_event.initial_urgency,
                description=new_event.description
            )
            new_event.score_card = score_card
            new_event.priority_score = (score_card.business_value / score_card.effort) * score_card.urgency * score_card.risk_level
            
            print(f"    Incoming Event Ticket: '{new_event.id}' has Priority Score: {new_event.priority_score:.2f}")
            print(f"    Currently Running Ticket: '{running_task.id}' has Priority Score: {running_task.priority_score:.2f}")
            
            # Preemption threshold check
            if new_event.priority_score > running_task.priority_score:
                print(f"    [PREEMPTION TRIGGERED] Inbound ticket '{new_event.id}' overrides '{running_task.id}'!")
                
                # Save state: simulate we made partial progress, e.g. 40% completed
                running_task.progress_pct = 40
                print(f"    - Saved progress state (Progress: {running_task.progress_pct}%) for '{running_task.id}'")
                
                # Push both back onto queue
                ctx.state.queue.append(running_task)
                ctx.state.queue.append(new_event)
                
                # Log preemption
                event_log = f"Ticket '{new_event.id}' preempted '{running_task.id}' (Progress saved at {running_task.progress_pct}%)"
                ctx.state.preemption_events.append(event_log)
                
                ctx.state.running_task = None
                ctx.state.new_ticket_event = None
                
                print("    Returning tasks to queue and rescheduling...")
                return PrioritizeNode()  # Reorder graph
            else:
                print(f"    [NO PREEMPTION] Inbound ticket '{new_event.id}' queued. Continuing current task '{running_task.id}'...")
                ctx.state.queue.append(new_event)
                ctx.state.new_ticket_event = None
                
        return ExecuteNode()

class ExecuteNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "CompleteNode":
        running = ctx.state.running_task
        if not running:
            return CompleteNode()
            
        print(f"\n--- [Execute Node] Processing Resolution for '{running.id}' ---")
        ctx.state.system_status = f"Resolving ticket {running.id}"
        
        worker = ctx.deps.worker_agent
        resolution = await worker.run(
            id=running.id,
            customer_tier=running.customer_tier,
            description=running.description
        )
        
        # Update state: completed resolution and progress
        running.progress_pct = 100
        running.description = f"{running.description}\n\n[RESOLVED SOLUTION]:\n{resolution}"
        
        print(f"    [Support Worker] Resolution compiled successfully.")
        return CompleteNode()

class CompleteNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "DispatchNode":
        running = ctx.state.running_task
        if running:
            print(f"--- [Complete Node] Logging Ticket Resolved: '{running.id}' ---")
            ctx.state.completed_tasks.append(running)
            ctx.state.running_task = None
            
        return DispatchNode()

class EndNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[State]:
        print("\n--- [End Node] Finalizing Stateful Prioritization Report ---")
        ctx.state.system_status = "Execution completed"
        
        print("\n" + "="*60)
        print("STATEFUL PRIORITY QUEUE & DISPATCH AUDIT REPORT")
        print("="*60)
        print(f"Resolved Tickets:    {len(ctx.state.completed_tasks)}")
        print(f"Preemption Triggers: {len(ctx.state.preemption_events)}")
        
        if ctx.state.preemption_events:
            print("\nPREEMPTION LOGS:")
            for event in ctx.state.preemption_events:
                print(f"  - [PREEMPTED]: {event}")
                
        print("\nRESOLVED RESOLUTIONS SUMMARY:")
        for idx, task in enumerate(ctx.state.completed_tasks, 1):
            print(f"\n  {idx}. Ticket: {task.id} (Tier: {task.customer_tier.upper()}, Urgency: {task.initial_urgency.upper()})")
            # Extract resolution
            res_parts = task.description.split("[RESOLVED SOLUTION]:")
            res_snippet = res_parts[-1].strip() if len(res_parts) > 1 else task.description
            # Get first 3 lines of resolution
            snippet_lines = res_snippet.split("\n")[:4]
            print("     " + "\n     ".join(snippet_lines))
            
        print("="*60 + "\n")
        
        return End(ctx.state)

def build_graph() -> Graph:
    return Graph(
        nodes=[StartNode, PrioritizeNode, DispatchNode, MonitorNode, ExecuteNode, CompleteNode, EndNode],
        state_type=State,
        run_end_type=State
    )

def build_deps() -> Dependencies:
    return Dependencies(
        prioritizer_agent=PrioritizerAgent(),
        worker_agent=SupportWorkerAgent(),
    )

async def run_graph(initial_tickets: list[SupportTicket], new_ticket_trigger: Optional[SupportTicket] = None) -> State:
    graph = build_graph()
    deps = build_deps()
    state = State(
        queue=initial_tickets,
        new_ticket_event=new_ticket_trigger
    )
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output
