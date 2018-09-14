# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/legacy/actions_validator.py
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PREBATTLE_RESTRICTION
from prebattle_shared import decodeRoster

class InQueueValidator(BaseActionsValidator):
    """
    Is our team in queue now.
    """

    def _validate(self):
        _, assigned = decodeRoster(self._entity.getRosterKey())
        return ValidationResult(False, PREBATTLE_RESTRICTION.TEAM_IS_IN_QUEUE) if self._entity.getTeamState().isInQueue() and assigned else super(InQueueValidator, self)._validate()


class LegacyVehicleValid(BaseActionsValidator):
    """
    Legacy vehicle validator due to team limits.
    """

    def _validate(self):
        return self._entity.getLimits().isVehicleValid()


class LegacyTeamValidator(BaseActionsValidator):
    """
    Legacy team validator due to team limits.
    """

    def _validate(self):
        return self._entity.getLimits().isTeamValid()

    def _isEnabled(self):
        return self._entity.isCommander()


class LegacyActionsValidator(ActionsValidatorComposite):
    """
    Legacy actions validator class.
    """

    def __init__(self, entity):
        validators = [InQueueValidator(entity), LegacyVehicleValid(entity), LegacyTeamValidator(entity)]
        super(LegacyActionsValidator, self).__init__(entity, validators)
