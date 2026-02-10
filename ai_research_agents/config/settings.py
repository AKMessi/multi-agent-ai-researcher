"""Configuration and settings management."""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml
from dotenv import load_dotenv

load_dotenv()


@dataclass
class LLMConfig:
    """Configuration for LLM providers."""
    provider: str = "gemini"
    model: str = "gemini-3-flash-preview"
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_output_tokens: int = 8192
    top_p: float = 0.95
    top_k: int = 40
    
    def __post_init__(self):
        if self.api_key is None:
            self.api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")


@dataclass
class AgentConfig:
    """Configuration for individual agents."""
    name: str
    role: str
    personality: str
    expertise: List[str]
    llm_config: LLMConfig = field(default_factory=LLMConfig)
    memory_enabled: bool = True
    max_context_length: int = 100000


@dataclass
class DebateConfig:
    """Configuration for debate mechanics."""
    max_rounds: int = 10
    min_consensus_threshold: float = 0.75
    enable_backtracking: bool = True
    argument_depth: int = 3
    critique_intensity: float = 0.8
    synthesis_threshold: float = 0.6
    

@dataclass
class ResearchConfig:
    """Main research configuration."""
    project_name: str = "ai_research_project"
    research_topic: str = ""
    output_dir: Path = field(default_factory=lambda: Path("./research_output"))
    agents: List[AgentConfig] = field(default_factory=list)
    debate_config: DebateConfig = field(default_factory=DebateConfig)
    enable_web_search: bool = True
    enable_code_execution: bool = True
    max_research_iterations: int = 5
    save_intermediate_results: bool = True
    
    def __post_init__(self):
        self.output_dir = Path(self.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)


class ConfigManager:
    """Manages configuration loading and validation."""
    
    DEFAULT_AGENTS = [
        {
            "name": "Visionary",
            "role": "visionary",
            "personality": "bold, imaginative, forward-thinking, unafraid of unconventional ideas",
            "expertise": ["emerging technologies", "long-term trends", "paradigm shifts", "theoretical frameworks"]
        },
        {
            "name": "Architect",
            "role": "architect",
            "personality": "systematic, detail-oriented, focused on implementation and structure",
            "expertise": ["system design", "software architecture", "scalability", "integration patterns"]
        },
        {
            "name": "Critic",
            "role": "critic",
            "personality": "rigorous, skeptical, focused on identifying flaws and limitations",
            "expertise": ["logical analysis", "bias detection", "risk assessment", "validation methods"]
        },
        {
            "name": "Synthesizer",
            "role": "synthesizer",
            "personality": "holistic, integrative, focused on connecting disparate ideas",
            "expertise": ["pattern recognition", "interdisciplinary research", "conceptual integration", "theory building"]
        },
        {
            "name": "Experimentalist",
            "role": "experimentalist",
            "personality": "empirical, methodical, focused on validation and testing",
            "expertise": ["experiment design", "statistical analysis", "ablation studies", "benchmarking"]
        },
        {
            "name": "Evidence",
            "role": "evidence",
            "personality": "fact-based, research-oriented, focused on real-world data",
            "expertise": ["literature review", "data analysis", "case studies", "state-of-the-art tracking"]
        }
    ]
    
    @classmethod
    def load_from_file(cls, path: str) -> ResearchConfig:
        """Load configuration from YAML file."""
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        return cls._parse_config(data)
    
    @classmethod
    def create_default_config(cls, topic: str) -> ResearchConfig:
        """Create default configuration for a research topic."""
        agents = [
            AgentConfig(
                name=a["name"],
                role=a["role"],
                personality=a["personality"],
                expertise=a["expertise"],
                llm_config=LLMConfig()
            )
            for a in cls.DEFAULT_AGENTS
        ]
        
        return ResearchConfig(
            project_name=f"research_{topic.replace(' ', '_').lower()}",
            research_topic=topic,
            agents=agents
        )
    
    @classmethod
    def _parse_config(cls, data: Dict[str, Any]) -> ResearchConfig:
        """Parse configuration dictionary."""
        # Implementation for YAML parsing
        pass
