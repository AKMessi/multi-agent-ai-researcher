"""Generate research reports."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import json


class ReportGenerator:
    """Generate comprehensive research reports."""
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_full_report(self, debate_result: Dict, analysis: Dict, topic: str) -> Path:
        """Generate a full research report."""
        report_path = self.output_dir / f"research_report_{datetime.now():%Y%m%d_%H%M%S}.md"
        
        content = self._build_report_content(debate_result, analysis, topic)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return report_path
    
    def generate_summary(self, debate_result: Dict, output_path: Path) -> Path:
        """Generate a summary report."""
        conclusion = debate_result.get("final_conclusion", {})
        
        content = f"""# Research Summary

## Topic
{debate_result.get('topic', 'Unknown')}

## Status
{debate_result.get('status', 'Unknown')}

## Rounds Completed
{debate_result.get('rounds_completed', 0)}

## Key Conclusion
{conclusion.get('content', 'No conclusion reached')[:1000] if conclusion else 'No conclusion reached'}

## Proposals Generated
{debate_result.get('proposals_generated', 0)}

## Critiques Provided
{debate_result.get('critiques_provided', 0)}

## Consensus Score
{debate_result.get('consensus_score', 0):.2f}

---
*Generated on {datetime.now():%Y-%m-%d %H:%M:%S}*
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return output_path
    
    def _build_report_content(self, debate_result: Dict, analysis: Dict, topic: str) -> str:
        """Build the full report content."""
        sections = []
        
        # Title
        sections.append(f"# Research Report: {topic}")
        sections.append(f"\n*Generated: {datetime.now():%Y-%m-%d %H:%M:%S}*\n")
        
        # Executive Summary
        sections.append("## Executive Summary\n")
        conclusion = debate_result.get("final_conclusion", {})
        if conclusion:
            sections.append(conclusion.get("content", "No conclusion reached"))
        sections.append("")
        
        # Research Process
        sections.append("## Research Process\n")
        sections.append(f"- **Topic**: {debate_result.get('topic', 'N/A')}")
        sections.append(f"- **Goal**: {debate_result.get('research_goal', 'N/A')}")
        sections.append(f"- **Rounds Completed**: {debate_result.get('rounds_completed', 0)}")
        sections.append(f"- **Phases**: {', '.join(debate_result.get('phases_completed', []))}")
        sections.append("")
        
        # Proposals
        sections.append("## Research Proposals\n")
        for i, proposal in enumerate(debate_result.get("all_proposals", []), 1):
            sections.append(f"### Proposal {i}")
            sections.append(f"**Author**: {proposal.get('author', 'Unknown')}")
            sections.append(f"\n{proposal.get('content', '')[:2000]}\n")
        
        # Critiques
        sections.append("## Critical Analysis\n")
        for i, critique in enumerate(debate_result.get("all_critiques", [])[:5], 1):
            sections.append(f"### Critique {i}")
            sections.append(f"**Author**: {critique.get('author', 'Unknown')}")
            sections.append(f"\n{critique.get('content', '')[:1500]}\n")
        
        # Syntheses
        sections.append("## Synthesis\n")
        for i, synthesis in enumerate(debate_result.get("all_syntheses", []), 1):
            sections.append(f"### Synthesis {i}")
            sections.append(f"**Author**: {synthesis.get('author', 'Unknown')}")
            sections.append(f"\n{synthesis.get('content', '')[:2000]}\n")
        
        # Analysis
        sections.append("## Deep Analysis\n")
        
        gaps = analysis.get("research_gaps", [])
        if gaps:
            sections.append("### Identified Research Gaps")
            for gap in gaps:
                sections.append(f"- {gap}")
            sections.append("")
        
        implications = analysis.get("implications", [])
        if implications:
            sections.append("### Research Implications")
            for imp in implications:
                sections.append(f"- {imp}")
            sections.append("")
        
        confidence = analysis.get("confidence_assessment", {})
        if confidence:
            sections.append("### Confidence Assessment")
            sections.append(f"- Consensus Score: {confidence.get('consensus_score', 0):.2f}")
            sections.append(f"- Confidence Level: {confidence.get('confidence_level', 'unknown')}")
            sections.append("")
        
        novelty = analysis.get("novelty_assessment", {})
        if novelty:
            sections.append("### Novelty Assessment")
            sections.append(f"- Unique Proposals: {novelty.get('unique_proposals', 0)}")
            sections.append(f"- Exploration Breadth: {novelty.get('exploration_breadth', 0)}")
            sections.append(f"- Novelty Score: {novelty.get('novelty_score', 0):.2f}")
            sections.append("")
        
        # Conclusion
        sections.append("## Conclusion\n")
        if conclusion:
            sections.append(conclusion.get("content", "No final conclusion"))
        else:
            sections.append("The research did not reach a definitive conclusion. Further investigation recommended.")
        
        return "\n".join(sections)
    
    def generate_latex_report(self, debate_result: Dict, topic: str) -> Path:
        """Generate a LaTeX-formatted research report."""
        # Simplified LaTeX generation
        latex_path = self.output_dir / f"research_report_{datetime.now():%Y%m%d_%H%M%S}.tex"
        
        latex_content = f"""\\documentclass{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{hyperref}}
\\title{{Research Report: {topic.replace('&', '\\&')}}}
\\author{{Multi-Agent AI Research System}}
\\date{{{datetime.now():%Y-%m-%d}}}

\\begin{{document}}

\\maketitle

\\begin{{abstract}}
This report presents the findings of a multi-agent collaborative research effort on {topic}.
The research involved structured debate between specialized AI agents to explore novel approaches
and synthesize comprehensive insights.
\\end{{abstract}}

\\section{{Introduction}}
Research topic: {topic}

\\section{{Methodology}}
Multi-agent structured debate with specialized roles including Visionary, Architect, Critic,
Synthesizer, Experimentalist, and Evidence agents.

\\section{{Results}}
Number of proposals generated: {debate_result.get('proposals_generated', 0)}
Number of critiques provided: {debate_result.get('critiques_provided', 0)}
Consensus score: {debate_result.get('consensus_score', 0):.2f}

\\section{{Conclusion}}
TODO: Add conclusion

\\end{{document}}
"""
        
        with open(latex_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        return latex_path
