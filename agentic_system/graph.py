import asyncio
from typing import Union
from pydantic_graph import BaseNode, End, GraphRunContext, Graph
from .agents import DecisionGateAgent, UIPresenterAgent, FeedbackLearningAgent, FatigueMonitorAgent
from .models import (
    State,
    Dependencies,
    GateType,
    DecisionType,
    QueueItem,
    HumanDecision,
    FeedbackLog,
)

class StartNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "IdentifyDecisionPointsNode":
        print("\n=== [Start Node] Beginning Agent Processing loop... ===")
        print(f"  Target Operation: '{ctx.state.query}'")
        print(f"  Active Scenario: {ctx.state.scenario.upper()}")
        return IdentifyDecisionPointsNode()

class IdentifyDecisionPointsNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "AddReviewQueueNode":
        print("\n=== [Identify Decision Points Node] Scanning operation query for Decision Gates... ===")
        gate = await ctx.deps.gate_agent.run(ctx.state.query, ctx.state.scenario)
        ctx.state.gate_identified = gate
        print(f"  Identified Decision Gate point: [{gate.value.upper()}]")
        return AddReviewQueueNode()

class AddReviewQueueNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "UIPresentationNode":
        print("\n=== [Add Review Queue Node] Routing task to Human Review Queue... ===")
        print("  - Batching similar operations.")
        print("  - Categorizing by task priority.")
        return UIPresentationNode()

class UIPresentationNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "HumanDecisionNode":
        print("\n=== [UI Presentation Node] Formulating review item presentation context... ===")
        item = await ctx.deps.ui_agent.run(ctx.state.query, ctx.state.scenario)
        ctx.state.queue_item = item
        
        print("\n[Human Operator Queue UI Card]")
        print("------------------------------------------------------------")
        print(f"  📌 Context: {item.context_summary}")
        print(f"  ⚠️ Urgency Tier: {item.urgency.upper()}")
        print(f"  ⏳ SLA response window: {item.sla_timer_sec}s countdown active")
        print(f"  🤖 AI Original draft output:\n    '{item.original_agent_output}'")
        print(f"  📄 Target Content Draft:\n    '{item.content_draft}'")
        print("------------------------------------------------------------")
        return HumanDecisionNode()

class HumanDecisionNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> Union[
        "AcceptAgentOutputNode",
        "RejectWithReasonNode",
        "HumanEditsContentNode",
        "FullManualControlNode",
    ]:
        print("\n=== [Human Decision Node] Intercepting Operator keyboard/mouse actions... ===")
        scenario = ctx.state.scenario
        
        # Simulate high-fidelity human decisions based on scenario
        if scenario == "approve":
            decision = HumanDecision(
                decision=DecisionType.APPROVE,
                reviewer_feedback="Original draft meets corporate SRE standards. Approved."
            )
            ctx.state.human_decision = decision
            print("  [Human Decision Triggered] APPROVED: Content accepted.")
            return AcceptAgentOutputNode()
            
        elif scenario == "deny":
            decision = HumanDecision(
                decision=DecisionType.DENY,
                reviewer_feedback="Resume screening error. Bob has Python and Go skills but the Rust Team requires senior-level native Rust experience."
            )
            ctx.state.human_decision = decision
            print("  [Human Decision Triggered] DENIED: Content rejected.")
            return RejectWithReasonNode()
            
        elif scenario == "edit":
            decision = HumanDecision(
                decision=DecisionType.EDIT,
                reviewer_feedback="French: Bonjour le monde",
                edited_content="French: Bonjour tout le monde"
            )
            ctx.state.human_decision = decision
            print("  [Human Decision Triggered] EDIT: Content polished manually.")
            return HumanEditsContentNode()
            
        else: # takeover_fatigue
            decision = HumanDecision(
                decision=DecisionType.TAKEOVER,
                takeover_reason="Refund transfer amount ($12,500) exceeds default agent credit limit ($10,000). Direct senior compliance officer manual takeover initiated."
            )
            ctx.state.human_decision = decision
            print("  [Human Decision Triggered] TAKEOVER: Manual operator control engaged.")
            return FullManualControlNode()

class AcceptAgentOutputNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ContinueWorkflowNode":
        print("\n=== [Accept Agent Output Node] Accepting agent draft... ===")
        print("  Proceeding to execute downstream publication.")
        return ContinueWorkflowNode()

class RejectWithReasonNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "CaptureRejectionPatternNode":
        print("\n=== [Reject With Reason Node] Rejecting content... ===")
        print(f"  Reason logged: '{ctx.state.human_decision.reviewer_feedback}'")
        return CaptureRejectionPatternNode()

class HumanEditsContentNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "RecordEditChangesNode":
        print("\n=== [Human Edits Content Node] Merging human edits into draft workspace... ===")
        print(f"  Original: '{ctx.state.human_decision.reviewer_feedback}'")
        print(f"  Modified: '{ctx.state.human_decision.edited_content}'")
        return RecordEditChangesNode()

class FullManualControlNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "LogTakeoverReasonNode":
        print("\n=== [Full Manual Control Node] AI Agent safely suspended. ===")
        print(f"  Takeover Reason: '{ctx.state.human_decision.takeover_reason}'")
        return LogTakeoverReasonNode()

class ContinueWorkflowNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "TrackDecisionMetricsNode":
        print("\n=== [Continue Workflow Node] Resuming main pipeline execution... ===")
        return TrackDecisionMetricsNode()

class CaptureRejectionPatternNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "UpdateAgentTrainingNode":
        print("\n=== [Capture Rejection Pattern Node] Recording negative feedback log... ===")
        return UpdateAgentTrainingNode()

class RecordEditChangesNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "UpdateAgentTrainingNode":
        print("\n=== [Record Edit Changes Node] Recording structural edits differences... ===")
        return UpdateAgentTrainingNode()

class LogTakeoverReasonNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "UpdateAgentTrainingNode":
        print("\n=== [Log Takeover Reason Node] Recording manual takeover override parameters... ===")
        return UpdateAgentTrainingNode()

class UpdateAgentTrainingNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ImproveFutureDecisionsNode":
        print("\n=== [Update Agent Training Node] Feeding corrections to SRE Learning loop... ===")
        feedback_agent = ctx.deps.feedback_agent
        log = await feedback_agent.run(ctx.state.human_decision)
        ctx.state.feedback_log = log
        return ImproveFutureDecisionsNode()

class ImproveFutureDecisionsNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "TrackDecisionMetricsNode":
        print("\n=== [Improve Future Decisions Node] Guidelines updated in agent context! ===")
        log = ctx.state.feedback_log
        print(f"  * Learning insights: {log.learning_points}")
        print(f"  * Guidelines constraint added: '{log.guidelines_updated}'")
        ctx.state.learned_patterns = f"Learned Constraint: {log.guidelines_updated}\nFeedback: {log.learning_points}"
        return TrackDecisionMetricsNode()

class TrackDecisionMetricsNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "MonitorFatigueNode":
        print("\n=== [Track Decision Metrics Node] Updating decision frequency databases... ===")
        return MonitorFatigueNode()

class MonitorFatigueNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> Union["ReduceHumanLoadNode", "MaintainCurrentFlowNode"]:
        print("\n=== [Monitor Fatigue Node] Auditing operator work fatigue thresholds... ===")
        score, action = await ctx.deps.fatigue_agent.evaluate(ctx.state.scenario)
        ctx.state.fatigue_score = score
        ctx.state.load_action = action
        
        if action == "REDUCE":
            return ReduceHumanLoadNode()
        else:
            return MaintainCurrentFlowNode()

class ReduceHumanLoadNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "IncreaseAutomationNode":
        print("\n=== [Reduce Human Load Node] HIGH WORKLOAD FATIGUE DETECTED! ===")
        print("  - Throttling human review queue rates.")
        print("  - Batching items in larger groups to lower notification count.")
        return IncreaseAutomationNode()

class IncreaseAutomationNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "GenerateReportsNode":
        print("\n=== [Increase Automation Node] Elevating AI confidence thresholds... ===")
        ctx.state.automation_level = 0.85
        print(f"  AI Automation Rate elevated: 50% ➡️ {ctx.state.automation_level * 100:.0f}% (OFFLOADING HUMAN)")
        return GenerateReportsNode()

class MaintainCurrentFlowNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "GenerateReportsNode":
        print("\n=== [Maintain Current Flow Node] Load within safe margins. ===")
        print(f"  Maintained baseline AI Automation Rate: {ctx.state.automation_level * 100:.0f}%")
        return GenerateReportsNode()

class GenerateReportsNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "EndNode":
        print("\n=== [Generate Reports Node] Consolidating HITL operational audit trails... ===")
        return EndNode()

class EndNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[str]:
        print("\n=== [End Node] Generating Final Workflow Complete Report... ===")
        
        gate_str = ctx.state.gate_identified.value if ctx.state.gate_identified else "N/A"
        decision_str = ctx.state.human_decision.decision.value if ctx.state.human_decision else "N/A"
        feedback_str = ctx.state.human_decision.reviewer_feedback or "N/A" if ctx.state.human_decision else "N/A"
        
        learning_section = ""
        if ctx.state.feedback_log:
            learning_section = (
                f"\nContinuous Training Feedback Log:\n"
                f"  * Insights Gained: {ctx.state.feedback_log.learning_points}\n"
                f"  * System Prompt Constraints Added: '{ctx.state.feedback_log.guidelines_updated}'\n"
            )
            
        report = (
            "==============================================================\n"
            "            HUMAN-IN-THE-LOOP (HITL) WORKFLOW REPORT\n"
            "==============================================================\n"
            f"Objective Task Query: '{ctx.state.query}'\n"
            f"Active Decision Gate: {gate_str}\n"
            f"Human Operator Action: {decision_str}\n"
            f"Operator Feedback/Notes: '{feedback_str}'\n"
            f"Reviewer Fatigue Index: {ctx.state.fatigue_score:.2f} ({ctx.state.load_action})\n"
            f"Final AI System Automation Rate: {ctx.state.automation_level * 100:.0f}%\n"
            f"{learning_section}"
            "=============================================================="
        )
        ctx.state.final_report = report
        print(report)
        return End(report)

def build_graph() -> Graph:
    return Graph(
        nodes=[
            StartNode,
            IdentifyDecisionPointsNode,
            AddReviewQueueNode,
            UIPresentationNode,
            HumanDecisionNode,
            AcceptAgentOutputNode,
            RejectWithReasonNode,
            HumanEditsContentNode,
            FullManualControlNode,
            ContinueWorkflowNode,
            CaptureRejectionPatternNode,
            RecordEditChangesNode,
            LogTakeoverReasonNode,
            UpdateAgentTrainingNode,
            ImproveFutureDecisionsNode,
            TrackDecisionMetricsNode,
            MonitorFatigueNode,
            ReduceHumanLoadNode,
            IncreaseAutomationNode,
            MaintainCurrentFlowNode,
            GenerateReportsNode,
            EndNode,
        ],
        state_type=State,
        run_end_type=str,
    )

def build_deps() -> Dependencies:
    return Dependencies(
        gate_agent=DecisionGateAgent(),
        ui_agent=UIPresenterAgent(),
        feedback_agent=FeedbackLearningAgent(),
        fatigue_agent=FatigueMonitorAgent(),
    )

async def run_graph(query: str, scenario: str = "approve") -> tuple[str, State]:
    graph = build_graph()
    deps = build_deps()
    state = State(query=query, scenario=scenario)
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output, state
