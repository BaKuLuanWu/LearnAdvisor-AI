from dataclasses import dataclass


@dataclass
class RuleResult:
    intent: str
    confidence: float
