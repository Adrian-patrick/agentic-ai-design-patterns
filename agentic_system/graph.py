from .agents import Summarizer, Pointer, Responder
from .models import State, Dependencies
from pydantic_graph import BaseNode, End, GraphRunContext, Graph

class StartNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ChainNode":
        return ChainNode()

class ChainNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[str]:
        
        summarizer = ctx.deps.summarizer
        pointer = ctx.deps.pointer
        responder = ctx.deps.responder
        
        # Run Summarizer
        summary_result = await summarizer.summarize(ctx.state.query)
        ctx.state.summarizer_response = summary_result.output
        
        # Run Pointer - it handles formatting internally
        pointer_result = await pointer.point(ctx.state.summarizer_response)
        ctx.state.pointer_response = pointer_result.output
        
        # Run Responder - it handles formatting internally
        responder_result = await responder.respond(ctx.state.pointer_response)
        ctx.state.responder_response = responder_result.output
        
        return End(ctx.state.responder_response)
        
def build_graph() -> Graph:
    return Graph(
        nodes=[StartNode, ChainNode],
        state_type=State,
        run_end_type=str
    )
        
def build_deps() -> Dependencies:
    return Dependencies(
        summarizer=Summarizer(),
        pointer=Pointer(),
        responder=Responder(),
    )

async def run_graph(query: str) -> str:
    graph = build_graph()
    deps = build_deps()
    state = State(query=query)
    # The run method returns a RunResult which contains the output
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output
    
    
