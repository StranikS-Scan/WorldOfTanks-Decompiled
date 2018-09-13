# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/ResearchPanel.py
from CurrentVehicle import g_currentVehicle
from adisp import process
from debug_utils import LOG_ERROR
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.ResearchPanelMeta import ResearchPanelMeta
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.utils.requesters import StatsRequester

class ResearchPanel(ResearchPanelMeta, DAAPIModule):

    def __init__(self):
        super(ResearchPanel, self).__init__()

    def _populate(self):
        super(ResearchPanel, self)._populate()
        g_clientUpdateManager.addCallbacks({'stats.vehTypeXP': self.onVehicleTypeXPChanged,
         'stats.eliteVehicles': self.onVehicleBecomeElite})
        self.onCurrentVehicleChanged()

    def _dispose(self):
        super(ResearchPanel, self)._dispose()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def goToResearch(self):
        if g_currentVehicle.isPresent():
            Event = events.LoadEvent
            exitEvent = Event(Event.LOAD_HANGAR)
            loadEvent = Event(Event.LOAD_RESEARCH, ctx={'rootCD': g_currentVehicle.item.intCD,
             'exit': exitEvent})
            self.fireEvent(loadEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            LOG_ERROR('Current vehicle is not preset')

    @process
    def onCurrentVehicleChanged(self):
        if g_currentVehicle.isPresent():
            xps = yield StatsRequester().getVehicleTypeExperiences()
            xp = xps.get(g_currentVehicle.item.intCD, 0)
            self.as_setEarnedXPS(xp)
            self.as_setEliteS(g_currentVehicle.item.isElite)
        else:
            self.as_setEarnedXPS(0)
            self.as_setEliteS(False)
            yield lambda callback = None: callback
        return

    def onVehicleTypeXPChanged(self, xps):
        if g_currentVehicle.isPresent():
            vehCD = g_currentVehicle.item.intCD
            if vehCD in xps:
                self.as_setEarnedXPS(xps[vehCD])

    def onVehicleBecomeElite(self, elite):
        if g_currentVehicle.isPresent():
            vehCD = g_currentVehicle.item.intCD
            if vehCD in elite:
                self.as_setEliteS(True)
