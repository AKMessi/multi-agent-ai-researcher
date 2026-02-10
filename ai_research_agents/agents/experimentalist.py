"""Experimentalist Agent - Designs and analyzes experiments."""

from typing import Dict, Any, Optional, List
from ai_research_agents.agents.base import BaseAgent
from ai_research_agents.core.message import Message, MessageType
from ai_research_agents.config.settings import AgentConfig


class ExperimentalistAgent(BaseAgent):
    """Experimentalist agent focused on empirical validation and experiment design."""
    
    def __init__(self, config: AgentConfig, message_bus, shared_kb):
        super().__init__(config, message_bus, shared_kb)
        self.experiments = []
    
    def _register_handlers(self):
        """Register message handlers."""
        self.message_handlers[MessageType.PROPOSAL] = self._consider_experiment
    
    def _consider_experiment(self, message: Message):
        """Consider if proposal needs experimental validation."""
        pass
    
    async def act(self, context: Dict[str, Any]) -> Optional[Message]:
        """Design experiments or analyze results."""
        
        if context.get("phase") == "experiment_design":
            return self._design_experiment(context)
        elif context.get("phase") == "ablation":
            return self._design_ablation(context)
        elif context.get("phase") == "benchmark":
            return self._propose_benchmarks(context)
        elif context.get("phase") == "analysis":
            return self._analyze_results(context)
        
        return None
    
    def _design_experiment(self, context: Dict) -> Message:
        """Design an experiment to validate a hypothesis."""
        hypothesis = context.get("hypothesis", "")
        theory = context.get("theory", "")
        
        schema = {
            "type": "object",
            "properties": {
                "experiment_name": {"type": "string"},
                "objective": {"type": "string"},
                "hypothesis_tested": {"type": "string"},
                "methodology": {"type": "string"},
                "variables": {
                    "type": "object",
                    "properties": {
                        "independent": {"type": "array", "items": {"type": "string"}},
                        "dependent": {"type": "array", "items": {"type": "string"}},
                        "controlled": {"type": "array", "items": {"type": "string"}}
                    }
                },
                "setup_description": {"type": "string"},
                "expected_outcomes": {"type": "array", "items": {"type": "string"}},
                "success_criteria": {"type": "array", "items": {"type": "string"}},
                "statistical_tests": {"type": "array", "items": {"type": "string"}},
                "resources_needed": {"type": "array", "items": {"type": "string"}},
                "duration_estimate": {"type": "string"},
                "code_skeleton": {"type": "string"}
            },
            "required": ["experiment_name", "objective", "methodology", "success_criteria"]
        }
        
        prompt = f"""Design a rigorous experiment to test this hypothesis:

HYPOTHESIS: {hypothesis}

THEORY CONTEXT: {theory}

Design an experiment that:
1. Clearly tests the hypothesis
2. Controls for confounding variables
3. Has measurable outcomes
4. Is statistically sound
5. Is feasible to implement
6. Includes code skeleton for implementation"""
        
        result = self.think_structured(prompt, schema)
        self.experiments.append(result)
        
        vars_data = result.get('variables', {})
        
        content = f"""**Experiment: {result.get('experiment_name', 'Unnamed Experiment')}**

**Objective:** {result.get('objective', 'N/A')}

**Hypothesis:** {result.get('hypothesis_tested', 'N/A')}

**Methodology:**
{result.get('methodology', 'N/A')}

**Variables:**
- Independent: {', '.join(vars_data.get('independent', []))}
- Dependent: {', '.join(vars_data.get('dependent', []))}
- Controlled: {', '.join(vars_data.get('controlled', []))}

**Setup:**
{result.get('setup_description', 'N/A')}

**Expected Outcomes:**
{chr(10).join(f"  - {o}" for o in result.get('expected_outcomes', ['TBD']))}

**Success Criteria:**
{chr(10).join(f"  - {s}" for s in result.get('success_criteria', ['TBD']))}

**Statistical Tests:**
{chr(10).join(f"  - {t}" for t in result.get('statistical_tests', ['TBD']))}

**Resources:** {', '.join(result.get('resources_needed', ['N/A']))}
**Duration:** {result.get('duration_estimate', 'N/A')}

**Implementation Sketch:**
```python
{result.get('code_skeleton', '# Experiment code')}
```"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.PROPOSAL,
            metadata={"experiment": result, "phase": "experiment_design"}
        )
    
    def _design_ablation(self, context: Dict) -> Message:
        """Design ablation studies."""
        architecture = context.get("architecture", "")
        
        schema = {
            "type": "object",
            "properties": {
                "ablation_studies": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "component": {"type": "string"},
                            "removal_method": {"type": "string"},
                            "expected_impact": {"type": "string"},
                            "interpretation": {"type": "string"}
                        }
                    }
                },
                "control_experiments": {"type": "array", "items": {"type": "string"}},
                "measurement_strategy": {"type": "string"}
            }
        }
        
        prompt = f"""Design ablation studies for this architecture:

ARCHITECTURE: {architecture}

Identify which components to ablate and how to interpret results."""
        
        result = self.think_structured(prompt, schema)
        
        ablations_str = "\n\n".join([
            f"**Ablate: {a.get('component', 'Unknown')}**\n"
            f"  Method: {a.get('removal_method', '')}\n"
            f"  Expected Impact: {a.get('expected_impact', '')}\n"
            f"  Interpretation: {a.get('interpretation', '')}"
            for a in result.get('ablation_studies', [])
        ])
        
        content = f"""**Ablation Study Design**

{ablations_str}

**Control Experiments:**
{chr(10).join(f"  - {c}" for c in result.get('control_experiments', []))}

**Measurement Strategy:**
{result.get('measurement_strategy', '')}"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.PROPOSAL,
            metadata={"ablation": result, "phase": "ablation"}
        )
    
    def _propose_benchmarks(self, context: Dict) -> Message:
        """Propose evaluation benchmarks."""
        approach = context.get("approach", "")
        
        schema = {
            "type": "object",
            "properties": {
                "benchmarks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "purpose": {"type": "string"},
                            "metrics": {"type": "array", "items": {"type": "string"}},
                            "datasets": {"type": "array", "items": {"type": "string"}},
                            "baselines": {"type": "array", "items": {"type": "string"}}
                        }
                    }
                },
                "evaluation_protocol": {"type": "string"},
                "comparison_metrics": {"type": "array", "items": {"type": "string"}}
            }
        }
        
        prompt = f"""Design comprehensive benchmarks for evaluating this approach:

APPROACH: {approach}

Include diverse evaluation scenarios and appropriate metrics."""
        
        result = self.think_structured(prompt, schema)
        
        benchmarks_str = "\n\n".join([
            f"**{b.get('name', 'Unnamed')}**\n"
            f"  Purpose: {b.get('purpose', '')}\n"
            f"  Metrics: {', '.join(b.get('metrics', []))}\n"
            f"  Datasets: {', '.join(b.get('datasets', []))}\n"
            f"  Baselines: {', '.join(b.get('baselines', []))}"
            for b in result.get('benchmarks', [])
        ])
        
        content = f"""**Benchmark Suite**

{benchmarks_str}

**Evaluation Protocol:**
{result.get('evaluation_protocol', '')}

**Key Comparison Metrics:**
{chr(10).join(f"  - {m}" for m in result.get('comparison_metrics', []))}"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.PROPOSAL,
            metadata={"benchmarks": result, "phase": "benchmark"}
        )
    
    def _analyze_results(self, context: Dict) -> Message:
        """Analyze experimental results."""
        results = context.get("results", {})
        
        schema = {
            "type": "object",
            "properties": {
                "summary": {"type": "string"},
                "key_findings": {"type": "array", "items": {"type": "string"}},
                "statistical_significance": {"type": "string"},
                "hypothesis_validation": {"type": "string"},
                "unexpected_observations": {"type": "array", "items": {"type": "string"}},
                "limitations": {"type": "array", "items": {"type": "string"}},
                "recommendations": {"type": "array", "items": {"type": "string"}}
            }
        }
        
        prompt = f"""Analyze these experimental results:

RESULTS:
{results}

Provide statistical interpretation and conclusions."""
        
        result = self.think_structured(prompt, schema)
        
        content = f"""**Experimental Analysis**

**Summary:**
{result.get('summary', '')}

**Key Findings:**
{chr(10).join(f"  - {f}" for f in result.get('key_findings', []))}

**Statistical Significance:**
{result.get('statistical_significance', '')}

**Hypothesis Validation:**
{result.get('hypothesis_validation', '')}

**Unexpected Observations:**
{chr(10).join(f"  - {o}" for o in result.get('unexpected_observations', []))}

**Limitations:**
{chr(10).join(f"  - {l}" for l in result.get('limitations', []))}

**Recommendations:**
{chr(10).join(f"  - {r}" for r in result.get('recommendations', []))}"""
        
        return self.send_message(
            content=content,
            message_type=MessageType.RESULT,
            metadata={"analysis": result, "phase": "analysis"}
        )
