# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/event/squad/actions_handler.py
from CurrentVehicle import g_currentVehicle
from gui.prb_control.entities.base.squad.actions_handler import SquadActionsHandler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from helpers import dependency
from skeletons.gui.server_events import IEventsCache

class EventBattleSquadActionsHandler(SquadActionsHandler):
    eventsCache = dependency.descriptor(IEventsCache)

    def _loadPage(self):
        pass

    def _showBattleQueueGUI(self):
        if not self.eventsCache.isEventEnabled():
            g_eventDispatcher.loadHangar()
        else:
            g_eventDispatcher.loadEventBattleQueue()

    def setUnitChanged(self, loadHangar=False):
        flags = self._entity.getFlags()
        if self._entity.getPlayerInfo().isReady and flags.isInQueue():
            _, unit = self._entity.getUnit()
            pInfo = self._entity.getPlayerInfo()
            vInfos = unit.getMemberVehicles(pInfo.dbID)
            if vInfos is not None:
                g_currentVehicle.selectVehicle(vInfos[0].vehInvID)
            self._showBattleQueueGUI()
        elif loadHangar:
            if not self.eventsCache.isEventEnabled():
                g_eventDispatcher.loadHangar()
            else:
                g_eventDispatcher.loadEventHangar()
        return
