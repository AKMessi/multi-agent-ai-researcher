"""Research session management."""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import uuid

from ai_research_agents.config.settings import ResearchConfig, ConfigManager
from ai_research_agents.core.message import MessageBus
from ai_research_agents.core.memory import SharedKnowledgeBase
from ai_research_agents.core.llm import LLMManager
from ai_research_agents.debate.orchestrator import DebateOrchestrator
from ai_research_agents.agents import (
    VisionaryAgent, ArchitectAgent, CriticAgent,
    SynthesizerAgent, ExperimentalistAgent, EvidenceAgent
)
from ai_research_agents.output.report_generator import ReportGenerator
from ai_research_agents.output.code_generator import CodeGenerator


@dataclass
class SessionState:
    """State of a research session."""
    session_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    started_at: datetime = field(default_factory=datetime.now)
    ended_at: Optional[datetime] = None
    status: str = "initialized"  # initialized, running, completed, failed
    current_phase: str = ""
    progress: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class ResearchSession:
    """Main research session managing the entire workflow."""
    
    def __init__(self, config: Optional[ResearchConfig] = None):
        self.config = config or ConfigManager.create_default_config("General AI Research")
        self.state = SessionState()
        
        # Core infrastructure
        self.message_bus = MessageBus()
        self.shared_kb = SharedKnowledgeBase()
        self.llm_manager = LLMManager()
        
        # Agents
        self.agents: Dict[str, Any] = {}
        self._initialize_agents()
        
        # Orchestration
        self.debate_orchestrator = DebateOrchestrator(
            self.config.debate_config,
            self.message_bus
        )
        self.debate_orchestrator.register_agents(list(self.agents.values()))
        
        # Output generators
        self.report_generator = ReportGenerator(self.config.output_dir)
        self.code_generator = CodeGenerator(self.config.output_dir / "code")
        
        # Session storage
        self.session_dir = self.config.output_dir / f"session_{self.state.session_id}"
        self.session_dir.mkdir(parents=True, exist_ok=True)
    
    def _initialize_agents(self):
        """Initialize all research agents."""
        agent_classes = {
            "visionary": VisionaryAgent,
            "architect": ArchitectAgent,
            "critic": CriticAgent,
            "synthesizer": SynthesizerAgent,
            "experimentalist": ExperimentalistAgent,
            "evidence": EvidenceAgent
        }
        
        for agent_config in self.config.agents:
            agent_class = agent_classes.get(agent_config.role)
            if agent_class:
                print(f"  [AGENT] Initializing {agent_config.name} ({agent_config.role})...")
                self.agents[agent_config.name] = agent_class(
                    agent_config,
                    self.message_bus,
                    self.shared_kb
                )
    
    async def conduct_research(self, topic: str, goal: str = "") -> Dict:
        """Conduct a full research session."""
        self.state.status = "running"
        self.config.research_topic = topic
        
        print(f"\n{'='*70}")
        print(f"[RESEARCH] AI RESEARCH SESSION #{self.state.session_id}")
        print(f"[TOPIC] {topic}")
        print(f"{'='*70}\n")
        
        # Phase 1: Initial Research & Evidence Gathering
        print("[PHASE 1] Gathering Evidence...")
        self.state.current_phase = "evidence_gathering"
        await self._phase_evidence_gathering(topic)
        self.state.progress = 0.15
        
        # Phase 2: Structured Debate
        print("\n[PHASE 2] Structured Debate...")
        self.state.current_phase = "debate"
        debate_result = await self.debate_orchestrator.start_debate(topic, goal)
        self.state.progress = 0.70
        
        # Phase 3: Deep Analysis
        print("\n[PHASE 3] Deep Analysis...")
        self.state.current_phase = "analysis"
        analysis = await self._phase_deep_analysis(debate_result)
        self.state.progress = 0.85
        
        # Phase 4: Output Generation
        print("\n[PHASE 4] Generating Outputs...")
        self.state.current_phase = "output_generation"
        outputs = await self._phase_output_generation(debate_result, analysis)
        self.state.progress = 1.0
        
        # Finalize
        self.state.status = "completed"
        self.state.ended_at = datetime.now()
        
        # Save session
        self._save_session({
            "topic": topic,
            "debate_result": debate_result,
            "analysis": analysis,
            "outputs": outputs
        })
        
        print(f"\n{'='*70}")
        print(f"[COMPLETE] Research Session Complete!")
        print(f"[OUTPUT] Outputs saved to: {self.session_dir}")
        print(f"{'='*70}\n")
        
        return {
            "session_id": self.state.session_id,
            "topic": topic,
            "debate_result": debate_result,
            "analysis": analysis,
            "outputs": outputs,
            "session_dir": str(self.session_dir)
        }
    
    async def _phase_evidence_gathering(self, topic: str):
        """Gather initial evidence."""
        evidence_agent = self.agents.get("Evidence")
        if evidence_agent:
            # This happens during debate phases too, but we do initial scan here
            pass  # The debate orchestrator handles evidence gathering
    
    async def _phase_deep_analysis(self, debate_result: Dict) -> Dict:
        """Perform deep analysis of debate results."""
        synthesizer = self.agents.get("Synthesizer")
        
        if not synthesizer:
            return {"error": "No synthesizer available"}
        
        # Identify research gaps
        gaps = synthesizer.identify_gaps(
            debate_result,
            self.config.research_topic
        )
        
        # Generate research implications
        implications = self._generate_implications(debate_result)
        
        return {
            "research_gaps": gaps,
            "implications": implications,
            "confidence_assessment": self._assess_confidence(debate_result),
            "novelty_assessment": self._assess_novelty(debate_result)
        }
    
    async def _phase_output_generation(self, debate_result: Dict, analysis: Dict) -> Dict:
        """Generate all output artifacts."""
        outputs = {}
        
        # Generate research report
        print("  [REPORT] Generating research report...")
        report_path = self.report_generator.generate_full_report(
            debate_result,
            analysis,
            self.config.research_topic
        )
        outputs["report"] = str(report_path)
        
        # Generate code if architecture was designed
        if any("architecture" in str(p.get("metadata", {})) for p in debate_result.get("all_proposals", [])):
            print("  [CODE] Generating implementation code...")
            code_paths = self.code_generator.generate_from_debate(debate_result)
            outputs["code_files"] = [str(p) for p in code_paths]
        
        # Generate summary
        summary_path = self.report_generator.generate_summary(
            debate_result,
            self.session_dir / "summary.md"
        )
        outputs["summary"] = str(summary_path)
        
        # Save raw data
        raw_path = self.session_dir / "raw_data.json"
        with open(raw_path, 'w') as f:
            json.dump(debate_result, f, indent=2, default=str)
        outputs["raw_data"] = str(raw_path)
        
        return outputs
    
    def _generate_implications(self, debate_result: Dict) -> List[str]:
        """Generate research implications."""
        implications = []
        
        final = debate_result.get("final_conclusion", {})
        if final:
            content = final.get("content", "")
            # Extract implications (simplified)
            implications.append(f"Primary contribution: {content[:200]}...")
        
        return implications
    
    def _assess_confidence(self, debate_result: Dict) -> Dict:
        """Assess confidence in the research conclusions."""
        return {
            "consensus_score": debate_result.get("consensus_score", 0),
            "rounds_to_convergence": debate_result.get("rounds_completed", 0),
            "confidence_level": "high" if debate_result.get("consensus_score", 0) > 0.7 else "medium"
        }
    
    def _assess_novelty(self, debate_result: Dict) -> Dict:
        """Assess novelty of the research."""
        proposals = debate_result.get("all_proposals", [])
        
        # Count unique directions
        directions = set()
        for p in proposals:
            metadata = p.get("metadata", {})
            if "proposal" in metadata:
                directions.add(metadata["proposal"].get("title", "unknown"))
        
        return {
            "unique_proposals": len(directions),
            "exploration_breadth": len(proposals),
            "novelty_score": min(1.0, len(directions) / 5)  # Simple metric
        }
    
    def _save_session(self, data: Dict):
        """Save session data."""
        session_file = self.session_dir / "session.json"
        
        session_data = {
            "state": {
                "session_id": self.state.session_id,
                "started_at": self.state.started_at.isoformat(),
                "ended_at": self.state.ended_at.isoformat() if self.state.ended_at else None,
                "status": self.state.status,
                "topic": self.config.research_topic
            },
            "results": data
        }
        
        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2, default=str)
    
    def get_status(self) -> Dict:
        """Get current session status."""
        return {
            "session_id": self.state.session_id,
            "status": self.state.status,
            "current_phase": self.state.current_phase,
            "progress": f"{self.state.progress*100:.1f}%",
            "agents": list(self.agents.keys()),
            "topic": self.config.research_topic
        }
