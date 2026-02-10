"""Critic Agent - Rigorously evaluates proposals and identifies flaws."""

from typing import Dict, Any, Optional, List
from ai_research_agents.agents.base import BaseAgent
from ai_research_agents.core.message import Message, MessageType
from ai_research_agents.config.settings import AgentConfig


class CriticAgent(BaseAgent):
    """Critic agent focused on identifying flaws, biases, and limitations."""
    
    def __init__(self, config: AgentConfig, message_bus, shared_kb):
        super().__init__(config, message_bus, shared_kb)
        self.critiques_given = []
    
    def _register_handlers(self):
        """Register message handlers."""
        self.message_handlers[MessageType.PROPOSAL] = self._critique_proposal
        self.message_handlers[MessageType.SYNTHESIS] = self._critique_synthesis
    
    def _critique_proposal(self, message: Message):
        """Auto-critique new proposals."""
        pass  # Handled in act()
    
    def _critique_synthesis(self, message: Message):
        """Critique syntheses."""
        pass
    
    async def act(self, context: Dict[str, Any]) -> Optional[Message]:
        """Critique current proposals or ideas."""
        
        if context.get("phase") == "critique":
            return self._detailed_critique(context)
        elif context.get("phase") == "stress_test":
            return self._stress_test(context)
        elif context.get("phase") == "bias_check":
            return self._check_biases(context)
        
        return None
    
    def _detailed_critique(self, context: Dict) -> Message:
        """Provide detailed critique of proposals."""
        target = context.get("target_proposal", "")
        proposal_author = context.get("author", "unknown")
        
        schema = {
            "type": "object",
            "properties": {
                "overall_assessment": {"type": "string"},
                "logical_flaws": {"type": "array", "items": {"type": "string"}},
                "unstated_assumptions": {"type": "array", "items": {"type": "string"}},
                "implementation_challenges": {"type": "array", "items": {"type": "string"}},
                "missing_considerations": {"type": "array", "items": {"type": "string"}},
                "risk_factors": {"type": "array", "items": {"type": "string"}},
                "constructive_suggestions": {"type": "array", "items": {"type": "string"}},
                "severity_score": {"type": "number", "minimum": 0, "maximum": 10}
            },
            "required": ["overall_assessment", "logical_flaws", "constructive_suggestions", "severity_score"]
        }
        
        prompt = f"""Provide a rigorous critique of this research proposal:

PROPOSAL:
{target}

Be thorough and honest. Consider:
1. Logical consistency and validity
2. Hidden assumptions
3. Implementation feasibility
4. Edge cases and failure modes
5. Comparison to existing approaches
6. Resource requirements
7. Ethical implications

Be constructive - identify problems but also suggest fixes."""
        
        result = self.think_structured(prompt, schema)
        self.critiques_given.append(result)
        
        severity_score = result.get('severity_score', 0)
        severity_label = "[HIGH]" if severity_score > 7 else "[MEDIUM]" if severity_score > 4 else "[LOW]"
        
        content = f"""{severity_label} **Critical Analysis**

**Overall Assessment:** {result.get('overall_assessment', '')}

**Logical Flaws Identified:**
{chr(10).join(f"  - {flaw}" for flaw in result.get('logical_flaws', []))}

**Unstated Assumptions:**
{chr(10).join(f"  - {a}" for a in result.get('unstated_assumptions', []))}

**Implementation Challenges:**
{chr(10).join(f"  - {c}" for c in result.get('implementation_challenges', []))}

**Missing Considerations:**
{chr(10).join(f"  - {m}" for m in result.get('missing_considerations', []))}

**Risk Factors:**
{chr(10).join(f"  - {r}" for r in result.get('risk_factors', []))}

**Constructive Suggestions:**
{chr(10).join(f"  - {s}" for s in result.get('constructive_suggestions', []))}

**Severity Score:** {severity_score}/10"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.CRITIQUE,
            recipient=proposal_author if proposal_author != "unknown" else None,
            metadata={"critique": result, "phase": "critique", "target": proposal_author}
        )
    
    def _stress_test(self, context: Dict) -> Message:
        """Stress test an idea under extreme conditions."""
        idea = context.get("idea", "")
        
        schema = {
            "type": "object",
            "properties": {
                "boundary_conditions_tested": {"type": "array", "items": {"type": "string"}},
                "failure_modes": {"type": "array", "items": {"type": "string"}},
                "adversarial_scenarios": {"type": "array", "items": {"type": "string"}},
                "scalability_limits": {"type": "string"},
                "robustness_assessment": {"type": "string"},
                "worst_case_analysis": {"type": "string"}
            },
            "required": ["failure_modes", "adversarial_scenarios", "robustness_assessment"]
        }
        
        prompt = f"""Stress test this idea under extreme conditions:

IDEA: {idea}

Test:
1. Boundary conditions and edge cases
2. Adversarial attacks or misuse
3. Scale limits (too small, too large)
4. Resource exhaustion scenarios
5. Cascading failure modes
6. Worst-case performance

How does it fail? When does it fail? Can it recover?"""
        
        result = self.think_structured(prompt, schema)
        
        content = f"""**Stress Test Results**

**Boundary Conditions Tested:**
{chr(10).join(f"  - {b}" for b in result.get('boundary_conditions_tested', []))}

**Failure Modes:**
{chr(10).join(f"  - {f}" for f in result.get('failure_modes', []))}

**Adversarial Scenarios:**
{chr(10).join(f"  - {a}" for a in result.get('adversarial_scenarios', []))}

**Scalability Limits:** {result.get('scalability_limits', '')}

**Robustness Assessment:** {result.get('robustness_assessment', '')}

**Worst-Case Analysis:** {result.get('worst_case_analysis', '')}"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.CRITIQUE,
            metadata={"stress_test": result, "phase": "stress_test"}
        )
    
    def _check_biases(self, context: Dict) -> Message:
        """Check for cognitive biases in research."""
        research_approach = context.get("approach", "")
        
        schema = {
            "type": "object",
            "properties": {
                "biases_detected": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "bias_type": {"type": "string"},
                            "manifestation": {"type": "string"},
                            "impact": {"type": "string"},
                            "mitigation": {"type": "string"}
                        }
                    }
                },
                "blind_spots": {"type": "array", "items": {"type": "string"}},
                "alternative_perspectives": {"type": "array", "items": {"type": "string"}},
                "recommendation": {"type": "string"}
            },
            "required": ["biases_detected", "blind_spots", "recommendation"]
        }
        
        prompt = f"""Analyze this research approach for cognitive biases and blind spots:

APPROACH: {research_approach}

Check for:
- Confirmation bias
- Availability bias
- Anchoring bias
- Groupthink
- Not-invented-here syndrome
- Overconfidence
- Sunk cost fallacy
- Novelty bias

Suggest alternative perspectives and mitigations."""
        
        result = self.think_structured(prompt, schema)
        
        biases_str = "\n\n".join([
            f"**{b.get('bias_type', 'Unknown')}**\n"
            f"  Manifestation: {b.get('manifestation', '')}\n"
            f"  Impact: {b.get('impact', '')}\n"
            f"  Mitigation: {b.get('mitigation', '')}"
            for b in result.get('biases_detected', [])
        ])
        
        content = f"""**Bias & Blind Spot Analysis**

**Biases Detected:**
{biases_str}

**Blind Spots:**
{chr(10).join(f"  - {b}" for b in result.get('blind_spots', []))}

**Alternative Perspectives to Consider:**
{chr(10).join(f"  - {p}" for p in result.get('alternative_perspectives', []))}

**Recommendation:** {result.get('recommendation', '')}"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.CRITIQUE,
            metadata={"bias_check": result, "phase": "bias_check"}
        )
    
    def evaluate_convergence(self, proposals: List[Dict]) -> Dict:
        """Evaluate if proposals are converging to a solution."""
        schema = {
            "type": "object",
            "properties": {
                "convergence_score": {"type": "number"},
                "common_elements": {"type": "array", "items": {"type": "string"}},
                "remaining_disagreements": {"type": "array", "items": {"type": "string"}},
                "readiness_for_synthesis": {"type": "boolean"}
            }
        }
        
        prompt = f"""Evaluate if these research proposals are converging:

PROPOSALS:
{chr(10).join(f"- {p}" for p in proposals)}

Assess convergence and identify what's blocking final synthesis."""
        
        return self.think_structured(prompt, schema)
