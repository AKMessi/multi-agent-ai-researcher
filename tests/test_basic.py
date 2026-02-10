"""Basic tests."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_research_agents.core.message import MessageBus, Message, MessageType
from ai_research_agents.core.memory import AgentMemory, SharedKnowledgeBase


def test_message_bus():
    """Test message bus."""
    bus = MessageBus()
    received = []
    
    def handler(msg):
        received.append(msg)
    
    bus.subscribe("test", handler)
    
    msg = Message(
        sender="a",
        recipient="test",
        content="hello"
    )
    bus.publish(msg)
    
    assert len(received) == 1
    print("✓ Message bus test passed")


def test_memory():
    """Test agent memory."""
    memory = AgentMemory("test", storage_path=Path("./test_mem"))
    memory.add("test content", importance=0.8)
    
    results = memory.search("test")
    assert len(results) > 0
    print("✓ Memory test passed")


if __name__ == "__main__":
    test_message_bus()
    test_memory()
    print("\nAll tests passed!")
