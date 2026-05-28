import time
from .agents import CodeGeneratorAgent, CodeCorrectorAgent
from .models import State, Dependencies, MetricSummary, AlertInfo
from pydantic_graph import BaseNode, End, GraphRunContext, Graph

class StartNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "GenerateNode":
        print(f"\n--- [Start Node] Deploying Evaluation & Monitoring Pipeline for task: '{ctx.state.task_name}' ---")
        ctx.state.system_status = "Pipeline initialized"
        return GenerateNode()

class GenerateNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "QualityGateNode":
        print("\n--- [Generate Node] Invoking Code Generator Agent ---")
        ctx.state.system_status = "Generating initial code"
        
        generator = ctx.deps.generator_agent
        
        # Run generator
        code = await generator.run(ctx.state.prompt, ctx.state.task_name)
        ctx.state.generated_code = code
        
        print("    [Generator Agent] Initial code generated successfully.")
        return QualityGateNode()

class QualityGateNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "AnalyzeNode":
        iteration = len(ctx.state.metrics_history) + 1
        print(f"\n--- [Quality Gate Node] Executing QA Gates (Iteration {iteration}) ---")
        ctx.state.system_status = f"Running quality gates on iteration {iteration}"
        
        code = ctx.state.generated_code or ""
        tests = ctx.state.unit_tests
        
        start_time = time.time()
        
        # 1. Compilation Gate
        compilation_success = True
        syntax_error = None
        try:
            compiled = compile(code, "<generated_code>", "exec")
        except Exception as e:
            compilation_success = False
            syntax_error = str(e)
            
        # 2. Execution & Unit Tests Gate
        test_pass_rate = 0.0
        test_failure_details = None
        
        if compilation_success:
            namespace = {}
            try:
                exec(compiled, namespace)
                passed = 0
                total = len(tests)
                failures = []
                
                for test in tests:
                    try:
                        exec(test, namespace)
                        passed += 1
                    except AssertionError:
                        failures.append(f"Assertion failed: {test}")
                    except Exception as ex:
                        failures.append(f"Test exception: {test} -> {str(ex)}")
                
                test_pass_rate = (passed / total) if total > 0 else 1.0
                if failures:
                    test_failure_details = "\n".join(failures)
            except Exception as import_err:
                test_pass_rate = 0.0
                test_failure_details = f"Runtime error during imports/setup: {str(import_err)}"
        else:
            test_failure_details = f"Syntax Compilation Failed: {syntax_error}"
            
        end_time = time.time()
        latency_ms = (end_time - start_time) * 1000
        
        # 3. Cost Instrumentation (Illustrative model pricing)
        input_tokens = len(ctx.state.prompt.split()) * 1.5
        output_tokens = len(code.split()) * 1.5
        estimated_cost = (input_tokens * 0.005 + output_tokens * 0.015) / 1000
        
        # Log metric summary
        metric = MetricSummary(
            iteration=iteration,
            compilation_success=compilation_success,
            syntax_error=syntax_error,
            test_pass_rate=test_pass_rate,
            test_failure_details=test_failure_details,
            latency_ms=latency_ms,
            estimated_cost=estimated_cost
        )
        ctx.state.metrics_history.append(metric)
        
        print(f"    - Compilation Success: {compilation_success}")
        print(f"    - Unit Test Pass Rate: {test_pass_rate * 100:.1f}%")
        print(f"    - Latency (Gate execution): {latency_ms:.1f}ms")
        print(f"    - Run Cost: ${estimated_cost:.6f} USD")
        
        return AnalyzeNode()

class AnalyzeNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "PatchNode | EndNode":
        print("\n--- [Analyze Node] Evaluating Thresholds & Anomalies ---")
        ctx.state.system_status = "Analyzing quality patterns"
        
        latest_metric = ctx.state.metrics_history[-1]
        
        # Reset active alerts for current analysis
        ctx.state.active_alerts = []
        
        # 1. Evaluate Gates
        breach_detected = False
        
        if not latest_metric.compilation_success:
            alert = AlertInfo(
                gate_name="Syntax Check",
                severity="CRITICAL",
                message=f"Syntax error found: {latest_metric.syntax_error}"
            )
            ctx.state.active_alerts.append(alert)
            breach_detected = True
            print(f"    [ALERT - CRITICAL] {alert.message}")
            
        if latest_metric.test_pass_rate < 1.0:
            alert = AlertInfo(
                gate_name="Unit Tests",
                severity="CRITICAL",
                message=f"Unit tests failed (Pass Rate: {latest_metric.test_pass_rate * 100:.1f}%). Details:\n{latest_metric.test_failure_details}"
            )
            ctx.state.active_alerts.append(alert)
            breach_detected = True
            print(f"    [ALERT - WARNING/CRITICAL] Test failures detected.")
            
        # SLA Latency breach (illustrative threshold of 500ms for gates)
        if latest_metric.latency_ms > 500:
            alert = AlertInfo(
                gate_name="Latency SLA",
                severity="WARNING",
                message=f"Execution gate latency took {latest_metric.latency_ms:.1f}ms (threshold is 500ms)."
            )
            ctx.state.active_alerts.append(alert)
            print(f"    [ALERT - WARNING] Latency SLA breached.")

        # 2. Decision Tree
        if breach_detected:
            # Self-healing attempt limit check (avoid loops)
            if len(ctx.state.metrics_history) >= 3:
                print("    Max self-healing iterations (3) reached. Halting pipeline with active alerts.")
                return EndNode()
                
            print("    Breach detected! Routing to Patch Node for automated self-healing...")
            return PatchNode()
            
        # Check if we recovered from previous iterations
        if len(ctx.state.metrics_history) > 1:
            ctx.state.recovered = True
            print("    All gates cleared! Recovery verified successfully.")
        else:
            print("    All gates cleared successfully on first iteration!")
            
        return EndNode()

class PatchNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "QualityGateNode":
        print("\n--- [Patch Node] Invoking Code Corrector Agent ---")
        ctx.state.system_status = "Patching buggy code"
        
        corrector = ctx.deps.corrector_agent
        latest_metric = ctx.state.metrics_history[-1]
        
        error_info = latest_metric.test_failure_details or latest_metric.syntax_error or "Unknown failure"
        
        # Run Corrector Patcher
        patched_code = await corrector.run(
            prompt=ctx.state.prompt,
            current_code=ctx.state.generated_code or "",
            error_message=error_info
        )
        ctx.state.generated_code = patched_code
        
        print("    [Corrector Agent] Code patched successfully. Re-submitting to Quality Gates...")
        return QualityGateNode()

class EndNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[State]:
        print("\n--- [End Node] Finalizing Performance Audit Report ---")
        ctx.state.system_status = "Execution completed"
        
        print("\n" + "="*60)
        print("SYSTEM QUALITY GATE & MONITORING AUDIT")
        print("="*60)
        print(f"Task Name:         {ctx.state.task_name}")
        print(f"Total Iterations:  {len(ctx.state.metrics_history)}")
        print(f"Self-Healed:       {ctx.state.recovered}")
        print(f"Active Alerts:     {len(ctx.state.active_alerts)}")
        
        # Sum total cost and average latency
        total_cost = sum(m.estimated_cost for m in ctx.state.metrics_history)
        avg_gate_latency = sum(m.latency_ms for m in ctx.state.metrics_history) / len(ctx.state.metrics_history)
        
        print(f"Total Token Cost:  ${total_cost:.6f} USD")
        print(f"Avg Gate Latency:  {avg_gate_latency:.1f}ms")
        
        print("\nITERATION LOG:")
        for metric in ctx.state.metrics_history:
            print(f"  Iteration {metric.iteration}: Compilation={metric.compilation_success}, "
                  f"Tests={metric.test_pass_rate*100:.1f}%, Latency={metric.latency_ms:.1f}ms, Cost=${metric.estimated_cost:.6f}")
                  
        if ctx.state.active_alerts:
            print("\nACTIVE ALERTS (UNRESOLVED):")
            for alert in ctx.state.active_alerts:
                print(f"  - [{alert.severity}] {alert.gate_name}: {alert.message}")
        elif ctx.state.recovered:
            print("\nSTATUS: GREEN (Successfully Healed from prior breaches!)")
        else:
            print("\nSTATUS: GREEN (Perfect first run, no alerts triggered!)")
            
        print("\nFINAL PRODUCED SOLUTION:")
        print("-" * 40)
        print(ctx.state.generated_code)
        print("-" * 40)
        print("="*60 + "\n")
        
        return End(ctx.state)

def build_graph() -> Graph:
    return Graph(
        nodes=[StartNode, GenerateNode, QualityGateNode, AnalyzeNode, PatchNode, EndNode],
        state_type=State,
        run_end_type=State
    )

def build_deps() -> Dependencies:
    return Dependencies(
        generator_agent=CodeGeneratorAgent(),
        corrector_agent=CodeCorrectorAgent(),
    )

async def run_graph(task_name: str, prompt: str, unit_tests: list[str]) -> State:
    graph = build_graph()
    deps = build_deps()
    state = State(
        task_name=task_name,
        prompt=prompt,
        unit_tests=unit_tests
    )
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output
