from .agents import ProponentAgent, OpponentAgent, JudgeAgent
from .models import State, Dependencies, Verdict
from pydantic_graph import BaseNode, End, GraphRunContext, Graph

class StartNode(BaseNode[State, Dependencies, Verdict]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ForNode":
        print("\n--- [Start Node] Initializing Dialectical Debate Pipeline ---")
        ctx.state.system_status = "Pipeline initialized"
        return ForNode()

class ForNode(BaseNode[State, Dependencies, Verdict]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "AgainstNode":
        print(f"\n--- [For Node] Invoking Proponent Agent (Arguments FOR) ---")
        ctx.state.system_status = "Generating arguments FOR the thesis"
        
        proponent_agent = ctx.deps.proponent_agent
        arguments_for = await proponent_agent.run(ctx.state.topic)
        ctx.state.arguments_for = arguments_for
        
        print("    [Proponent Agent] Arguments generated successfully.")
        return AgainstNode()

class AgainstNode(BaseNode[State, Dependencies, Verdict]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "DiscussNode":
        print(f"\n--- [Against Node] Invoking Opponent Agent (Arguments AGAINST) ---")
        ctx.state.system_status = "Generating arguments AGAINST the thesis"
        
        opponent_agent = ctx.deps.opponent_agent
        arguments_against = await opponent_agent.run(ctx.state.topic)
        ctx.state.arguments_against = arguments_against
        
        print("    [Opponent Agent] Arguments generated successfully.")
        return DiscussNode()

class DiscussNode(BaseNode[State, Dependencies, Verdict]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "EndNode":
        print("\n--- [Discuss Node] Invoking Judge Agent (Synthesis & Verdict) ---")
        ctx.state.system_status = "Synthesizing and evaluating arguments"
        
        judge_agent = ctx.deps.judge_agent
        verdict = await judge_agent.run(
            ctx.state.topic, 
            ctx.state.arguments_for or "", 
            ctx.state.arguments_against or ""
        )
        ctx.state.verdict = verdict
        
        ctx.state.system_status = "Verdict successfully generated"
        print("    [Judge Agent] Argument analysis & synthesis complete.")
        return EndNode()

class EndNode(BaseNode[State, Dependencies, Verdict]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[Verdict]:
        print("\n--- [End Node] Finalizing Debate Execution & Verification Report ---")
        ctx.state.system_status = "Execution completed"
        
        verdict = ctx.state.verdict
        if not verdict:
            raise ValueError("Verdict not found in state when executing EndNode")
            
        print("\n" + "="*60)
        print("DEBATE ANALYSIS AND JUDGE VERDICT REPORT")
        print("="*60)
        print(f"Topic: \"{ctx.state.topic}\"\n")
        
        print("LOGICAL ERROR/WEAKNESS CHECK:")
        for check in verdict.logical_checks:
            print(f"  - [{check.side}]: {check.fallacy_or_weakness}")
        print()
        
        print("RANKED & RATED ARGUMENTS:")
        # Sort by strength rank (lowest number is strongest)
        sorted_points = sorted(verdict.point_ratings, key=lambda x: x.strength_rank)
        for rank, item in enumerate(sorted_points, 1):
            print(f"  {rank}. [{item.side} - Strength Rank {item.strength_rank}] {item.point}")
        print()
        
        print("FINAL SYNTHESIS AND COMPROMISE:")
        print(verdict.synthesis)
        print("="*60 + "\n")
        
        return End(verdict)

def build_graph() -> Graph:
    return Graph(
        nodes=[StartNode, ForNode, AgainstNode, DiscussNode, EndNode],
        state_type=State,
        run_end_type=Verdict
    )

def build_deps() -> Dependencies:
    return Dependencies(
        proponent_agent=ProponentAgent(),
        opponent_agent=OpponentAgent(),
        judge_agent=JudgeAgent(),
    )

async def run_graph(topic: str) -> Verdict:
    graph = build_graph()
    deps = build_deps()
    state = State(topic=topic)
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output
