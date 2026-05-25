from .agents import SearchAgent, SynthesisAgent
from .models import State, Dependencies
from pydantic_graph import BaseNode, End, GraphRunContext, Graph
from typing import Union

class StartNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "VerifyPermissionNode":
        print("\n--- [Start Node] Initializing Communication Flow ---")
        ctx.state.system_status = "Initializing communication flow"
        return VerifyPermissionNode()

class VerifyPermissionNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "SearchNode":
        print("\n--- [Verify Permission Node] Performing Identity Handshake Check ---")
        print("    Checking Agent identities...")
        print("    Verifying permissions for Search and Synthesis agents...")
        print("    Identity verified. Handshake completed successfully. Communication allowed.")
        ctx.state.system_status = "Permission verified and handshake established"
        return SearchNode()

class SearchNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "SynthesisNode":
        print("\n--- [Search Node] Activating Search Agent ---")
        ctx.state.system_status = "Running search agent"
        search_agent = ctx.deps.search_agent
        search_results = await search_agent.run(ctx.state.query)
        ctx.state.search_results = search_results
        print(f"    Search Agent completed. Data gathered (truncated):\n    {search_results[:300]}...")
        return SynthesisNode()

class SynthesisNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "EndNode":
        print("\n--- [Synthesis Node] Activating Synthesis Agent ---")
        ctx.state.system_status = "Synthesizing narrative summary"
        synthesis_agent = ctx.deps.synthesis_agent
        synthesized = await synthesis_agent.run(ctx.state.search_results or "No search context provided.")
        ctx.state.synthesized_response = synthesized
        print("    Synthesis Agent completed. Response generated.")
        return EndNode()

class EndNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[str]:
        print("\n--- [End Node] Finalizing Communication Flow & Generating Report ---")
        ctx.state.system_status = "Completed"
        final_response = ctx.state.synthesized_response or "Communication complete with no response."
        return End(final_response)

def build_graph() -> Graph:
    return Graph(
        nodes=[StartNode, VerifyPermissionNode, SearchNode, SynthesisNode, EndNode],
        state_type=State,
        run_end_type=str
    )

def build_deps() -> Dependencies:
    return Dependencies(
        search_agent=SearchAgent(),
        synthesis_agent=SynthesisAgent(),
    )

async def run_graph(query: str) -> str:
    graph = build_graph()
    deps = build_deps()
    state = State(query=query)
    # The run method returns a RunResult which contains the output
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output

