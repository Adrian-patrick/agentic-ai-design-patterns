from typing import Union
from .agents import GoalCreatorAgent, WorkerAgent, MonitorAgent, AdapterAgent
from .models import State, Dependencies, GoalSpec, ProgressSnapshot, FixAction
from .prompts import turns
from pydantic_graph import BaseNode, End, GraphRunContext, Graph

class StartNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "CreateGoalNode":
        return CreateGoalNode()

class CreateGoalNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "StartWorkNode":
        print("\n=== [Create Goal Node] Creating clear goal specification... ===")
        creator = ctx.deps.goal_creator_agent
        goal_spec = await creator.run(ctx.state.query)
        ctx.state.goal_spec = goal_spec
        ctx.state.current_plan = "Establish core system endpoints and schema."
        
        print("\n[Goal Specification Formulated]")
        print(f"  - Specific: {goal_spec.specific}")
        print(f"  - Measurable: {goal_spec.measurable}")
        print(f"  - Achievable: {goal_spec.achievable}")
        print(f"  - Relevant: {goal_spec.relevant}")
        print(f"  - Limits: Max {goal_spec.deadline_turns} Turns | Budget {goal_spec.budget_limit} Credits")
        print(f"  - Quality Standard: {goal_spec.quality_standard}")
        return StartWorkNode()

class StartWorkNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "WatchProgressNode":
        ctx.state.step_count += 1
        print(f"\n=== [Start Work Node] Turn {ctx.state.step_count}: Working on Plan... ===")
        print(f"  Current Plan: '{ctx.state.current_plan}'")
        
        worker = ctx.deps.worker_agent
        goal_spec = ctx.state.goal_spec
        
        # Execute the worker
        output = await worker.run(
            goal_spec=goal_spec,
            current_plan=ctx.state.current_plan,
            current_turn=ctx.state.step_count
        )
        ctx.state.last_worker_output = output
        print(f"\n--- Worker Action Output: ---\n{output}\n")
        return WatchProgressNode()

class WatchProgressNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "CompareNode":
        print("\n=== [Watch Progress Node] Gaining telemetry & collecting metrics... ===")
        monitor = ctx.deps.monitor_agent
        goal_spec = ctx.state.goal_spec
        
        # Retrieve simulated turn telemetry
        turn_idx = min(ctx.state.step_count - 1, len(turns) - 1)
        turn_data = turns[turn_idx]
        telemetry = turn_data["raw_telemetry"]
        # Monitor validates progress against GoalSpec
        snapshot = await monitor.run(
            goal_spec=goal_spec,
            worker_output=ctx.state.last_worker_output,
            telemetry=telemetry
        )
        
        ctx.state.status_history.append(snapshot)
        ctx.state.budget_spent += snapshot.budget_spent_this_turn
        
        print("\n[Progress Telemetry]")
        for k, v in snapshot.metrics_collected.items():
            print(f"  - {k}: {v}")
        print(f"  - Credits Spent This Turn: {snapshot.budget_spent_this_turn}")
        print(f"  - Total Budget Consumed: {ctx.state.budget_spent}/{goal_spec.budget_limit}")
        print(f"  - Status Assessed: {snapshot.current_status.upper()}")
        print(f"  - Monitor Note: {snapshot.explanation}")
        
        return CompareNode()

class CompareNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> Union["GoalAchievedNode", "FixNode"]:
        print("\n=== [Compare Node] Evaluating status against targets... ===")
        last_snapshot = ctx.state.status_history[-1]
        
        if last_snapshot.current_status == "on_track":
            print("   [Decision] System is ON TRACK. Proceeding to achievement check...")
            return GoalAchievedNode()
        else:
            status_str = last_snapshot.current_status.upper()
            print(f"   [ALERT] System is {status_str}! Activating Alarm & Escalation...")
            return FixNode()

class FixNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "StartWorkNode":
        print("\n=== [Fix Node] Troubleshooting issues & formulating adjustments... ===")
        adapter = ctx.deps.adapter_agent
        goal_spec = ctx.state.goal_spec
        
        # Capture last monitor snapshot
        last_snapshot = ctx.state.status_history[-1]
        
        fix = await adapter.run(
            goal_spec=goal_spec,
            worker_output=ctx.state.last_worker_output,
            snapshot=last_snapshot
        )
        
        ctx.state.fix_action = fix
        print(f"   [Proposed Adaptation] Type: {fix.fix_type} | Action: {fix.value}")
        
        if fix.fix_type == "ChangePlan":
            ctx.state.current_plan = fix.value
            print(f"   [Action Applied] Execution plan successfully adjusted to: '{fix.value}'")
        elif fix.fix_type == "GetMoreResources":
            # Expand capacity/credits
            print(f"   [Action Applied] Requested additional processing nodes and resource limit increase.")
        elif fix.fix_type == "ChangeGoal":
            # Adjust quality constraint slightly
            print(f"   [Action Applied] Scaled back goal expectations to meet operating limits.")
            
        return StartWorkNode()

class GoalAchievedNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> Union["ReportNode", "StartWorkNode"]:
        print("\n=== [Goal Achieved Node] Verifying completion metrics... ===")
        goal_spec = ctx.state.goal_spec
        last_snapshot = ctx.state.status_history[-1]
        
        # Check if the goal criteria are met
        accuracy = last_snapshot.metrics_collected.get("inventory_accuracy_pct", 0)
        latency = last_snapshot.metrics_collected.get("database_latency_ms", 999)
        
        # Goal achieved if accuracy is high and database latency is low
        if accuracy >= 99.0 and latency <= 50:
            ctx.state.is_achieved = True
            print("   [SUCCESS] Goal achieved! All quality targets and SLA standards met.")
            return ReportNode()
        
        # If not achieved, check budget and deadline
        if ctx.state.step_count >= goal_spec.deadline_turns:
            print("   [Deadline Reached] Project turns limit reached without full achievement.")
            return ReportNode()
            
        if ctx.state.budget_spent >= goal_spec.budget_limit:
            print("   [Budget Exhausted] Project budget limit hit. Stopping work.")
            return ReportNode()
            
        print("   [Keep Going] Standards not fully satisfied yet, but budget remains. Continuing execution...")
        return StartWorkNode()

class ReportNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[str]:
        print("\n=== [Report Node] Generating Project Completion Report... ===")
        
        status = "SUCCESS" if ctx.state.is_achieved else "FAILED / BUDGET EXHAUSTED"
        history_summary = []
        for i, snap in enumerate(ctx.state.status_history, 1):
            history_summary.append(f"Turn {i}: {snap.current_status.upper()} (Spent {snap.budget_spent_this_turn}c) - {snap.explanation}")
            
        report = (
            "==================================================\n"
            "          PROJECT COMPLETE MONITORING REPORT\n"
            "==================================================\n"
            f"Objective Query: '{ctx.state.query}'\n"
            f"Final Outcome Status: {status}\n"
            f"Total Execution Turns: {ctx.state.step_count}/{ctx.state.goal_spec.deadline_turns}\n"
            f"Total Budget Consumed: {ctx.state.budget_spent}/{ctx.state.goal_spec.budget_limit} credits\n"
            "\nExecution History:\n  " + "\n  ".join(history_summary) + "\n"
            "=================================================="
        )
        ctx.state.final_report = report
        print(report)
        return End(report)

def build_graph() -> Graph:
    return Graph(
        nodes=[StartNode, CreateGoalNode, StartWorkNode, WatchProgressNode, CompareNode, FixNode, GoalAchievedNode, ReportNode],
        state_type=State,
        run_end_type=str
    )

def build_deps() -> Dependencies:
    return Dependencies(
        goal_creator_agent=GoalCreatorAgent(),
        worker_agent=WorkerAgent(),
        monitor_agent=MonitorAgent(),
        adapter_agent=AdapterAgent()
    )

async def run_graph(query: str, state: State = None) -> tuple[str, State]:
    graph = build_graph()
    deps = build_deps()
    if state is None:
        state = State(query=query)
    else:
        state.query = query
        
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output, state
