"""Visionary Agent - Proposes novel ideas and directions."""

from typing import Dict, Any, Optional
from ai_research_agents.agents.base import BaseAgent
from ai_research_agents.core.message import Message, MessageType, Priority
from ai_research_agents.config.settings import AgentConfig


class VisionaryAgent(BaseAgent):
    """Visionary agent focused on breakthrough ideas and long-term vision."""
    
    def __init__(self, config: AgentConfig, message_bus, shared_kb):
        super().__init__(config, message_bus, shared_kb)
        self.innovation_history = []
    
    def _register_handlers(self):
        """Register message handlers."""
        self.message_handlers[MessageType.CRITIQUE] = self._handle_critique
        self.message_handlers[MessageType.SYNTHESIS] = self._handle_synthesis
    
    def _handle_critique(self, message: Message):
        """Handle critique by refining or defending ideas."""
        pass  # Respond in act() cycle
    
    def _handle_synthesis(self, message: Message):
        """Handle synthesis by building on integrated ideas."""
        pass
    
    async def act(self, context: Dict[str, Any]) -> Optional[Message]:
        """Generate novel proposals or respond to context."""
        
        if context.get("phase") == "ideation":
            return self._generate_proposal(context)
        elif context.get("phase") == "evolution":
            return self._evolve_ideas(context)
        elif context.get("phase") == "breakthrough":
            return self._seek_breakthrough(context)
        
        return None
    
    def _generate_proposal(self, context: Dict) -> Message:
        """Generate a novel research proposal."""
        topic = context.get("topic", "AI research")
        constraints = context.get("constraints", [])
        
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "core_idea": {"type": "string"},
                "novelty": {"type": "string"},
                "potential_impact": {"type": "string"},
                "key_innovations": {"type": "array", "items": {"type": "string"}},
                "inspiration_sources": {"type": "array", "items": {"type": "string"}},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1}
            },
            "required": ["title", "core_idea", "novelty", "potential_impact", "key_innovations"]
        }
        
        prompt = f"""Generate a bold, visionary proposal for research on: {topic}

Think beyond current paradigms. Consider:
- What would be a paradigm shift in this area?
- What seemingly impossible things could become possible?
- What cross-disciplinary inspirations could apply?

Constraints to consider: {constraints}

Propose something genuinely novel that could change the field."""
        
        result = self.think_structured(prompt, schema)
        self.innovation_history.append(result)
        
        content = f"""**{result.get('title', 'Untitled Proposal')}**

**Core Vision:** {result.get('core_idea', '')}

**Novelty:** {result.get('novelty', '')}

**Potential Impact:** {result.get('potential_impact', '')}

**Key Innovations:**
{chr(10).join(f"  - {inv}" for inv in result.get('key_innovations', []))}

**Inspiration:** {', '.join(result.get('inspiration_sources', []))}"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.PROPOSAL,
            confidence=result.get('confidence', 0.8),
            metadata={"proposal": result, "phase": "ideation"}
        )
    
    def _evolve_ideas(self, context: Dict) -> Message:
        """Evolve existing ideas based on feedback."""
        current_proposals = context.get("proposals", [])
        feedback = context.get("feedback", [])
        
        schema = {
            "type": "object",
            "properties": {
                "evolved_concept": {"type": "string"},
                "improvements": {"type": "array", "items": {"type": "string"}},
                "new_directions": {"type": "array", "items": {"type": "string"}},
                "breakthrough_potential": {"type": "string"}
            },
            "required": ["evolved_concept", "improvements", "new_directions"]
        }
        
        prompt = f"""Given these existing proposals and feedback, evolve the ideas into something even more powerful:

EXISTING PROPOSALS:
{chr(10).join(f"- {p}" for p in current_proposals[:3])}

FEEDBACK RECEIVED:
{chr(10).join(f"- {f}" for f in feedback[:5])}

Create an evolved vision that addresses critiques while pushing boundaries further."""
        
        result = self.think_structured(prompt, schema)
        
        content = f"""**Evolved Vision**

**Refined Concept:** {result.get('evolved_concept', '')}

**Key Improvements:**
{chr(10).join(f"  - {imp}" for imp in result.get('improvements', []))}

**New Directions Opened:**
{chr(10).join(f"  - {d}" for d in result.get('new_directions', []))}

**Breakthrough Potential:** {result.get('breakthrough_potential', '')}"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.PROPOSAL,
            metadata={"evolution": result, "phase": "evolution"}
        )
    
    def _seek_breakthrough(self, context: Dict) -> Message:
        """Seek radical breakthrough ideas."""
        current_paradigm = context.get("current_paradigm", "")
        
        schema = {
            "type": "object",
            "properties": {
                "paradigm_challenged": {"type": "string"},
                "new_paradigm": {"type": "string"},
                "enabling_factors": {"type": "array", "items": {"type": "string"}},
                "implementation_roadmap": {"type": "array", "items": {"type": "string"}},
                "risk_assessment": {"type": "string"}
            },
            "required": ["paradigm_challenged", "new_paradigm", "enabling_factors"]
        }
        
        prompt = f"""Challenge fundamental assumptions in this area:

CURRENT PARADIGM: {current_paradigm}

What if the fundamental assumptions are wrong? What paradigm shift would unlock unprecedented capabilities?

Think radically but ground your vision in emerging trends and theoretical possibilities."""
        
        result = self.think_structured(prompt, schema)
        
        content = f"""**Paradigm Shift Proposal**

**Challenging:** {result.get('paradigm_challenged', '')}

**New Paradigm:** {result.get('new_paradigm', '')}

**Enabling Factors:**
{chr(10).join(f"  - {f}" for f in result.get('enabling_factors', []))}

**Implementation Roadmap:**
{chr(10).join(f"  {i+1}. {step}" for i, step in enumerate(result.get('implementation_roadmap', [])))}

**Risk Assessment:** {result.get('risk_assessment', '')}"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.PROPOSAL,
            priority=Priority.HIGH if len(self.innovation_history) < 3 else Priority.NORMAL,
            metadata={"breakthrough": result, "phase": "breakthrough"}
        )
