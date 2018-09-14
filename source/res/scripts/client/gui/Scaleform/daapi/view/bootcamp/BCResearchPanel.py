# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCResearchPanel.py
from gui.Scaleform.daapi.view.meta.BCResearchPanelMeta import BCResearchPanelMeta
from CurrentVehicle import g_currentVehicle
from gui.shared import event_dispatcher as shared_events
from debug_utils import LOG_ERROR, LOG_DEBUG

class BCResearchPanel(BCResearchPanelMeta):

    def __init__(self):
        super(BCResearchPanel, self).__init__()

    def _populate(self):
        super(BCResearchPanel, self)._populate()

    def goToResearch(self):
        LOG_DEBUG('BCResearchPanel::goToResearch')
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
