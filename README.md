# Reflection

A multi-agent orchestration system demonstrating the **Evaluator-Optimizer** pattern (also known as the **Reflection** pattern) using `pydantic-ai` and `pydantic-graph`.

## Project Overview

This project implements an iterative refinement workflow where a **Summarizer** agent generates content and a **Critic** agent evaluates it. The system uses a feedback loop to continuously improve the quality of the output until it meets a specific satisfaction threshold or reaches a maximum number of iterations.

### Architectural Workflow
1. **Initial Generation**: The `Summarizer` agent creates an initial executive summary based on the raw input content.
2. **Critical Evaluation**: The `Critic` agent analyzes the generated summary and produces a structured `CriticOutput` containing:
   - `satisfied`: A boolean flag indicating if the quality meets requirements.
   - `feedback`: Specific instructions for improvement if not satisfied.
   - `reason`: The rationale behind the evaluation.
3. **Iterative Refinement**: If the `Critic` is not satisfied, the `Summarizer` receives the feedback and generates an improved version of the summary.
4. **Termination**: The loop ends when the `Critic` sets `satisfied=True` or the system reaches the `max_iterations` limit (default: 3).

## Technology Stack
- **Framework**: [pydantic-ai](https://ai.pydantic.dev/) & [pydantic-graph](https://ai.pydantic.dev/graph/)
- **LLM Provider**: Azure OpenAI
- **Structured Output**: Pydantic models for reliable agent-to-agent communication
- **Environment**: Python 3.13+, Managed via `uv`

## Project Structure
- `main.py`: Entry point for running the iterative graph.
- `agentic_system/`:
    - `graph.py`: Defines the `SummarizerCriticNode` which orchestrates the refinement loop.
    - `agents.py`: Implementations for the `Summarizer` and `Critic` agents.
    - `models.py`: Shared `State` (tracking iterations and feedback) and `Dependencies`.
    - `prompts.py`: Optimized prompts for generation and critical reflection.
    - `config.py`: Azure OpenAI configuration.

## Getting Started

1. Configure your `.env` file with Azure OpenAI credentials.
2. Run the system:
   ```bash
   uv run python main.py
   ```
