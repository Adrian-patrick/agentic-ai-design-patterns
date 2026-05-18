from .agents import ClassifierAgent, OrchestratorAgent, SummarizerAgent, PointerAgent
from .models import State, Dependencies
from pydantic_graph import BaseNode, End, GraphRunContext, Graph
from typing import Union

class StartNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ClassifierNode":
        return ClassifierNode()

class ClassifierNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "OrchestratorNode":
        print("\n=== [Classifier Node] Classifying Query... ===")
        classifier = ctx.deps.classifier_agent
        output = await classifier.run(ctx.state.query)
        
        ctx.state.requires_summarizer = output.requires_summarizer
        ctx.state.requires_pointer = output.requires_pointer
        
        print(f"--- [Classifier Decision] Requires Summarizer: {output.requires_summarizer}, Requires Pointer: {output.requires_pointer} ---")
        return OrchestratorNode()

class OrchestratorNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> Union["SummarizerNode", "PointerNode", "SynthesisNode"]:
        print("\n=== [Orchestrator Node] Delegating Instructions... ===")
        orchestrator = ctx.deps.orchestrator_agent
        instructions = await orchestrator.delegate(
            query=ctx.state.query,
            requires_summarizer=ctx.state.requires_summarizer,
            requires_pointer=ctx.state.requires_pointer
        )
        
        ctx.state.summarizer_instruction = instructions.summarizer_instruction
        ctx.state.pointer_instruction = instructions.pointer_instruction
        
        if ctx.state.requires_summarizer:
            print("--- [Orchestrator Decision] Routing to Summarizer ---")
            return SummarizerNode()
        elif ctx.state.requires_pointer:
            print("--- [Orchestrator Decision] Routing to Pointer ---")
            return PointerNode()
        else:
            print("--- [Orchestrator Decision] Routing to Synthesis (No specialists needed) ---")
            return SynthesisNode()

class SummarizerNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> Union["PointerNode", "SynthesisNode"]:
        print("\n=== [Summarizer Node] Summarizing Content... ===")
        summarizer = ctx.deps.summarizer_agent
        output = await summarizer.run(
            content=ctx.state.query,
            instructions=ctx.state.summarizer_instruction or "Summarize the text."
        )
        ctx.state.summarizer_output = output
        print(f"--- [Summarizer Result (truncated)] ---\n{output[:300]}...\n")
        
        if ctx.state.requires_pointer:
            return PointerNode()
        else:
            return SynthesisNode()

class PointerNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "SynthesisNode":
        print("\n=== [Pointer Node] Extracting Key Points... ===")
        pointer = ctx.deps.pointer_agent
        output = await pointer.run(
            content=ctx.state.query,
            instructions=ctx.state.pointer_instruction or "Extract key points."
        )
        ctx.state.pointer_output = output
        print(f"--- [Pointer Result (truncated)] ---\n{output[:300]}...\n")
        
        return SynthesisNode()

class SynthesisNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[str]:
        print("\n=== [Synthesis Node] Formulating Final Response... ===")
        orchestrator = ctx.deps.orchestrator_agent
        final_ans = await orchestrator.synthesize(
            query=ctx.state.query,
            summarizer_output=ctx.state.summarizer_output,
            pointer_output=ctx.state.pointer_output
        )
        ctx.state.final_response = final_ans
        return End(final_ans)

def build_graph() -> Graph:
    return Graph(
        nodes=[StartNode, ClassifierNode, OrchestratorNode, SummarizerNode, PointerNode, SynthesisNode],
        state_type=State,
        run_end_type=str
    )

def build_deps() -> Dependencies:
    return Dependencies(
        classifier_agent=ClassifierAgent(),
        orchestrator_agent=OrchestratorAgent(),
        summarizer_agent=SummarizerAgent(),
        pointer_agent=PointerAgent(),
    )

async def run_graph(query: str) -> str:
    graph = build_graph()
    deps = build_deps()
    state = State(query=query)
    # The run method returns a RunResult which contains the output
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output
