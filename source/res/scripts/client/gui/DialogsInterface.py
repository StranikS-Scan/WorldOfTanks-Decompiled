# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/DialogsInterface.py
import BigWorld
import WGC
from account_shared import getFairPlayViolationName
from adisp import adisp_process
from constants import ACCOUNT_KICK_REASONS
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nInfoDialogMeta, I18nConfirmDialogMeta, DisconnectMeta, CheckBoxDialogMeta, DemoAccountBootcampFailureMeta, DIALOG_BUTTON_ID
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.EVENT import EVENT
from gui.impl.gen import R
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.formatters.time_formatters import getTillTimeByResource
from gui.shared.utils import decorators
from helpers import i18n
from messenger.formatters import TimeFormatter
from PlayerEvents import g_extPlayerEvents

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
     'callback': _DialogCallbackWrapper(callback),
     'submitID': ''}
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.BOOTCAMP_MESSAGE_WINDOW), ctx=effectData), EVENT_BUS_SCOPE.LOBBY)


@decorators.adisp_async
def showI18nInfoDialog(i18nKey, callback, meta=None):
    showDialog(I18nInfoDialogMeta(i18nKey, meta=meta), callback)


@decorators.adisp_async
@adisp_process
def showDemoAccountBootcampFailureDialog(i18nKey, meta=None):
    result = yield showDialog(DemoAccountBootcampFailureMeta(i18nKey, meta=meta))
    if result == DIALOG_BUTTON_ID.HYPERLINK:
        WGC.requestCompleteAccount()
    BigWorld.quit()


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

    if kickReasonType == ACCOUNT_KICK_REASONS.DEMO_ACCOUNT_BOOTCAMP_FAILURE:
        showDemoAccountBootcampFailureDialog(reason)
    else:
        __ifDisconnectDialogShown = True
        showDialog(DisconnectMeta(reason, kickReasonType, expiryTime), callback)


def showPunishmentDialog(arenaType, arenaCreateTime, fairplayViolations, banDuration):
    from gui.Scaleform.daapi.view.dialogs import I18PunishmentDialogMeta
    from gui.Scaleform.daapi.view.lobby.comp7.dialogs.comp7_punishment_dialog_meta import Comp7PunishmentDialogMeta
    if arenaType.gameplayName == 'comp7':
        durationStr = getTillTimeByResource(banDuration, R.strings.comp7.alertMessage.timeLeft, removeLeadingZeros=True)
        styledDurationStr = text_styles.hightlight(durationStr)
        metaClass = Comp7PunishmentDialogMeta
        key = 'comp7/punishmentWindow'
        messageCtx = {'banDuration': styledDurationStr}
    else:
        penaltyType = None
        violation = None
        if fairplayViolations[1] != 0:
            penaltyType = 'penalty'
            violation = fairplayViolations[1]
        elif fairplayViolations[0] != 0:
            penaltyType = 'warning'
            violation = fairplayViolations[0]
        violationName = getFairPlayViolationName(violation)
        msgID = 'punishmentWindow/reason/{}'.format(violationName)
        metaClass = I18PunishmentDialogMeta
        key = 'punishmentWindow'
        messageCtx = {'penaltyType': penaltyType,
         'arenaName': i18n.makeString(arenaType.name),
         'time': TimeFormatter.getActualMsgTimeStr(arenaCreateTime),
         'reason': i18n.makeString(_getLocalizationPunishmentString(msgID, violationName)),
         'violationName': violationName}
    ctx = {'messageCtx': messageCtx,
     'showWindowCallback': None}
    g_extPlayerEvents.onExtGetCustomPunishmentWindow(ctx)
    showWindowCallback = ctx.get('showWindowCallback')
    if showWindowCallback is not None:
        showWindowCallback()
        ctx = None
    else:
        showDialog(metaClass(key, None, messageCtx), lambda *args: None)
    return


def _getLocalizationPunishmentString(msgID, violationName):
    if 'event' in violationName:
        res = EVENT.all(msgID)
    else:
        res = DIALOGS.all(msgID)
    return res
