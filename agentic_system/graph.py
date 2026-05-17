from .agents import PlannerAgent, WorkerAgent
from .models import State, Dependencies, PlannerOutput
from pydantic_graph import BaseNode, End, GraphRunContext, Graph
from typing import Union
from dataclasses import dataclass

class StartNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "PlannerNode":
        return PlannerNode()

@dataclass
class WorkerNode(BaseNode[State, Dependencies, str]):
    step: str
    
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "PlannerNode":
        print(f"\n--- [Worker Node] Executing Step: {self.step} ---")
        worker_agent = ctx.deps.worker_agent
        worker_output = await worker_agent.run(step=self.step)
        
        # print worker output
        print(f"--- [Worker Node] Result (truncated) ---\n{worker_output[:500]}...\n")
        
        ctx.state.history.append(f"Worker output for '{self.step}': {worker_output}")
        ctx.state.iteration += 1
        return PlannerNode()

class PlannerNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> Union[WorkerNode, End[str]]:
        print(f"\n=== [Planner Node] Iteration {ctx.state.iteration + 1} ===")
        
        planner_agent = ctx.deps.planner_agent
        
        # HARD CAP AT 3 ITERATIONS
        if ctx.state.iteration >= 3:
            print("--- [Planner Node] HARD CAP reached (Max 3 iterations). Forcing final synthesis... ---")
            forced_history = ctx.state.history + [
                "SYSTEM: Maximum of 3 iterations reached. You MUST summarize the final answer now based on the information gathered so far."
            ]
            plan_out = await planner_agent.run(ctx.state.query, forced_history)
            final_ans = plan_out.final_response or "Maximum iterations reached. Failsafe final summary: " + "\n".join(ctx.state.history)
            return End(final_ans)
            
        print("--- [Planner Node] Analyzing request and history to make a plan... ---")
        plan_out = await planner_agent.run(ctx.state.query, ctx.state.history)
        
        if plan_out.is_complete:
            print(f"--- [Planner Node] Plan Complete! Finalizing response... ---")
            return End(plan_out.final_response or "No final response provided.")
        else:
            print(f"--- [Planner Node] Next Step Decided: {plan_out.next_step} ---")
            ctx.state.history.append(f"Planner assigned step: {plan_out.next_step}")
            return WorkerNode(step=plan_out.next_step or "Proceed to next step.")
        
def build_graph() -> Graph:
    return Graph(
        nodes=[StartNode, PlannerNode, WorkerNode],
        state_type=State,
        run_end_type=str
    )
        
def build_deps() -> Dependencies:
    return Dependencies(
        planner_agent=PlannerAgent(),
        worker_agent=WorkerAgent(),
    )

async def run_graph(query: str) -> str:
    graph = build_graph()
    deps = build_deps()
    state = State(query=query)
    # The run method returns a RunResult which contains the output
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output
