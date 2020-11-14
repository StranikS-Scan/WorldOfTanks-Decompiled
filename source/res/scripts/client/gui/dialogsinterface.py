# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/DialogsInterface.py
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.utils import decorators
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nInfoDialogMeta, I18nConfirmDialogMeta, DisconnectMeta, CheckBoxDialogMeta

class _DialogCallbackWrapper(object):

    def __init__(self, cb):
        Waiting.suspend(lockerID=id(self))
        self.__cb = cb

    def __call__(self, result):
        Waiting.resume(lockerID=id(self))
        if self.__cb is not None:
            self.__cb(result)
        return


@decorators.async
def showDialog(meta, callback):
    g_eventBus.handleEvent(events.ShowDialogEvent(meta, _DialogCallbackWrapper(callback)))


@decorators.async
def showBCConfirmationDialog(meta, callback):
    effectData = {'messages': [{'messagePreset': 'BCMessageGreenUI',
                   'label': meta.getLabel(),
                   'iconPath': meta.getIcon(),
                   'labelExecute': meta.getLabelExecute(),
                   'costValue': meta.getCostValue(),
                   'isBuy': meta.getIsBuy(),
                   'isTraining': meta.getIsTraining(),
                   'message': meta.getMessage()}],
     'voiceovers': [],
     'callback': _DialogCallbackWrapper(callback)}
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BOOTCAMP_MESSAGE_WINDOW), ctx=effectData), EVENT_BUS_SCOPE.LOBBY)


@decorators.async
def showI18nInfoDialog(i18nKey, callback, meta=None):
    showDialog(I18nInfoDialogMeta(i18nKey, meta=meta), callback)


@decorators.async
def showI18nConfirmDialog(i18nKey, callback, ctx=None, meta=None, focusedID=None):
    showDialog(I18nConfirmDialogMeta(i18nKey, messageCtx=ctx, meta=meta, focusedID=focusedID), callback)


@decorators.async
def showI18nCheckBoxDialog(i18nKey, callback, meta=None, focusedID=None):
    showDialog(CheckBoxDialogMeta(i18nKey, meta=meta, focusedID=focusedID), callback)


__ifDisconnectDialogShown = False

def showDisconnect(reason=None, isBan=False, expiryTime=None):
    global __ifDisconnectDialogShown
    if __ifDisconnectDialogShown:
        return
    Waiting.close()

    def callback(_):
        global __ifDisconnectDialogShown
        __ifDisconnectDialogShown = False

    __ifDisconnectDialogShown = True
    showDialog(DisconnectMeta(reason, isBan, expiryTime), callback)
