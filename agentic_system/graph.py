from .agents import Summarizer, Pointer, Router
from .models import State, Dependencies
from pydantic_graph import BaseNode, End, GraphRunContext, Graph

class StartNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "RoutingNode":
        return RoutingNode()

class RoutingNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "SummaryNode | PointerNode":

        router = ctx.deps.router
        
        route_result = await router.route(ctx.state.query)
        ctx.state.route = route_result.output.route

        print("================route", ctx.state.route,"================")
        
        if ctx.state.route == "summarizer":
            return SummaryNode()
        elif ctx.state.route == "pointer":
            return PointerNode()
        else :
            return End("Invalid route")

class SummaryNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[str]:
        
        print("============inside summary node============")
        summarizer = ctx.deps.summarizer
        
        # Run Summarizer
        summary_result = await summarizer.summarize(ctx.state.query)
        ctx.state.summarizer_response = summary_result.output
        
        return End(ctx.state.summarizer_response)

class PointerNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[str]:
        
        print("============inside pointer node============")
        pointer = ctx.deps.pointer
        
        # Run Pointer - it handles formatting internally
        pointer_result = await pointer.point(ctx.state.query)
        ctx.state.pointer_response = pointer_result.output
        
        return End(ctx.state.pointer_response)

        
def build_graph() -> Graph:
    return Graph(
        nodes=[StartNode, RoutingNode, SummaryNode, PointerNode],
        state_type=State,
        run_end_type=str
    )
        
def build_deps() -> Dependencies:
    return Dependencies(
        summarizer=Summarizer(),
        pointer=Pointer(),
        router=Router(),
    )

async def run_graph(query: str) -> str:
    graph = build_graph()
    deps = build_deps()
    state = State(query=query)
    # The run method returns a RunResult which contains the output
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output
    
    
