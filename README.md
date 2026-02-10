# 🚀 Ultimate Multi-Agent AI Research System

The most advanced multi-agent AI research framework ever built. Specialized agents collaborate through structured debate to conduct groundbreaking AI research, generate novel architectures, and produce comprehensive research outputs.

## ✨ Features

- **6 Specialized Research Agents**: Visionary, Architect, Critic, Synthesizer, Experimentalist, Evidence
- **Structured Debate**: Multi-phase research process with convergence detection
- **Web Search Integration**: Real-time evidence gathering from the web
- **Memory & Knowledge Graph**: Persistent agent memory and shared knowledge base
- **Code Generation**: Automatic implementation generation from research designs
- **Comprehensive Reporting**: Markdown, JSON, and LaTeX output formats

## 🏗️ Architecture

```
ai_research_agents/
├── agents/           # Specialized agent implementations
├── core/             # Message bus, memory, LLM integration
├── debate/           # Debate orchestration engine
├── tools/            # Web search and utilities
├── output/           # Report and code generators
└── config/           # Configuration management
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repo-url>
cd ai-research-agents

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY
```

### 2. Run Research

```bash
# Single topic research
python main.py research "Novel transformer architectures for long-context modeling"

# Multi-topic research program
python main.py program "Neural architecture search" "Self-improving AI" "Multi-modal reasoning"

# Interactive mode
python main.py interactive
```

### 3. View Results

Research outputs are saved to `./research_output/`:
- `research_report_*.md` - Full research report
- `summary.md` - Executive summary
- `code/` - Generated implementation code
- `raw_data.json` - Complete research data

## 🤖 Agent Roles

| Agent | Role | Function |
|-------|------|----------|
| **Visionary** | Idea Generation | Proposes breakthrough concepts and paradigm shifts |
| **Architect** | System Design | Designs concrete, implementable architectures |
| **Critic** | Analysis | Identifies flaws, biases, and stress-tests ideas |
| **Synthesizer** | Integration | Combines insights into unified theories |
| **Experimentalist** | Validation | Designs experiments and benchmarks |
| **Evidence** | Research | Gathers external evidence and literature |

## 📝 Example Output

```markdown
# Research Report: Novel Neural Architecture

## Executive Summary
Proposed architecture combines attention mechanisms with...

## Research Process
- Rounds Completed: 8
- Proposals Generated: 6
- Critiques Provided: 12

## Key Conclusion
A hybrid approach using [innovative technique] achieves...

## Implementation
```python
class NovelArchitecture:
    ...
```
```

## ⚙️ Configuration

Create a `research_config.yaml`:

```yaml
project_name: my_research
research_topic: "Transformer alternatives"
max_rounds: 15
consensus_threshold: 0.8

agents:
  - name: Visionary
    role: visionary
    temperature: 0.9
  - name: Critic
    role: critic
    temperature: 0.3
```

## 🔧 Advanced Usage

### Programmatic API

```python
import asyncio
from ai_research_agents import ResearchOrchestrator

async def main():
    orchestrator = ResearchOrchestrator()
    result = await orchestrator.conduct_single_research(
        topic="Your research topic",
        goal="Specific research goal"
    )
    print(result)

asyncio.run(main())
```

### Custom Agents

```python
from ai_research_agents.agents import BaseAgent

class MyAgent(BaseAgent):
    async def act(self, context):
        # Your logic here
        pass
```

## 📊 Research Process

1. **Initialization**: Agents prepare with research context
2. **Exploration**: Evidence gathering and breakthrough ideation
3. **Proposal**: Agents generate novel research proposals
4. **Critique**: Rigorous analysis and stress-testing
5. **Synthesis**: Integration of best ideas
6. **Verification**: Experimental validation design
7. **Convergence**: Final theory formation
8. **Output**: Report and code generation

## 🛠️ Requirements

- Python 3.9+
- Gemini API key (get at makersuite.google.com)
- See `requirements.txt` for dependencies

## 📜 License

MIT License - See LICENSE file

## 🙏 Acknowledgments

Built with:
- Google Gemini
- LangChain patterns
- Multi-agent research literature
- Tree of Thoughts methodology

---

**Go forth and discover!** 🚀🔬
