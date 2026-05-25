import os
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from .config import create_model
from .prompts import (
    ingestion_prompt,
    query_improvement_prompt,
    retrieval_ranking_prompt,
    generation_citation_prompt,
)
from .models import (
    Document,
    Chunk,
    SearchResult,
    RAGResponse,
)

# Check if Azure OpenAI API key is provided
IS_CONFIGURED = all(
    os.environ.get(var) for var in ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]
)

if not IS_CONFIGURED:
    print("[Info] Azure credentials not found. Falling back to local high-fidelity RAG mock agents for showcase...")

class IngestionMetadata(BaseModel):
    summary: str = Field(description="Brief summary of document content.")
    tags: List[str] = Field(description="Searchable keyword tags.")
    doc_type: str = Field(description="Document type classification.")

class ChunkRelevance(BaseModel):
    score: float = Field(description="Relevance score between 0.0 and 1.0.")
    is_relevant: bool = Field(description="Whether relevance score satisfies the 0.40 cutoff.")

class DocumentIngestionAgent:
    """Parses text, categorizes document metadata, and assigns labels/tags."""
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=ingestion_prompt,
                output_type=IngestionMetadata,
                retries=3,
            )

    async def run(self, doc_title: str, text: str) -> IngestionMetadata:
        if not IS_CONFIGURED:
            # Local high-fidelity mock ingestion based on title
            if "battery" in doc_title.lower():
                return IngestionMetadata(
                    summary="Warranty and specifications for product power systems.",
                    tags=["battery", "warranty", "power", "hardware"],
                    doc_type="Product Manual"
                )
            else:
                return IngestionMetadata(
                    summary="SRE recovery steps, throttling, and credit limits under load spikes.",
                    tags=["sre", "queue spikes", "recovery", "limits"],
                    doc_type="SRE Playbook"
                )

        prompt = f"Document Title: {doc_title}\nContent:\n{text}"
        result = await self.agent.run(prompt)
        return result.output

class QueryExpansionAgent:
    """Expands raw user question into optimized technical terms and synonyms."""
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=query_improvement_prompt,
                retries=3,
            )

    async def run(self, raw_query: str) -> str:
        if not IS_CONFIGURED:
            # High-fidelity mock query expansions
            if "battery" in raw_query.lower():
                return "expanded query: battery warranty period, power pack replacement guarantee limits, hardware SLA"
            else:
                return "expanded query: recovery steps queue spikes, traffic throttling limits, queue overload safeguards"

        result = await self.agent.run(f"Raw User Query: {raw_query}")
        return result.output.strip()

class RetrievalRankingAgent:
    """Scores matching relevance of segment chunks to queries and filters low scores."""
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=retrieval_ranking_prompt,
                output_type=ChunkRelevance,
                retries=3,
            )

    async def run(self, query: str, chunk_text: str) -> ChunkRelevance:
        if not IS_CONFIGURED:
            # High-fidelity mock relevance scoring
            if "battery" in query.lower() and "battery" in chunk_text.lower():
                return ChunkRelevance(score=0.92, is_relevant=True)
            elif "spike" in query.lower() or "recovery" in query.lower():
                if "recovery steps" in chunk_text.lower() or "traffic throttling" in chunk_text.lower():
                    return ChunkRelevance(score=0.95, is_relevant=True)
                elif "warn" in chunk_text.lower() or "spikes" in chunk_text.lower():
                    return ChunkRelevance(score=0.48, is_relevant=True)
            return ChunkRelevance(score=0.15, is_relevant=False)

        prompt = f"Query: {query}\nChunk Content:\n{chunk_text}"
        result = await self.agent.run(prompt)
        return result.output

class ResponseGenerationAgent:
    """Synthesizes factual answers grounded in chunks and performs quality/completeness self-checks."""
    def __init__(self):
        if IS_CONFIGURED:
            self.agent = Agent(
                model=create_model(),
                system_prompt=generation_citation_prompt,
                output_type=RAGResponse,
                retries=3,
            )

    async def run(self, query: str, chunks: List[Chunk], attempt: int) -> RAGResponse:
        if not IS_CONFIGURED:
            # Scenario-based mock response generation
            if "battery" in query.lower():
                return RAGResponse(
                    answer="The warranty period for product batteries is 3 years from the date of purchase. Replacement is fully covered if capacity degrades below 70%.",
                    citations=["Product Manual: Section 4.2"],
                    is_good=True,
                    confidence_score=0.94
                )
            else: # Queue spikes scenario
                if attempt == 1:
                    # Sparse search (Scenario 2, Attempt 1): missing detailed recovery steps
                    return RAGResponse(
                        answer="Severe queue spikes trigger standard alerts. Workloads can be heavy.",
                        citations=[],
                        is_good=False,
                        confidence_score=0.48
                    )
                else:
                    # Expanded search (Scenario 2, Attempt 2): full SRE recovery steps
                    return RAGResponse(
                        answer="During severe queue spikes, recovery steps are: 1) Activate traffic throttling, 2) Batch items into chunks of 10+, and 3) Elevate the AI automation rate to 85% to offload operators. The standard agent credit limit is $10,000.",
                        citations=["SRE Playbook: Recovery Rules", "Compliance Code: Article 8"],
                        is_good=True,
                        confidence_score=0.96
                    )

        chunks_prompt = ""
        for i, chunk in enumerate(chunks):
            chunks_prompt += f"--- Chunk {i+1} [{chunk.doc_title} (Idx {chunk.index})] ---\n{chunk.text}\n\n"

        prompt = (
            f"Query: {query}\n"
            f"Attempt: {attempt}\n"
            f"Retrieved Context Sources:\n{chunks_prompt}\n"
            "Generate answer, source references, and quality checks."
        )
        result = await self.agent.run(prompt)
        return result.output
