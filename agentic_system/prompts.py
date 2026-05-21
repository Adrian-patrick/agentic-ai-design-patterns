# Scenario definitions for simulating Goal Setting and Monitoring
# Each turn contains worker updates and raw metrics that the monitor evaluates.
turns = [
    {
        "turn": 1,
        "worker_update": "Completed initial supply chain inventory tracking pipeline. PostgreSQL tables populated with inventory levels.",
        "raw_telemetry": {
            "database_latency_ms": 120, # Exceeds quality SLA of 50ms
            "inventory_accuracy_pct": 98.5,
            "credits_consumed": 45
        }
    },
    {
        "turn": 2,
        "worker_update": "Implemented a Redis caching layer as per the adjusted plan to bypass PostgreSQL for hot reads and reduce latency.",
        "raw_telemetry": {
            "database_latency_ms": 15, # Now within SLA limits
            "inventory_accuracy_pct": 99.1,
            "credits_consumed": 55
        }
    },
    {
        "turn": 3,
        "worker_update": "Finalized the supply chain system. All inventory calculations verified, caching layer fully integrated, ready for rollout.",
        "raw_telemetry": {
            "database_latency_ms": 12,
            "inventory_accuracy_pct": 100.0,
            "credits_consumed": 20
        }
    }
]

# Agent Prompts
goal_creator_system_prompt = """
You are a project manager and goal architect.
Your job is to translate a vague user request into a highly structured SMART Goal Specification.
Define:
1. Specific: Clear statement of the goal.
2. Measurable: The concrete success criteria.
3. Achievable: The feasibility check.
4. Relevant: Business value alignment.
5. Deadline Turns: Maximum number of execution turns (typically 3).
6. Budget Limit: Maximum credit units to consume (typically 150).
7. Quality Standard: Quality constraints (e.g., maximum latency < 50ms, data accuracy > 99%).

Output the specification matching the GoalSpec structure.
"""

worker_system_prompt = """
You are a systems engineer implementing the project goals.
Perform work for the current turn based on the Goal Specification, rules, and current plan.
Describe what was accomplished during this turn.
"""

monitor_system_prompt = """
You are a systems monitoring and evaluation agent.
Analyze the worker's updates and the raw telemetry numbers.
Compare these metrics against the Goal Specification success standards:
- Check if budget limit is exceeded.
- Check if deadline turns limit is reached.
- Check if quality standards (e.g. database_latency_ms < 50ms) are satisfied.

Produce a ProgressSnapshot detailing:
- 'metrics_collected': Key metrics parsed from telemetry. You MUST include the keys 'database_latency_ms' and 'inventory_accuracy_pct' with their corresponding values from raw telemetry inside this dictionary. Do not omit them!
- 'budget_spent_this_turn': Telemetry credit cost.
- 'current_status': Set to:
  - 'on_track' if everything is running fine.
  - 'off_track' if metrics violate quality standards or budget is running low.
  - 'blocked' if progress is entirely stuck.
- 'explanation': Brief reasoning.
"""

adapter_system_prompt = """
You are an optimization and adaptation agent.
Analyze why the project is off-track or blocked by examining the goal specification, plan, worker logs, and monitor evaluation.
Recommend one of the following fix types to get back on track:
1. 'ChangePlan': Suggest a concrete adjustment to the execution plan (e.g., add caching, change query strategy).
2. 'GetMoreResources': Request additional budget or processing tools.
3. 'ChangeGoal': Scale back the goal specification to fit constraints.

Provide the exact type and value for the fix.
"""