# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/actions_handler.py
from gui.prb_control.entities.base.squad.actions_handler import SquadActionsHandler
from helpers import dependency
from skeletons.gui.server_events import IEventsCache
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from CurrentVehicle import g_currentVehicle

class EventBattleSquadActionsHandler(SquadActionsHandler):
    """
    Event battle squad actions handler
    """
    eventsCache = dependency.descriptor(IEventsCache)

    def _loadWindow(self, ctx):
        super(EventBattleSquadActionsHandler, self)._loadWindow(ctx)
        if not self._entity.getPlayerInfo().isReady:
            curVehicle = g_currentVehicle.item
            if curVehicle is not None and VEHICLE_TAGS.EVENT not in curVehicle.tags:
                eventVehicle = self.eventsCache.getEventVehicles()[0]
                g_currentVehicle.selectVehicle(eventVehicle.invID)
        return
