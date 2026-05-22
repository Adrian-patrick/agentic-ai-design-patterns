import asyncio
from typing import Union
from pydantic_graph import BaseNode, End, GraphRunContext, Graph
from .agents import SafetyCheckAgent, ServiceCallAgent, TriageAgent, RecoveryAgent, LearningAgent
from .models import (
    State,
    Dependencies,
    ErrorRecord,
    ExceptionCategory,
    BackupOption,
    SafetyVerdict,
)

class StartNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "SafetyChecksNode":
        print("\n=== [Start Node] Initializing service request... ===")
        print(f"  Target Operation: '{ctx.state.query}'")
        print(f"  Active Scenario: {ctx.state.scenario.upper()}")
        return SafetyChecksNode()

class SafetyChecksNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "MakeCallNode":
        print("\n=== [Safety Checks Node] Wrapping execution in safety envelopes... ===")
        safety_agent = ctx.deps.safety_agent
        passed = await safety_agent.check(ctx.state.query, ctx.state.scenario)
        ctx.state.safety_checked = passed
        print(f"  Prerequisites & input format checks: {'PASSED' if passed else 'FAILED'}")
        return MakeCallNode()

class MakeCallNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> Union["ProcessResultNode", "CatchErrorNode"]:
        ctx.state.call_attempts += 1
        print(f"\n=== [Make Call Node] Invoking external tool/service (Attempt {ctx.state.call_attempts})... ===")
        
        service = ctx.deps.service_agent
        try:
            # Simulate real execution and let exceptions bubble up naturally
            result = await service.run(ctx.state.scenario, ctx.state.call_attempts)
            print(f"  [Service Success] Call returned raw result successfully.")
            return ProcessResultNode(raw_result=result)
        except Exception as e:
            error_class_name = e.__class__.__name__
            print(f"  [Service Failure] Caught raised exception: {error_class_name}: {e}")
            ctx.state.last_error = f"{error_class_name}: {e}"
            return CatchErrorNode()

class ProcessResultNode(BaseNode[State, Dependencies, str]):
    raw_result: str

    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "SuccessNode":
        print("\n=== [Process Result Node] Deserializing and validating return payload... ===")
        print(f"  Result content used: '{self.raw_result}'")
        return SuccessNode()

class SuccessNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "RecordNode":
        print("\n=== [Success Node] Core task completed! Marking execution as SUCCESS. ===")
        ctx.state.operation_outcome = "SUCCESS"
        return RecordNode()

class CatchErrorNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> Union["RetryNode", "FallbackNode", "EmergencyNode"]:
        print("\n=== [Catch Error Node] Interrupt intercepted. Sending details to SRE Diagnosis Agent... ===")
        triage_agent = ctx.deps.triage_agent
        
        triage_result = await triage_agent.run(
            query=ctx.state.query,
            scenario=ctx.state.scenario,
            error_msg=ctx.state.last_error or "Unknown Exception"
        )
        
        print("\n[Diagnostic Triage Report]")
        print(f"  - Severity: {triage_result.severity.upper()}")
        print(f"  - Category: {triage_result.category.value.upper()}")
        print(f"  - Reasoning: {triage_result.reasoning}")
        print(f"  - Action Proposed: {triage_result.recommended_action}")
        
        if triage_result.category == ExceptionCategory.TEMPORARY:
            return RetryNode()
        elif triage_result.category == ExceptionCategory.PERMANENT:
            return FallbackNode()
        else: # CRITICAL
            return EmergencyNode()

class RetryNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> Union["MakeCallNode", "FallbackNode"]:
        print("\n=== [Retry Node] Calculating retry budget and backoff parameters... ===")
        
        if ctx.state.call_attempts <= ctx.state.max_retries:
            # Exponential backoff wait time (simulated)
            wait_sec = float(2 ** ctx.state.call_attempts)
            ctx.state.current_wait_sec = wait_sec
            
            print(f"  - Active Retries: {ctx.state.call_attempts}/{ctx.state.max_retries}")
            print(f"  - Backoff Jitter: Waiting {wait_sec} seconds before next try...")
            
            # Simulated sleep
            await asyncio.sleep(0.1)  # small sleep for fast showcase runs
            
            record = ErrorRecord(
                attempt=ctx.state.call_attempts,
                error_msg=ctx.state.last_error or "Temporary error",
                category="Temporary",
                action_taken=f"Backoff {wait_sec}s and retry connection."
            )
            ctx.state.error_history.append(record)
            return MakeCallNode()
        else:
            print("  [Limit Exceeded] Maximum retries reached. Out of retry budget.")
            record = ErrorRecord(
                attempt=ctx.state.call_attempts,
                error_msg=ctx.state.last_error or "Temporary error",
                category="Temporary",
                action_taken="Max retries reached. Escalate to Fallback Plan."
            )
            ctx.state.error_history.append(record)
            return FallbackNode()

class FallbackNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "StartRecoveryNode":
        print("\n=== [Fallback Node] Activating Graceful Degradation Protocol... ===")
        recovery_agent = ctx.deps.recovery_agent
        
        backup_opt = await recovery_agent.select_backup(
            query=ctx.state.query,
            error_msg=ctx.state.last_error or "Permanent error"
        )
        
        ctx.state.backup_plan_selected = backup_opt
        print(f"  Selected Backup Strategy: [{backup_opt.value.upper()}]")
        
        record = ErrorRecord(
            attempt=ctx.state.call_attempts,
            error_msg=ctx.state.last_error or "Permanent error",
            category="Permanent",
            action_taken=f"Gracefully degraded to Backup: {backup_opt.value}"
        )
        ctx.state.error_history.append(record)
        return StartRecoveryNode()

class StartRecoveryNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "RecordNode":
        print("\n=== [Start Recovery Node] Engaging backup data and endpoints... ===")
        backup = ctx.state.backup_plan_selected
        
        if backup == BackupOption.SIMPLE_METHOD:
            print("  [Recovery Action] Switched to simpler, lightweight CPU execution path. Success.")
        elif backup == BackupOption.SAVED_DATA:
            print("  [Recovery Action] Fetched read-only database replica from local cache filesystem. Integrity restored.")
        elif backup == BackupOption.DEFAULT_ANSWER:
            print("  [Recovery Action] Serving default generic safe JSON response. Integrity restored.")
        else:
            print("  [Recovery Action] Paging human operator on-call via pagerduty. Handed off.")
            
        ctx.state.operation_outcome = "RECOVERED"
        return RecordNode()

class EmergencyNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> Union["ResumeNode", "StopNode"]:
        print("\n=== [Emergency Node] FATAL ALARM! Activating Emergency Operations! ===")
        
        # Save Work
        ctx.state.emergency_saved = True
        print("  [Emergency Save] Serializing transaction state to encrypted fallback file: C:/temp/active_state.json... SUCCESS.")
        
        # Alert Team
        ctx.state.emergency_alerted = True
        print("  [Emergency Alert] Sounding pager/Siren! Dispatching webhook alert to SRE team on slack channel #ops-alerts... SENT.")
        
        # Run safety evaluation
        recovery_agent = ctx.deps.recovery_agent
        verdict = await recovery_agent.evaluate_safety(ctx.state.error_history)
        ctx.state.safety_verdict = verdict
        
        print("\n[Safety Review Assessment]")
        print(f"  - Continue Allowed?: {'YES' if verdict.is_safe else 'NO'}")
        print(f"  - Reasoning: {verdict.reasoning}")
        print(f"  - Next Structural Move: {verdict.next_action.upper()}")
        
        record = ErrorRecord(
            attempt=ctx.state.call_attempts,
            error_msg=ctx.state.last_error or "Critical error",
            category="Critical",
            action_taken=f"Emergency state saved. Team alerted. Safety verdict next action: {verdict.next_action}"
        )
        ctx.state.error_history.append(record)
        
        if verdict.next_action == "RESUME":
            return ResumeNode()
        else:
            return StopNode()

class ResumeNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "RecordNode":
        print("\n=== [Resume Node] Attempting self-healing reconstruction from state snapshot... ===")
        print("  Restored operation from previous valid checkpoint. Continuing execution...")
        return RecordNode()

class StopNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "RecordNode":
        print("\n=== [Stop Node] Commencing Safe Shutdown protocols... ===")
        print("  - Disconnecting read-write socket listeners.")
        print("  - Setting PostgreSQL database into READ-ONLY protection-mode.")
        print("  - Releasing resources and exiting gracefully.")
        ctx.state.operation_outcome = "EMERGENCY_STOP"
        return RecordNode()

class RecordNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "EndNode":
        print("\n=== [Record Node] Recording event log & feeding continuous learning loop... ===")
        learning_agent = ctx.deps.learning_agent
        
        patterns = await learning_agent.run(
            error_history=ctx.state.error_history,
            outcome=ctx.state.operation_outcome
        )
        ctx.state.learned_patterns = patterns
        print("  Learning synthesized. Root causes traced, system updates queued for reinforcement.")
        return EndNode()

class EndNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[str]:
        print("\n=== [End Node] Finalizing Execution & Generating Report... ===")
        
        outcome_color_map = {
            "SUCCESS": "SUCCESS (🟢 GREEN)",
            "RECOVERED": "RECOVERED (🟡 YELLOW - GRACEFUL DEGRADATION)",
            "EMERGENCY_STOP": "EMERGENCY STOPPED (🔴 RED - SAFE PROTECTED SHUTDOWN)"
        }
        
        outcome_desc = outcome_color_map.get(ctx.state.operation_outcome, ctx.state.operation_outcome)
        
        error_summary = []
        for i, rec in enumerate(ctx.state.error_history, 1):
            error_summary.append(
                f"  Attempt {rec.attempt} | Class: {rec.category} | Reason: {rec.error_msg}\n"
                f"    -> Resolution Action taken: {rec.action_taken}"
            )
            
        history_text = "\n".join(error_summary) if error_summary else "  None. Completed on first attempt."
        
        report = (
            "==============================================================\n"
            "            RELIABILITY SYSTEM EXECUTION REPORT\n"
            "==============================================================\n"
            f"Operation Description: '{ctx.state.query}'\n"
            f"Final System Outcome Status: {outcome_desc}\n"
            f"Total Service Invocations: {ctx.state.call_attempts}\n"
            f"Pre-checks Verified?: {'Yes' if ctx.state.safety_checked else 'No'}\n"
            f"Emergency State Saved?: {'Yes' if ctx.state.emergency_saved else 'No'}\n"
            f"On-Call Engineers Paged?: {'Yes' if ctx.state.emergency_alerted else 'No'}\n"
            "\nEncountered Error History log:\n"
            f"{history_text}\n"
            "\nTracked Error Patterns & Continuous Learning Insights:\n"
            f"{ctx.state.learned_patterns}\n"
            "=============================================================="
        )
        ctx.state.final_report = report
        print(report)
        return End(report)

def build_graph() -> Graph:
    return Graph(
        nodes=[
            StartNode,
            SafetyChecksNode,
            MakeCallNode,
            ProcessResultNode,
            SuccessNode,
            CatchErrorNode,
            RetryNode,
            FallbackNode,
            StartRecoveryNode,
            EmergencyNode,
            ResumeNode,
            StopNode,
            RecordNode,
            EndNode,
        ],
        state_type=State,
        run_end_type=str,
    )

def build_deps() -> Dependencies:
    return Dependencies(
        safety_agent=SafetyCheckAgent(),
        service_agent=ServiceCallAgent(),
        triage_agent=TriageAgent(),
        recovery_agent=RecoveryAgent(),
        learning_agent=LearningAgent(),
    )

async def run_graph(query: str, scenario: str = "transient_success") -> tuple[str, State]:
    graph = build_graph()
    deps = build_deps()
    state = State(query=query, scenario=scenario)
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output, state
