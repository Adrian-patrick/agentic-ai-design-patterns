# Multi-Agent Collaboration

A multi-agent orchestration system demonstrating the **Multi-Agent Collaboration** pattern using `pydantic-ai` and `pydantic-graph`.

## Project Overview

This project implements a cooperative multi-agent workflow where a **ClassifierAgent** first determines which specialized sub-agents are needed to fulfill a user request, and an **OrchestratorAgent** delegates specific instructions to each required sub-agent (the **SummarizerAgent** and the **PointerAgent**) before synthesizing the final, consolidated response.

### Architectural Workflow
1. **Classification Phase**: The `ClassifierAgent` receives the user query and decides whether the task requires a summary, key points, or both.
2. **Delegation Phase**: The `OrchestratorAgent` takes the query and decision to generate targeted, custom instructions for each required sub-agent.
3. **Execution Phase**: The required sub-agents (the `SummarizerAgent` and `PointerAgent`) execute their respective tasks on the source text using the instructions provided by the orchestrator.
4. **Synthesis Phase**: The `OrchestratorAgent` gathers the sub-agents' outputs and compiles them into a unified, comprehensive final response.
5. **Graph Orchestration**: The workflow is managed via a stateful graph: `StartNode` -> `ClassifierNode` -> `OrchestratorNode` -> `SummarizerNode` -> `PointerNode` -> `SynthesisNode`.

## Technology Stack
- **Framework**: [pydantic-ai](https://ai.pydantic.dev/) & [pydantic-graph](https://ai.pydantic.dev/graph/)
- **LLM Provider**: Azure OpenAI
- **Environment**: Python 3.13+, Managed via `uv`

## Project Structure
- `main.py`: Entry point for running the agentic graph.
- `agentic_system/`:
    - `graph.py`: Defines the graph nodes (`ClassifierNode`, `OrchestratorNode`, `SummarizerNode`, `PointerNode`, `SynthesisNode`) which orchestrate the workflow.
    - `agents.py`: Implementations for the agents (`ClassifierAgent`, `OrchestratorAgent`, `SummarizerAgent`, `PointerAgent`).
    - `models.py`: Shared `State` (tracking sub-agent requirements, instructions, and outputs) and `Dependencies`.
    - `prompts.py`: Optimized system prompts and query content for the collaboration pattern.
    - `config.py`: Azure OpenAI configuration.

## Getting Started

1. Configure your `.env` file with Azure OpenAI credentials.
2. Ensure you have dependencies installed (managed automatically via `uv run`).
3. Run the system:
   ```bash
   uv run main.py
   ```
