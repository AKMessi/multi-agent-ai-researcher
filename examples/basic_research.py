"""
Basic Research Example
======================

Demonstrates how to use the multi-agent research system programmatically.
"""

import asyncio
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_research_agents.core.orchestrator import ResearchOrchestrator
from ai_research_agents.config.settings import ConfigManager, ResearchConfig


async def basic_research():
    """Run a basic research session."""
    
    print("=" * 70)
    print("BASIC RESEARCH EXAMPLE")
    print("=" * 70)
    
    # Create orchestrator
    orchestrator = ResearchOrchestrator(output_dir="./example_output")
    
    # Conduct research
    result = await orchestrator.conduct_single_research(
        topic="Self-improving neural network architectures",
        goal="Explore architectures that can modify their own structure during training"
    )
    
    print("\n" + "=" * 70)
    print("RESEARCH COMPLETE")
    print("=" * 70)
    
    # Print summary
    debate = result.get("debate_result", {})
    print(f"\nTopic: {result.get('topic')}")
    print(f"Rounds: {debate.get('rounds_completed')}")
    print(f"Proposals: {debate.get('proposals_generated')}")
    print(f"Consensus: {debate.get('consensus_score', 0):.2f}")
    
    print(f"\nOutputs saved to: {result.get('session_dir')}")
    
    return result


async def custom_config_research():
    """Research with custom configuration."""
    
    print("\n" + "=" * 70)
    print("CUSTOM CONFIG RESEARCH")
    print("=" * 70)
    
    # Create custom config
    config = ConfigManager.create_default_config("Multi-modal reasoning")
    config.debate_config.max_rounds = 5  # Shorter debate
    config.output_dir = Path("./example_output/custom")
    
    # Create orchestrator with config
    orchestrator = ResearchOrchestrator()
    
    result = await orchestrator.conduct_single_research(
        topic="Multi-modal reasoning with limited data",
        goal="Design approaches for multi-modal learning when training data is scarce",
        config=config
    )
    
    return result


async def main():
    """Run examples."""
    
    # Check for API key
    import os
    if not os.getenv("GEMINI_API_KEY"):
        print("WARNING: GEMINI_API_KEY not set!")
        print("Set it with: export GEMINI_API_KEY='your-key'")
        return
    
    # Run basic research
    try:
        await basic_research()
    except Exception as e:
        print(f"\nError: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
