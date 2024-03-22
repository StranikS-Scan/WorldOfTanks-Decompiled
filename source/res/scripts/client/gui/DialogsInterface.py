# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/DialogsInterface.py
from constants import ACCOUNT_KICK_REASONS
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.dialogs import I18nInfoDialogMeta, I18nConfirmDialogMeta, DisconnectMeta, CheckBoxDialogMeta
from gui.shared import events, g_eventBus
from gui.shared.utils import decorators

class _DialogCallbackWrapper(object):

    def __init__(self, cb):
        Waiting.suspend(lockerID=id(self))
        self.__cb = cb

    def __call__(self, result):
        Waiting.resume(lockerID=id(self))
        if self.__cb is not None:
            self.__cb(result)
        return


@decorators.adisp_async
def showDialog(meta, callback, parent=None):
    g_eventBus.handleEvent(events.ShowDialogEvent(meta, _DialogCallbackWrapper(callback), parent=parent))


@decorators.adisp_async
def showI18nInfoDialog(i18nKey, callback, meta=None):
    showDialog(I18nInfoDialogMeta(i18nKey, meta=meta), callback)


@decorators.adisp_async
def showI18nConfirmDialog(i18nKey, callback, ctx=None, meta=None, focusedID=None):
    showDialog(I18nConfirmDialogMeta(i18nKey, messageCtx=ctx, meta=meta, focusedID=focusedID), callback)


@decorators.adisp_async
def showI18nCheckBoxDialog(i18nKey, callback, meta=None, focusedID=None):
    showDialog(CheckBoxDialogMeta(i18nKey, meta=meta, focusedID=focusedID), callback)


__ifDisconnectDialogShown = False

def showDisconnect(reason=None, kickReasonType=ACCOUNT_KICK_REASONS.UNKNOWN, expiryTime=None):
    global __ifDisconnectDialogShown
    if __ifDisconnectDialogShown:
        return
    Waiting.close()

    def callback(_):
        global __ifDisconnectDialogShown
        __ifDisconnectDialogShown = False

    __ifDisconnectDialogShown = True
    showDialog(DisconnectMeta(reason, kickReasonType, expiryTime), callback)
