"""
Universal Enterprise Benchmark (Backwards Compatibility Proxy)
Re-exports from app.engine.enterprise_benchmark.
"""

from app.engine.enterprise_benchmark import (
    ENTERPRISE_GROUND_TRUTH,
    SECTOR_GROUND_TRUTHS,
    CANDIDATE_MODEL_EXTRACTIONS,
    run_enterprise_golden_benchmark,
    run_wipro_golden_benchmark
)

__all__ = [
    "ENTERPRISE_GROUND_TRUTH",
    "SECTOR_GROUND_TRUTHS",
    "CANDIDATE_MODEL_EXTRACTIONS",
    "run_enterprise_golden_benchmark",
    "run_wipro_golden_benchmark"
]
