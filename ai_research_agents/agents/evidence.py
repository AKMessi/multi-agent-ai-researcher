"""Evidence Agent - Searches for and analyzes external evidence."""

from typing import Dict, Any, Optional, List
from ai_research_agents.agents.base import BaseAgent
from ai_research_agents.core.message import Message, MessageType
from ai_research_agents.config.settings import AgentConfig
from ai_research_agents.tools.web_search import WebSearchTool


class EvidenceAgent(BaseAgent):
    """Evidence agent focused on gathering and analyzing external research."""
    
    def __init__(self, config: AgentConfig, message_bus, shared_kb):
        super().__init__(config, message_bus, shared_kb)
        self.search_tool = WebSearchTool()
        self.evidence_collected = []
    
    def _register_handlers(self):
        """Register message handlers."""
        self.message_handlers[MessageType.PROPOSAL] = self._check_evidence
    
    def _check_evidence(self, message: Message):
        """Check for supporting or refuting evidence."""
        pass
    
    async def act(self, context: Dict[str, Any]) -> Optional[Message]:
        """Gather and analyze evidence."""
        
        if context.get("phase") == "literature_review":
            return await self._conduct_literature_review(context)
        elif context.get("phase") == "fact_check":
            return await self._fact_check(context)
        elif context.get("phase") == "state_of_art":
            return await self._analyze_state_of_art(context)
        elif context.get("phase") == "find_precedents":
            return await self._find_precedents(context)
        
        return None
    
    async def _conduct_literature_review(self, context: Dict) -> Message:
        """Conduct literature review on a topic."""
        topic = context.get("topic", "")
        
        # Search for relevant papers
        search_results = await self.search_tool.search(
            f"{topic} research paper arxiv",
            max_results=10
        )
        
        schema = {
            "type": "object",
            "properties": {
                "key_papers": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "authors": {"type": "string"},
                            "key_contribution": {"type": "string"},
                            "relevance": {"type": "string"}
                        }
                    }
                },
                "research_trends": {"type": "array", "items": {"type": "string"}},
                "gaps_in_literature": {"type": "array", "items": {"type": "string"}},
                "supporting_evidence": {"type": "array", "items": {"type": "string"}},
                "conflicting_findings": {"type": "array", "items": {"type": "string"}},
                "synthesis": {"type": "string"}
            }
        }
        
        prompt = f"""Based on these search results, provide a literature review for: {topic}

SEARCH RESULTS:
{search_results}

Synthesize the current state of research, identify trends, gaps, and how our work fits."""
        
        result = self.think_structured(prompt, schema)
        
        # Add to shared knowledge base
        for paper in result.get('key_papers', []):
            self.shared_kb.add_paper(
                title=paper.get('title', 'Unknown'),
                authors=[paper.get('authors', 'Unknown')],
                abstract=paper.get('key_contribution', ''),
                key_findings=[paper.get('relevance', '')]
            )
        
        papers_str = "\n\n".join([
            f"**{p.get('title', 'Unknown')}** ({p.get('authors', 'Unknown')})\n"
            f"  Contribution: {p.get('key_contribution', '')}\n"
            f"  Relevance: {p.get('relevance', '')}"
            for p in result.get('key_papers', [])
        ])
        
        content = f"""**Literature Review: {topic}**

**Key Papers:**
{papers_str}

**Research Trends:**
{chr(10).join(f"  - {t}" for t in result.get('research_trends', []))}

**Gaps in Literature:**
{chr(10).join(f"  - {g}" for g in result.get('gaps_in_literature', []))}

**Supporting Evidence:**
{chr(10).join(f"  - {e}" for e in result.get('supporting_evidence', []))}

**Conflicting Findings:**
{chr(10).join(f"  - {c}" for c in result.get('conflicting_findings', []))}

**Synthesis:**
{result.get('synthesis', '')}"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.EVIDENCE,
            metadata={"literature_review": result, "phase": "literature_review"}
        )
    
    async def _fact_check(self, context: Dict) -> Message:
        """Fact-check a claim."""
        claim = context.get("claim", "")
        
        search_results = await self.search_tool.search(
            claim,
            max_results=5
        )
        
        schema = {
            "type": "object",
            "properties": {
                "claim_accuracy": {"type": "string", "enum": ["verified", "partially_verified", "disputed", "unverified"]},
                "supporting_sources": {"type": "array", "items": {"type": "string"}},
                "conflicting_sources": {"type": "array", "items": {"type": "string"}},
                "nuance": {"type": "string"},
                "confidence": {"type": "number"}
            }
        }
        
        prompt = f"""Fact-check this claim:

CLAIM: {claim}

SEARCH RESULTS:
{search_results}

Assess accuracy based on credible sources."""
        
        result = self.think_structured(prompt, schema)
        
        accuracy_map = {
            "verified": "Confirmed",
            "partially_verified": "Partial",
            "disputed": "Disputed",
            "unverified": "Unverified"
        }
        
        content = f"""**Fact Check Result**

**Claim:** {claim}

**Verdict:** {accuracy_map.get(result.get('claim_accuracy', 'unverified'), 'Unknown')}

**Confidence:** {result.get('confidence', 0)*100:.0f}%

**Supporting Sources:**
{chr(10).join(f"  - {s}" for s in result.get('supporting_sources', []))}

**Conflicting Sources:**
{chr(10).join(f"  - {s}" for s in result.get('conflicting_sources', []))}

**Nuance:**
{result.get('nuance', '')}"""
        
        # Add fact to shared knowledge base
        if result.get('claim_accuracy') == 'verified':
            self.shared_kb.add_fact(
                claim, 
                source="fact_check",
                confidence=result.get('confidence', 0)
            )
        
        return self.send_message(
            content=content,
            message_type=MessageType.EVIDENCE,
            metadata={"fact_check": result, "phase": "fact_check"}
        )
    
    async def _analyze_state_of_art(self, context: Dict) -> Message:
        """Analyze state-of-the-art in a field."""
        field = context.get("field", "")
        
        search_results = await self.search_tool.search(
            f"state of the art {field} 2024 2025 benchmark",
            max_results=10
        )
        
        schema = {
            "type": "object",
            "properties": {
                "sota_methods": {"type": "array", "items": {"type": "string"}},
                "best_reported_results": {"type": "array", "items": {"type": "string"}},
                "leading_institutions": {"type": "array", "items": {"type": "string"}},
                "key_datasets": {"type": "array", "items": {"type": "string"}},
                "open_challenges": {"type": "array", "items": {"type": "string"}},
                "emerging_approaches": {"type": "array", "items": {"type": "string"}}
            }
        }
        
        prompt = f"""Analyze the state-of-the-art in: {field}

SEARCH RESULTS:
{search_results}

Identify the best methods, results, and open challenges."""
        
        result = self.think_structured(prompt, schema)
        
        content = f"""**State-of-the-Art Analysis: {field}**

**Leading Methods:**
{chr(10).join(f"  - {m}" for m in result.get('sota_methods', []))}

**Best Reported Results:**
{chr(10).join(f"  - {r}" for r in result.get('best_reported_results', []))}

**Leading Institutions:**
{chr(10).join(f"  - {i}" for i in result.get('leading_institutions', []))}

**Key Datasets:**
{chr(10).join(f"  - {d}" for d in result.get('key_datasets', []))}

**Open Challenges:**
{chr(10).join(f"  - {c}" for c in result.get('open_challenges', []))}

**Emerging Approaches:**
{chr(10).join(f"  - {a}" for a in result.get('emerging_approaches', []))}"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.EVIDENCE,
            metadata={"sota": result, "phase": "state_of_art"}
        )
    
    async def _find_precedents(self, context: Dict) -> Message:
        """Find precedents for an idea."""
        idea = context.get("idea", "")
        
        search_results = await self.search_tool.search(
            f"{idea} similar concept precedent prior work",
            max_results=8
        )
        
        schema = {
            "type": "object",
            "properties": {
                "direct_precedents": {"type": "array", "items": {"type": "string"}},
                "related_work": {"type": "array", "items": {"type": "string"}},
                "inspirations": {"type": "array", "items": {"type": "string"}},
                "differentiation": {"type": "string"},
                "intellectual_lineage": {"type": "string"}
            }
        }
        
        prompt = f"""Find precedents and related work for this idea:

IDEA: {idea}

SEARCH RESULTS:
{search_results}

Identify what came before and how this idea differs."""
        
        result = self.think_structured(prompt, schema)
        
        content = f"""**Precedent Analysis**

**Direct Precedents:**
{chr(10).join(f"  - {p}" for p in result.get('direct_precedents', []))}

**Related Work:**
{chr(10).join(f"  - {r}" for r in result.get('related_work', []))}

**Inspirations:**
{chr(10).join(f"  - {i}" for i in result.get('inspirations', []))}

**How This Idea Differs:**
{result.get('differentiation', '')}

**Intellectual Lineage:**
{result.get('intellectual_lineage', '')}"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.EVIDENCE,
            metadata={"precedents": result, "phase": "find_precedents"}
        )
