# Parallelization

A multi-agent orchestration system demonstrating the **Parallelization Pattern** (Worker-Aggregator) using `pydantic-ai` and `pydantic-graph`.

## Project Overview

This project implements a parallelized agentic workflow designed for high-efficiency content analysis. Instead of processing tasks sequentially, the system executes multiple specialized analytical agents simultaneously and then aggregates their findings into a cohesive, professional response.

### Architectural Workflow
1. **Worker Node**: The primary entry point that triggers concurrent execution.
   - **Summarizer (Worker 1)**: Generates a high-level executive summary of the input content.
   - **Pointer (Worker 2)**: Extracts critical key points and strategic insights.
2. **Parallel Execution**: Uses `asyncio.gather` to run the Summarizer and Pointer in parallel, significantly reducing total processing latency.
3. **Response Node (Aggregator)**: Synthesizes the outputs from both workers.
   - **Responder**: Creates a brief, cited final report that attributes information back to its source (Summarizer or Pointer).

## Technology Stack
- **Framework**: [pydantic-ai](https://ai.pydantic.dev/) & [pydantic-graph](https://ai.pydantic.dev/graph/)
- **LLM Provider**: Azure OpenAI
- **Concurrency**: `asyncio` for parallel agent execution
- **Environment**: Python 3.13+, Managed via `uv`

## Project Structure
- `main.py`: Entry point for running the parallel graph with sample content.
- `agentic_system/`:
    - `graph.py`: Defines the `WorkerNode` and `ResponseNode` with parallel orchestration logic.
    - `agents.py`: Implementations for the `Summarizer`, `Pointer`, and `Responder` agents.
    - `models.py`: Shared `State` and `Dependencies`.
    - `prompts.py`: Optimized prompts for synthesis and citation.
    - `config.py`: Azure OpenAI configuration.

## Getting Started

1. Configure your `.env` file with Azure OpenAI credentials.
2. Run the system:
   ```bash
   uv run python main.py
   ```
