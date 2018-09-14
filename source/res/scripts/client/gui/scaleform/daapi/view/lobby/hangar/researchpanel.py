# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/ResearchPanel.py
from CurrentVehicle import g_currentVehicle
from adisp import process
from debug_utils import LOG_ERROR
from helpers.i18n import makeString
from gui import makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.ResearchPanelMeta import ResearchPanelMeta
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.utils.requesters import DeprecatedStatsRequester

class ResearchPanel(ResearchPanelMeta, DAAPIModule):

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
            exitEvent = events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR)
            loadEvent = events.LoadViewEvent(VIEW_ALIAS.LOBBY_RESEARCH, ctx={'rootCD': g_currentVehicle.item.intCD,
             'exit': exitEvent})
            self.fireEvent(loadEvent, scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            LOG_ERROR('Current vehicle is not preset')

    @process
    def onCurrentVehicleChanged(self):
        if g_currentVehicle.isPresent():
            xps = yield DeprecatedStatsRequester().getVehicleTypeExperiences()
            xp = xps.get(g_currentVehicle.item.intCD, 0)
            isElite = g_currentVehicle.item.isElite
            vTypeId = g_currentVehicle.item.type
            vTypeName = makeString('#menu:header/vehicleType/elite/%s' % vTypeId) if isElite is True else makeString('#menu:header/vehicleType/%s' % vTypeId)
            vDescription = makeString('#menu:header/level', vTypeName=vTypeName)
            vLevel = makeString('#menu:header/level/%s' % g_currentVehicle.item.level)
            vDescription = makeHtmlString('html_templates:lobby/header', 'vehicle-level', {'level': vLevel,
             'vDescription': vDescription})
            self.as_updateCurrentVehicleS(g_currentVehicle.item.userName, vTypeId, vDescription, xp, isElite, g_currentVehicle.item.isPremiumIGR)
        else:
            self.as_updateCurrentVehicleS('', '', '', 0, False, False)
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
