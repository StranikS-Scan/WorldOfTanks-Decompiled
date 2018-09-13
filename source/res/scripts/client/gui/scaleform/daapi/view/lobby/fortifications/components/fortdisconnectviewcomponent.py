# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortDisconnectViewComponent.py
from debug_utils import LOG_WARNING
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils import fort_text
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortDisconnectViewMeta import FortDisconnectViewMeta
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.shared.fortifications.settings import CLIENT_FORT_STATE
from helpers import i18n

class FortDisconnectViewComponent(FortDisconnectViewMeta, FortViewHelper):

    def __init__(self):
        super(FortDisconnectViewMeta, self).__init__()

    def _populate(self):
        super(FortDisconnectViewMeta, self)._populate()
        state = self.fortState
        warningIcon = i18n.makeString(fort_text.getIcon(fort_text.ALERT_ICON))
        warningText = warningIcon + i18n.makeString(FORTIFICATIONS.DISCONNECTED_WARNING)
        warningDescrText = ''
        if state.getStateID() == CLIENT_FORT_STATE.ROAMING:
            warningDescrText = FORTIFICATIONS.DISCONNECTED_WARNINGDESCRIPTIONROAMING
        elif state.getStateID() == CLIENT_FORT_STATE.CENTER_UNAVAILABLE:
            warningDescrText = FORTIFICATIONS.DISCONNECTED_WARNINGDESCRIPTIONCENTERUNAVAILABLE
        else:
            LOG_WARNING('Unknown fort state for disconnectView: %d' % state.getStateID())
        warningDescrText = i18n.makeString(warningDescrText)
        self.as_setWarningTextsS(warningText, warningDescrText)

    def _dispose(self):
        super(FortDisconnectViewMeta, self)._dispose()
