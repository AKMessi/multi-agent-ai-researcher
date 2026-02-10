"""Message system for agent communication."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Dict, List, Optional, Any
import uuid
import json


class MessageType(Enum):
    """Types of messages agents can exchange."""
    PROPOSAL = auto()           # New idea or proposal
    CRITIQUE = auto()           # Criticism of a proposal
    SUPPORT = auto()            # Supporting argument
    QUESTION = auto()           # Question for clarification
    EVIDENCE = auto()           # Supporting evidence
    SYNTHESIS = auto()          # Combined insights
    COUNTER = auto()            # Counter-proposal
    VERDICT = auto()            # Final judgment
    META = auto()               # Meta-discussion
    CODE = auto()               # Code snippet
    RESULT = auto()             # Experimental result


class Priority(Enum):
    """Message priority levels."""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4


@dataclass
class Message:
    """A message exchanged between agents."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    sender: str = ""
    recipient: Optional[str] = None  # None = broadcast
    message_type: MessageType = MessageType.PROPOSAL
    content: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    priority: Priority = Priority.NORMAL
    parent_id: Optional[str] = None  # For threaded conversations
    thread_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0  # Sender's confidence in this message
    citations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type.name,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "priority": self.priority.name,
            "parent_id": self.parent_id,
            "thread_id": self.thread_id,
            "metadata": self.metadata,
            "confidence": self.confidence,
            "citations": self.citations
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "Message":
        """Create message from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            sender=data.get("sender", ""),
            recipient=data.get("recipient"),
            message_type=MessageType[data.get("message_type", "PROPOSAL")],
            content=data.get("content", ""),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            priority=Priority[data.get("priority", "NORMAL")],
            parent_id=data.get("parent_id"),
            thread_id=data.get("thread_id"),
            metadata=data.get("metadata", {}),
            confidence=data.get("confidence", 1.0),
            citations=data.get("citations", [])
        )
    
    def reply(self, content: str, sender: str, **kwargs) -> "Message":
        """Create a reply to this message."""
        return Message(
            sender=sender,
            parent_id=self.id,
            thread_id=self.thread_id or self.id,
            content=content,
            **kwargs
        )


class MessageBus:
    """Central message broker for agent communication."""
    
    def __init__(self):
        self.messages: List[Message] = []
        self.subscribers: Dict[str, List[callable]] = {}
        self.threads: Dict[str, List[Message]] = {}
    
    def subscribe(self, agent_name: str, callback: callable):
        """Subscribe an agent to receive messages."""
        if agent_name not in self.subscribers:
            self.subscribers[agent_name] = []
        self.subscribers[agent_name].append(callback)
    
    def publish(self, message: Message) -> None:
        """Publish a message to the bus."""
        self.messages.append(message)
        
        # Track in thread
        thread_id = message.thread_id or message.id
        if thread_id not in self.threads:
            self.threads[thread_id] = []
        self.threads[thread_id].append(message)
        
        # Notify subscribers
        if message.recipient:
            if message.recipient in self.subscribers:
                for callback in self.subscribers[message.recipient]:
                    try:
                        callback(message)
                    except Exception as e:
                        print(f"Error notifying subscriber {message.recipient}: {e}")
        else:
            # Broadcast to all
            for subs in self.subscribers.values():
                for callback in subs:
                    try:
                        callback(message)
                    except Exception as e:
                        pass
    
    def get_thread(self, thread_id: str) -> List[Message]:
        """Get all messages in a thread."""
        return self.threads.get(thread_id, [])
    
    def get_messages_for(self, agent_name: str, message_type: Optional[MessageType] = None) -> List[Message]:
        """Get messages for a specific agent."""
        msgs = [m for m in self.messages if m.recipient == agent_name or m.recipient is None]
        if message_type:
            msgs = [m for m in msgs if m.message_type == message_type]
        return msgs
    
    def get_conversation_history(self, limit: int = 50) -> List[Message]:
        """Get recent conversation history."""
        return self.messages[-limit:]
    
    def clear(self):
        """Clear all messages."""
        self.messages.clear()
        self.threads.clear()
