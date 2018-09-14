# Embedded file name: scripts/client/gui/DialogsInterface.py
from gui.Scaleform.Waiting import Waiting
from gui.battle_control import g_sessionProvider
from gui.shared import events, g_eventBus
from gui.shared.utils.decorators import dialog
from gui.shared.utils.functions import showInformationDialog, showConfirmDialog
from gui.Scaleform.daapi.view.dialogs import I18nInfoDialogMeta, I18nConfirmDialogMeta, DisconnectMeta

@dialog
def showDialog(meta, callback):
    g_eventBus.handleEvent(events.ShowDialogEvent(meta, callback))


@dialog
def showI18nInfoDialog(i18nKey, callback, meta = None):
    if g_sessionProvider.isBattleUILoaded():
        customMsg = None
        if meta is not None:
            customMsg.getMessage()
        showInformationDialog(i18nKey, callback, customMessage=customMsg, ns='battle')
    else:
        showDialog(I18nInfoDialogMeta(i18nKey, meta=meta), callback)
    return


@dialog
def showI18nConfirmDialog(i18nKey, callback, meta = None, focusedID = None):
    if g_sessionProvider.isBattleUILoaded():
        customMsg = None
        if meta is not None:
            customMsg.getMessage()
        showConfirmDialog(i18nKey, callback, customMessage=customMsg, ns='battle')
    else:
        showDialog(I18nConfirmDialogMeta(i18nKey, meta=meta, focusedID=focusedID), callback)
    return


__ifDisconnectDialogShown = False

def showDisconnect(reason = None, isBan = False, expiryTime = None):
    global __ifDisconnectDialogShown
    if __ifDisconnectDialogShown:
        return
    Waiting.close()

    def callback(_):
        global __ifDisconnectDialogShown
        __ifDisconnectDialogShown = False

    __ifDisconnectDialogShown = True
    showDialog(DisconnectMeta(reason, isBan, expiryTime), callback)
