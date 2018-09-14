# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortDisconnectViewComponent.py
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortDisconnectViewMeta import FortDisconnectViewMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.fortifications.settings import CLIENT_FORT_STATE
from gui.shared.formatters import icons
from helpers import i18n

class FortDisconnectViewComponent(FortDisconnectViewMeta, FortViewHelper):

    def __init__(self):
        super(FortDisconnectViewComponent, self).__init__()

    def _populate(self):
        super(FortDisconnectViewComponent, self)._populate()
        state = self.fortState
        warningIcon = icons.alert()
        warningText = warningIcon + i18n.makeString(FORTIFICATIONS.DISCONNECTED_WARNING)
        if state.getStateID() == CLIENT_FORT_STATE.ROAMING:
            warningDescrText = FORTIFICATIONS.DISCONNECTED_WARNINGDESCRIPTIONROAMING
        else:
            warningDescrText = FORTIFICATIONS.DISCONNECTED_WARNINGDESCRIPTIONCENTERUNAVAILABLE
        warningDescrText = i18n.makeString(warningDescrText)
        self.as_setWarningTextsS(warningText, warningDescrText)
        g_eventBus.handleEvent(events.FortEvent(events.FortEvent.VIEW_LOADED), scope=EVENT_BUS_SCOPE.FORT)

    def _dispose(self):
        super(FortDisconnectViewComponent, self)._dispose()
