# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/formatters/invites.py
from constants import PREBATTLE_TYPE_NAMES, PREBATTLE_TYPE
from constants import QUEUE_TYPE_NAMES
from debug_utils import LOG_ERROR
from gui import makeHtmlString
from gui.Scaleform.locale.INVITES import INVITES as I18N_INVITES
from gui.prb_control.formatters import getPrebattleFullDescription
from gui.prb_control.formatters import getBattleSessionStartTimeString
from gui.prb_control import prbDispatcherProperty, prbAutoInvitesProperty, prbInvitesProperty
from gui.prb_control.settings import PRB_INVITE_STATE
from helpers import dependency
from helpers import i18n, html
from messenger.ext import passCensor
from skeletons.gui.lobby_context import ILobbyContext

def getPrbName(prbType, lowercase=False):
    try:
        prbName = PREBATTLE_TYPE_NAMES[prbType]
        if lowercase:
            prbName = prbName.lower()
    except KeyError:
        LOG_ERROR('Prebattle name not found', prbType)
        prbName = 'N/A'

    return prbName


def getPreQueueName(queueType, lowercase=False):
    try:
        queueName = QUEUE_TYPE_NAMES[queueType]
        if lowercase:
            queueName = queueName.lower()
    except KeyError:
        LOG_ERROR('PreQueue name not found', queueType)
        queueName = 'N/A'

    return queueName


def getPrbInviteStateName(state):
    try:
        stateName = PRB_INVITE_STATE.getKeyByValue(state)
    except KeyError:
        LOG_ERROR('State of prebattle invite not found', state)
        stateName = 'N/A'

    return stateName


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getAcceptNotAllowedText(prbType, peripheryID, isInviteActive=True, isAlreadyJoined=False, lobbyContext=None):
    key, kwargs = None, {}
    if lobbyContext is not None:
        isAnotherPeriphery = lobbyContext.isAnotherPeriphery(peripheryID)
    else:
        isAnotherPeriphery = False
    if isInviteActive:
        if isAlreadyJoined:
            key = I18N_INVITES.invites_prebattle_alreadyjoined(getPrbName(prbType))
        elif isAnotherPeriphery:
            host = lobbyContext.getPeripheryName(peripheryID)
            if host:
                key = I18N_INVITES.invites_prebattle_acceptnotallowed('otherPeriphery')
                kwargs = {'host': host}
            else:
                key = I18N_INVITES.invites_prebattle_acceptnotallowed('undefinedPeriphery')
    if key:
        text = i18n.makeString(key, **kwargs)
    else:
        text = ''
    return text


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getLeaveOrChangeText(funcState, invitePrbType, peripheryID, lobbyContext=None):
    key, kwargs = None, {}
    if lobbyContext is not None:
        isAnotherPeriphery = lobbyContext.isAnotherPeriphery(peripheryID)
    else:
        isAnotherPeriphery = False
    if funcState.doLeaveToAcceptInvite(invitePrbType):
        if funcState.isInLegacy() or funcState.isInUnit():
            entityName = getPrbName(funcState.entityTypeID)
        elif funcState.isInPreQueue():
            entityName = getPreQueueName(funcState.entityTypeID)
        else:
            LOG_ERROR('Can not resolve name of entity', funcState)
            return ''
        if isAnotherPeriphery:
            key = I18N_INVITES.invites_note_change_and_leave(entityName)
            kwargs = {'host': lobbyContext.getPeripheryName(peripheryID) or ''}
        else:
            key = I18N_INVITES.invites_note_leave(entityName)
    elif isAnotherPeriphery:
        key = I18N_INVITES.INVITES_NOTE_SERVER_CHANGE
        kwargs = {'host': lobbyContext.getPeripheryName(peripheryID) or ''}
    if key:
        text = i18n.makeString(key, **kwargs)
    else:
        text = ''
    return text


class InviteFormatter(object):

    def getCtx(self, invite):
        return {'sender': invite.senderFullName,
         'receiver': invite.receiverFullName}

    def getNote(self, invite):
        pass

    def getText(self, invite):
        pass


class PrbInviteHtmlTextFormatter(InviteFormatter):

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def getIconName(self, invite):
        return '{0:>s}InviteIcon'.format(getPrbName(invite.type, True))

    def getTitle(self, invite):
        if invite.senderFullName:
            creatorName = makeHtmlString('html_templates:lobby/prebattle', 'inviteTitleCreatorName', ctx={'name': invite.senderFullName})
        else:
            creatorName = ''
        return makeHtmlString('html_templates:lobby/prebattle', 'inviteTitle', ctx={'sender': creatorName}, sourceKey=getPrbName(invite.type))

    def getComment(self, invite):
        comment = passCensor(invite.comment)
        return '' if not comment else makeHtmlString('html_templates:lobby/prebattle', 'inviteComment', {'comment': i18n.makeString(I18N_INVITES.INVITES_COMMENT, comment=html.escape(comment))})

    def getNote(self, invite):
        note = ''
        if self.prbInvites.canAcceptInvite(invite):
            if self.prbDispatcher:
                note = getLeaveOrChangeText(self.prbDispatcher.getFunctionalState(), invite.type, invite.peripheryID)
        else:
            note = getAcceptNotAllowedText(invite.type, invite.peripheryID, invite.isActive(), invite.alreadyJoined)
        if note:
            note = makeHtmlString('html_templates:lobby/prebattle', 'inviteNote', {'note': note})
        return note

    def getState(self, invite):
        key = I18N_INVITES.invites_state(getPrbInviteStateName(invite.getState()))
        if not key:
            return ''
        state = i18n.makeString(key)
        if state:
            state = makeHtmlString('html_templates:lobby/prebattle', 'inviteState', {'state': state})
        return state

    def getText(self, invite):
        result = []
        text = self.getTitle(invite)
        if text:
            result.append(text)
        text = self.getComment(invite)
        if text:
            result.append(text)
        text = self.getNote(invite)
        if text:
            result.append(text)
        text = self.getState(invite)
        if text:
            result.append(text)
        return ''.join(result)


class PrbExternalBattleInviteHtmlTextFormatter(PrbInviteHtmlTextFormatter):

    def getComment(self, invite):
        comment = passCensor(invite.comment)
        return '' if not comment else makeHtmlString('html_templates:lobby/prebattle', 'inviteComment', {'comment': html.escape(comment)})


def getPrbInviteHtmlFormatter(invite):
    return PrbExternalBattleInviteHtmlTextFormatter() if invite.type == PREBATTLE_TYPE.EXTERNAL else PrbInviteHtmlTextFormatter()


class PrbInviteTitleFormatter(InviteFormatter):

    def getText(self, _):
        return i18n.makeString(I18N_INVITES.GUI_TITLES_INVITE)


class AutoInviteTextFormatter(InviteFormatter):

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @prbAutoInvitesProperty
    def prbAutoInvites(self):
        return None

    def getNote(self, invite):
        note = ''
        if self.prbAutoInvites.canAcceptInvite(invite):
            if self.prbAutoInvites:
                note = getLeaveOrChangeText(self.prbDispatcher.getFunctionalState(), invite.prbType, invite.peripheryID)
        else:
            note = getAcceptNotAllowedText(invite.prbType, invite.peripheryID)
        return note

    def getText(self, invite):
        return u'%s, %s' % (unicode(getPrebattleFullDescription(invite.description), 'utf-8'), unicode(getBattleSessionStartTimeString(invite.startTime), 'utf-8'))


class _PrbInviteInfo(object):

    def as_dict(self):
        raise NotImplementedError


class PrbAutoInviteInfo(_PrbInviteInfo):

    def __init__(self, prbID):
        self.__prbID = prbID

    @prbAutoInvitesProperty
    def prbAutoInvites(self):
        return None

    def getID(self):
        return self.__prbID

    def getTitle(self):
        return PrbInviteTitleFormatter().getText(None)

    def as_dict(self):
        invite = self.prbAutoInvites.getInvite(self.__prbID)
        canAccept = self.prbAutoInvites.canAcceptInvite(invite)
        formatter = AutoInviteTextFormatter()
        result = {'id': self.__prbID,
         'text': formatter.getText(invite),
         'comment': '',
         'note': formatter.getNote(invite),
         'canAccept': canAccept,
         'canDecline': True,
         'isAcceptVisible': True,
         'isDeclineVisible': False}
        return result
