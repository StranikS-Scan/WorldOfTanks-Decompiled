# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clans/formatters.py
import BigWorld
from client_request_lib.exceptions import ResponseCodes
from gui import makeHtmlString
from gui.shared.formatters.text_styles import standard as standard_text_style, alert as alert_text_style
from helpers.i18n import doesTextExist, makeString
from gui.wgcg.settings import WebRequestDataType as REQUEST_TYPE
from gui.clans.settings import CLAN_MEMBERS
ERROR_SYS_MSG_TPL = '#system_messages:clans/request/errors/%s'
DUMMY_UNAVAILABLE_DATA = '--'
DUMMY_NULL_DATA = '--'

def _makeHtmlString(style, ctx=None):
    if ctx is None:
        ctx = {}
    return makeHtmlString('html_templates:lobby/clans', style, ctx)


def getHtmlLineDivider(margin=3):
    return _makeHtmlString('lineDivider', {'margin': margin})


def formatInvitesCount(count):
    if count is None:
        count = DUMMY_UNAVAILABLE_DATA
    elif count <= 999:
        count = str(count)
    elif count <= 99999:
        count = '{}K'.format(int(count / 1000))
    else:
        count = '99K+'
    return count


def formatDataToString(data):
    return DUMMY_UNAVAILABLE_DATA if data is None else str(data)


def formatShortDateShortTimeString(timestamp):
    return str(' ').join((BigWorld.wg_getShortDateFormat(timestamp), '  ', BigWorld.wg_getShortTimeFormat(timestamp)))


_CUSTOM_ERR_MESSAGES_BY_REQUEST = {REQUEST_TYPE.CREATE_INVITES: lambda result, ctx: ''}
_CUSTOM_ERR_MESSAGES = {(REQUEST_TYPE.CLAN_GLOBAL_MAP_STATS, ResponseCodes.GLOBAL_MAP_ERROR): '',
 (REQUEST_TYPE.CLAN_RATINGS, ResponseCodes.WGRS_ERROR): '',
 (REQUEST_TYPE.CLAN_GLOBAL_MAP_STATS, ResponseCodes.CLAN_DOES_NOT_EXIST): '',
 (REQUEST_TYPE.CLAN_INFO, ResponseCodes.WGCCBE_ERROR): '',
 (REQUEST_TYPE.CLAN_APPLICATIONS, ResponseCodes.WGCCBE_ERROR): '',
 (REQUEST_TYPE.CLAN_INVITES, ResponseCodes.WGCCBE_ERROR): '',
 (REQUEST_TYPE.ACCOUNT_INVITES, ResponseCodes.WGCCBE_ERROR): '',
 (REQUEST_TYPE.CLAN_ACCOUNTS, ResponseCodes.WGCCBE_ERROR): '',
 (REQUEST_TYPE.ACCEPT_INVITE, ResponseCodes.CLAN_IN_TRANSACTION): 'DEFAULT',
 (REQUEST_TYPE.DECLINE_INVITE, ResponseCodes.CLAN_IN_TRANSACTION): 'DEFAULT',
 (REQUEST_TYPE.DECLINE_INVITES, ResponseCodes.CLAN_IN_TRANSACTION): 'DEFAULT',
 (REQUEST_TYPE.ACCEPT_APPLICATION, ResponseCodes.CLAN_IN_TRANSACTION): 'DEFAULT',
 (REQUEST_TYPE.DECLINE_APPLICATION, ResponseCodes.CLAN_IN_TRANSACTION): 'DEFAULT'}

def getRequestErrorMsg(result, ctx):
    msgReqKey = ctx.getRequestType()
    msgKey = (msgReqKey, result.code)
    if msgKey in _CUSTOM_ERR_MESSAGES:
        errorMsg = _CUSTOM_ERR_MESSAGES[msgKey]
    elif msgReqKey in _CUSTOM_ERR_MESSAGES_BY_REQUEST:
        errorMsg = _CUSTOM_ERR_MESSAGES_BY_REQUEST[msgReqKey]
    else:
        errorMsg = result.txtStr
    msg = ''
    if callable(errorMsg):
        msg = errorMsg(result, ctx)
    else:
        key = ERROR_SYS_MSG_TPL % errorMsg
        if doesTextExist(key):
            msg = makeString(key)
    return msg


def getRequestUserName(rqTypeID):
    return _sysMsg('clan/request/name/%s' % REQUEST_TYPE.getKeyByValue(rqTypeID))


def getClanRoleString(position):
    return makeString('#menu:profile/header/clan/position/%s' % CLAN_MEMBERS[position]) if position in CLAN_MEMBERS else ''


def getClanRoleIcon(role):
    return '../maps/icons/clans/roles/%s.png' % CLAN_MEMBERS[role] if role in CLAN_MEMBERS else ''


def getClanAbbrevString(clanAbbrev):
    return '[{0:>s}]'.format(clanAbbrev)


def getClanFullName(clanName, clanAbbrev):
    return '{} {}'.format(getClanAbbrevString(clanAbbrev), clanName)


def getAppSentSysMsg(clanName, clanAbbrev):
    return _sysMsg('clans/notifications/requestSent', clanName=getClanFullName(clanName, clanAbbrev))


def getInviteNotSentSysMsg(accountName, specKey=None):
    key = specKey or 'clans/notifications/inviteSendError'
    return _sysMsg(key, userName=accountName)


def getInvitesNotSentSysMsg(accountNames):
    return _formatMsg(accountNames, 'clans/notifications/inviteSendError', 'clans/notifications/invitesSendError')


def getInvitesSentSysMsg(accountNames):
    return _formatMsg(accountNames, 'clans/notifications/inviteSent', 'clans/notifications/invitesSent')


def _formatMsg(items, singleKey, multiKey):
    count = len(items)
    if count == 1:
        msg = _sysMsg(singleKey, userName=items[0])
    else:
        msg = _sysMsg(multiKey, userCount=count)
    return msg


def _sysMsg(i18nKey, *args, **kwargs):
    return makeString(('#system_messages:%s' % i18nKey), *args, **kwargs)


class _BaseClanAppHtmlTextFormatter(object):

    def __init__(self, titleKey, commentKey):
        super(_BaseClanAppHtmlTextFormatter, self).__init__()
        self._commentKey = commentKey
        self._titleKey = titleKey

    def getText(self, entity):
        result = []
        text = self.getTitle(entity)
        if text:
            result.append(text)
        text = self.getComment(entity)
        if text:
            result.append(text)
        return ''.join(result)

    def getTitle(self, entity):
        return makeHtmlString('html_templates:lobby/clans', self._titleKey, {'appsCount': entity})

    def getComment(self, entity):
        return makeHtmlString('html_templates:lobby/clans', self._commentKey)


class ClanMultiNotificationsHtmlTextFormatter(_BaseClanAppHtmlTextFormatter):

    def __init__(self, titleKey, commentKey, commentAction):
        self.__commentAction = commentAction
        super(ClanMultiNotificationsHtmlTextFormatter, self).__init__(titleKey, commentKey)

    def getTitle(self, entity):
        return makeHtmlString('html_templates:lobby/clans', self._titleKey, {'appsCount': entity})

    def getComment(self, entity):
        return makeHtmlString('html_templates:lobby/clans', self._commentKey) % {'eventType': self.__commentAction}


class ClanSingleNotificationHtmlTextFormatter(_BaseClanAppHtmlTextFormatter):

    def __init__(self, titleKey, commentKey, commentAction):
        self.__commentAction = commentAction
        super(ClanSingleNotificationHtmlTextFormatter, self).__init__(titleKey, commentKey)

    def getTitle(self, uName):
        return makeHtmlString('html_templates:lobby/clans', self._titleKey, {'name': uName})

    def getComment(self, _):
        return makeHtmlString('html_templates:lobby/clans', self._commentKey) % {'eventType': self.__commentAction}

    def getText(self, data):
        userName, state, isWarning = data
        text = super(ClanSingleNotificationHtmlTextFormatter, self).getText(userName)
        stateTxt = self._getStateText(state, isWarning)
        if stateTxt:
            text += stateTxt
        return text

    def _getStateText(self, state, isWarning):
        if not doesTextExist(state):
            return ''
        stateStr = makeString(state)
        if stateStr:
            if isWarning:
                stateStr = '<br/><br/>%s' % alert_text_style(stateStr)
            else:
                stateStr = '<br/><br/>%s' % standard_text_style(stateStr)
        return stateStr


class ClanAppActionHtmlTextFormatter(object):

    def __init__(self, actType):
        super(ClanAppActionHtmlTextFormatter, self).__init__()
        self.__actType = actType

    def getTitle(self):
        pass

    def getComment(self, clanName):
        return makeHtmlString('html_templates:lobby/clans/', self.__actType, ctx={'name': clanName})

    def getText(self, clanName):
        result = []
        text = self.getTitle()
        if text:
            result.append(text)
        text = self.getComment(clanName)
        if text:
            result.append(text)
        return ''.join(result)
