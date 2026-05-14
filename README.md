# Routing 

A multi-agent orchestration system demonstrating the **Routing Pattern** using `pydantic-ai` and `pydantic-graph`.

## Project Overview

This project implements a dynamic routing workflow where a specialized **Router** agent analyzes incoming queries and directs them to the most appropriate specialized agent. This architecture allows the system to handle multiple intents (summarization vs. analytical extraction) efficiently within a single graph.

### Architectural Workflow
1. **Router**: Analyzes the query intent and classifies it into one of the available routes.
2. **Specialized Nodes**:
   - **Summarizer**: If the intent is summarization, the system routes to this node for a comprehensive content overview.
   - **Pointer**: If the intent is analytical (key points/insights), the system routes to this node for deep insight extraction.
3. **Execution**: The graph transitions dynamically from the `RoutingNode` to either the `SummaryNode` or `PointerNode` based on the router's decision.

## Technology Stack
- **Framework**: [pydantic-ai](https://ai.pydantic.dev/) & [pydantic-graph](https://ai.pydantic.dev/graph/)
- **LLM Provider**: Azure OpenAI
- **Environment**: Python 3.13+, Managed via `uv`

## Project Structure
- `main.py`: Entry point for running the graph with sample queries.
- `agentic_system/`:
    - `graph.py`: Defines the `pydantic-graph` nodes and transitions.
    - `agents.py`: Contains the `Router`, `Summarizer`, and `Pointer` agent implementations.
    - `models.py`: Defines the shared `State` and `Dependencies`.
    - `prompts.py`: Centralized management of system and user prompts.
    - `config.py`: Azure OpenAI model configuration.

## Getting Started

1. Configure your `.env` file with Azure OpenAI credentials.
2. Run the system:
   ```bash
   uv run python main.py
   ```
