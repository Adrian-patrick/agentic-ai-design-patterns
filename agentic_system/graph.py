from .agents import RouterAgent, ExecutionAgent
from .models import State, Dependencies
from pydantic_graph import BaseNode, End, GraphRunContext, Graph

class StartNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "RouterNode":
        print("\n--- [Start Node] Initializing Resource-Aware Processing Pipeline ---")
        ctx.state.system_status = "Pipeline initialized"
        return RouterNode()

class RouterNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ExecutionNode":
        print("\n--- [Router Node] Analyzing Query Complexity & Budget Requirements ---")
        ctx.state.system_status = "Analyzing query complexity"
        
        router_agent = ctx.deps.router_agent
        classification = await router_agent.run(ctx.state.query)
        
        ctx.state.complexity = classification.complexity
        ctx.state.selected_model = "Low-Cost Model" if classification.complexity == "simple" else "High-Cost Model"
        
        print(f"    Classified Complexity: '{classification.complexity.upper()}'")
        print(f"    Reasoning: {classification.reason}")
        print(f"    Resource Allocation: Routed to '{ctx.state.selected_model}'")
        
        ctx.state.system_status = f"Query classified as {classification.complexity}, routing to {ctx.state.selected_model}"
        return ExecutionNode()

class ExecutionNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "EndNode":
        print(f"\n--- [Execution Node] Invoking {ctx.state.selected_model} ---")
        ctx.state.system_status = f"Executing using {ctx.state.selected_model}"
        
        execution_agent = ctx.deps.execution_agent
        response = await execution_agent.run(ctx.state.query, ctx.state.complexity or "simple")
        ctx.state.execution_response = response
        
        # Calculate illustrative tokens and costs
        if ctx.state.complexity == "simple":
            # Low cost model pricing
            input_tokens = len(ctx.state.query.split()) * 1.3
            output_tokens = len(response.split()) * 1.3
            actual_cost = (input_tokens * 0.0005 + output_tokens * 0.0015) / 1000
            high_cost_baseline = (input_tokens * 0.0050 + output_tokens * 0.0150) / 1000
            savings = high_cost_baseline - actual_cost
        else:
            # High cost model pricing
            input_tokens = len(ctx.state.query.split()) * 1.3
            output_tokens = len(response.split()) * 1.3
            actual_cost = (input_tokens * 0.0050 + output_tokens * 0.0150) / 1000
            savings = 0.00
            
        ctx.state.estimated_cost = actual_cost
        ctx.state.estimated_savings = savings
        
        print(f"    Response generated successfully. (Tokens processed: Input ~{int(input_tokens)}, Output ~{int(output_tokens)})")
        return EndNode()

class EndNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[str]:
        print("\n--- [End Node] Finalizing Optimization Report ---")
        ctx.state.system_status = "Execution completed"
        
        print(f"    [Cost Metrics]")
        print(f"    - Model Used:      {ctx.state.selected_model}")
        print(f"    - Estimated Cost:  ${ctx.state.estimated_cost:.6f} USD")
        print(f"    - Total Savings:   ${ctx.state.estimated_savings:.6f} USD")
        
        final_report = (
            f"=== Resource Optimization Report ===\n"
            f"Query: \"{ctx.state.query}\"\n"
            f"Complexity Classification: {ctx.state.complexity.upper()}\n"
            f"Allocated Resource: {ctx.state.selected_model}\n"
            f"Estimated Run Cost: ${ctx.state.estimated_cost:.6f} USD\n"
            f"Estimated Savings (vs. Max Model): ${ctx.state.estimated_savings:.6f} USD\n"
            f"------------------------------------\n"
            f"Response:\n{ctx.state.execution_response}"
        )
        return End(final_report)

def build_graph() -> Graph:
    return Graph(
        nodes=[StartNode, RouterNode, ExecutionNode, EndNode],
        state_type=State,
        run_end_type=str
    )

def build_deps() -> Dependencies:
    return Dependencies(
        router_agent=RouterAgent(),
        execution_agent=ExecutionAgent(),
    )

async def run_graph(query: str) -> str:
    graph = build_graph()
    deps = build_deps()
    state = State(query=query)
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output


