# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/actions_handler.py
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.squad.actions_handler import SquadActionsHandler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from helpers import dependency
from skeletons.gui.server_events import IEventsCache

class EventBattleSquadActionsHandler(SquadActionsHandler):
    eventsCache = dependency.descriptor(IEventsCache)

    def _loadWindow(self, ctx):
        super(EventBattleSquadActionsHandler, self)._loadWindow(ctx)
        if not self._entity.getPlayerInfo().isReady:
            eventVehicle = self.eventsCache.getEventVehicles()[0]
            g_currentVehicle.selectVehicle(eventVehicle.invID)

    def _showBattleQueueGUI(self):
        g_eventDispatcher.loadEventBattleQueue()
