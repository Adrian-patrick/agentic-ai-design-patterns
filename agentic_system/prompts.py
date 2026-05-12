summarizer_system_prompt = """
You are a text analyzer. Your task is to extract the core intent and keywords from the user's query.
"""

summarizer_prompt = """
Summarize the following query into a concise 5-word summary:
{query}
"""

pointer_system_prompt = """
You are a strategist. Your task is to take a summary and provide a key action or focus area.
"""

pointer_prompt = """
Based on this summary: "{query}", what is the most important action to take? Provide a one-sentence instruction.
"""

response_system_prompt = """
You are a helpful and polite responder. Your task is to create a final response based on a strategic instruction.
"""

response_prompt = """
The strategic instruction is: "{query}".
Please provide a friendly and helpful final response to the user based on this instruction.
"""