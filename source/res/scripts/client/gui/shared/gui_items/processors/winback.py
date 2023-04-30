# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/winback.py
import typing
import BigWorld
from gui import SystemMessages
from gui.Scaleform.Waiting import Waiting
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.dialogs.dialogs import showSingleDialogWithResultData
from gui.impl.gen import R
from gui.shared.gui_items.processors import Processor, plugins
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
    from frameworks import wulf
_WINBACK_MESSAGES = R.strings.system_messages.winback

class WinbackTurnOffBattlesProcessor(Processor):

    def __init__(self, reason, dialog=None, parent=None):
        confirmators = None
        if dialog is not None:
            layoutID = R.views.lobby.winback.WinbackLeaveModeDialogView()
            confirmators = [plugins.AsyncDialogConfirmator(showSingleDialogWithResultData, dialog, layoutID, parent)]
        super(WinbackTurnOffBattlesProcessor, self).__init__(confirmators)
        self.__reason = reason
        return

    def _request(self, callback):
        Waiting.show('updating')
        BigWorld.player().winback.turnOffBattles(self.__reason, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def _successHandler(self, code, ctx=None):
        Waiting.hide('updating')
        return super(WinbackTurnOffBattlesProcessor, self)._successHandler(code, ctx)

    def _errorHandler(self, code, errStr='', ctx=None):
        Waiting.hide('updating')
        SystemMessages.pushMessage(text=backport.text(_WINBACK_MESSAGES.turnOffBattlesError()), type=SM_TYPE.ErrorSimple)
        return super(WinbackTurnOffBattlesProcessor, self)._errorHandler(code, errStr, ctx)
