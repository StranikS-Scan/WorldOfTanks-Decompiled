# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/dialogs/__init__.py
import BigWorld
from constants import ACCOUNT_KICK_REASONS, IS_CHINA
from gui import makeHtmlString
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.impl import backport
from gui.shared import events
from helpers import i18n, time_utils
I18N_PRICE_KEY = '{0:>s}/messagePrice'
I18N_TITLE_KEY = '{0:>s}/title'
I18N_MESSAGE_KEY = '{0:>s}/message'
I18N_CANCEL_KEY = '{0:>s}/cancel'
I18N_SUBMIT_KEY = '{0:>s}/submit'

def _getDialogStr(i18nKey):
    return '#dialogs:%s' % i18nKey


class DIALOG_BUTTON_ID(object):
    SUBMIT = 'submit'
    CLOSE = 'close'
    HYPERLINK = 'hyperLink'


class IDialogMeta(object):

    def getEventType(self):
        raise NotImplementedError('Dialog event type must be specified')

    def getViewScopeType(self):
        raise NotImplementedError('Dialog scope must be specified')


class ISimpleDialogButtonsMeta(object):

    def getLabels(self):
        pass


class ISimpleDialogMeta(IDialogMeta):

    def getTitle(self):
        pass

    def getMessage(self):
        pass

    def getButtonLabels(self):
        return []

    def getTimer(self):
        pass


class InfoDialogButtons(ISimpleDialogButtonsMeta):

    def __init__(self, close):
        super(InfoDialogButtons, self).__init__()
        self._close = close

    def getLabels(self):
        return [{'id': DIALOG_BUTTON_ID.CLOSE,
          'label': self._close,
          'focused': True}]


class ConfirmDialogButtons(InfoDialogButtons):

    def __init__(self, submit, close):
        super(ConfirmDialogButtons, self).__init__(close)
        self._submit = submit

    def getLabels(self):
        return [{'id': DIALOG_BUTTON_ID.SUBMIT,
          'label': self._submit,
          'focused': True}, {'id': DIALOG_BUTTON_ID.SUBMIT,
          'label': self._close,
          'focused': False}]


class I18nInfoDialogButtons(ISimpleDialogButtonsMeta):

    def __init__(self, i18nKey='common', buttonID=DIALOG_BUTTON_ID.CLOSE):
        super(I18nInfoDialogButtons, self).__init__()
        self._i18nKey = i18nKey
        self._buttonID = buttonID

    def getLabels(self):
        return [{'id': self._buttonID,
          'label': _getDialogStr(I18N_CANCEL_KEY.format(self._i18nKey)),
          'focused': True}]


class I18nConfirmDialogButtons(I18nInfoDialogButtons):

    def __init__(self, i18nKey='common', focusedIndex=None):
        super(I18nInfoDialogButtons, self).__init__()
        self._i18nKey = i18nKey
        self._focusedIndex = focusedIndex

    def getLabels(self):
        return [self.__getButtonInfoObject(DIALOG_BUTTON_ID.SUBMIT, _getDialogStr(I18N_SUBMIT_KEY.format(self._i18nKey)), self._focusedIndex == DIALOG_BUTTON_ID.SUBMIT if self._focusedIndex is not None else True), self.__getButtonInfoObject(DIALOG_BUTTON_ID.CLOSE, _getDialogStr(I18N_CANCEL_KEY.format(self._i18nKey)), self._focusedIndex == DIALOG_BUTTON_ID.CLOSE if self._focusedIndex is not None else False)]

    def __getButtonInfoObject(self, buttonID, label, focused):
        return {'id': buttonID,
         'label': label,
         'focused': focused}


class SimpleDialogMeta(ISimpleDialogMeta):

    def __init__(self, title=None, message=None, buttons=None, timer=0, scope=ScopeTemplates.DEFAULT_SCOPE):
        super(SimpleDialogMeta, self).__init__()
        self._title = title
        self._message = message
        self._buttons = buttons
        self._timer = timer
        self._scope = scope

    def getTitle(self):
        return self._title

    def getMessage(self):
        return self._message

    def getButtonLabels(self):
        return self._buttons.getLabels() if self._buttons is not None else []

    def getTimer(self):
        return self._timer

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_SIMPLE_DLG

    def getCallbackWrapper(self, callback):
        return callback

    def getViewScopeType(self):
        return self._scope


class I18nDialogMeta(SimpleDialogMeta):

    def __init__(self, key, buttons, titleCtx=None, messageCtx=None, meta=None, scope=ScopeTemplates.DEFAULT_SCOPE):
        super(I18nDialogMeta, self).__init__(scope=scope)
        self._key = key
        self._titleCtx = titleCtx if titleCtx is not None else {}
        self._messageCtx = messageCtx if messageCtx is not None else {}
        self._buttons = buttons
        self._meta = meta
        return

    def getTitle(self):
        result = None
        if self._meta is not None:
            result = self._meta.getTitle()
        if not result:
            result = self._makeString(I18N_TITLE_KEY.format(self._key), self._titleCtx)
        return result

    def getMessage(self):
        result = None
        if self._meta is not None:
            result = self._meta.getMessage()
        if not result:
            result = self._makeString(I18N_MESSAGE_KEY.format(self._key), self._messageCtx)
        return result

    def getButtonLabels(self):
        if self._buttons is not None:
            return self._buttons.getLabels()
        else:
            return self._meta.getButtonLabels() if self._meta is not None else []

    def getTimer(self):
        result = self._timer
        if self._meta is not None:
            result = self._meta.getTimer()
        return result

    def getKey(self):
        return self._meta.getKey() if self._meta else self._key

    def _makeString(self, key, ctx):
        return i18n.makeString(_getDialogStr(key), **ctx)

    def getViewScopeType(self):
        return self._meta.getViewScopeType() if self._meta is not None else super(I18nDialogMeta, self).getViewScopeType()


class I18nInfoDialogMeta(I18nDialogMeta):

    def __init__(self, key, titleCtx=None, messageCtx=None, meta=None, scope=ScopeTemplates.VIEW_SCOPE):
        buttons = I18nInfoDialogButtons(key)
        super(I18nInfoDialogMeta, self).__init__(key, buttons, titleCtx, messageCtx, meta, scope)


class I18nConfirmDialogMeta(I18nDialogMeta):

    def __init__(self, key, titleCtx=None, messageCtx=None, meta=None, focusedID=None, scope=ScopeTemplates.VIEW_SCOPE):
        buttons = I18nConfirmDialogButtons(key, focusedID)
        super(I18nConfirmDialogMeta, self).__init__(key, buttons, titleCtx, messageCtx, meta, scope)


class IconDialogMeta(I18nConfirmDialogMeta):

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_ICON_DIALOG

    def getIcon(self):
        result = None
        if self._meta is not None:
            result = self._meta.getIcon()
        if not result:
            result = self._messageCtx.get('icon')
        return result


class IconPriceDialogMeta(IconDialogMeta):

    def __init__(self, key, titleCtx=None, messageCtx=None, meta=None, focusedID=None):
        super(IconPriceDialogMeta, self).__init__(key, titleCtx, messageCtx, meta, focusedID)
        self._operationPrice = self.__calcMessagePrice()
        self._action = self.__calcAction()
        self._item = messageCtx.get('item')

    def __calcMessagePrice(self):
        result = None
        if self._meta is not None:
            result = self._meta.getMessagePrice()
        if not result:
            result = self._messageCtx.get('price')
        return result

    def __calcAction(self):
        result = None
        if self._meta is not None:
            result = self._meta.getAction()
        if not result:
            result = self._messageCtx.get('action')
        return result

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_ICON_PRICE_DIALOG

    def getMessagePrice(self):
        return self._operationPrice

    def getAction(self):
        return self._action


class PMConfirmationDialogMeta(IconDialogMeta):

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_PM_CONFIRMATION_DIALOG


class HtmlMessageDialogMeta(SimpleDialogMeta):

    def __init__(self, path, key, ctx=None, scope=ScopeTemplates.VIEW_SCOPE, sourceKey='text'):
        super(HtmlMessageDialogMeta, self).__init__(scope=scope)
        self._path = path
        self._key = key
        self._ctx = ctx
        self._sourceKey = sourceKey

    def getTitle(self):
        return None

    def getMessage(self):
        return makeHtmlString(self._path, self._key, ctx=self._ctx, sourceKey=self._sourceKey)


class HtmlMessageLocalDialogMeta(HtmlMessageDialogMeta):

    def __init__(self, path, key, ctx=None):
        super(HtmlMessageLocalDialogMeta, self).__init__(path, key, ctx, ScopeTemplates.LOBBY_SUB_SCOPE)


class DisconnectMeta(I18nInfoDialogMeta):

    def __init__(self, reason=None, kickReasonType=ACCOUNT_KICK_REASONS.UNKNOWN, expiryTime=None):
        super(DisconnectMeta, self).__init__('disconnected', scope=ScopeTemplates.GLOBAL_SCOPE)
        self.reason = reason
        self.kickReasonType = kickReasonType
        self.expiryTime = expiryTime
        if hasattr(BigWorld.player(), 'setForcedGuiControlMode'):
            BigWorld.player().setForcedGuiControlMode(False)

    def getCallbackWrapper(self, callback):

        def wrapper(args):
            callback(args)

        return wrapper

    def getMessage(self):
        formatArgs = {'reason': '',
         'expiryTime': ''}
        if self.reason:
            formatArgs['reason'] = i18n.makeString(DIALOGS.DISCONNECTED_REASON, i18n.makeString(self.reason))
        if self.expiryTime:
            expiryTime = time_utils.makeLocalServerTime(int(self.expiryTime))
            formatArgs['expiryTime'] = '%s %s' % (backport.getLongDateFormat(expiryTime), backport.getLongTimeFormat(expiryTime))
        key = DIALOGS.DISCONNECTED_MESSAGEKICK
        if self.kickReasonType in ACCOUNT_KICK_REASONS.BAN_RANGE:
            if IS_CHINA and self.kickReasonType == ACCOUNT_KICK_REASONS.CURFEW_BAN:
                return i18n.makeString(self.reason)
            key = DIALOGS.DISCONNECTED_MESSAGEBANPERIOD if self.expiryTime else DIALOGS.DISCONNECTED_MESSAGEBAN
        return i18n.makeString(key, **formatArgs)


class TimerConfirmDialogMeta(I18nConfirmDialogMeta):

    def __init__(self, key, titleCtx=None, messageCtx=None, meta=None, focusedID=None, timer=0):
        super(TimerConfirmDialogMeta, self).__init__(key, titleCtx, messageCtx, meta, focusedID)
        self._timer = timer


class CheckBoxDialogMeta(I18nConfirmDialogMeta):

    def __init__(self, key, titleCtx=None, messageCtx=None, meta=None, focusedID=None, scope=ScopeTemplates.VIEW_SCOPE, selected=False):
        self.__checkBoxSelected = selected
        super(CheckBoxDialogMeta, self).__init__(key, titleCtx, messageCtx, meta, focusedID, scope)

    def getEventType(self):
        return events.ShowDialogEvent.SHOW_CHECK_BOX_DIALOG

    def getButtonsSubmitCancel(self):
        submit, cancel = self.getButtonLabels()
        return {'submit': i18n.makeString(submit['label']),
         'cancel': i18n.makeString(cancel['label'])}

    def getCheckBoxButtonLabel(self):
        return self._makeString('%s/checkBox' % self._key, {})

    def getCheckBoxSelected(self):
        return self.__checkBoxSelected

    def getViewScopeType(self):
        return ScopeTemplates.DYNAMIC_SCOPE
