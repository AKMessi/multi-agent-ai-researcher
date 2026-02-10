"""Architect Agent - Designs concrete system architectures."""

from typing import Dict, Any, Optional
from ai_research_agents.agents.base import BaseAgent
from ai_research_agents.core.message import Message, MessageType
from ai_research_agents.config.settings import AgentConfig


class ArchitectAgent(BaseAgent):
    """Architect agent focused on designing concrete systems and implementations."""
    
    def __init__(self, config: AgentConfig, message_bus, shared_kb):
        super().__init__(config, message_bus, shared_kb)
        self.designs = []
    
    def _register_handlers(self):
        """Register message handlers."""
        self.message_handlers[MessageType.PROPOSAL] = self._on_proposal
    
    def _on_proposal(self, message: Message):
        """Note proposals for potential architectural design."""
        pass
    
    async def act(self, context: Dict[str, Any]) -> Optional[Message]:
        """Design architectures based on proposals."""
        
        if context.get("phase") == "architecture":
            return self._design_architecture(context)
        elif context.get("phase") == "refinement":
            return self._refine_architecture(context)
        elif context.get("phase") == "integration":
            return self._design_integration(context)
        
        return None
    
    def _design_architecture(self, context: Dict) -> Message:
        """Design a concrete architecture from proposals."""
        proposals = context.get("proposals", [])
        requirements = context.get("requirements", [])
        
        schema = {
            "type": "object",
            "properties": {
                "architecture_name": {"type": "string", "description": "Name of the architecture"},
                "overview": {"type": "string", "description": "High-level description of the architecture"},
                "core_components": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "purpose": {"type": "string"},
                            "inputs": {"type": "array", "items": {"type": "string"}},
                            "outputs": {"type": "array", "items": {"type": "string"}},
                            "implementation_notes": {"type": "string"}
                        }
                    }
                },
                "data_flow": {"type": "string", "description": "Description of how data flows through the system"},
                "scalability_considerations": {"type": "string"},
                "technical_requirements": {"type": "array", "items": {"type": "string"}},
                "pseudo_code": {"type": "string", "description": "Python-like pseudo code as a string (not a code block)"}
            },
            "required": ["architecture_name", "overview", "core_components", "data_flow"]
        }
        
        prompt = f"""Design a concrete, implementable architecture based on these research proposals:

PROPOSALS:
{chr(10).join(f"- {p}" for p in proposals[:3])}

REQUIREMENTS:
{chr(10).join(f"- {r}" for r in requirements)}

Create a detailed architecture specification that:
1. Is technically feasible
2. Addresses scalability and efficiency
3. Has clear interfaces between components
4. Can be implemented by skilled engineers

Include pseudo-code for critical components."""
        
        result = self.think_structured(prompt, schema)
        self.designs.append(result)
        
        # Format component details
        components_str = "\n\n".join([
            f"**{c.get('name', 'Unnamed')}**\n"
            f"  Purpose: {c.get('purpose', '')}\n"
            f"  Inputs: {', '.join(c.get('inputs', []))}\n"
            f"  Outputs: {', '.join(c.get('outputs', []))}\n"
            f"  Notes: {c.get('implementation_notes', '')}"
            for c in result.get('core_components', [])
        ])
        
        content = f"""**Architecture: {result.get('architecture_name', 'Unnamed')}**

**Overview:** {result.get('overview', '')}

**Core Components:**
{components_str}

**Data Flow:** {result.get('data_flow', '')}

**Scalability:** {result.get('scalability_considerations', '')}

**Technical Requirements:**
{chr(10).join(f"  - {tr}" for tr in result.get('technical_requirements', []))}

**Key Implementation Sketch:**
```python
{result.get('pseudo_code', '# Pseudo-code not generated')}
```"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.PROPOSAL,
            metadata={"architecture": result, "phase": "architecture"}
        )
    
    def _refine_architecture(self, context: Dict) -> Message:
        """Refine architecture based on feedback."""
        current_design = context.get("current_design", {})
        critiques = context.get("critiques", [])
        
        schema = {
            "type": "object",
            "properties": {
                "refinements": {"type": "array", "items": {"type": "string"}},
                "optimizations": {"type": "array", "items": {"type": "string"}},
                "simplified_components": {"type": "array", "items": {"type": "string"}},
                "performance_improvements": {"type": "string"},
                "updated_pseudo_code": {"type": "string"}
            },
            "required": ["refinements", "optimizations"]
        }
        
        prompt = f"""Refine this architecture based on critiques:

CURRENT DESIGN:
{current_design}

CRITIQUES TO ADDRESS:
{chr(10).join(f"- {c}" for c in critiques)}

Make concrete improvements while maintaining the core vision."""
        
        result = self.think_structured(prompt, schema)
        
        content = f"""**Architecture Refinement**

**Key Refinements:**
{chr(10).join(f"  - {r}" for r in result.get('refinements', []))}

**Optimizations:**
{chr(10).join(f"  - {o}" for o in result.get('optimizations', []))}

**Simplified Components:**
{chr(10).join(f"  - {s}" for s in result.get('simplified_components', []))}

**Performance Gains:** {result.get('performance_improvements', '')}

**Updated Implementation:**
```python
{result.get('updated_pseudo_code', '# Code update pending')}
```"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.SYNTHESIS,
            metadata={"refinement": result, "phase": "refinement"}
        )
    
    def _design_integration(self, context: Dict) -> Message:
        """Design how multiple components integrate."""
        components = context.get("components", [])
        
        schema = {
            "type": "object",
            "properties": {
                "integration_strategy": {"type": "string"},
                "interface_definitions": {"type": "array", "items": {"type": "string"}},
                "coordination_mechanism": {"type": "string"},
                "failure_handling": {"type": "string"},
                "deployment_architecture": {"type": "string"}
            },
            "required": ["integration_strategy", "interface_definitions", "coordination_mechanism"]
        }
        
        prompt = f"""Design the integration strategy for these components:

COMPONENTS:
{chr(10).join(f"- {c}" for c in components)}

Specify:
1. How components communicate
2. Interface contracts
3. Coordination mechanisms
4. Error handling
5. Deployment topology"""
        
        result = self.think_structured(prompt, schema)
        
        content = f""" **Integration Architecture**

**Strategy:** {result.get('integration_strategy', '')}

**Interface Definitions:**
{chr(10).join(f"  - {i}" for i in result.get('interface_definitions', []))}

**Coordination:** {result.get('coordination_mechanism', '')}

**Failure Handling:** {result.get('failure_handling', '')}

                    **Deployment:** {result.get('deployment_architecture', '')}"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.SYNTHESIS,
            metadata={"integration": result, "phase": "integration"}
        )
