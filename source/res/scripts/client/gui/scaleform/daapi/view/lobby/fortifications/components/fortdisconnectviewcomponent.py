# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/fortifications/components/FortDisconnectViewComponent.py
from debug_utils import LOG_WARNING
from gui.Scaleform.daapi.view.lobby.fortifications.fort_utils.FortViewHelper import FortViewHelper
from gui.Scaleform.daapi.view.meta.FortDisconnectViewMeta import FortDisconnectViewMeta
from gui.Scaleform.framework import AppRef
from gui.Scaleform.framework.managers.TextManager import TextIcons
from gui.Scaleform.locale.FORTIFICATIONS import FORTIFICATIONS
from gui.shared.fortifications.settings import CLIENT_FORT_STATE
from gui.Scaleform.Waiting import Waiting
from helpers import i18n

class FortDisconnectViewComponent(FortDisconnectViewMeta, FortViewHelper, AppRef):

    def __init__(self):
        super(FortDisconnectViewComponent, self).__init__()

    def _populate(self):
        super(FortDisconnectViewComponent, self)._populate()
        state = self.fortState
        warningIcon = i18n.makeString(self.app.utilsManager.textManager.getIcon(TextIcons.ALERT_ICON))
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
        Waiting.hide('loadPage')
        Waiting.hide('Flash')

    def _dispose(self):
        super(FortDisconnectViewComponent, self)._dispose()
