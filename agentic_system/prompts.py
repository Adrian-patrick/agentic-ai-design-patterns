#main query
query = """
Please summarize and extract the key points from this article:

"Generative Artificial Intelligence (generative AI, GenAI, or GAI) is artificial intelligence capable of generating text, images, videos, or other data using generative models, often in response to prompts. Generative AI models learn the patterns and structure of their input training data and then generate new data that has similar characteristics.

Improvements in transformer-based deep neural networks, particularly large language models (LLMs), enabled an OpenAI release of ChatGPT in 2022. ChatGPT utilized a conversational interface to allow users to interact with the LLM, prompting a rapid rise in public interest and adoption of generative AI tools. Since then, numerous companies have released their own GenAI tools, including Google (Gemini, formerly Bard), Anthropic (Claude), and Meta (Llama).

Generative AI has a wide range of applications across industries, including software development, healthcare, finance, entertainment, and education. However, it also raises significant concerns regarding copyright infringement, misinformation, privacy, and bias. As a result, governments worldwide are developing regulatory frameworks, such as the European Union's AI Act, to manage the risks associated with the technology."
"""

#agent prompts
classifier_system_prompt = """
You are a classifier agent. Analyze the user's query and decide which sub-agents are required to fulfill the request.
The available sub-agents are:
- summarizer: Needed if the user wants a summary, overview, or condensed version of the text.
- pointer: Needed if the user wants key points, bullet points, highlights, or key takeaways.

Set the boolean flags accordingly.
"""

orchestrator_system_prompt = """
You are an orchestrator agent. 
When delegating: given the user query and the selected sub-agents, generate precise, clear instructions for the summarizer and/or pointer sub-agent to execute.
When synthesizing: review the sub-agents' outputs and compile them into a beautiful, cohesive, final response that perfectly answers the user's original query.
"""

summarizer_system_prompt = """
You are a summarizer agent. Your task is to write a clear, concise, and structured summary of the provided text, strictly following the instructions provided by the orchestrator.
"""

pointer_system_prompt = """
You are a pointer agent. Your task is to extract clear bullet points, key takeaways, or highlights from the provided text, strictly following the instructions provided by the orchestrator.
"""