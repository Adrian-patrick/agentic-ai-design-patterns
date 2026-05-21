from .agents import TaskAgent, FeedbackValidatorAgent, LearnerAgent, EvaluatorAgent
from .models import State, Dependencies, FewShotExample, LearningReport, FeedbackSignal
from pydantic_graph import BaseNode, End, GraphRunContext, Graph
from typing import Union

class StartNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ExecuteNode":
        return ExecuteNode()

class ExecuteNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "FeedbackCollectionNode":
        print("\n=== [Execute Node] Running Task Agent... ===")
        task_agent = ctx.deps.task_agent
        response = await task_agent.run(
            query=ctx.state.query,
            prompt_template=ctx.state.prompt_template,
            few_shot_examples=ctx.state.few_shot_examples,
            preference_rules=ctx.state.preference_rules
        )
        ctx.state.response = response
        print(f"--- Response Generated: ---\n{response}\n")
        return FeedbackCollectionNode()

class FeedbackCollectionNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "CleanNode":
        print("\n=== [Feedback Collection Node] Aggregating Signals... ===")
        fb = ctx.state.feedback
        if fb:
            print(f"   [Signal] Quality Rating: {fb.quality_rating}/5")
            print(f"   [Signal] Automated Evaluation Score: {fb.automated_eval_score:.2f}")
            print(f"   [Signal] User Correction: '{fb.user_correction}'")
            print(f"   [Signal] Task Outcome: {fb.task_outcome}")
        else:
            print("   [Signal] No feedback signals collected this turn.")
        return CleanNode()

class CleanNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> Union["ValidateNode", "ReportNode"]:
        print("\n=== [Clean Node] Performing Data Quality Check... ===")
        validator = ctx.deps.feedback_validator_agent
        fb = ctx.state.feedback
        
        result = await validator.run(
            query=ctx.state.query,
            user_correction=fb.user_correction if fb else None
        )
        
        if result.is_adversarial:
            print("   [ALERT] Malicious/Adversarial feedback detected! Rejecting update...")
            ctx.state.is_malicious = True
            return ReportNode()
        
        if result.is_noisy:
            print("   [Info] Noisy feedback detected. Filtering signal...")
            
        ctx.state.validation_passed = True
        print("   [Clean Check] Feedback verified. Processing...")
        return ValidateNode()

class ValidateNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> Union["LearnNode", "ReportNode"]:
        print("\n=== [Validate Node] Validating Patterns for Learning... ===")
        fb = ctx.state.feedback
        
        # Decide if we need adaptation (low rating or explicit correction)
        if fb and (fb.quality_rating < 4 or fb.user_correction):
            print("   [Decision] Quality below threshold. Triggering Learning Loop...")
            return LearnNode()
            
        print("   [Decision] Performance stable. No learning required.")
        return ReportNode()

class LearnNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "TestNode":
        print("\n=== [Learn Node] Selecting Optimization Method... ===")
        learner = ctx.deps.learner_agent
        fb = ctx.state.feedback
        
        action = await learner.run(
            query=ctx.state.query,
            response=ctx.state.response or "",
            user_correction=fb.user_correction or ""
        )
        
        print(f"   [Proposed Adaptation] Method: {action.action_type} | Change: '{action.value}'")
        ctx.state.adaptation_applied = f"{action.action_type}: {action.value}"
        return TestNode()

class TestNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ReportNode":
        print("\n=== [Test Node] A/B Testing & Evaluation... ===")
        evaluator = ctx.deps.evaluator_agent
        fb = ctx.state.feedback
        
        # Parse proposed adaptation
        adaptation = ctx.state.adaptation_applied or ""
        action_type, action_value = adaptation.split(":", 1)
        action_type = action_type.strip()
        action_value = action_value.strip()
        
        score = await evaluator.run(
            query=ctx.state.query,
            failed_response=ctx.state.response or "",
            user_correction=fb.user_correction or "",
            proposed_action=action_type,
            proposed_value=action_value
        )
        
        print(f"   [A/B Evaluation] Simulated score: {score:.2f}")
        
        # Deploy if improvement, rollback if regression
        if score >= 0.7:
            print("   [Monitor Node] Improvement confirmed! Deploying changes...")
            ctx.state.monitor_status = "improvement"
            if action_type == "UpdatePrompts":
                ctx.state.prompt_template = action_value
            elif action_type == "AddExamples":
                ctx.state.few_shot_examples.append(FewShotExample(query=ctx.state.query, preferred_response=action_value))
            elif action_type == "UpdatePrefs":
                ctx.state.preference_rules.append(action_value)
        else:
            print("   [Monitor Node] Performance regression or neutral outcome. Rolling back changes...")
            ctx.state.monitor_status = "regression"
            
        return ReportNode()

class ReportNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[str]:
        print("\n=== [Report Node] Generating Learning Report... ===")
        
        deployed = []
        failures = []
        
        if ctx.state.monitor_status == "improvement" and ctx.state.adaptation_applied:
            deployed.append(ctx.state.adaptation_applied)
        elif ctx.state.monitor_status == "regression" and ctx.state.adaptation_applied:
            failures.append(f"Rolled back regression: {ctx.state.adaptation_applied}")
            
        if ctx.state.is_malicious:
            failures.append("Blocked adversarial prompt injection attempt")
            
        status = "Improved" if deployed else ("Security Guard Triggered" if ctx.state.is_malicious else "Stable")
        
        ctx.state.learning_report = LearningReport(
            turns_operated=1,
            improvements_deployed=deployed,
            failures_analyzed=failures,
            system_status=status
        )
        
        print(f"--- Learning Report Generated: System Status -> {status} ---")
        return End(ctx.state.response or "")

def build_graph() -> Graph:
    return Graph(
        nodes=[StartNode, ExecuteNode, FeedbackCollectionNode, CleanNode, ValidateNode, LearnNode, TestNode, ReportNode],
        state_type=State,
        run_end_type=str
    )

def build_deps() -> Dependencies:
    return Dependencies(
        task_agent=TaskAgent(),
        feedback_validator_agent=FeedbackValidatorAgent(),
        learner_agent=LearnerAgent(),
        evaluator_agent=EvaluatorAgent(),
    )

async def run_graph(query: str, feedback: FeedbackSignal = None, state: State = None) -> tuple[str, State]:
    graph = build_graph()
    deps = build_deps()
    if state is None:
        state = State(query=query, feedback=feedback)
    else:
        state.query = query
        state.feedback = feedback
        
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output, state
