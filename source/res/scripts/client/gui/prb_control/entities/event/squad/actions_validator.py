# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/actions_validator.py
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from gui.prb_control.entities.random.pre_queue.actions_validator import EventPrimeTimeValidator

class _EventBattleVehiclesValidator(SquadVehiclesValidator):

    def _isValidMode(self, vehicle):
        return vehicle.isEvent and not vehicle.isOnlyForEpicBattles


class EventBattleSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return _EventBattleVehiclesValidator(entity)

    def _createStateValidator(self, entity):
        return EventPrimeTimeValidator(entity)
