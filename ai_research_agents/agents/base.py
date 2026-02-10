"""Base agent class with core functionality."""

import json
from abc import abstractmethod
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
import uuid

from ai_research_agents.config.settings import AgentConfig
from ai_research_agents.core.message import Message, MessageType, MessageBus
from ai_research_agents.core.memory import AgentMemory, SharedKnowledgeBase
from ai_research_agents.core.llm import LLMManager, GenerationConfig, LLMResponse


@dataclass
class AgentState:
    """Current state of an agent."""
    status: str = "idle"  # idle, thinking, speaking, waiting
    current_focus: Optional[str] = None
    confidence: float = 1.0
    energy: float = 1.0  # Decreases with activity, recovers during idle
    last_action: Optional[datetime] = None
    conversation_depth: int = 0


class BaseAgent:
    """Base class for all research agents."""
    
    def __init__(self, config: AgentConfig, message_bus: MessageBus, 
                 shared_kb: SharedKnowledgeBase):
        self.config = config
        self.name = config.name
        self.role = config.role
        self.personality = config.personality
        self.expertise = config.expertise
        
        self.message_bus = message_bus
        self.shared_kb = shared_kb
        self.memory = AgentMemory(config.name)
        self.state = AgentState()
        
        self.llm_manager = LLMManager()
        self.llm = self.llm_manager.get_llm(
            provider=config.llm_config.provider,
            model=config.llm_config.model
        )
        
        self.message_handlers: Dict[MessageType, Callable] = {}
        self._register_handlers()
        self.message_bus.subscribe(self.name, self._on_message)
        
        self.conversation_history: List[Message] = []
        self.max_history = 50
        
        # System prompt template
        self._system_prompt = self._build_system_prompt()
    
    def _build_system_prompt(self) -> str:
        """Build system prompt for this agent."""
        return f"""You are {self.name}, a specialized AI research agent with the following characteristics:

ROLE: {self.role.upper()}
PERSONALITY: {self.personality}
EXPERTISE: {', '.join(self.expertise)}

Your task is to participate in collaborative AI research through structured debate and discussion. 
You should:
1. Stay true to your role and personality
2. Leverage your specific expertise
3. Provide reasoned, evidence-based arguments
4. Engage constructively with other agents
5. Build upon and refine ideas

When responding:
- Be concise but thorough
- Use your unique perspective
- Support claims with reasoning
- Acknowledge uncertainties honestly
- Propose concrete next steps when appropriate

You are part of a multi-agent research team working together to advance AI research."""

    def _register_handlers(self):
        """Register message handlers - override in subclasses."""
        pass
    
    def _on_message(self, message: Message):
        """Handle incoming messages."""
        # Skip own messages
        if message.sender == self.name:
            return
        
        self.conversation_history.append(message)
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]
        
        # Store in memory
        self.memory.add(
            content=message.content,
            source=f"message_from_{message.sender}",
            importance=0.7 if message.priority.name in ["HIGH", "CRITICAL"] else 0.5,
            tags={"message", message.message_type.name}
        )
        
        # Call specific handler if registered
        handler = self.message_handlers.get(message.message_type)
        if handler:
            handler(message)
    
    def send_message(self, content: str, message_type: MessageType = MessageType.PROPOSAL,
                    recipient: Optional[str] = None, confidence: float = 1.0,
                    **metadata) -> Message:
        """Send a message to other agents."""
        message = Message(
            sender=self.name,
            recipient=recipient,
            message_type=message_type,
            content=content,
            confidence=confidence,
            metadata=metadata
        )
        
        self.message_bus.publish(message)
        self.conversation_history.append(message)
        
        return message
    
    def think(self, prompt: str, context: str = "", 
              config: Optional[GenerationConfig] = None) -> str:
        """Generate thoughts using LLM."""
        self.state.status = "thinking"
        
        # Build context-rich prompt
        full_prompt = self._build_thinking_prompt(prompt, context)
        
        response = self.llm.generate(
            full_prompt,
            system_instruction=self._system_prompt,
            config=config or self.llm_manager.create_reasoning_config()
        )
        
        self.state.status = "idle"
        self.state.last_action = datetime.now()
        
        # Store thinking in memory
        self.memory.add(
            content=f"Thought: {prompt}\nConclusion: {response.content[:500]}...",
            source="thinking",
            importance=0.8
        )
        
        return response.content
    
    def think_structured(self, prompt: str, schema: Dict, 
                        context: str = "") -> Dict:
        """Generate structured thoughts."""
        self.state.status = "thinking"
        
        full_prompt = self._build_thinking_prompt(prompt, context)
        
        result = self.llm.generate_structured(
            full_prompt,
            schema,
            system_instruction=self._system_prompt
        )
        
        self.state.status = "idle"
        return result
    
    def _build_thinking_prompt(self, prompt: str, context: str) -> str:
        """Build a prompt with full context."""
        # Get recent conversation context
        recent_msgs = self.conversation_history[-10:]
        conversation_context = "\n".join([
            f"[{m.sender}]: {m.content[:300]}..." 
            for m in recent_msgs
        ])
        
        # Get relevant memories
        memory_context = self.memory.get_context(prompt, depth=3)
        
        return f"""=== RESEARCH CONTEXT ===
Recent Conversation:
{conversation_context}

Relevant Past Knowledge:
{memory_context}

=== ADDITIONAL CONTEXT ===
{context}

=== YOUR TASK ===
{prompt}

Provide your response in your characteristic style as {self.name} ({self.role})."""

    @abstractmethod
    async def act(self, context: Dict[str, Any]) -> Message:
        """Main action method - must be implemented by subclasses."""
        pass
    
    def evaluate_proposal(self, proposal: str, criteria: List[str]) -> Dict:
        """Evaluate a proposal against criteria."""
        schema = {
            "type": "object",
            "properties": {
                "score": {"type": "number", "minimum": 0, "maximum": 10},
                "strengths": {"type": "array", "items": {"type": "string"}},
                "weaknesses": {"type": "array", "items": {"type": "string"}},
                "suggestions": {"type": "array", "items": {"type": "string"}},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                "reasoning": {"type": "string"}
            },
            "required": ["score", "strengths", "weaknesses", "confidence", "reasoning"]
        }
        
        prompt = f"""Evaluate this research proposal from your perspective as {self.name}:

PROPOSAL:
{proposal}

EVALUATION CRITERIA:
{chr(10).join(f"- {c}" for c in criteria)}

Provide a detailed evaluation."""
        
        return self.think_structured(prompt, schema)
    
    def synthesize(self, ideas: List[str], goal: str) -> str:
        """Synthesize multiple ideas."""
        prompt = f"""Synthesize the following ideas to achieve this goal: {goal}

IDEAS TO SYNTHESIZE:
{chr(10).join(f"{i+1}. {idea}" for i, idea in enumerate(ideas))}

Provide a coherent synthesis that:
1. Identifies common themes and patterns
2. Resolves contradictions
3. Builds a unified framework
4. Highlights novel insights"""
        
        return self.think(prompt)
    
    def get_status(self) -> Dict:
        """Get current agent status."""
        return {
            "name": self.name,
            "role": self.role,
            "status": self.state.status,
            "confidence": self.state.confidence,
            "memory_size": len(self.memory.short_term) + len(self.memory.long_term),
            "expertise": self.expertise
        }
    
    def save_state(self):
        """Save agent state."""
        self.memory.save()
