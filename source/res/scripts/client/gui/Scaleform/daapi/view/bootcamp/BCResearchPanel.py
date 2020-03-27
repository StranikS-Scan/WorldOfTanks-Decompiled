# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCResearchPanel.py
from gui.Scaleform.daapi.view.lobby.hangar.ResearchPanel import ResearchPanel
from CurrentVehicle import g_currentVehicle
from gui.shared import event_dispatcher as shared_events
from debug_utils import LOG_ERROR
from bootcamp.statistic.decorators import loggerTarget, loggerEntry, simpleLog
from bootcamp.statistic.logging_constants import BC_LOG_ACTIONS, BC_LOG_KEYS

@loggerTarget(logKey=BC_LOG_KEYS.BC_RESEARCH_VEHICLES)
class BCResearchPanel(ResearchPanel):

    @loggerEntry
    def _populate(self):
        super(BCResearchPanel, self)._populate()

    @simpleLog(action=BC_LOG_ACTIONS.RESEARCH_BUTTON_PRESSED, logOnce=True)
    def goToResearch(self):
        if g_currentVehicle.isPresent():
            shared_events.showResearchView(g_currentVehicle.item.intCD)
        else:
            LOG_ERROR('Current vehicle is not preset')

    def as_updateCurrentVehicleS(self, data):
        if 'isElite' in data:
            data['isElite'] = False
        super(BCResearchPanel, self).as_updateCurrentVehicleS(data)

    def as_setEliteS(self, isElite):
        super(BCResearchPanel, self).as_setEliteS(False)
