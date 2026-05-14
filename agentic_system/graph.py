import asyncio
from .agents import Summarizer, Pointer, Responder
from .models import State, Dependencies
from pydantic_graph import BaseNode, End, GraphRunContext, Graph

class StartNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "WorkerNode":
        return WorkerNode()

import asyncio  # <--- Fix 3: Ensure asyncio is explicitly imported
from pydantic_graph import BaseNode, End, GraphRunContext


class WorkerNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ResponseNode | End[str]":  # <--- Fix 1: Add End[str] to the type hint

        print("============inside worker node============")

        summarizer = ctx.deps.summarizer
        pointer = ctx.deps.pointer

        # Fix 2: Verify these methods are 'async def' in your dependency classes
        summarizer_task = summarizer.summarize(ctx.state.query)
        pointer_task = pointer.point(ctx.state.query)

        try:
            summarizer_output, pointer_output = await asyncio.gather(
                summarizer_task, pointer_task
            )
            ctx.state.summarizer_response = summarizer_output
            ctx.state.pointer_response = pointer_output
        except Exception as e:
            return End(f"Error: {str(e)}")
            
        return ResponseNode()

class ResponseNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[str]:
        
        print("============inside response node============")
        responder = ctx.deps.responder
        
        # Run Responder
        try : 
            response_result = await responder.respond(
                ctx.state.pointer_response, 
                ctx.state.summarizer_response, 
                ctx.state.query
            )
            ctx.state.responder_response = response_result.output
        except Exception as e:
            return End(f"Error: {str(e)}")
        
        return End(ctx.state.responder_response)


        
def build_graph() -> Graph:
    return Graph(
        nodes=[StartNode, WorkerNode, ResponseNode],
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
    
    
