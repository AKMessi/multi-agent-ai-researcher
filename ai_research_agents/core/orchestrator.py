"""High-level orchestrator for multi-session research."""

import asyncio
from typing import List, Dict, Optional
from pathlib import Path
import json

from ai_research_agents.core.session import ResearchSession
from ai_research_agents.config.settings import ResearchConfig, ConfigManager


class ResearchOrchestrator:
    """Orchestrates multiple research sessions and manages research programs."""
    
    def __init__(self, output_dir: str = "./research_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.sessions: List[ResearchSession] = []
        self.active_session: Optional[ResearchSession] = None
    
    async def conduct_single_research(self, topic: str, goal: str = "", 
                                     config: Optional[ResearchConfig] = None) -> Dict:
        """Conduct a single research session."""
        if config is None:
            config = ConfigManager.create_default_config(topic)
            config.output_dir = self.output_dir
        
        session = ResearchSession(config)
        self.sessions.append(session)
        self.active_session = session
        
        result = await session.conduct_research(topic, goal)
        return result
    
    async def conduct_research_program(self, topics: List[str], 
                                       program_name: str = "research_program") -> Dict:
        """Conduct a coordinated research program across multiple topics."""
        print(f"\n{'='*70}")
        print(f"[PROGRAM] RESEARCH PROGRAM: {program_name}")
        print(f"[TOPICS] Topics to investigate: {len(topics)}")
        print(f"{'='*70}\n")
        
        results = []
        
        for i, topic in enumerate(topics, 1):
            print(f"\n{'─'*70}")
            print(f"Research {i}/{len(topics)}: {topic}")
            print('─'*70)
            
            result = await self.conduct_single_research(
                topic=topic,
                goal=f"Investigate {topic} as part of {program_name}"
            )
            results.append(result)
            
            # Small delay between sessions
            if i < len(topics):
                await asyncio.sleep(2)
        
        # Generate program-level synthesis
        synthesis = self._synthesize_program_results(results)
        
        # Save program report
        program_file = self.output_dir / f"{program_name}_synthesis.json"
        with open(program_file, 'w') as f:
            json.dump({
                "program_name": program_name,
                "topics": topics,
                "session_results": results,
                "synthesis": synthesis
            }, f, indent=2, default=str)
        
        print(f"\n{'='*70}")
        print(f"[COMPLETE] Research Program Complete!")
        print(f"[OUTPUT] Synthesis saved to: {program_file}")
        print(f"{'='*70}\n")
        
        return {
            "program_name": program_name,
            "sessions": results,
            "synthesis": synthesis
        }
    
    def _synthesize_program_results(self, results: List[Dict]) -> Dict:
        """Synthesize results across multiple research sessions."""
        themes = []
        innovations = []
        
        for r in results:
            debate = r.get("debate_result", {})
            if debate.get("final_conclusion"):
                innovations.append(debate["final_conclusion"].get("content", "")[:200])
        
        return {
            "total_sessions": len(results),
            "successful_sessions": sum(1 for r in results if r.get("debate_result", {}).get("final_conclusion")),
            "key_innovations": innovations,
            "cross_cutting_themes": themes
        }
    
    def list_sessions(self) -> List[Dict]:
        """List all research sessions."""
        return [
            {
                "session_id": s.state.session_id,
                "topic": s.config.research_topic,
                "status": s.state.status,
                "started": s.state.started_at.isoformat()
            }
            for s in self.sessions
        ]
