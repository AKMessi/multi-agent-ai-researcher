#!/usr/bin/env python3
"""
Ultimate Multi-Agent AI Research System
=======================================

Run collaborative AI research with multiple specialized agents.

Usage:
    python main.py research "Your research topic here"
    python main.py program --topics "Topic 1" "Topic 2" "Topic 3"
    python main.py interactive

Environment Variables:
    GEMINI_API_KEY: Required for LLM access
"""

import asyncio
import os
import sys
from typing import List, Optional
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

# Add the package to path
sys.path.insert(0, str(Path(__file__).parent))

from ai_research_agents.core.orchestrator import ResearchOrchestrator
from ai_research_agents.core.session import ResearchSession
from ai_research_agents.config.settings import ConfigManager


app = typer.Typer(help="Ultimate Multi-Agent AI Research System")
console = Console()


def check_api_key():
    """Check if API key is set."""
    if not os.getenv("GEMINI_API_KEY") and not os.getenv("GOOGLE_API_KEY"):
        console.print(Panel(
            "[red bold]Error: GEMINI_API_KEY not set![/red bold]\n\n"
            "Please set your Gemini API key:\n"
            "  export GEMINI_API_KEY='your-key-here'\n\n"
            "Get your key at: https://makersuite.google.com/app/apikey",
            title="API Key Required",
            border_style="red"
        ))
        sys.exit(1)


@app.command()
def research(
    topic: str = typer.Argument(..., help="Research topic"),
    goal: str = typer.Option("", "--goal", "-g", help="Research goal/description"),
    output_dir: str = typer.Option("./research_output", "--output", "-o", help="Output directory"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output")
):
    """Conduct single research session on a topic."""
    check_api_key()
    
    console.print(Panel(
        f"[bold blue]Research Topic:[/bold blue] {topic}\n"
        f"[dim]{goal or 'Exploring new frontiers...'}[/dim]",
        title="🚀 AI Research Session",
        border_style="blue"
    ))
    
    async def run():
        orchestrator = ResearchOrchestrator(output_dir=output_dir)
        result = await orchestrator.conduct_single_research(topic, goal)
        return result
    
    try:
        result = asyncio.run(run())
        
        # Display results
        console.print("\n[green]✅ Research completed successfully![/green]\n")
        
        table = Table(title="Research Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        debate = result.get("debate_result", {})
        table.add_row("Session ID", result.get("session_id", "N/A"))
        table.add_row("Rounds", str(debate.get("rounds_completed", 0)))
        table.add_row("Proposals", str(debate.get("proposals_generated", 0)))
        table.add_row("Critiques", str(debate.get("critiques_provided", 0)))
        table.add_row("Consensus", f"{debate.get('consensus_score', 0):.2f}")
        
        console.print(table)
        
        # Show output locations
        console.print("\n[bold]Generated Files:[/bold]")
        outputs = result.get("outputs", {})
        for key, path in outputs.items():
            console.print(f"  📄 {key}: [dim]{path}[/dim]")
        
        # Show conclusion preview
        conclusion = debate.get("final_conclusion", {})
        if conclusion:
            console.print(Panel(
                conclusion.get("content", "")[:500] + "...",
                title="📝 Key Conclusion (Preview)",
                border_style="green"
            ))
            
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        raise


@app.command()
def program(
    topics: List[str] = typer.Argument(..., help="Research topics to investigate"),
    name: str = typer.Option("research_program", "--name", "-n", help="Program name"),
    output_dir: str = typer.Option("./research_output", "--output", "-o", help="Output directory")
):
    """Conduct a multi-topic research program."""
    check_api_key()
    
    console.print(Panel(
        f"[bold blue]Research Program:[/bold blue] {name}\n"
        f"[dim]Topics: {len(topics)}[/dim]",
        title="🎯 Multi-Topic Research",
        border_style="purple"
    ))
    
    async def run():
        orchestrator = ResearchOrchestrator(output_dir=output_dir)
        result = await orchestrator.conduct_research_program(topics, name)
        return result
    
    try:
        result = asyncio.run(run())
        
        console.print("\n[green]✅ Research program completed![/green]\n")
        
        table = Table(title="Program Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        synthesis = result.get("synthesis", {})
        table.add_row("Total Sessions", str(synthesis.get("total_sessions", 0)))
        table.add_row("Successful", str(synthesis.get("successful_sessions", 0)))
        
        console.print(table)
        
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")
        raise


@app.command()
def interactive():
    """Start interactive research mode."""
    check_api_key()
    
    console.print(Panel(
        "Welcome to Interactive AI Research Mode\n"
        "Type your research topics or 'quit' to exit.",
        title="🤖 Interactive Mode",
        border_style="green"
    ))
    
    orchestrator = ResearchOrchestrator()
    
    while True:
        topic = console.input("\n[bold cyan]Research Topic:[/bold cyan] ")
        
        if topic.lower() in ['quit', 'exit', 'q']:
            break
        
        goal = console.input("[dim]Research Goal (optional):[/dim] ")
        
        async def run():
            return await orchestrator.conduct_single_research(topic, goal)
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("[cyan]Researching...", total=None)
                result = asyncio.run(run())
                progress.remove_task(task)
            
            console.print("[green]✅ Research complete![/green]")
            
            # Show brief summary
            debate = result.get("debate_result", {})
            conclusion = debate.get("final_conclusion", {})
            if conclusion:
                console.print(Panel(
                    conclusion.get("content", "")[:300] + "...",
                    title="Key Finding",
                    border_style="blue"
                ))
                
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


@app.command()
def agents():
    """List available agents and their roles."""
    table = Table(title="Available Research Agents")
    table.add_column("Agent", style="cyan")
    table.add_column("Role", style="green")
    table.add_column("Expertise", style="yellow")
    
    default_agents = ConfigManager.DEFAULT_AGENTS
    for agent in default_agents:
        table.add_row(
            agent["name"],
            agent["role"],
            ", ".join(agent["expertise"][:3]) + "..."
        )
    
    console.print(table)
    
    console.print("\n[dim]Each agent contributes unique capabilities to the research process.[/dim]")


@app.command()
def config(
    api_key: Optional[str] = typer.Option(None, "--set-key", help="Set Gemini API key")
):
    """Manage configuration."""
    if api_key:
        # Would save to config file in real implementation
        console.print("[green]API key would be saved to config file[/green]")
    else:
        # Show current config
        key_status = "[green]✓ Set[/green]" if os.getenv("GEMINI_API_KEY") else "[red]✗ Not Set[/red]"
        console.print(f"GEMINI_API_KEY: {key_status}")


if __name__ == "__main__":
    app()
