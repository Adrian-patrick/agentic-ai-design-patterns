# Agentic AI Design Patterns

A multi-agent orchestration system demonstrating the **Chain of Responsibility** pattern using `pydantic-ai` and `pydantic-graph`.

## Project Overview

This project implements a sequential agentic workflow where multiple specialized agents collaborate to process complex queries. The orchestration is managed by a directed graph that ensures robust state management and clear execution paths.

### Agentic Chain
1. **Summarizer**: Analyzes the input query and extracts core intent.
2. **Pointer**: Formulates a strategic focus or key action based on the summary.
3. **Responder**: Synthesizes the final helpful response based on the strategic direction.

## Technology Stack
- **Framework**: [pydantic-ai](https://ai.pydantic.dev/) & [pydantic-graph](https://ai.pydantic.dev/graph/)
- **LLM Provider**: Azure OpenAI
- **Environment**: Python 3.13+, Managed via `uv`

## Getting Started

1. Configure your `.env` file with Azure OpenAI credentials.
2. Run the system:
   ```bash
   uv run python main.py
   ```
