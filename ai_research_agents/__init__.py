"""
Ultimate Multi-Agent AI Research System

A world-class multi-agent framework for collaborative AI research with
structured debate, web search integration, code execution, and comprehensive
research output generation.
"""

__version__ = "1.0.0"
__author__ = "AI Research Team"

from ai_research_agents.core.session import ResearchSession
from ai_research_agents.core.orchestrator import ResearchOrchestrator

__all__ = ["ResearchSession", "ResearchOrchestrator"]
