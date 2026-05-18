from .agents import ToolAgent, ResponseAgent
from .models import State, Dependencies
from pydantic_graph import BaseNode, End, GraphRunContext, Graph

class StartNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ToolNode":
        return ToolNode()

class ToolNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ResponseNode":
        print("============inside Tool node============")
        tool_agent = ctx.deps.tool_agent
        tool_output = await tool_agent.run(ctx.state.query)
        ctx.state.tool_agent_response = tool_output
        return ResponseNode()

class ResponseNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[str]:
        print("============inside Response node============")
        response_agent = ctx.deps.response_agent
        response_output = await response_agent.run(
            query=ctx.state.query,
            data=ctx.state.tool_agent_response
        )
        ctx.state.response_agent_response = response_output
        return End(response_output)
        
def build_graph() -> Graph:
    return Graph(
        nodes=[StartNode, ToolNode, ResponseNode],
        state_type=State,
        run_end_type=str
    )
        
def build_deps() -> Dependencies:
    return Dependencies(
        tool_agent=ToolAgent(),
        response_agent=ResponseAgent(),
    )

async def run_graph(query: str) -> str:
    graph = build_graph()
    deps = build_deps()
    state = State(query=query)
    # The run method returns a RunResult which contains the output
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output
