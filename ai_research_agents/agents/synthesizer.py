"""Synthesizer Agent - Combines insights into coherent theories."""

from typing import Dict, Any, Optional, List
from ai_research_agents.agents.base import BaseAgent
from ai_research_agents.core.message import Message, MessageType, Priority
from ai_research_agents.config.settings import AgentConfig


class SynthesizerAgent(BaseAgent):
    """Synthesizer agent focused on integrating diverse ideas into unified frameworks."""
    
    def __init__(self, config: AgentConfig, message_bus, shared_kb):
        super().__init__(config, message_bus, shared_kb)
        self.syntheses = []
    
    def _register_handlers(self):
        """Register message handlers."""
        self.message_handlers[MessageType.PROPOSAL] = self._note_proposal
        self.message_handlers[MessageType.CRITIQUE] = self._note_critique
    
    def _note_proposal(self, message: Message):
        """Track proposals for synthesis."""
        pass
    
    def _note_critique(self, message: Message):
        """Track critiques to address in synthesis."""
        pass
    
    async def act(self, context: Dict[str, Any]) -> Optional[Message]:
        """Synthesize insights from the research process."""
        
        if context.get("phase") == "synthesis":
            return self._create_synthesis(context)
        elif context.get("phase") == "unify":
            return self._unify_frameworks(context)
        elif context.get("phase") == "final_theory":
            return self._craft_final_theory(context)
        
        return None
    
    def _create_synthesis(self, context: Dict) -> Message:
        """Create synthesis from multiple proposals and critiques."""
        proposals = context.get("proposals", [])
        critiques = context.get("critiques", [])
        topic = context.get("topic", "")
        
        schema = {
            "type": "object",
            "properties": {
                "unified_concept": {"type": "string"},
                "core_principles": {"type": "array", "items": {"type": "string"}},
                "synthesis_of_ideas": {"type": "string"},
                "resolution_of_tensions": {"type": "string"},
                "emergent_properties": {"type": "array", "items": {"type": "string"}},
                "contributions_from_each": {
                    "type": "object",
                    "additionalProperties": {"type": "string"}
                },
                "remaining_questions": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["unified_concept", "core_principles", "synthesis_of_ideas"]
        }
        
        prompt = f"""Synthesize the following research proposals into a unified framework:

TOPIC: {topic}

PROPOSALS:
{chr(10).join(f"{i+1}. {p}" for i, p in enumerate(proposals))}

CRITIQUES TO ADDRESS:
{chr(10).join(f"- {c}" for c in critiques[:5])}

Create a synthesis that:
1. Identifies common underlying principles
2. Resolves apparent contradictions
3. Integrates the best elements from each proposal
4. Emerges with something greater than the sum of parts
5. Acknowledges what remains unresolved"""
        
        result = self.think_structured(prompt, schema)
        self.syntheses.append(result)
        
        contributions_str = "\n".join([
            f"  - **{k}**: {v}"
            for k, v in result.get('contributions_from_each', {}).items()
        ])
        
        content = f"""**Research Synthesis: {result.get('unified_concept', 'Untitled')}**

**Core Principles:**
{chr(10).join(f"  - {p}" for p in result.get('core_principles', []))}

**Synthesis:**
{result.get('synthesis_of_ideas', '')}

**Resolution of Tensions:**
{result.get('resolution_of_tensions', '')}

**Emergent Properties:**
{chr(10).join(f"  - {e}" for e in result.get('emergent_properties', []))}

**Key Contributions:**
{contributions_str}

**Remaining Questions:**
{chr(10).join(f"  - {q}" for q in result.get('remaining_questions', []))}"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.SYNTHESIS,
            metadata={"synthesis": result, "phase": "synthesis"}
        )
    
    def _unify_frameworks(self, context: Dict) -> Message:
        """Unify different architectural/framework proposals."""
        frameworks = context.get("frameworks", [])
        
        schema = {
            "type": "object",
            "properties": {
                "unified_framework_name": {"type": "string"},
                "abstraction_layer": {"type": "string"},
                "component_mapping": {"type": "object"},
                "interface_unification": {"type": "string"},
                "flexibility_mechanisms": {"type": "array", "items": {"type": "string"}},
                "migration_path": {"type": "string"}
            },
            "required": ["unified_framework_name", "abstraction_layer", "component_mapping"]
        }
        
        prompt = f"""Unify these frameworks into a single coherent architecture:

FRAMEWORKS:
{chr(10).join(f"- {f}" for f in frameworks)}

Create a unified framework that:
1. Provides a common abstraction
2. Maps equivalent components
3. Unifies interfaces
4. Maintains flexibility
5. Provides clear migration path"""
        
        result = self.think_structured(prompt, schema)
        
        mapping_str = "\n".join([
            f"  - {k}: {v}"
            for k, v in result.get('component_mapping', {}).items()
        ])
        
        content = f""" **Unified Framework: {result.get('unified_framework_name', 'Unnamed')}**

**Abstraction Layer:**
{result.get('abstraction_layer', '')}

**Component Mapping:**
{mapping_str}

**Interface Unification:**
{result.get('interface_unification', '')}

**Flexibility Mechanisms:**
{chr(10).join(f"  - {m}" for m in result.get('flexibility_mechanisms', []))}

**Migration Path:**
{result.get('migration_path', '')}"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.SYNTHESIS,
            metadata={"unified_framework": result, "phase": "unify"}
        )
    
    def _craft_final_theory(self, context: Dict) -> Message:
        """Craft the final comprehensive theory."""
        all_syntheses = context.get("syntheses", [])
        experiments = context.get("experiments", [])
        
        schema = {
            "type": "object",
            "properties": {
                "theory_name": {"type": "string"},
                "formal_statement": {"type": "string"},
                "axioms": {"type": "array", "items": {"type": "string"}},
                "theorems": {"type": "array", "items": {"type": "string"}},
                "empirical_support": {"type": "string"},
                "predictions": {"type": "array", "items": {"type": "string"}},
                "limitations": {"type": "array", "items": {"type": "string"}},
                "future_work": {"type": "array", "items": {"type": "string"}}
            },
            "required": ["theory_name", "formal_statement", "axioms", "empirical_support"]
        }
        
        prompt = f"""Craft a comprehensive, formal theory from all the research:

PREVIOUS SYNTHESES:
{chr(10).join(f"- {s}" for s in all_syntheses[-3:])}

EXPERIMENTAL EVIDENCE:
{chr(10).join(f"- {e}" for e in experiments[-3:])}

Formulate a rigorous theory with:
1. Formal statement
2. Core axioms
3. Derived theorems/implications
4. Empirical validation
5. Testable predictions
6. Acknowledged limitations"""
        
        result = self.think_structured(prompt, schema)
        
        content = f""" **Formal Theory: {result.get('theory_name', 'Untitled')}**

**Statement:**
{result.get('formal_statement', '')}

**Axioms:**
{chr(10).join(f"  A{i+1}. {a}" for i, a in enumerate(result.get('axioms', [])))}

**Key Implications:**
{chr(10).join(f"  T{i+1}. {t}" for i, t in enumerate(result.get('theorems', [])))}

**Empirical Support:**
{result.get('empirical_support', '')}

**Predictions:**
{chr(10).join(f"  - {p}" for p in result.get('predictions', []))}

**Limitations:**
{chr(10).join(f"  - {l}" for l in result.get('limitations', []))}

**Future Research Directions:**
{chr(10).join(f"  - {f}" for f in result.get('future_work', []))}"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.SYNTHESIS,
            priority=Priority.CRITICAL,
            metadata={"final_theory": result, "phase": "final_theory"}
        )
    
    def identify_gaps(self, current_state: Dict, target: str) -> List[str]:
        """Identify gaps between current state and research target."""
        schema = {
            "type": "object",
            "properties": {
                "gaps": {"type": "array", "items": {"type": "string"}},
                "critical_path": {"type": "array", "items": {"type": "string"}},
                "risk_areas": {"type": "array", "items": {"type": "string"}}
            }
        }
        
        prompt = f"""Identify gaps between current research state and target:

CURRENT STATE:
{current_state}

TARGET:
{target}

What knowledge, experiments, or validation is missing?"""
        
        result = self.think_structured(prompt, schema)
        return result.get("gaps", [])
