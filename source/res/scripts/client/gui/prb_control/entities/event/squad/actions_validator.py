# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/actions_validator.py
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION
from helpers import dependency
from gui.prb_control.entities.base.actions_validator import ActionsValidatorComposite
from gui.prb_control.entities.base.unit.actions_validator import CommanderValidator
from shared_utils import findFirst
from skeletons.gui.game_event_controller import IGameEventController

class _EventBattleVehiclesValidator(SquadVehiclesValidator):
    gameEventController = dependency.descriptor(IGameEventController)

    def _validate(self):
        if not self._isValidMode(None):
            return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_WRONG_MODE)
        else:
            vInfos = self._getVehiclesInfo()
            return ValidationResult(False, UNIT_RESTRICTION.VEHICLE_NOT_SELECTED) if not findFirst(lambda v: not v.isEmpty(), vInfos, False) else None

    def _isValidMode(self, vehicle):
        return self.gameEventController.isEnabled()


class EventSquadSlotsValidator(CommanderValidator):

    def _validate(self):
        stats = self._entity.getStats()
        pInfo = self._entity.getPlayerInfo()
        return ValidationResult(False, UNIT_RESTRICTION.EVENT_UNIT_COMMANDER_NOT_SELECTED) if stats.occupiedSlotsCount > 1 and not pInfo.isReady else None


class EventBattleSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return _EventBattleVehiclesValidator(entity)

    def _createSlotsValidator(self, entity):
        baseValidator = super(EventBattleSquadActionsValidator, self)._createSlotsValidator(entity)
        return ActionsValidatorComposite(entity, validators=[baseValidator, EventSquadSlotsValidator(entity)])
