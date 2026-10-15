from dataclasses import dataclass

from app.domain.models import FailureSummary


@dataclass(frozen=True)
class AlertPolicy:
    version: str
    failure_rate_threshold: float


class PolicyEngine:
    def __init__(self, alert_policy: AlertPolicy) -> None:
        self._alert_policy = alert_policy

    @property
    def version(self) -> str:
        return self._alert_policy.version

    def threshold_exceeded(self, summary: FailureSummary) -> bool:
        return summary.failure_rate >= self._alert_policy.failure_rate_threshold
