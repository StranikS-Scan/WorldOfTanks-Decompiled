# Embedded file name: scripts/client/gui/prb_control/formatters/invites.py
from constants import PREBATTLE_TYPE_NAMES, PREBATTLE_INVITE_STATE
from constants import QUEUE_TYPE_NAMES
from debug_utils import LOG_ERROR
from gui import makeHtmlString
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.locale.INVITES import INVITES as I18N_INVITES
from gui.prb_control.formatters import getPrebattleFullDescription
from gui.prb_control.formatters import getBattleSessionStartTimeString
from gui.prb_control.prb_helpers import prbInvitesProperty
from gui.prb_control.prb_helpers import prbDispatcherProperty
from gui.prb_control.prb_helpers import prbAutoInvitesProperty
from helpers import i18n
from messenger.ext import passCensor

def getPrbName(prbType, lowercase = False):
    try:
        prbName = PREBATTLE_TYPE_NAMES[prbType]
        if lowercase:
            prbName = prbName.lower()
    except KeyError:
        LOG_ERROR('Prebattle name not found', prbType)
        prbName = 'N/A'

    return prbName


def getPreQueueName(queueType, lowercase = False):
    try:
        queueName = QUEUE_TYPE_NAMES[queueType]
        if lowercase:
            queueName = queueName.lower()
    except KeyError:
        LOG_ERROR('PreQueue name not found', queueType)
        queueName = 'N/A'

    return queueName


PREBATTLE_INVITE_STATE_NAMES = dict([ (v, k) for k, v in PREBATTLE_INVITE_STATE.__dict__.iteritems() if not k.startswith('_') ])

def getPrbInviteStateName(state):
    try:
        stateName = PREBATTLE_INVITE_STATE_NAMES[state]
    except KeyError:
        LOG_ERROR('State of prebattle invite not found', state)
        stateName = 'N/A'

    return stateName


def getAcceptNotAllowedText(prbType, peripheryID, isInviteActive = True, isAlreadyJoined = False):
    key, kwargs = None, {}
    isAnotherPeriphery = g_lobbyContext.isAnotherPeriphery(peripheryID)
    if isInviteActive:
        if isAlreadyJoined:
            key = I18N_INVITES.invites_prebattle_alreadyjoined(getPrbName(prbType))
        elif isAnotherPeriphery:
            host = g_lobbyContext.getPeripheryName(peripheryID)
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


def getLeaveOrChangeText(funcState, invitePrbType, peripheryID):
    key, kwargs = None, {}
    isAnotherPeriphery = g_lobbyContext.isAnotherPeriphery(peripheryID)
    if funcState.doLeaveToAcceptInvite(invitePrbType):
        if funcState.isInPrebattle() or funcState.isInUnit():
            entityName = getPrbName(funcState.entityTypeID)
        elif funcState.isInPreQueue():
            entityName = getPreQueueName(funcState.entityTypeID)
        else:
            LOG_ERROR('Can not resolve name of entity', funcState)
            return ''
        if isAnotherPeriphery:
            key = I18N_INVITES.invites_note_change_and_leave(entityName)
            kwargs = {'host': g_lobbyContext.getPeripheryName(peripheryID) or ''}
        else:
            key = I18N_INVITES.invites_note_leave(entityName)
    elif isAnotherPeriphery:
        key = I18N_INVITES.INVITES_NOTE_SERVER_CHANGE
        kwargs = {'host': g_lobbyContext.getPeripheryName(peripheryID) or ''}
    if key:
        text = i18n.makeString(key, **kwargs)
    else:
        text = ''
    return text


class InviteFormatter(object):

    def getCtx(self, invite):
        return {'sender': invite.creatorFullName,
         'receiver': invite.receiverFullName}

    def getNote(self, invite):
        return ''

    def getText(self, invite):
        return ''


class PrbInviteHtmlTextFormatter(InviteFormatter):

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    @prbInvitesProperty
    def prbInvites(self):
        return None

    def getTitle(self, invite):
        return makeHtmlString('html_templates:lobby/prebattle', 'inviteTitle', ctx={'sender': invite.creatorFullName}, sourceKey=getPrbName(invite.type))

    def getComment(self, invite):
        comment = passCensor(invite.comment)
        if not comment:
            return ''
        return makeHtmlString('html_templates:lobby/prebattle', 'inviteComment', {'comment': i18n.makeString(I18N_INVITES.INVITES_COMMENT, comment=comment)})

    def getNote(self, invite):
        if self.prbInvites.canAcceptInvite(invite):
            note = getLeaveOrChangeText(self.prbDispatcher.getFunctionalState(), invite.type, invite.peripheryID)
        else:
            note = getAcceptNotAllowedText(invite.type, invite.peripheryID, invite.isActive(), invite.alreadyJoined)
        if len(note):
            note = makeHtmlString('html_templates:lobby/prebattle', 'inviteNote', {'note': note})
        return note

    def getState(self, invite):
        key = I18N_INVITES.invites_state(getPrbInviteStateName(invite.state))
        if not key:
            return ''
        state = i18n.makeString(key)
        if state:
            state = makeHtmlString('html_templates:lobby/prebattle', 'inviteState', {'state': state})
        return state

    def getText(self, invite):
        result = []
        text = self.getTitle(invite)
        if len(text):
            result.append(text)
        text = self.getComment(invite)
        if len(text):
            result.append(text)
        text = self.getNote(invite)
        if len(text):
            result.append(text)
        text = self.getState(invite)
        if len(text):
            result.append(text)
        return ''.join(result)


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
        if self.prbAutoInvites.canAcceptInvite(invite):
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
