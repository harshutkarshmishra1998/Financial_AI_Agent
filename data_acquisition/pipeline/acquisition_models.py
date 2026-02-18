from dataclasses import dataclass, field
from typing import Dict, Any, List


@dataclass
class DomainExecutionRecord:
    domain: str
    success: bool
    message: str


@dataclass
class AcquisitionResult:
    plan: Any
    domain_results: Dict[str, Any] = field(default_factory=dict)
    execution_log: List[DomainExecutionRecord] = field(default_factory=list)
    success: bool = True