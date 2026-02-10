"""LLM integration for various providers."""

import os
import json
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Iterator
from dataclasses import dataclass
import asyncio

import google.generativeai as genai
from tenacity import retry, stop_after_attempt, wait_exponential


@dataclass
class GenerationConfig:
    """Configuration for text generation."""
    temperature: float = 0.7
    max_output_tokens: int = 8192
    top_p: float = 0.95
    top_k: int = 40
    response_mime_type: str = "text/plain"


@dataclass
class LLMResponse:
    """Response from LLM."""
    content: str
    usage: Dict[str, int]
    finish_reason: str
    safety_ratings: List[Dict] = None
    metadata: Dict[str, Any] = None


class BaseLLM(ABC):
    """Base class for LLM implementations."""
    
    @abstractmethod
    def generate(self, prompt: str, system_instruction: str = None, 
                 config: GenerationConfig = None) -> LLMResponse:
        pass
    
    @abstractmethod
    async def generate_async(self, prompt: str, system_instruction: str = None,
                            config: GenerationConfig = None) -> LLMResponse:
        pass
    
    @abstractmethod
    def generate_stream(self, prompt: str, system_instruction: str = None,
                       config: GenerationConfig = None) -> Iterator[str]:
        pass


class GeminiLLM(BaseLLM):
    """Google Gemini LLM implementation."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-3-flash-preview"):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key required. Set GEMINI_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(model)
        
        # Safety settings - balanced approach for research
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_ONLY_HIGH"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"
            }
        ]
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def generate(self, prompt: str, system_instruction: str = None,
                 config: GenerationConfig = None) -> LLMResponse:
        """Generate text synchronously."""
        config = config or GenerationConfig()
        
        generation_config = genai.GenerationConfig(
            temperature=config.temperature,
            max_output_tokens=config.max_output_tokens,
            top_p=config.top_p,
            top_k=config.top_k,
            response_mime_type=config.response_mime_type
        )
        
        if system_instruction:
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_instruction
            )
        else:
            model = self.model
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=self.safety_settings
        )
        
        return self._parse_response(response)
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_async(self, prompt: str, system_instruction: str = None,
                            config: GenerationConfig = None) -> LLMResponse:
        """Generate text asynchronously."""
        config = config or GenerationConfig()
        
        generation_config = genai.GenerationConfig(
            temperature=config.temperature,
            max_output_tokens=config.max_output_tokens,
            top_p=config.top_p,
            top_k=config.top_k
        )
        
        if system_instruction:
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_instruction
            )
        else:
            model = self.model
        
        response = await model.generate_content_async(
            prompt,
            generation_config=generation_config,
            safety_settings=self.safety_settings
        )
        
        return self._parse_response(response)
    
    def generate_stream(self, prompt: str, system_instruction: str = None,
                       config: GenerationConfig = None) -> Iterator[str]:
        """Generate text with streaming."""
        config = config or GenerationConfig()
        
        generation_config = genai.GenerationConfig(
            temperature=config.temperature,
            max_output_tokens=config.max_output_tokens,
            top_p=config.top_p,
            top_k=config.top_k
        )
        
        if system_instruction:
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_instruction
            )
        else:
            model = self.model
        
        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            safety_settings=self.safety_settings,
            stream=True
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
    
    def generate_structured(self, prompt: str, schema: Dict, 
                           system_instruction: str = None) -> Dict:
        """Generate structured JSON output."""
        # Use higher token limit for structured generation
        config = GenerationConfig(
            response_mime_type="application/json",
            max_output_tokens=16384,  # Double the default for structured output
            temperature=0.3  # Lower temperature for more consistent JSON
        )
        
        # Add schema to prompt
        full_prompt = f"""{prompt}

CRITICAL: You must respond with ONLY valid JSON matching this schema. Do not use markdown formatting, do not wrap in code blocks, do not add any explanatory text before or after the JSON.

Schema:
{json.dumps(schema, indent=2)}

Your response must be pure JSON that can be parsed directly. Start with '{{' and end with '}}'."""
        
        response = self.generate(full_prompt, system_instruction, config)
        
        content = response.content.strip()
        
        # Try direct JSON parsing first
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # Try to extract JSON from markdown code blocks
        import re
        
        # Look for JSON in code blocks
        patterns = [
            r'```json\s*(.*?)\s*```',  # ```json ... ```
            r'```\s*(\{.*\})\s*```',   # ``` { ... } ```
            r'```\s*(\[.*\])\s*```',   # ``` [ ... ] ```
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1).strip())
                except json.JSONDecodeError:
                    continue
        
        # Try to find JSON-like content (objects or arrays)
        json_patterns = [
            r'(\{.*\})',  # { ... }
            r'(\[.*\])',   # [ ... ]
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, content, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1).strip())
                except json.JSONDecodeError:
                    continue
        
        # Try to fix incomplete JSON (truncated responses)
        # Look for the longest valid JSON prefix
        fixed_result = self._try_fix_incomplete_json(content, schema)
        if fixed_result:
            return fixed_result
        
        # If all else fails, return a basic structure with the raw content
        print(f"Warning: Could not parse JSON, returning fallback. Content preview: {content[:200]}...")
        return self._create_fallback_response(schema, content)
    
    def _try_fix_incomplete_json(self, content: str, schema: Dict) -> Optional[Dict]:
        """Try to fix and extract partial/incomplete JSON."""
        import re
        
        # Try to find the start of a JSON object
        obj_start = content.find('{')
        if obj_start == -1:
            return None
        
        # Try progressively smaller chunks from the end
        for end_pos in range(len(content), obj_start + 10, -50):  # Step back by 50 chars
            try:
                chunk = content[obj_start:end_pos]
                # Try to close open structures
                chunk = self._close_json_structures(chunk)
                result = json.loads(chunk)
                print(f"Warning: Parsed incomplete JSON by fixing structure")
                return result
            except json.JSONDecodeError:
                continue
        
        return None
    
    def _close_json_structures(self, json_str: str) -> str:
        """Attempt to close unclosed JSON structures."""
        # Count opening and closing braces/brackets
        braces = json_str.count('{') - json_str.count('}')
        brackets = json_str.count('[') - json_str.count(']')
        quotes = json_str.count('"') % 2
        
        # Close strings first
        result = json_str
        if quotes:
            result += '"'
        
        # Close braces and brackets
        result += '}' * braces
        result += ']' * brackets
        
        return result
    
    def _create_fallback_response(self, schema: Dict, raw_content: str) -> Dict:
        """Create a minimal valid response from schema when parsing fails."""
        result = {}
        
        # Try to extract any field values we can find
        import re
        for field in schema.get('properties', {}).keys():
            # Look for "field": "value" or "field": [ ... ] or "field": { ... }
            pattern = rf'"{field}"\s*:\s*("[^"]*"|\[[^\]]*\]|\{{[^\}}]*\}}|true|false|null|\d+)'
            match = re.search(pattern, raw_content, re.IGNORECASE)
            if match:
                try:
                    value = json.loads(match.group(1))
                    result[field] = value
                except:
                    # If we can't parse it, use as string
                    result[field] = match.group(1).strip('"')
        
        # Fill in ALL missing fields (required AND optional) with defaults
        for field, prop_def in schema.get('properties', {}).items():
            if field not in result:
                prop_type = prop_def.get('type', 'string')
                
                if prop_type == 'array':
                    result[field] = []
                elif prop_type == 'object':
                    result[field] = {}
                elif prop_type == 'boolean':
                    result[field] = False
                elif prop_type == 'number':
                    result[field] = 0
                elif prop_type == 'integer':
                    result[field] = 0
                else:
                    result[field] = f"[Could not extract {field} from response]"
        
        return result if result else {"raw_content": raw_content[:500]}
    
    def _parse_response(self, response) -> LLMResponse:
        """Parse Gemini response."""
        usage = {}
        if hasattr(response, 'usage_metadata'):
            usage = {
                "prompt_tokens": response.usage_metadata.prompt_token_count,
                "completion_tokens": response.usage_metadata.candidates_token_count,
                "total_tokens": response.usage_metadata.total_token_count
            }
        
        safety_ratings = []
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'safety_ratings'):
                safety_ratings = [
                    {"category": sr.category.name, "probability": sr.probability.name}
                    for sr in candidate.safety_ratings
                ]
        
        finish_reason = "STOP"
        if hasattr(response, 'candidates') and response.candidates:
            finish_reason = response.candidates[0].finish_reason.name
        
        return LLMResponse(
            content=response.text,
            usage=usage,
            finish_reason=finish_reason,
            safety_ratings=safety_ratings
        )


class LLMManager:
    """Manages LLM instances and routing."""
    
    def __init__(self):
        self.instances: Dict[str, BaseLLM] = {}
        self.default_model = "gemini"
    
    def get_llm(self, provider: str = "gemini", **kwargs) -> BaseLLM:
        """Get or create LLM instance."""
        cache_key = f"{provider}:{kwargs.get('model', 'default')}"
        
        if cache_key not in self.instances:
            if provider == "gemini":
                self.instances[cache_key] = GeminiLLM(**kwargs)
            else:
                raise ValueError(f"Unknown provider: {provider}")
        
        return self.instances[cache_key]
    
    def create_reasoning_config(self) -> GenerationConfig:
        """Create config optimized for reasoning."""
        return GenerationConfig(
            temperature=0.3,  # Lower for more focused reasoning
            max_output_tokens=16384,  # Higher for detailed analysis
            top_p=0.95,
            top_k=40
        )
    
    def create_creative_config(self) -> GenerationConfig:
        """Create config optimized for creative generation."""
        return GenerationConfig(
            temperature=0.9,  # Higher for creativity
            max_output_tokens=8192,
            top_p=0.95,
            top_k=60
        )
