from typing import Optional
from .agents import ScoutAgent, ClusteringAgent, TargetSelectorAgent, DeepDiveSpecialistAgent
from .models import State, Dependencies, ScoutedSource, ClusteredTheme, ThemeEvaluation, DeepDiveArtifacts
from pydantic_graph import BaseNode, End, GraphRunContext, Graph

class StartNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ScoutNode":
        print(f"\n--- [Start Node] Launching Broad Exploration & Discovery Pipeline ---")
        ctx.state.system_status = "Pipeline initialized"
        return ScoutNode()

class ScoutNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ClusterNode":
        print("\n--- [Scout Node] Gaining Broad Literature & Patent Domain Intelligence ---")
        ctx.state.system_status = "Scouting broad literature space"
        
        scout = ctx.deps.scout_agent
        sources = await scout.run(ctx.state.goal)
        ctx.state.sources = sources
        
        print(f"    Scouting Complete. Collected {len(sources)} high-fidelity research sources.")
        for s in sources:
            print(f"      - [{s.source_type}] '{s.title}' ({s.author})")
        print()
        
        return ClusterNode()

class ClusterNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "SelectNode":
        print("--- [Cluster Node] Mapping Knowledge Space & Emerging Themes ---")
        ctx.state.system_status = "Clustering themes"
        
        clustering = ctx.deps.clustering_agent
        themes = await clustering.run(ctx.state.sources)
        ctx.state.themes = themes
        
        print(f"    Conceptual Mapping Complete. Clustered {len(themes)} distinct emerging research areas:")
        for idx, t in enumerate(themes, 1):
            print(f"      Theme {idx}: {t.name}")
            print(f"               Description: {t.description}")
            print(f"               Sources: {len(t.associated_source_titles)} items grouped.")
        print()
        
        return SelectNode()

class SelectNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "DeepDiveNode":
        print("--- [Select Node] Scoring Themes & Picking Deep-Dive Target ---")
        ctx.state.system_status = "Evaluating target themes"
        
        selector = ctx.deps.target_selector_agent
        evaluations = []
        
        for theme in ctx.state.themes:
            evaluation = await selector.run(theme)
            evaluations.append(evaluation)
            
        ctx.state.theme_evaluations = evaluations
        
        # Calculate rank score and find highest (Average score)
        best_theme = None
        best_score = -1.0
        
        print("\n    SELECTION CRITERIA EVALUATIONS:")
        for ev in evaluations:
            avg_score = (ev.novelty_score + ev.potential_impact + ev.feasibility + ev.knowledge_gaps) / 4.0
            print(f"      - Theme: '{ev.theme_name}' (Overall Score: {avg_score:.2f})")
            print(f"        [Novelty: {ev.novelty_score:.1f}, Impact: {ev.potential_impact:.1f}, Feasibility: {ev.feasibility:.1f}, Gaps: {ev.knowledge_gaps:.1f}]")
            print(f"        Justification: {ev.justification}")
            
            if avg_score > best_score:
                best_score = avg_score
                # Find matching clustered theme object
                best_theme = next((t for t in ctx.state.themes if t.name == ev.theme_name), None)
                
        if not best_theme and ctx.state.themes:
            best_theme = ctx.state.themes[0]
            best_score = 8.0
            
        ctx.state.selected_target = best_theme
        print(f"\n    [Winner Selected] Target Picked for Deep-Dive: '{best_theme.name if best_theme else 'N/A'}' (Score: {best_score:.2f})")
        print()
        
        return DeepDiveNode()

class DeepDiveNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "EndNode":
        target = ctx.state.selected_target
        if not target:
            return EndNode()
            
        print(f"--- [Deep-Dive Node] Performing Deep Investigation & Hypothesis Formulation ---")
        ctx.state.system_status = f"Deep investigation on {target.name}"
        
        # Find evaluation matching selected target
        eval_match = next((ev for ev in ctx.state.theme_evaluations if ev.theme_name == target.name), None)
        if not eval_match:
            eval_match = ThemeEvaluation(
                theme_name=target.name, novelty_score=8.0, potential_impact=8.0, feasibility=8.0, knowledge_gaps=8.0, justification="Default target evaluation."
            )
            
        deep_diver = ctx.deps.deep_dive_agent
        artifacts = await deep_diver.run(target, eval_match)
        ctx.state.artifacts = artifacts
        
        print("    [Deep-Dive Specialist] Extracted scientific artifacts and formulated hypotheses successfully.")
        return EndNode()

class EndNode(BaseNode[State, Dependencies, State]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[State]:
        print("\n--- [End Node] Finalizing Technical Scouting Report ---")
        ctx.state.system_status = "Exploration completed"
        
        target = ctx.state.selected_target
        artifacts = ctx.state.artifacts
        
        print("\n" + "="*60)
        print("SCIENTIFIC DISCOVERY & TECHNOLOGY SCOUTING REPORT")
        print("="*60)
        print(f"Research Goal:     {ctx.state.goal}")
        print(f"Selected Target:   {target.name if target else 'N/A'}")
        
        if artifacts:
            print("\nCONCEPTUAL MODEL:")
            print(artifacts.notes)
            
            print("\nBIBLIOGRAPHY & CITATIONS:")
            for bib in artifacts.bibliography:
                print(f"  - {bib}")
                
            print("\nFORMULATED TESTABLE HYPOTHESES:")
            for hyp in artifacts.hypotheses:
                print(f"  * {hyp}")
                
        print("\nRECOMMENDED NEXT STEPS:")
        print("  1. Synthesize graded solid-state polymer membranes based on hybrid PEO/LLZO composite matrices.")
        print("  2. Perform initial atomic layer deposition (ALD) alumina coatings to test chemical degradation kinetics.")
        print("  3. Run baseline electrochemical impedance spectroscopy (EIS) checks to validate Hypothesis 1.")
        print("="*60 + "\n")
        
        return End(ctx.state)

def build_graph() -> Graph:
    return Graph(
        nodes=[StartNode, ScoutNode, ClusterNode, SelectNode, DeepDiveNode, EndNode],
        state_type=State,
        run_end_type=State
    )

def build_deps() -> Dependencies:
    return Dependencies(
        scout_agent=ScoutAgent(),
        clustering_agent=ClusteringAgent(),
        target_selector_agent=TargetSelectorAgent(),
        deep_dive_agent=DeepDiveSpecialistAgent(),
    )

async def run_graph(goal: str) -> State:
    graph = build_graph()
    deps = build_deps()
    state = State(goal=goal)
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output
