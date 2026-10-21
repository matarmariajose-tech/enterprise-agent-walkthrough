import pytest

from app.domain.models import ActionProposal, ActionStatus
from app.services.action_workflow import ActionWorkflow, InvalidTransitionError


def proposal() -> ActionProposal:
    return ActionProposal(
        type="publish_operational_alert",
        idempotency_key="test-key",
        request_fingerprint="a" * 64,
        payload={"region": "LATAM"},
    )


def test_rejects_execution_before_approval() -> None:
    with pytest.raises(InvalidTransitionError):
        ActionWorkflow().transition(proposal(), ActionStatus.EXECUTING, expected_version=1)


def test_rejects_stale_approval() -> None:
    with pytest.raises(InvalidTransitionError, match="Stale"):
        ActionWorkflow().transition(proposal(), ActionStatus.APPROVED, expected_version=0)


def test_valid_transition_increments_version() -> None:
    updated = ActionWorkflow().transition(proposal(), ActionStatus.APPROVED, expected_version=1)
    assert updated.status is ActionStatus.APPROVED
    assert updated.version == 2
