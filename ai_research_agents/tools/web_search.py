"""Web search tool for gathering evidence."""

import asyncio
from typing import List, Dict, Optional
from dataclasses import dataclass

try:
    from duckduckgo_search import DDGS
    DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False


@dataclass
class SearchResult:
    """Web search result."""
    title: str
    url: str
    snippet: str
    source: str = "duckduckgo"


class WebSearchTool:
    """Tool for searching the web."""
    
    def __init__(self):
        self.ddgs = DDGS() if DDGS_AVAILABLE else None
    
    async def search(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search the web for information."""
        if not self.ddgs:
            return self._fallback_search(query, max_results)
        
        try:
            results = []
            ddgs_results = self.ddgs.text(query, max_results=max_results)
            
            for r in ddgs_results:
                results.append(SearchResult(
                    title=r.get('title', ''),
                    url=r.get('href', ''),
                    snippet=r.get('body', '')
                ))
            
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return self._fallback_search(query, max_results)
    
    async def search_news(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search for news articles."""
        if not self.ddgs:
            return []
        
        try:
            results = []
            ddgs_results = self.ddgs.news(query, max_results=max_results)
            
            for r in ddgs_results:
                results.append(SearchResult(
                    title=r.get('title', ''),
                    url=r.get('url', ''),
                    snippet=r.get('body', ''),
                    source="news"
                ))
            
            return results
        except Exception as e:
            return []
    
    async def search_papers(self, query: str, max_results: int = 5) -> List[SearchResult]:
        """Search for academic papers."""
        # Enhance query for academic search
        academic_query = f"{query} site:arxiv.org OR filetype:pdf"
        return await self.search(academic_query, max_results)
    
    def _fallback_search(self, query: str, max_results: int) -> List[SearchResult]:
        """Fallback when search is unavailable."""
        return [SearchResult(
            title="Search unavailable",
            url="",
            snippet=f"Web search is not available. Query was: {query}",
            source="fallback"
        )]
    
    def format_results(self, results: List[SearchResult]) -> str:
        """Format search results for consumption by agents."""
        if not results:
            return "No search results found."
        
        formatted = []
        for i, r in enumerate(results, 1):
            formatted.append(
                f"[{i}] {r.title}\n"
                f"    URL: {r.url}\n"
                f"    {r.snippet[:300]}..."
            )
        
        return "\n\n".join(formatted)


class EvidenceAggregator:
    """Aggregate evidence from multiple sources."""
    
    def __init__(self):
        self.search_tool = WebSearchTool()
        self.cache: Dict[str, List[SearchResult]] = {}
    
    async def gather_evidence(self, claims: List[str]) -> Dict[str, List[SearchResult]]:
        """Gather evidence for multiple claims."""
        results = {}
        
        for claim in claims:
            if claim in self.cache:
                results[claim] = self.cache[claim]
            else:
                search_results = await self.search_tool.search(claim, max_results=3)
                self.cache[claim] = search_results
                results[claim] = search_results
        
        return results
    
    async def find_supporting_evidence(self, hypothesis: str) -> Dict:
        """Find evidence supporting or refuting a hypothesis."""
        # Search for supporting evidence
        supporting = await self.search_tool.search(
            f"evidence for {hypothesis}",
            max_results=5
        )
        
        # Search for refuting evidence
        refuting = await self.search_tool.search(
            f"criticism limitations {hypothesis}",
            max_results=5
        )
        
        return {
            "supporting": supporting,
            "refuting": refuting,
            "balanced_view": self._format_balanced(supporting, refuting)
        }
    
    def _format_balanced(self, supporting: List[SearchResult], 
                        refuting: List[SearchResult]) -> str:
        """Format balanced view of evidence."""
        lines = ["=== SUPPORTING EVIDENCE ==="]
        for r in supporting[:3]:
            lines.append(f" {r.title}: {r.snippet[:200]}")
        
        lines.append("\n=== CONTRADICTING/CRITICAL EVIDENCE ===")
        for r in refuting[:3]:
            lines.append(f" {r.title}: {r.snippet[:200]}")
        
        return "\n".join(lines)
