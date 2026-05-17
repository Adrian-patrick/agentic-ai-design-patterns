# Tool Use Architecture

A multi-agent orchestration system demonstrating the **Tool Use (Function Calling)** pattern using `pydantic-ai` and `pydantic-graph`.

## Project Overview

This project implements a tool-driven workflow where a **ToolAgent** leverages external capabilities (such as web search and calculation) to gather necessary data for a query, and a **ResponseAgent** synthesizes this data into a final, comprehensive response.

### Architectural Workflow
1. **Tool Execution**: The `ToolAgent` receives the user query and uses its available tools (DuckDuckGo Search, Calculator) to gather relevant real-world or computational data.
2. **Response Synthesis**: The `ResponseAgent` takes the context and data gathered by the `ToolAgent` along with the original user query, and formulates a final, well-structured answer.
3. **Graph Orchestration**: The workflow is managed via a stateful graph transitioning from `StartNode` -> `ToolNode` -> `ResponseNode`.

## Technology Stack
- **Framework**: [pydantic-ai](https://ai.pydantic.dev/) & [pydantic-graph](https://ai.pydantic.dev/graph/)
- **LLM Provider**: Azure OpenAI
- **Tools**: DuckDuckGo Search (`ddgs`), Python `eval` (Calculator)
- **Environment**: Python 3.13+, Managed via `uv`

## Project Structure
- `main.py`: Entry point for running the agentic graph.
- `agentic_system/`:
    - `graph.py`: Defines the `ToolNode` and `ResponseNode` which orchestrate the workflow.
    - `agents.py`: Implementations for the `ToolAgent` (containing `@agent.tool` definitions) and `ResponseAgent`.
    - `models.py`: Shared `State` (tracking responses) and `Dependencies`.
    - `prompts.py`: Optimized system prompts for data gathering and response formulation.
    - `config.py`: Azure OpenAI configuration.

## Getting Started

1. Configure your `.env` file with Azure OpenAI credentials.
2. Ensure you have dependencies installed (managed automatically via `uv run`).
3. Run the system:
   ```bash
   uv run main.py
   ```
