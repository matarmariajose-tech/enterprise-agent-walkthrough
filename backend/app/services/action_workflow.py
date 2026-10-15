from app.domain.models import ActionProposal, ActionStatus


class InvalidTransitionError(ValueError):
    pass


class ActionWorkflow:
    _transitions: dict[ActionStatus, frozenset[ActionStatus]] = {
        ActionStatus.PROPOSED: frozenset({ActionStatus.APPROVED}),
        ActionStatus.APPROVED: frozenset({ActionStatus.EXECUTING}),
        ActionStatus.EXECUTING: frozenset({ActionStatus.COMPLETED, ActionStatus.FAILED}),
        ActionStatus.COMPLETED: frozenset(),
        ActionStatus.FAILED: frozenset(),
    }

    def transition(
        self, proposal: ActionProposal, target: ActionStatus, *, expected_version: int
    ) -> ActionProposal:
        if proposal.version != expected_version:
            raise InvalidTransitionError("Stale action version")
        if target not in self._transitions[proposal.status]:
            raise InvalidTransitionError(f"Invalid transition: {proposal.status} -> {target}")
        return proposal.model_copy(update={"status": target, "version": proposal.version + 1})
