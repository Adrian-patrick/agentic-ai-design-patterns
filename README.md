# Planner-Worker Architecture

A multi-agent orchestration system demonstrating the **Planner-Worker** pattern using `pydantic-ai` and `pydantic-graph`.

## Project Overview

This project implements a planning and execution workflow where a **PlannerAgent** breaks down a complex query into a step-by-step executable plan, and a **WorkerAgent** uses external capabilities (such as web search and calculation) to execute the plan and formulate the final response.

### Architectural Workflow
1. **Planning Phase**: The `PlannerAgent` receives the user query and generates a structured, step-by-step plan.
2. **Execution Phase**: The `WorkerAgent` receives the original query and the execution plan. It then leverages its available tools (DuckDuckGo Search, Calculator) to gather necessary data and synthesize the final response.
3. **Graph Orchestration**: The workflow is managed via a stateful graph transitioning from `StartNode` -> `PlannerNode` -> `WorkerNode`.

## Technology Stack
- **Framework**: [pydantic-ai](https://ai.pydantic.dev/) & [pydantic-graph](https://ai.pydantic.dev/graph/)
- **LLM Provider**: Azure OpenAI
- **Tools**: DuckDuckGo Search (`ddgs`), Python `eval` (Calculator)
- **Environment**: Python 3.13+, Managed via `uv`

## Project Structure
- `main.py`: Entry point for running the agentic graph.
- `agentic_system/`:
    - `graph.py`: Defines the `PlannerNode` and `WorkerNode` which orchestrate the workflow.
    - `agents.py`: Implementations for the `PlannerAgent` and `WorkerAgent` (containing `@agent.tool` definitions).
    - `models.py`: Shared `State` (tracking plans and responses) and `Dependencies`.
    - `prompts.py`: Optimized system prompts for planning and execution.
    - `config.py`: Azure OpenAI configuration.

## Getting Started

1. Configure your `.env` file with Azure OpenAI credentials.
2. Ensure you have dependencies installed (managed automatically via `uv run`).
3. Run the system:
   ```bash
   uv run main.py
   ```
