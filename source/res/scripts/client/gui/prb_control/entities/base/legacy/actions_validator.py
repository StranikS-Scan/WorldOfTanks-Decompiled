# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/legacy/actions_validator.py
import typing
from PlayerEvents import g_playerEvents
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PREBATTLE_RESTRICTION, PREBATTLE_SETTING_NAME
from prebattle_shared import decodeRoster
if typing.TYPE_CHECKING:
    from typing import Dict, List, Type
    from constants import ARENA_GUI_TYPE
ARENA_GUI_TYPE_VALIDATORS = {}

class InQueueValidator(BaseActionsValidator):

    def _validate(self):
        if g_playerEvents.isPlayerEntityChanging:
            return ValidationResult(False, PREBATTLE_RESTRICTION.TEAM_IS_IN_QUEUE)
        _, assigned = decodeRoster(self._entity.getRosterKey())
        return ValidationResult(False, PREBATTLE_RESTRICTION.TEAM_IS_IN_QUEUE) if self._entity.getTeamState().isInQueue() and assigned else super(InQueueValidator, self)._validate()


class LegacyVehicleValid(BaseActionsValidator):

    def _validate(self):
        return self._entity.getLimits().isVehicleValid()


class LegacyTeamValidator(BaseActionsValidator):

    def _validate(self):
        return self._entity.getLimits().isTeamValid()

    def _isEnabled(self):
        return self._entity.isCommander()


class LegacyActionsValidator(ActionsValidatorComposite):

    def __init__(self, entity):
        validators = [InQueueValidator(entity), LegacyVehicleValid(entity), LegacyTeamValidator(entity)]
        arenaGuiType = entity.getSettings()[PREBATTLE_SETTING_NAME.ARENA_GUI_TYPE]
        validator = ARENA_GUI_TYPE_VALIDATORS.get(arenaGuiType)
        if validator is not None:
            validators.append(validator(entity))
        super(LegacyActionsValidator, self).__init__(entity, validators)
        return
