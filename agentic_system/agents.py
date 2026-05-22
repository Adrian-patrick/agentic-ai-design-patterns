import os
from typing import Optional
from pydantic_ai import Agent
from .config import create_model
from .prompts import (
    triage_system_prompt,
    recovery_system_prompt,
    learning_system_prompt,
)
from .models import (
    ExceptionCategory,
    BackupOption,
    ErrorTriageResult,
    SafetyVerdict,
    ErrorRecord,
)

# Check if Azure OpenAI API key is provided
IS_CONFIGURED = all(
    os.environ.get(var) for var in ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]
)

if not IS_CONFIGURED:
    print("[Info] Azure credentials not found. Falling back to local high-fidelity mock agents for showcase...")

class SafetyCheckAgent:
    """Performs pre-execution safety and system prerequisite checks."""
    async def check(self, query: str, scenario: str) -> bool:
        # Pre-execution safety checking
        print(f"   [Safety Agent] Inspecting request payload and environment config...")
        if scenario == "critical_emergency" and "fatal" in query.lower():
            # Pretend we detected a dangerous operation beforehand, but let it proceed for testing
            print("   [Safety Agent] WARNING: Request contains terms matching high-severity metrics.")
        return True

class ServiceCallAgent:
    """Simulates external service calls or tool invocations and raises realistic exceptions."""
    async def run(self, scenario: str, attempt: int) -> str:
        print(f"   [Service Agent] Attempting service call (Attempt {attempt})...")
        
        if scenario == "transient_success":
            if attempt == 1:
                raise ConnectionResetError("Connection timed out on socket 443 (network glitch).")
            elif attempt == 2:
                raise ConnectionAbortedError("Database pool connection lost temporarily.")
            else:
                return "Data retrieved successfully: [User ID: 8841, Level: Admin, Region: IN]"
                
        elif scenario == "permanent_fallback":
            raise PermissionError("API key revoked or expired (Error Code: 401 Unauthorized).")
            
        elif scenario == "critical_emergency":
            raise OSError("Critical System Failure: database storage disk 100% full, write permissions disabled.")
            
        else:
            return "Generic success response."

class TriageAgent:
    """Diagnoses and classifies exceptions into Temporary, Permanent, or Critical categories."""
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=triage_system_prompt,
                output_type=ErrorTriageResult,
                retries=3,
            )

    async def run(self, query: str, scenario: str, error_msg: str) -> ErrorTriageResult:
        if not IS_CONFIGURED:
            # High-fidelity local triage based on scenario
            if scenario == "transient_success":
                return ErrorTriageResult(
                    category=ExceptionCategory.TEMPORARY,
                    severity="Medium",
                    reasoning="Connection timeout / abort errors are transient infrastructure glitches. Sockets should recover after a short pause.",
                    recommended_action="Wait with exponential backoff and retry the connection."
                )
            elif scenario == "permanent_fallback":
                return ErrorTriageResult(
                    category=ExceptionCategory.PERMANENT,
                    severity="High",
                    reasoning="Permission Error: 401 Unauthorized indicates that the credential itself is revoked. Retrying will not solve this.",
                    recommended_action="Gracefully degrade to alternate backup plan using cached/saved data."
                )
            else:
                return ErrorTriageResult(
                    category=ExceptionCategory.CRITICAL,
                    severity="High",
                    reasoning="OS Error: Disk 100% full blocks all database writes. Proceeding with execution could corrupt database files.",
                    recommended_action="Preserve current memory state immediately, alert the team, and run safety checks."
                )

        prompt = (
            f"Query: {query}\n"
            f"Active Scenario: {scenario}\n"
            f"Exception Message: {error_msg}\n"
            "Please triage this error."
        )
        result = await self.agent.run(prompt)
        return result.output

class RecoveryAgent:
    """Selects backup solutions for permanent errors, or evaluates safety for critical alerts."""
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=recovery_system_prompt,
                retries=3,
            )

    async def select_backup(self, query: str, error_msg: str) -> BackupOption:
        if not IS_CONFIGURED:
            # Fallback backup option: we want to demonstrate the 'Saved Data' fallback
            return BackupOption.SAVED_DATA

        prompt = (
            f"TASK: Select Backup Option\n"
            f"Query: {query}\n"
            f"Error Encountered: {error_msg}\n\n"
            "Respond with one of these precise strings: 'Simple Method', 'Saved Data', 'Default Answer', or 'Get Human Help'."
        )
        # Using string matching for backup selection to be resilient
        result = await self.agent.run(prompt)
        content = result.output.strip()
        for option in BackupOption:
            if option.value.lower() in content.lower():
                return option
        return BackupOption.DEFAULT_ANSWER

    async def evaluate_safety(self, error_history: list[ErrorRecord]) -> SafetyVerdict:
        if not IS_CONFIGURED:
            # High-fidelity safety verdict for critical disk full error
            return SafetyVerdict(
                is_safe=False,
                reasoning="The database partition is reported at 100% capacity. Any continuation of system writes is unsafe and will result in transactional failures.",
                next_action="STOP"
            )

        history_str = "\n".join([f"Attempt {r.attempt}: [{r.category}] {r.error_msg} -> Action: {r.action_taken}" for r in error_history])
        prompt = (
            f"TASK: Formulate Safety Verdict\n"
            f"Critical Error History Log:\n{history_str}\n\n"
            "Please analyze the situation and decide if it is safe to RESUME or if we must trigger a safety STOP.\n"
            "Your output must adhere to the SafetyVerdict schema: is_safe (bool), reasoning (str), next_action ('RESUME' or 'STOP')."
        )
        
        # We instantiate a specialized safety agent returning SafetyVerdict
        safety_agent = Agent(
            model=create_model(),
            system_prompt=recovery_system_prompt,
            output_type=SafetyVerdict,
        )
        result = await safety_agent.run(prompt)
        return result.output

class LearningAgent:
    """Reviews the error log history and generates insights, tracking patterns to prevent future occurrences."""
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=learning_system_prompt,
                output_type=str,
                retries=3,
            )

    async def run(self, error_history: list[ErrorRecord], outcome: str) -> str:
        if not IS_CONFIGURED:
            # Return highly formatted, premium, and structured analysis text
            history_str = "\n".join([f"  * Attempt {r.attempt} [{r.category}]: {r.error_msg} -> {r.action_taken}" for r in error_history])
            
            if outcome == "SUCCESS":
                return (
                    "### 1. Error Patterns & Frequency\n"
                    "- 2x Connection resets/timeouts encountered sequentially.\n"
                    "- Frequency: 100% of initial attempts failed before resolving.\n\n"
                    "### 2. Root Cause Summary\n"
                    "- Infrastructure network interface jitter resulting in socket drops on port 443.\n\n"
                    "### 3. Learned Lessons & Improvements\n"
                    "- **Lesson**: Network glitch was temporary; retries successfully healed the system.\n"
                    "- **Action**: Implement connection pooling and adjust the TCP keep-alive settings to reduce socket drops."
                )
            elif outcome == "RECOVERED":
                return (
                    "### 1. Error Patterns & Frequency\n"
                    "- 1x PermissionError (401 Unauthorized) encountered.\n"
                    "- Frequency: Single persistent error blocking primary service call.\n\n"
                    "### 2. Root Cause Summary\n"
                    "- API keys expired/revoked, rendering primary cloud API calls completely invalid.\n\n"
                    "### 3. Learned Lessons & Improvements\n"
                    "- **Lesson**: Permanent errors cannot be retried away; a fallback strategy is vital.\n"
                    "- **Action**: Set up active API credential expiration alerts and automate key rotation."
                )
            else: # EMERGENCY_STOP
                return (
                    "### 1. Error Patterns & Frequency\n"
                    "- 1x OSError (Disk 100% full, write permissions disabled) encountered.\n"
                    "- Frequency: High-severity fatal system error.\n\n"
                    "### 2. Root Cause Summary\n"
                    "- Disk storage capacity exceeded. Write operations are physically blocked.\n\n"
                    "### 3. Learned Lessons & Improvements\n"
                    "- **Lesson**: Continuing database writes on full partition poses corruption risks. Immediate STOP is correct.\n"
                    "- **Action**: Set up automated disk cleanup cron jobs and add system alerts at 85% disk usage."
                )

        history_str = "\n".join([f"Attempt {r.attempt}: [{r.category}] {r.error_msg} -> {r.action_taken}" for r in error_history])
        prompt = (
            f"Outcome: {outcome}\n"
            f"Error logs history:\n{history_str}\n\n"
            "Analyze and provide the final continuous learning and pattern tracking report."
        )
        result = await self.agent.run(prompt)
        return result.output
