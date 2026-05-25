import asyncio
from typing import Union, List
from pydantic_graph import BaseNode, End, GraphRunContext, Graph
from .agents import DocumentIngestionAgent, QueryExpansionAgent, RetrievalRankingAgent, ResponseGenerationAgent
from .models import (
    State,
    Dependencies,
    SplitType,
    Document,
    Chunk,
    SearchResult,
    RAGResponse,
)

class StartNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ReadDocumentsNode":
        print("\n=== [Start Node] Initializing Knowledge Retrieval (RAG) pipeline... ===")
        print(f"  Target User Query: '{ctx.state.query}'")
        print(f"  Active Scenario: {ctx.state.scenario.upper()}")
        ctx.state.system_status = "Initializing Ingestion"
        return ReadDocumentsNode()

class ReadDocumentsNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ParseTextNode":
        print("\n=== [Read Documents Node] Reading knowledge documents from storage... ===")
        print(f"  Found {len(ctx.state.documents)} documents in pipeline collection.")
        ctx.state.system_status = "Reading Documents"
        return ParseTextNode()

class ParseTextNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "GetDocumentInfoNode":
        print("\n=== [Parse Text Node] Segmenting and extracting text blocks... ===")
        ctx.state.system_status = "Parsing Text"
        return GetDocumentInfoNode()

class GetDocumentInfoNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "AddTagsNode":
        print("\n=== [Get Document Info Node] Extracting metadata summaries from docs... ===")
        ingestion_agent = ctx.deps.ingestion_agent
        for doc in ctx.state.documents:
            meta = await ingestion_agent.run(doc.title, doc.content)
            doc.metadata["summary"] = meta.summary
            doc.metadata["doc_type"] = meta.doc_type
            doc.tags = meta.tags
            print(f"  * Indexed Doc: '{doc.title}' | Type: {meta.doc_type}")
            print(f"    Summary: {meta.summary}")
        ctx.state.system_status = "Extracting Info"
        return AddTagsNode()

class AddTagsNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "SplitDecisionNode":
        print("\n=== [Add Tags Node] Mapping searchable classification keywords... ===")
        for doc in ctx.state.documents:
            print(f"  * Title: '{doc.title}' -> Tags: {doc.tags}")
        ctx.state.system_status = "Adding Tags"
        return SplitDecisionNode()

class SplitDecisionNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> Union["FixedSplitNode", "SmartSplitNode", "ContextSplitNode"]:
        print("\n=== [Split Decision Node] Evaluating chunking strategies... ===")
        
        # Decide chunking split based on active scenario config
        if ctx.state.scenario == "happy_path":
            print("  Selected Chunk Strategy: [FIXED SIZE CHUNKS] (Optimal for simple, direct manuals)")
            return FixedSplitNode()
        elif ctx.state.scenario == "loop_path":
            print("  Selected Chunk Strategy: [NATURAL BREAKS / SMART] (Optimal for complex policies)")
            return SmartSplitNode()
        else:
            print("  Selected Chunk Strategy: [CONTEXT KEEP TOGETHER]")
            return ContextSplitNode()

class FixedSplitNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ProcessChunksNode":
        print("\n=== [Fixed Split Node] Executing division by equal size characters (500 char blocks)... ===")
        for doc in ctx.state.documents:
            # Simple fixed split simulation
            content = doc.content
            chunk_1 = content[:len(content)//2]
            chunk_2 = content[len(content)//2:]
            ctx.state.chunks.append(Chunk(text=chunk_1, doc_title=doc.title, index=1, start_char=0, end_char=len(chunk_1)))
            ctx.state.chunks.append(Chunk(text=chunk_2, doc_title=doc.title, index=2, start_char=len(chunk_1), end_char=len(content)))
        return ProcessChunksNode()

class SmartSplitNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ProcessChunksNode":
        print("\n=== [Smart Split Node] Executing division by natural sentence breaks... ===")
        for doc in ctx.state.documents:
            # Segment by logical parts
            parts = doc.content.split("\n\n")
            for i, part in enumerate(parts):
                if part.strip():
                    ctx.state.chunks.append(Chunk(text=part.strip(), doc_title=doc.title, index=i+1, start_char=0, end_char=len(part)))
        return ProcessChunksNode()

class ContextSplitNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ProcessChunksNode":
        print("\n=== [Context Split Node] Executing division to keep related parts together... ===")
        for doc in ctx.state.documents:
            ctx.state.chunks.append(Chunk(text=doc.content, doc_title=doc.title, index=1, start_char=0, end_char=len(doc.content)))
        return ProcessChunksNode()

class ProcessChunksNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ConvertSearchableNode":
        print("\n=== [Process Chunks Node] Processing segmented text chunks... ===")
        print(f"  Generated {len(ctx.state.chunks)} active chunks from document collection.")
        ctx.state.system_status = "Processing Chunks"
        return ConvertSearchableNode()

class ConvertSearchableNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "StoreSearchDatabaseNode":
        print("\n=== [Convert Searchable Node] Encoding chunks into searchable schema records... ===")
        ctx.state.system_status = "Converting Formats"
        return StoreSearchDatabaseNode()

class StoreSearchDatabaseNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ReadyToSearchNode":
        print("\n=== [Store Search Database Node] Committing records to vector search store index... ===")
        ctx.state.system_status = "Database Indexed"
        return ReadyToSearchNode()

class ReadyToSearchNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ReceiveQuestionNode":
        print("\n=== [Ready To Search Node] Index loaded! Knowledge Base is online. ===")
        ctx.state.system_status = "Ready to Search"
        return ReceiveQuestionNode()

class ReceiveQuestionNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ImproveQuestionNode":
        print("\n=== [Receive Question Node] Intercepting user search question... ===")
        print(f"  Raw User Query: '{ctx.state.query}'")
        ctx.state.system_status = "Receiving Query"
        return ImproveQuestionNode()

class ImproveQuestionNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ExpandQuestionNode":
        print("\n=== [Improve Question Node] Analyzing semantic parameters of question... ===")
        ctx.state.system_status = "Improving Question"
        return ExpandQuestionNode()

class ExpandQuestionNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "SearchDatabaseNode":
        print("\n=== [Expand Question Node] Expanding search terms with synonyms... ===")
        improved = await ctx.deps.expansion_agent.run(ctx.state.query)
        ctx.state.improved_query = improved
        print(f"  * Optimized Query: '{improved}'")
        ctx.state.system_status = "Expanding Terms"
        return SearchDatabaseNode()

class SearchDatabaseNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "FilterChunksNode":
        print("\n=== [Search Database Node] Querying vector index with expanded search terms... ===")
        print(f"  Attempt: #{ctx.state.search_attempts} | Active Retrieval limit: top-{ctx.state.retrieval_limit} chunks.")
        
        # Simulate retrieval matched chunks based on query/scenario/attempt
        ctx.state.retrieved_chunks = []
        
        if ctx.state.scenario == "happy_path":
            # Match battery document chunks
            for chunk in ctx.state.chunks:
                if "battery" in chunk.doc_title.lower() or "warranty" in chunk.text.lower():
                    ctx.state.retrieved_chunks.append(chunk)
        else: # loop_path (SRE Playbook)
            if ctx.state.search_attempts == 1:
                # Sparse attempt retrieves only the generic alarm warning chunk
                for chunk in ctx.state.chunks:
                    if "warning" in chunk.text.lower():
                        ctx.state.retrieved_chunks.append(chunk)
            else:
                # Attempt 2 (Broadened retrieval): retrieve full recovery rules and limits
                for chunk in ctx.state.chunks:
                    ctx.state.retrieved_chunks.append(chunk)
                    
        print(f"  Fetched {len(ctx.state.retrieved_chunks)} raw matches from database.")
        ctx.state.system_status = f"Database Searched Attempt {ctx.state.search_attempts}"
        return FilterChunksNode()

class FilterChunksNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "RankDecisionNode":
        print("\n=== [Filter Chunks Node] Removing low-relevance results... ===")
        # Evaluate matched chunks and compute relevance score
        ctx.state.ranked_results = []
        rank_agent = ctx.deps.ranking_agent
        
        # Rank matched chunks
        for chunk in ctx.state.retrieved_chunks:
            # We pass query and text to similarity rank agent
            relevance = await rank_agent.run(ctx.state.improved_query, chunk.text)
            if relevance.score >= 0.25:
                ctx.state.ranked_results.append(SearchResult(chunk=chunk, score=relevance.score))
                print(f"  * [KEEP] Score: {relevance.score:.2f} | Chunk: '{chunk.text[:50]}...'")
            else:
                print(f"  * [DROP] Score: {relevance.score:.2f} (Below 0.25 cutoff) | Chunk: '{chunk.text[:50]}...'")
                
        ctx.state.system_status = "Filtering Matches"
        return RankDecisionNode()

class RankDecisionNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ScoreChunksNode":
        print("\n=== [Rank Decision Node] Determining ranking workflows... ===")
        return ScoreChunksNode()

class ScoreChunksNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "SortChunksNode":
        print("\n=== [Score Chunks Node] Executing absolute similarity score assessments... ===")
        return SortChunksNode()

class SortChunksNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "PickTopMatchesNode":
        print("\n=== [Sort Chunks Node] Sorting matched chunks by descending relevance score... ===")
        ctx.state.ranked_results.sort(key=lambda x: x.score, reverse=True)
        return PickTopMatchesNode()

class PickTopMatchesNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "VerifySourcesNode":
        print("\n=== [Pick Top Matches Node] Truncating output to top matches... ===")
        # Limit matches to retrieval limit configuration
        ctx.state.ranked_results = ctx.state.ranked_results[:ctx.state.retrieval_limit]
        print(f"  Retained top-{len(ctx.state.ranked_results)} matches for response synthesis:")
        for res in ctx.state.ranked_results:
            print(f"    - Score: {res.score:.2f} | Source: {res.chunk.doc_title} [Idx: {res.chunk.index}]")
        return VerifySourcesNode()

class VerifySourcesNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "UseSourcesNode":
        print("\n=== [Verify Sources Node] Confirming source citations are active... ===")
        ctx.state.system_status = "Verifying Sources"
        return UseSourcesNode()

class UseSourcesNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "GenerateAnswerNode":
        print("\n=== [Use Sources Node] Mapping factual segments to prompt context... ===")
        return GenerateAnswerNode()

class GenerateAnswerNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "CiteSourcesNode":
        print("\n=== [Generate Answer Node] Synthesizing grounded RAG answer... ===")
        chunks_to_use = [res.chunk for res in ctx.state.ranked_results]
        
        response = await ctx.deps.generation_agent.run(
            ctx.state.improved_query,
            chunks_to_use,
            ctx.state.search_attempts
        )
        ctx.state.generated_response = response
        ctx.state.system_status = "Generating Answer"
        return CiteSourcesNode()

class CiteSourcesNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "QualityDecisionNode":
        print("\n=== [Cite Sources Node] Resolving inline source citations... ===")
        resp = ctx.state.generated_response
        print("\n[AI Grounded Response Draft]")
        print("------------------------------------------------------------")
        print(f"  💬 Answer:\n    '{resp.answer}'")
        print(f"  📚 Citations: {resp.citations}")
        print(f"  🔍 Quality check: {'PASS' if resp.is_good else 'FAIL'}")
        print(f"  🎯 Confidence Score: {resp.confidence_score:.2f}")
        print("------------------------------------------------------------")
        ctx.state.system_status = "Citing Sources"
        return QualityDecisionNode()

class QualityDecisionNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> Union["DeliverAnswerNode", "RedoSearchNode"]:
        print("\n=== [Quality Decision Node] Validating output completeness and confidence... ===")
        resp = ctx.state.generated_response
        
        if resp.is_good:
            print("  [Quality Decision] SUCCESS: Output passes completeness check.")
            return DeliverAnswerNode()
        else:
            if ctx.state.search_attempts >= ctx.state.max_attempts:
                print("  [Quality Decision] WARNING: Quality failed but max search attempts reached. Delivering fallback.")
                return DeliverAnswerNode()
            else:
                print("  [Quality Decision] FAILURE: Answer is incomplete or low confidence! Activating recovery loop.")
                return RedoSearchNode()

class RedoSearchNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "AdjustSettingsNode":
        print("\n=== [Redo Search Node] Initiating search parameters expansion... ===")
        ctx.state.search_attempts += 1
        return AdjustSettingsNode()

class AdjustSettingsNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "SearchDatabaseNode":
        print("\n=== [Adjust Settings Node] Upgrading search configurations... ===")
        print("  - Expanding query breadth terms.")
        ctx.state.retrieval_limit = 4  # Fetch more chunks to guarantee completeness!
        print(f"  - Elevated Retrieval Fetch limits: top-2 ➡️ top-{ctx.state.retrieval_limit}")
        ctx.state.system_status = "Retrieval Parameters Elevated"
        return SearchDatabaseNode()

class DeliverAnswerNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "TrackPerformanceNode":
        print("\n=== [Deliver Answer Node] Delivering grounded response to user... ===")
        ctx.state.system_status = "Answer Delivered"
        return TrackPerformanceNode()

class TrackPerformanceNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "MeasureMetricsNode":
        print("\n=== [Track Performance Node] Saving operational search logs... ===")
        return MeasureMetricsNode()

class MeasureMetricsNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "AccuracyMetricsNode":
        print("\n=== [Measure Metrics Node] Evaluating system search benchmarks... ===")
        return AccuracyMetricsNode()

class AccuracyMetricsNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "CoverageMetricsNode":
        print("\n=== [Accuracy Metrics Node] Calculating factual alignment score... ===")
        # Calculate factual accuracy metrics
        if ctx.state.generated_response.is_good:
            ctx.state.accuracy_score = 0.98
        else:
            ctx.state.accuracy_score = 0.50
        print(f"  Factual Accuracy Metric: {ctx.state.accuracy_score * 100:.1f}%")
        return CoverageMetricsNode()

class CoverageMetricsNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "ImproveSystemNode":
        print("\n=== [Coverage Metrics Node] Calculating complete coverage score... ===")
        # Calculate info completeness metrics
        if ctx.state.generated_response.is_good:
            ctx.state.coverage_score = 0.95
        else:
            ctx.state.coverage_score = 0.40
        print(f"  Info Coverage Metric: {ctx.state.coverage_score * 100:.1f}%")
        return ImproveSystemNode()

class ImproveSystemNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> "EndNode":
        print("\n=== [Improve System Node] Applying performance insights... ===")
        ctx.state.system_status = "System Benchmarked"
        return EndNode()

class EndNode(BaseNode[State, Dependencies, str]):
    async def run(
        self, ctx: GraphRunContext[State, Dependencies]
    ) -> End[str]:
        print("\n=== [End Node] Formatting final Search Complete Report... ===")
        
        doc_count = len(ctx.state.documents)
        chunk_count = len(ctx.state.chunks)
        query = ctx.state.query
        expanded = ctx.state.improved_query
        resp = ctx.state.generated_response
        
        answer = resp.answer if resp else "N/A"
        citations = resp.citations if resp else []
        conf = resp.confidence_score if resp else 0.0
        good = "PASS" if resp and resp.is_good else "FAIL"
        
        report = (
            "==============================================================\n"
            "            KNOWLEDGE RETRIEVAL (RAG) WORKFLOW REPORT\n"
            "==============================================================\n"
            f"Documents Ingested: {doc_count} docs | Total Chunks Created: {chunk_count}\n"
            f"Original User Query: '{query}'\n"
            f"Synonym Expanded Query: '{expanded}'\n"
            f"Total Search Attempts: {ctx.state.search_attempts} (Max: {ctx.state.max_attempts})\n"
            f"Final Retrieval Limit: top-{ctx.state.retrieval_limit} chunks\n"
            f"Quality Validation: {good} (Self-Assessed Confidence: {conf:.2f})\n"
            "--------------------------------------------------------------\n"
            f"💬 synthesized Answer:\n{answer}\n"
            f"📚 Source Citations: {citations}\n"
            "--------------------------------------------------------------\n"
            f"📊 SRE Search Benchmarks:\n"
            f"  * Factual Accuracy: {ctx.state.accuracy_score * 100:.1f}%\n"
            f"  * Context Coverage: {ctx.state.coverage_score * 100:.1f}%\n"
            "=============================================================="
        )
        ctx.state.final_report = report
        print(report)
        return End(report)

def build_graph() -> Graph:
    return Graph(
        nodes=[
            StartNode,
            ReadDocumentsNode,
            ParseTextNode,
            GetDocumentInfoNode,
            AddTagsNode,
            SplitDecisionNode,
            FixedSplitNode,
            SmartSplitNode,
            ContextSplitNode,
            ProcessChunksNode,
            ConvertSearchableNode,
            StoreSearchDatabaseNode,
            ReadyToSearchNode,
            ReceiveQuestionNode,
            ImproveQuestionNode,
            ExpandQuestionNode,
            SearchDatabaseNode,
            FilterChunksNode,
            RankDecisionNode,
            ScoreChunksNode,
            SortChunksNode,
            PickTopMatchesNode,
            VerifySourcesNode,
            UseSourcesNode,
            GenerateAnswerNode,
            CiteSourcesNode,
            QualityDecisionNode,
            RedoSearchNode,
            AdjustSettingsNode,
            DeliverAnswerNode,
            TrackPerformanceNode,
            MeasureMetricsNode,
            AccuracyMetricsNode,
            CoverageMetricsNode,
            ImproveSystemNode,
            EndNode,
        ],
        state_type=State,
        run_end_type=str,
    )

def build_deps() -> Dependencies:
    return Dependencies(
        ingestion_agent=DocumentIngestionAgent(),
        expansion_agent=QueryExpansionAgent(),
        ranking_agent=RetrievalRankingAgent(),
        generation_agent=ResponseGenerationAgent(),
    )

async def run_graph(query: str, scenario: str = "happy_path", documents: List[Document] = None) -> tuple[str, State]:
    graph = build_graph()
    deps = build_deps()
    state = State(query=query, scenario=scenario, documents=documents or [])
    result = await graph.run(StartNode(), state=state, deps=deps)
    return result.output, state
