from .agents import InputGuardrailAgent, ExecutionAgent, OutputGuardrailAgent
from .models import State, Dependencies, InputEvaluation, OutputEvaluation
from pydantic_graph import BaseNode, End, GraphRunContext, Graph

class StartNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "InputGuardNode":
        print(f"\n--- [Start Node] Deploying Guardrails & Safety Pipeline ---")
        ctx.state.system_status = "Pipeline initialized"
        return InputGuardNode()

class InputGuardNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ExecuteNode | RejectNode":
        print("\n--- [Input Guard Node] Analyzing User Input Safety ---")
        ctx.state.system_status = "Executing input safety checks"
        
        guardrail = ctx.deps.input_guardrail_agent
        evaluation = await guardrail.run(ctx.state.original_input)
        
        ctx.state.risk_level = evaluation.risk_level
        
        print(f"    Risk Classification: '{evaluation.risk_level.upper()}'")
        print(f"    Analysis Details:    {evaluation.reason}")
        
        if evaluation.risk_level == "very_high":
            ctx.state.final_decision = "block"
            ctx.state.rejection_reason = evaluation.reason
            ctx.state.system_status = "Input blocked by security gates"
            return RejectNode()
            
        ctx.state.cleaned_input = evaluation.redacted_input
        ctx.state.system_status = f"Input cleared with risk level: {evaluation.risk_level}"
        return ExecuteNode()

class ExecuteNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "OutputGuardNode":
        print("\n--- [Execute Node] Fulfilling Cleared Request ---")
        ctx.state.system_status = "Processing work safely"
        
        cleaned_prompt = ctx.state.cleaned_input or ctx.state.original_input
        executor = ctx.deps.execution_agent
        
        output = await executor.run(cleaned_prompt)
        ctx.state.worker_output = output
        
        print("    [Execution Agent] Response drafted successfully.")
        return OutputGuardNode()

class OutputGuardNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "EditNode | RejectNode | EndNode":
        print("\n--- [Output Guard Node] Reviewing Response Compliance ---")
        ctx.state.system_status = "Inspecting output compliance"
        
        guardrail = ctx.deps.output_guardrail_agent
        evaluation = await guardrail.run(
            ctx.state.original_input, 
            ctx.state.worker_output or ""
        )
        
        ctx.state.output_evaluation = evaluation
        ctx.state.final_decision = evaluation.synthesis_decision
        
        print(f"    Compliance Action:  '{evaluation.synthesis_decision.upper()}'")
        if evaluation.policy_violation:
            print(f"    Policy Violation:   {evaluation.policy_violation}")
            
        if evaluation.synthesis_decision == "block":
            ctx.state.rejection_reason = evaluation.policy_violation or "Corporate compliance breach"
            ctx.state.system_status = "Output blocked by guardrails"
            return RejectNode()
        elif evaluation.synthesis_decision == "edit":
            ctx.state.system_status = "Output flagged for minor safety correction"
            return EditNode()
            
        ctx.state.system_status = "Output cleared successfully"
        return EndNode()

class EditNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "EndNode":
        print("\n--- [Edit Node] Applying Automated Compliance Patch ---")
        ctx.state.system_status = "Editing response for safety compliance"
        
        # Append corporate safety disclaimer as a patch
        ctx.state.worker_output = (
            f"{ctx.state.worker_output}\n\n"
            f"[Compliance Note: This response has been dynamically edited to comply with enterprise safety standards.]"
        )
        ctx.state.final_decision = "allow"
        print("    Response edited to add safety disclaimers.")
        return EndNode()

class RejectNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "EndNode":
        print("\n--- [Reject Node] Blocking Violation ---")
        ctx.state.system_status = "Enforcing block command"
        
        ctx.state.worker_output = (
            "ERROR: Request blocked. This transaction violates our enterprise safety policies. "
            f"Reason: {ctx.state.rejection_reason}"
        )
        print("    Policy enforced. Response substituted with warning disclaimer.")
        return EndNode()

class EndNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[State]:
        print("\n--- [End Node] Finalizing Security & Safety Report ---")
        ctx.state.system_status = "Security check complete"
        
        print("\n" + "="*60)
        print("ENTERPRISE AI ASSISTANT SAFETY & COMPLIANCE REPORT")
        print("="*60)
        print(f"Input Risk Tier:   {ctx.state.risk_level.upper()}")
        print(f"Final Decision:    {ctx.state.final_decision.upper()}")
        
        if ctx.state.risk_level == "medium":
            print(f"Original Prompt:   \"{ctx.state.original_input}\"")
            print(f"Sanitized Prompt:  \"{ctx.state.cleaned_input}\"")
        else:
            print(f"User Prompt:       \"{ctx.state.original_input}\"")
            
        print("-" * 60)
        print("TRANSACTION OUTPUT:")
        print(ctx.state.worker_output)
        print("="*60 + "\n")
        
        return End(ctx.state)

def build_graph() -> Graph:
    return Graph(
        nodes=[StartNode, InputGuardNode, ExecuteNode, OutputGuardNode, EditNode, RejectNode, EndNode],
        state_type=State,
        run_end_type=State
    )

def build_deps() -> Dependencies:
    return Dependencies(
        input_guardrail_agent=InputGuardrailAgent(),
        execution_agent=ExecutionAgent(),
        output_guardrail_agent=OutputGuardrailAgent(),
    )

async def run_graph(original_input: str) -> State:
    graph = build_graph()
    deps = build_deps()
    state = State(original_input=original_input)
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output
