# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/BCAmmunitionPanel.py
from gui.Scaleform.daapi.view.meta.BCAmmunitionPanelMeta import BCAmmunitionPanelMeta
from gui.shared.events import LoadViewEvent
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.event_bus import EVENT_BUS_SCOPE
from debug_utils import LOG_DEBUG

class BCAmmunitionPanel(BCAmmunitionPanelMeta):

    def __init__(self):
        super(BCAmmunitionPanel, self).__init__()

    def _dispose(self):
        super(BCAmmunitionPanel, self)._dispose()

    def showTechnicalMaintenance(self):
        LOG_DEBUG('BCAmmunitionPanel.showTechnicalMaintenance')
        self.fireEvent(LoadViewEvent(VIEW_ALIAS.BOOTCAMP_TECHNICAL_MAINTENANCE), EVENT_BUS_SCOPE.LOBBY)
