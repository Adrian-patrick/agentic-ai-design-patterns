from .agents import Summarizer,Critic
from .models import State, Dependencies
from pydantic_graph import BaseNode, End, GraphRunContext, Graph

class StartNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "SummarizerCriticNode":
        return SummarizerCriticNode()

class SummarizerCriticNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[str]:

        summarizer = ctx.deps.summarizer
        critic = ctx.deps.critic

        for iter_no in range(ctx.state.max_iterations):

            print("============inside SummarizerCritic node iter no============",iter_no+1)

            if not ctx.state.critic_response:
                summarizer_output = await summarizer.summarize(ctx.state.query)
            else:
                summarizer_output = await summarizer.summarizewithfeedback(ctx.state.query,ctx.state.critic_response.feedback)

            ctx.state.summarizer_response = summarizer_output

            critic_output = await critic.critics(summarizer_output)
            ctx.state.critic_response = critic_output

            if critic_output.satisfied:
                break
        
        return End(summarizer_output)




        
def build_graph() -> Graph:
    return Graph(
        nodes=[StartNode, SummarizerCriticNode],
        state_type=State,
        run_end_type=str
    )
        
def build_deps() -> Dependencies:
    return Dependencies(
        summarizer=Summarizer(),
        critic=Critic(),
    )

async def run_graph(query: str) -> str:
    graph = build_graph()
    deps = build_deps()
    state = State(query=query)
    # The run method returns a RunResult which contains the output
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output
    
    
