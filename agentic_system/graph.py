from .agents import ResponderAgent, MemoryClassifierAgent, CompressorAgent
from .models import State, Dependencies, MemoryItem
from pydantic_graph import BaseNode, End, GraphRunContext, Graph
from typing import Union

class StartNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "RetrieveNode":
        return RetrieveNode()

class RetrieveNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ProcessNode":
        print("\n=== [Retrieve Node] Searching Memory Store... ===")
        # Load all episodic and long term memories into context
        memories = []
        for m in ctx.state.episodic_memory:
            memories.append(f"[Past Interaction Event] {m.content}")
        for m in ctx.state.long_term_memory:
            memories.append(f"[Factual Knowledge] {m.content}")
            
        ctx.state.loaded_memories = memories
        print(f"--- Loaded {len(memories)} memory items into active context. ---")
        return ProcessNode()

class ProcessNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "MemoryClassificationNode":
        print("\n=== [Process Node] Processing User Request... ===")
        responder = ctx.deps.responder_agent
        response = await responder.run(
            query=ctx.state.query,
            loaded_memories=ctx.state.loaded_memories,
            short_term_buffer=ctx.state.short_term_buffer
        )
        ctx.state.response = response
        print(f"--- Responder Answer: ---\n{response}\n")
        return MemoryClassificationNode()

class MemoryClassificationNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> Union["CompressNode", End[str]]:
        print("\n=== [Memory Classification Node] Classifying & Extracting Memories... ===")
        classifier = ctx.deps.memory_classifier_agent
        output = await classifier.run(ctx.state.query, ctx.state.response or "")
        
        # Privacy Check & Write to memory
        if output.has_new_memories:
            for item in output.memories:
                print(f"   [Write Memory] Category: {item.category} | Content: {item.content}")
                if item.category == "Short-Term":
                    ctx.state.short_term_buffer.append(f"Q: {ctx.state.query} | A: {ctx.state.response}")
                elif item.category == "Episodic":
                    ctx.state.episodic_memory.append(item)
                elif item.category == "Long-Term":
                    ctx.state.long_term_memory.append(item)
                    
        # Check if conversation buffer has reached max limit (e.g., 2 turns)
        if len(ctx.state.short_term_buffer) >= 2:
            print("--- [Context Check] Short-term buffer limit reached! Routing to Compress Node... ---")
            return CompressNode()
            
        return End(ctx.state.response or "")

class CompressNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[str]:
        print("\n=== [Compress Node] Summarizing & Compressing Buffer... ===")
        compressor = ctx.deps.compressor_agent
        summary = await compressor.run(ctx.state.short_term_buffer)
        
        print(f"   [Store Summary] Archived to Long-Term Memory: '{summary}'")
        ctx.state.long_term_memory.append(
            MemoryItem(content=f"Archived chat summary: {summary}", category="Long-Term")
        )
        
        # Clear the immediate buffer (forgetting detailed turns for space efficiency)
        ctx.state.short_term_buffer.clear()
        print("   [Clean Buffer] Short-term buffer successfully cleared.")
        
        return End(ctx.state.response or "")

def build_graph() -> Graph:
    return Graph(
        nodes=[StartNode, RetrieveNode, ProcessNode, MemoryClassificationNode, CompressNode],
        state_type=State,
        run_end_type=str
    )

def build_deps() -> Dependencies:
    return Dependencies(
        responder_agent=ResponderAgent(),
        memory_classifier_agent=MemoryClassifierAgent(),
        compressor_agent=CompressorAgent(),
    )

async def run_graph(query: str, state: State = None) -> tuple[str, State]:
    graph = build_graph()
    deps = build_deps()
    if state is None:
        state = State(query=query)
    else:
        state.query = query
    # The run method returns a RunResult which contains the output
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output, state
