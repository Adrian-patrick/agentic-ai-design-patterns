# Learning & Adaptation

A small demonstrator implementing an adaptive multi-agent learning pipeline. The system
simulates multi-turn interactions, collects feedback signals, validates them, and—when
necessary—applies lightweight learning steps (prompt updates, examples, or preference rules)
followed by A/B-style evaluation.

This repository is intended as a reference / teaching artifact rather than a production
system. It shows patterns for orchestration, validation, adaptation, and reporting using
`pydantic-ai` and `pydantic-graph`.

## Quick summary
- Purpose: Demonstrate a multi-turn learning loop that adapts system prompts and examples
   based on feedback.
- Entry point: `main.py` — runs a short scripted transcript (see `agentic_system/prompts.py`).
- LLM integrations: configured for Azure OpenAI via `agentic_system/config.py`.

## Requirements
- Python 3.11+ (3.13+ is recommended in the original notes).
- An Azure OpenAI deployment and credentials (see `agentic_system/config.py`).

## Setup

1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install project dependencies (uses `pyproject.toml`):

```powershell
pip install -e .
```

3. Add your Azure OpenAI credentials to a `.env` file at the repository root. The
    following environment variables are expected by `agentic_system/config.py`:

- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_KEY`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME`

Example `.env` (DO NOT commit credentials):

```
AZURE_OPENAI_ENDPOINT=https://your-azure-endpoint.openai.azure.com/
AZURE_OPENAI_API_KEY=sk-...
AZURE_OPENAI_API_VERSION=2023-10-01-preview
AZURE_OPENAI_CHAT_DEPLOYMENT_NAME=gpt-4o
```

## Run the showcase

Run the scripted multi-turn demonstration:

```powershell
python main.py
# or (if you have the `uv` runner mentioned in the original notes):
uv run main.py
```

The script will iterate through the examples defined in `agentic_system/prompts.py`, run
the orchestration graph in `agentic_system/graph.py`, and print the response and a short
learning report for each turn.

## Project structure
- `main.py` — script that drives the showcase.
- `agentic_system/`
   - `graph.py` — the orchestrator graph and node implementations.
   - `agents.py` — wrapper agents that call the configured LLM model.
   - `models.py` — Pydantic models for state, feedback, and adaptation artifacts.
   - `prompts.py` — scripted turns and system prompt templates used in the demo.
   - `config.py` — Azure OpenAI configuration helper (reads from environment).
- `test_transcript.py` — an example transcript used for testing/notes.

## Notes & next steps
- The demo expects valid Azure OpenAI credentials. If you don't have them, you can
   stub `create_model()` in `agentic_system/config.py` to use a local or mock model for
   offline testing.
- The repository is intended as a learning artifact: it focuses on architecture and
   patterns (validation, adaptation loop, A/B evaluation), not production concerns
   (robust error handling, secrets management, or observability plumbing).

If you'd like, I can also:
- add a `requirements.txt` or `README` section showing how to run the project with mocked
   agents for offline development, or
- run the demo (if you allow me to run tests/commands in this environment).
