# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/actions_validator.py
from gui.prb_control.entities.base.squad.actions_validator import SquadActionsValidator, SquadVehiclesValidator
from helpers import dependency
from skeletons.gui.server_events import IEventsCache

class _EventBattleVehiclesValidator(SquadVehiclesValidator):
    eventsCache = dependency.descriptor(IEventsCache)

    def _isValidMode(self, vehicle):
        return self.eventsCache.isEventEnabled() and vehicle.isEvent


class EventBattleSquadActionsValidator(SquadActionsValidator):

    def _createVehiclesValidator(self, entity):
        return _EventBattleVehiclesValidator(entity)
