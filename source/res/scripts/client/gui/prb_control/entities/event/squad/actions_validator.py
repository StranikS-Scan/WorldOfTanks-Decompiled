# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/actions_validator.py
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator

class _EventBattleVehiclesValidator(SquadVehiclesValidator):
    """
    Event battle squad vehicles validation
    """

    def _isValidMode(self, vehicle):
        return vehicle.isEvent


class EventBattleSquadActionsValidator(SquadActionsValidator):
    """
    Event battle squad actions validation class
    """

    def _createVehiclesValidator(self, entity):
        return _EventBattleVehiclesValidator(entity)
