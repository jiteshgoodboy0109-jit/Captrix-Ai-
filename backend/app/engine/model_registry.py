"""
Model Registry Module
Configurable registry tracking available AI candidate models, provider metadata,
capabilities (vision, long context, structured output, table reasoning), and status.
"""

from typing import Dict, List, Any, Optional

MODEL_REGISTRY: List[Dict[str, Any]] = [
    {
        "id": "gemini-3.6-flash-high",
        "provider": "Google DeepMind",
        "model_name": "Gemini 3.6 Flash (High)",
        "version": "3.6.0",
        "capabilities": ["vision_support", "long_context", "structured_output", "table_reasoning"],
        "context_window": 1000000,
        "vision_support": True,
        "structured_output_support": True,
        "tool_support": True,
        "cost_per_1k_tokens": 0.00015,
        "latency_ms": 450,
        "status": "APPROVED",
        "enabled": True
    },
    {
        "id": "gemini-1.5-pro",
        "provider": "Google DeepMind",
        "model_name": "Gemini 1.5 Pro",
        "version": "1.5.0",
        "capabilities": ["vision_support", "long_context", "structured_output", "table_reasoning"],
        "context_window": 2000000,
        "vision_support": True,
        "structured_output_support": True,
        "tool_support": True,
        "cost_per_1k_tokens": 0.00125,
        "latency_ms": 850,
        "status": "APPROVED",
        "enabled": True
    },
    {
        "id": "gpt-4o-financial-extractor",
        "provider": "OpenAI / Candidate Route",
        "model_name": "GPT-4o Financial Engine",
        "version": "4.0.0",
        "capabilities": ["vision_support", "structured_output", "table_reasoning"],
        "context_window": 128000,
        "vision_support": True,
        "structured_output_support": True,
        "tool_support": True,
        "cost_per_1k_tokens": 0.0025,
        "latency_ms": 920,
        "status": "CANDIDATE",
        "enabled": True
    },
    {
        "id": "claude-3-5-sonnet-financial",
        "provider": "Anthropic / Candidate Route",
        "model_name": "Claude 3.5 Sonnet Financial",
        "version": "3.5.0",
        "capabilities": ["vision_support", "structured_output", "table_reasoning"],
        "context_window": 200000,
        "vision_support": True,
        "structured_output_support": True,
        "tool_support": True,
        "cost_per_1k_tokens": 0.0030,
        "latency_ms": 1100,
        "status": "CANDIDATE",
        "enabled": True
    },
    {
        "id": "deterministic-source-parser",
        "provider": "Native Deterministic Engine",
        "model_name": "Deterministic Excel & Document Parser",
        "version": "2.1.0",
        "capabilities": ["structured_output", "exact_table_extraction", "zero_hallucination"],
        "context_window": 500000,
        "vision_support": False,
        "structured_output_support": True,
        "tool_support": False,
        "cost_per_1k_tokens": 0.0000,
        "latency_ms": 120,
        "status": "PRODUCTION",
        "enabled": True
    }
]

def get_registered_models(enabled_only: bool = True) -> List[Dict[str, Any]]:
    """Retrieve list of registered models."""
    if enabled_only:
        return [m for m in MODEL_REGISTRY if m.get("enabled", True)]
    return MODEL_REGISTRY

def get_model_by_id(model_id: str) -> Optional[Dict[str, Any]]:
    """Lookup model entry by ID."""
    for m in MODEL_REGISTRY:
        if m["id"] == model_id:
            return m
    return None

def filter_candidate_models(document_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Filter models based on document capability requirements."""
    requires_vision = document_profile.get("requires_vision", False)
    is_large_doc = document_profile.get("page_count", 1) > 50 or document_profile.get("file_size_mb", 0) > 10
    
    candidates = []
    for model in get_registered_models():
        if model["status"] == "DEPRECATED":
            continue
        if requires_vision and not model.get("vision_support", False):
            continue
        if is_large_doc and model.get("context_window", 0) < 100000:
            continue
        candidates.append(model)
        
    return candidates if candidates else get_registered_models()
