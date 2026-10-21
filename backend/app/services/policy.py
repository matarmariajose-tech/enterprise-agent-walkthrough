import math
from dataclasses import dataclass

from app.domain.models import FailureSummary


@dataclass(frozen=True)
class AlertPolicy:
    version: str
    failure_rate_threshold: float

    def __post_init__(self) -> None:
        if not self.version.strip():
            raise ValueError("Policy version is required")
        if (
            not math.isfinite(self.failure_rate_threshold)
            or not 0 <= self.failure_rate_threshold <= 1
        ):
            raise ValueError("Policy threshold must be between zero and one")


class PolicyEngine:
    def __init__(self, alert_policy: AlertPolicy) -> None:
        self._alert_policy = alert_policy

    @property
    def version(self) -> str:
        return self._alert_policy.version

    def threshold_exceeded(self, summary: FailureSummary) -> bool:
        return summary.failure_rate >= self._alert_policy.failure_rate_threshold
