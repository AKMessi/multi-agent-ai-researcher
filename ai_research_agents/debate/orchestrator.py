"""Debate orchestration engine."""

import asyncio
from enum import Enum, auto
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import json

from ai_research_agents.core.message import Message, MessageType, MessageBus
from ai_research_agents.agents.base import BaseAgent
from ai_research_agents.config.settings import DebateConfig


class DebatePhase(Enum):
    """Phases of the debate process."""
    INITIALIZATION = auto()
    EXPLORATION = auto()
    PROPOSAL = auto()
    CRITIQUE = auto()
    SYNTHESIS = auto()
    VERIFICATION = auto()
    CONVERGENCE = auto()
    CONCLUSION = auto()


class DebateState(Enum):
    """State of debate execution."""
    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()
    CONVERGED = auto()
    MAX_ROUNDS = auto()
    ERROR = auto()


@dataclass
class DebateRound:
    """A single round of debate."""
    number: int
    phase: DebatePhase
    start_time: datetime
    end_time: Optional[datetime] = None
    messages: List[Message] = field(default_factory=list)
    summary: str = ""
    consensus_score: float = 0.0


@dataclass
class ConsensusMetrics:
    """Metrics tracking consensus formation."""
    agreement_matrix: Dict[str, Dict[str, float]] = field(default_factory=dict)
    proposal_scores: Dict[str, float] = field(default_factory=dict)
    confidence_trend: List[float] = field(default_factory=list)
    key_disagreements: List[str] = field(default_factory=list)
    
    def update_agreement(self, agent_a: str, agent_b: str, score: float):
        """Update agreement between two agents."""
        if agent_a not in self.agreement_matrix:
            self.agreement_matrix[agent_a] = {}
        self.agreement_matrix[agent_a][agent_b] = score
    
    def get_average_consensus(self) -> float:
        """Calculate average consensus level."""
        scores = []
        for row in self.agreement_matrix.values():
            scores.extend(row.values())
        return sum(scores) / len(scores) if scores else 0.0


class DebateOrchestrator:
    """Orchestrates structured debate between agents."""
    
    def __init__(self, config: DebateConfig, message_bus: MessageBus):
        self.config = config
        self.message_bus = message_bus
        self.agents: List[BaseAgent] = []
        
        self.state = DebateState.IDLE
        self.current_phase = DebatePhase.INITIALIZATION
        self.current_round = 0
        self.rounds: List[DebateRound] = []
        
        self.consensus = ConsensusMetrics()
        self.proposals: List[Dict] = []
        self.critiques: List[Dict] = []
        self.syntheses: List[Dict] = []
        
        self.phase_handlers: Dict[DebatePhase, Callable] = {
            DebatePhase.INITIALIZATION: self._phase_initialization,
            DebatePhase.EXPLORATION: self._phase_exploration,
            DebatePhase.PROPOSAL: self._phase_proposal,
            DebatePhase.CRITIQUE: self._phase_critique,
            DebatePhase.SYNTHESIS: self._phase_synthesis,
            DebatePhase.VERIFICATION: self._phase_verification,
            DebatePhase.CONVERGENCE: self._phase_convergence,
            DebatePhase.CONCLUSION: self._phase_conclusion
        }
        
        self.topic = ""
        self.research_goal = ""
        self.final_conclusion: Optional[Dict] = None
        
        # Track active proposals and their status
        self.active_proposals: Dict[str, Dict] = {}
    
    def register_agents(self, agents: List[BaseAgent]):
        """Register agents for the debate."""
        self.agents = agents
    
    async def start_debate(self, topic: str, goal: str = "") -> Dict:
        """Start the debate process."""
        self.topic = topic
        self.research_goal = goal or f"Research and develop novel approaches for: {topic}"
        self.state = DebateState.RUNNING
        
        print(f"[STARTING] Debate on: {topic}")
        print(f"[GOAL] {self.research_goal}")
        print(f"[AGENTS] {[a.name for a in self.agents]}")
        
        # Run through phases
        phases = [
            DebatePhase.INITIALIZATION,
            DebatePhase.EXPLORATION,
            DebatePhase.PROPOSAL,
            DebatePhase.CRITIQUE,
            DebatePhase.SYNTHESIS,
            DebatePhase.VERIFICATION,
            DebatePhase.CONVERGENCE,
            DebatePhase.CONCLUSION
        ]
        
        for phase in phases:
            if self.state != DebateState.RUNNING:
                break
            
            self.current_phase = phase
            print(f"\n{'='*60}")
            print(f"[PHASE] {phase.name}")
            print('='*60)
            
            await self.phase_handlers[phase]()
            
            # Check for early convergence
            if self._check_convergence():
                print("\n[CONSENSUS] Reached! Moving to conclusion.")
                self.state = DebateState.CONVERGED
                await self._phase_conclusion()
                break
        
        self.state = DebateState.CONVERGED if self.final_conclusion else DebateState.MAX_ROUNDS
        return self._generate_final_report()
    
    async def _phase_initialization(self):
        """Initialize agents with context."""
        context = {
            "topic": self.topic,
            "goal": self.research_goal,
            "phase": "initialization"
        }
        
        # Each agent does initial thinking
        for agent in self.agents:
            print(f"  [PREP] {agent.name} is preparing...")
            # Agents can do initial setup if needed
    
    async def _phase_exploration(self):
        """Phase for exploring the problem space."""
        self.current_round += 1
        round_record = DebateRound(
            number=self.current_round,
            phase=self.current_phase,
            start_time=datetime.now()
        )
        
        # Evidence agent leads with literature review
        evidence_agent = self._get_agent("evidence")
        if evidence_agent:
            msg = await evidence_agent.act({
                "phase": "literature_review",
                "topic": self.topic
            })
            if msg:
                round_record.messages.append(msg)
                await asyncio.sleep(0.5)  # Rate limiting
        
        # Visionary explores breakthrough directions
        visionary = self._get_agent("visionary")
        if visionary:
            msg = await visionary.act({
                "phase": "breakthrough",
                "current_paradigm": self.topic
            })
            if msg:
                round_record.messages.append(msg)
                await asyncio.sleep(0.5)
        
        round_record.end_time = datetime.now()
        self.rounds.append(round_record)
    
    async def _phase_proposal(self):
        """Phase for generating proposals."""
        self.current_round += 1
        round_record = DebateRound(
            number=self.current_round,
            phase=self.current_phase,
            start_time=datetime.now()
        )
        
        # Multiple agents generate proposals
        proposing_agents = [
            self._get_agent("visionary"),
            self._get_agent("architect")
        ]
        
        for agent in proposing_agents:
            if agent:
                print(f"  [PROPOSAL] {agent.name} is generating...")
                msg = await agent.act({
                    "phase": "ideation" if agent.role == "visionary" else "architecture",
                    "topic": self.topic,
                    "proposals": [p.get("content", "") for p in self.proposals]
                })
                if msg:
                    round_record.messages.append(msg)
                    self._extract_proposal(msg)
                    await asyncio.sleep(0.5)
        
        round_record.end_time = datetime.now()
        self.rounds.append(round_record)
    
    async def _phase_critique(self):
        """Phase for critiquing proposals."""
        self.current_round += 1
        round_record = DebateRound(
            number=self.current_round,
            phase=self.current_phase,
            start_time=datetime.now()
        )
        
        critic = self._get_agent("critic")
        if critic and self.proposals:
            # Critique each major proposal
            for i, proposal in enumerate(self.proposals[-2:]):  # Last 2 proposals
                print(f"  [CRITIQUE] Analyzing proposal {i+1}...")
                msg = await critic.act({
                    "phase": "critique",
                    "target_proposal": proposal.get("content", ""),
                    "author": proposal.get("author", "unknown")
                })
                if msg:
                    round_record.messages.append(msg)
                    self._extract_critique(msg)
                    await asyncio.sleep(0.5)
            
            # Stress test
            if self.proposals:
                print(f"  [STRESS TEST] Running tests...")
                msg = await critic.act({
                    "phase": "stress_test",
                    "idea": self.proposals[-1].get("content", "")
                })
                if msg:
                    round_record.messages.append(msg)
    
        round_record.end_time = datetime.now()
        self.rounds.append(round_record)
    
    async def _phase_synthesis(self):
        """Phase for synthesizing ideas."""
        self.current_round += 1
        round_record = DebateRound(
            number=self.current_round,
            phase=self.current_phase,
            start_time=datetime.now()
        )
        
        synthesizer = self._get_agent("synthesizer")
        if synthesizer and len(self.proposals) >= 2:
            print(f"  [SYNTHESIS] Integrating ideas...")
            msg = await synthesizer.act({
                "phase": "synthesis",
                "topic": self.topic,
                "proposals": [p.get("content", "") for p in self.proposals[-4:]],
                "critiques": [c.get("content", "") for c in self.critiques[-4:]]
            })
            if msg:
                round_record.messages.append(msg)
                self._extract_synthesis(msg)
                await asyncio.sleep(0.5)
        
        # Architect refines based on synthesis
        architect = self._get_agent("architect")
        if architect and self.syntheses:
            print(f"  [REFINE] Architect refining design...")
            msg = await architect.act({
                "phase": "refinement",
                "current_design": self.syntheses[-1].get("content", ""),
                "critiques": [c.get("content", "") for c in self.critiques[-3:]]
            })
            if msg:
                round_record.messages.append(msg)
        
        round_record.end_time = datetime.now()
        self.rounds.append(round_record)
    
    async def _phase_verification(self):
        """Phase for experimental verification."""
        self.current_round += 1
        round_record = DebateRound(
            number=self.current_round,
            phase=self.current_phase,
            start_time=datetime.now()
        )
        
        experimentalist = self._get_agent("experimentalist")
        if experimentalist and self.syntheses:
            # Design experiments for latest synthesis
            print(f"  [EXPERIMENT] Experimentalist is designing validation...")
            msg = await experimentalist.act({
                "phase": "experiment_design",
                "hypothesis": self.syntheses[-1].get("content", ""),
                "theory": self.topic
            })
            if msg:
                round_record.messages.append(msg)
                await asyncio.sleep(0.5)
            
            # Design benchmarks
            msg = await experimentalist.act({
                "phase": "benchmark",
                "approach": self.syntheses[-1].get("content", "")
            })
            if msg:
                round_record.messages.append(msg)
        
        round_record.end_time = datetime.now()
        self.rounds.append(round_record)
    
    async def _phase_convergence(self):
        """Phase for driving towards consensus."""
        self.current_round += 1
        round_record = DebateRound(
            number=self.current_round,
            phase=self.current_phase,
            start_time=datetime.now()
        )
        
        synthesizer = self._get_agent("synthesizer")
        if synthesizer:
            print(f"   Crafting final theory...")
            msg = await synthesizer.act({
                "phase": "final_theory",
                "syntheses": [s.get("content", "") for s in self.syntheses[-3:]],
                "experiments": ["experiment_design"]  # Simplified
            })
            if msg:
                round_record.messages.append(msg)
                self.final_conclusion = self._extract_final_conclusion(msg)
        
        round_record.end_time = datetime.now()
        self.rounds.append(round_record)
    
    async def _phase_conclusion(self):
        """Generate final conclusion."""
        if not self.final_conclusion and self.syntheses:
            self.final_conclusion = {
                "content": self.syntheses[-1].get("content", ""),
                "source": "synthesis"
            }
        
        print(f"\n{'='*60}")
        print(" RESEARCH CONCLUSION")
        print('='*60)
        if self.final_conclusion:
            print(self.final_conclusion.get("content", "")[:500] + "...")
    
    def _get_agent(self, role: str) -> Optional[BaseAgent]:
        """Get agent by role."""
        for agent in self.agents:
            if agent.role == role:
                return agent
        return None
    
    def _extract_proposal(self, message: Message):
        """Extract proposal from message."""
        self.proposals.append({
            "content": message.content,
            "author": message.sender,
            "metadata": message.metadata,
            "timestamp": message.timestamp
        })
    
    def _extract_critique(self, message: Message):
        """Extract critique from message."""
        self.critiques.append({
            "content": message.content,
            "author": message.sender,
            "metadata": message.metadata
        })
    
    def _extract_synthesis(self, message: Message):
        """Extract synthesis from message."""
        self.syntheses.append({
            "content": message.content,
            "author": message.sender,
            "metadata": message.metadata
        })
    
    def _extract_final_conclusion(self, message: Message) -> Dict:
        """Extract final conclusion from message."""
        return {
            "content": message.content,
            "author": message.sender,
            "metadata": message.metadata
        }
    
    def _check_convergence(self) -> bool:
        """Check if debate has converged."""
        if len(self.rounds) < 3:
            return False
        
        # Check consensus metrics
        consensus_score = self.consensus.get_average_consensus()
        
        # Converged if high consensus and enough rounds
        if consensus_score >= self.config.min_consensus_threshold and len(self.rounds) >= 5:
            return True
        
        # Converged if max rounds reached
        if self.current_round >= self.config.max_rounds:
            return True
        
        return False
    
    def _generate_final_report(self) -> Dict:
        """Generate final research report."""
        return {
            "topic": self.topic,
            "research_goal": self.research_goal,
            "status": self.state.name,
            "rounds_completed": self.current_round,
            "phases_completed": [r.phase.name for r in self.rounds],
            "proposals_generated": len(self.proposals),
            "critiques_provided": len(self.critiques),
            "syntheses_created": len(self.syntheses),
            "final_conclusion": self.final_conclusion,
            "consensus_score": self.consensus.get_average_consensus(),
            "all_proposals": self.proposals,
            "all_critiques": self.critiques,
            "all_syntheses": self.syntheses
        }
