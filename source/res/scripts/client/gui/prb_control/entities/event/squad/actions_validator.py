# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/actions_validator.py
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import UNIT_RESTRICTION

class _EventBattleVehiclesValidator(SquadVehiclesValidator):

    def _isValidMode(self, vehicle):
        return vehicle.isEvent

    def _validate(self):
        pInfo = self._entity.getPlayerInfo()
        if not pInfo.isReady and g_currentVehicle.isPresent():
            if not self._entity.hasSlotForRole(g_currentVehicle.item.getFootballRole()):
                return ValidationResult(False, UNIT_RESTRICTION.FOOTBALL_INCONSISTENT)
        return super(_EventBattleVehiclesValidator, self)._validate()


class EventBattleSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return _EventBattleVehiclesValidator(entity)
