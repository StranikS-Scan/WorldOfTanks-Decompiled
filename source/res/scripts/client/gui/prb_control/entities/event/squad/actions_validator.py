# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/actions_validator.py
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.base.actions_validator import BaseActionsValidator, ActionsValidatorComposite
from gui.prb_control.entities.base.unit.actions_validator import CommanderValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION

class _EventBattleVehiclesValidator(SquadVehiclesValidator):
    """
    Event battle squad vehicles validation
    """

    def _isValidMode(self, vehicle):
        return vehicle.isEvent


class EventSquandSlotsValidator(CommanderValidator):
    """
    Event squad slots validation
    """

    def _validate(self):
        stats = self._entity.getStats()
        pInfo = self._entity.getPlayerInfo()
        return ValidationResult(False, UNIT_RESTRICTION.COMMANDER_VEHICLE_NOT_SELECTED) if stats.occupiedSlotsCount > 1 and not pInfo.isReady else None


class EventBattleSquadActionsValidator(SquadActionsValidator):
    """
    Event battle squad actions validation class
    """

    def _createVehiclesValidator(self, entity):
        return _EventBattleVehiclesValidator(entity)

    def _createSlotsValidator(self, entity):
        baseValidator = super(EventBattleSquadActionsValidator, self)._createSlotsValidator(entity)
        return ActionsValidatorComposite(entity, validators=[baseValidator, EventSquandSlotsValidator(entity)])
