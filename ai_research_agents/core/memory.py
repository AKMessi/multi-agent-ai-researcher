"""Memory and knowledge management for agents."""

import json
import pickle
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
import hashlib
import networkx as nx
import numpy as np


@dataclass
class MemoryEntry:
    """A single memory entry."""
    id: str
    content: str
    source: str
    timestamp: datetime
    importance: float = 1.0
    tags: Set[str] = field(default_factory=set)
    related_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[np.ndarray] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "source": self.source,
            "timestamp": self.timestamp.isoformat(),
            "importance": self.importance,
            "tags": list(self.tags),
            "related_ids": self.related_ids,
            "metadata": self.metadata
        }


class KnowledgeGraph:
    """Graph-based knowledge representation."""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.concepts: Dict[str, Dict] = {}
    
    def add_concept(self, concept: str, concept_type: str = "general", properties: Dict = None):
        """Add a concept node to the graph."""
        self.graph.add_node(concept, type=concept_type, **(properties or {}))
        self.concepts[concept] = {
            "type": concept_type,
            "properties": properties or {},
            "added_at": datetime.now().isoformat()
        }
    
    def add_relation(self, from_concept: str, to_concept: str, relation_type: str, strength: float = 1.0):
        """Add a relationship between concepts."""
        self.graph.add_edge(from_concept, to_concept, 
                          relation=relation_type, strength=strength)
    
    def get_related(self, concept: str, depth: int = 1) -> List[Dict]:
        """Get related concepts within a certain depth."""
        if concept not in self.graph:
            return []
        
        related = []
        for target in nx.single_source_shortest_path_length(
            self.graph, concept, cutoff=depth
        ):
            if target != concept:
                edge_data = self.graph.get_edge_data(concept, target) or \
                           self.graph.get_edge_data(target, concept)
                related.append({
                    "concept": target,
                    "distance": nx.shortest_path_length(self.graph, concept, target),
                    "relation": edge_data.get("relation") if edge_data else None
                })
        return related
    
    def find_path(self, start: str, end: str) -> Optional[List[str]]:
        """Find reasoning path between two concepts."""
        try:
            return nx.shortest_path(self.graph, start, end)
        except nx.NetworkXNoPath:
            return None
    
    def export(self, path: Path):
        """Export knowledge graph."""
        data = {
            "nodes": list(self.graph.nodes(data=True)),
            "edges": list(self.graph.edges(data=True)),
            "concepts": self.concepts
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)


class AgentMemory:
    """Memory system for individual agents."""
    
    def __init__(self, agent_name: str, storage_path: Optional[Path] = None):
        self.agent_name = agent_name
        self.storage_path = storage_path or Path(f"./memory/{agent_name}")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.short_term: List[MemoryEntry] = []
        self.long_term: Dict[str, MemoryEntry] = {}
        self.knowledge_graph = KnowledgeGraph()
        self.working_memory: Dict[str, Any] = {}
        
        self.max_short_term = 100
        self.importance_threshold = 0.7
        
        self._load_memory()
    
    def add(self, content: str, source: str = "", importance: float = 1.0, 
            tags: Set[str] = None, **metadata) -> MemoryEntry:
        """Add a memory entry."""
        entry_id = hashlib.md5(f"{content}{datetime.now()}".encode()).hexdigest()[:12]
        
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            source=source,
            timestamp=datetime.now(),
            importance=importance,
            tags=tags or set(),
            metadata=metadata
        )
        
        self.short_term.append(entry)
        
        # Consolidate to long-term if important
        if importance >= self.importance_threshold:
            self._consolidate_to_long_term(entry)
        
        # Trim short-term memory
        if len(self.short_term) > self.max_short_term:
            self._consolidate_oldest()
        
        return entry
    
    def search(self, query: str, tags: Set[str] = None, 
               min_importance: float = 0.0, limit: int = 10) -> List[MemoryEntry]:
        """Search memory entries."""
        results = []
        
        # Search both short and long term
        all_memories = list(self.short_term) + list(self.long_term.values())
        
        for entry in all_memories:
            if entry.importance < min_importance:
                continue
            if tags and not tags.issubset(entry.tags):
                continue
            
            # Simple text matching (could use embeddings in production)
            score = self._calculate_relevance(query, entry)
            if score > 0:
                results.append((score, entry))
        
        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:limit]]
    
    def get_context(self, topic: str, depth: int = 3) -> str:
        """Get relevant context for a topic."""
        memories = self.search(topic, limit=depth * 5)
        
        # Build context string
        context_parts = []
        for mem in memories[:depth]:
            context_parts.append(f"[{mem.source}] {mem.content}")
        
        return "\n".join(context_parts)
    
    def add_to_working_memory(self, key: str, value: Any):
        """Add to working memory."""
        self.working_memory[key] = value
    
    def get_from_working_memory(self, key: str) -> Any:
        """Get from working memory."""
        return self.working_memory.get(key)
    
    def _calculate_relevance(self, query: str, entry: MemoryEntry) -> float:
        """Calculate relevance score."""
        query_words = set(query.lower().split())
        content_words = set(entry.content.lower().split())
        
        intersection = query_words & content_words
        if not intersection:
            return 0.0
        
        return len(intersection) / len(query_words) * entry.importance
    
    def _consolidate_to_long_term(self, entry: MemoryEntry):
        """Move entry to long-term memory."""
        self.long_term[entry.id] = entry
    
    def _consolidate_oldest(self):
        """Move oldest short-term memories to long-term."""
        to_move = self.short_term[:-self.max_short_term]
        self.short_term = self.short_term[-self.max_short_term:]
        
        for entry in to_move:
            if entry.importance >= self.importance_threshold:
                self.long_term[entry.id] = entry
    
    def save(self):
        """Save memory to disk."""
        # Save long-term memory
        memory_file = self.storage_path / "long_term.json"
        with open(memory_file, 'w') as f:
            json.dump(
                {k: v.to_dict() for k, v in self.long_term.items()},
                f,
                indent=2,
                default=str
            )
        
        # Save knowledge graph
        self.knowledge_graph.export(self.storage_path / "knowledge_graph.json")
        
        # Save working memory
        with open(self.storage_path / "working_memory.pkl", 'wb') as f:
            pickle.dump(self.working_memory, f)
    
    def _load_memory(self):
        """Load memory from disk."""
        memory_file = self.storage_path / "long_term.json"
        if memory_file.exists():
            with open(memory_file, 'r') as f:
                data = json.load(f)
                for k, v in data.items():
                    self.long_term[k] = MemoryEntry(
                        id=v["id"],
                        content=v["content"],
                        source=v["source"],
                        timestamp=datetime.fromisoformat(v["timestamp"]),
                        importance=v["importance"],
                        tags=set(v["tags"]),
                        related_ids=v["related_ids"],
                        metadata=v["metadata"]
                    )
        
        working_file = self.storage_path / "working_memory.pkl"
        if working_file.exists():
            with open(working_file, 'rb') as f:
                self.working_memory = pickle.load(f)


class SharedKnowledgeBase:
    """Shared knowledge across all agents."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("./memory/shared")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        self.facts: Dict[str, Dict] = {}
        self.research_papers: List[Dict] = []
        self.code_snippets: Dict[str, str] = {}
        self.experiment_results: List[Dict] = []
        
        self._load()
    
    def add_fact(self, fact: str, source: str, confidence: float = 1.0):
        """Add a verified fact."""
        fact_id = hashlib.md5(fact.encode()).hexdigest()[:12]
        self.facts[fact_id] = {
            "content": fact,
            "source": source,
            "confidence": confidence,
            "added_at": datetime.now().isoformat(),
            "verified_by": []
        }
    
    def add_paper(self, title: str, authors: List[str], abstract: str, 
                  url: str = "", key_findings: List[str] = None):
        """Add research paper reference."""
        self.research_papers.append({
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "url": url,
            "key_findings": key_findings or [],
            "added_at": datetime.now().isoformat()
        })
    
    def add_code(self, name: str, code: str, language: str = "python"):
        """Add code snippet to shared base."""
        self.code_snippets[name] = {
            "code": code,
            "language": language,
            "added_at": datetime.now().isoformat()
        }
    
    def add_experiment_result(self, experiment_name: str, results: Dict, 
                              conclusion: str = ""):
        """Add experiment result."""
        self.experiment_results.append({
            "name": experiment_name,
            "results": results,
            "conclusion": conclusion,
            "timestamp": datetime.now().isoformat()
        })
    
    def search_facts(self, query: str) -> List[Dict]:
        """Search facts."""
        results = []
        for fact_id, fact in self.facts.items():
            if query.lower() in fact["content"].lower():
                results.append(fact)
        return results
    
    def save(self):
        """Save shared knowledge."""
        with open(self.storage_path / "facts.json", 'w') as f:
            json.dump(self.facts, f, indent=2)
        with open(self.storage_path / "papers.json", 'w') as f:
            json.dump(self.research_papers, f, indent=2)
        with open(self.storage_path / "code.json", 'w') as f:
            json.dump(self.code_snippets, f, indent=2)
        with open(self.storage_path / "experiments.json", 'w') as f:
            json.dump(self.experiment_results, f, indent=2, default=str)
    
    def _load(self):
        """Load shared knowledge."""
        files = [
            ("facts.json", "facts"),
            ("papers.json", "research_papers"),
            ("code.json", "code_snippets"),
            ("experiments.json", "experiment_results")
        ]
        
        for filename, attr in files:
            filepath = self.storage_path / filename
            if filepath.exists():
                with open(filepath, 'r') as f:
                    setattr(self, attr, json.load(f))
