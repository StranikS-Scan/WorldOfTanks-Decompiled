# Embedded file name: scripts/client/gui/prb_control/formatters/invites.py
from constants import PREBATTLE_TYPE_NAMES, PREBATTLE_TYPE
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
from gui.prb_control.settings import PRB_INVITE_STATE
from gui.shared.fortifications import formatters as fort_fmt
from helpers import i18n, html
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


def getPrbInviteStateName(state):
    try:
        stateName = PRB_INVITE_STATE.getKeyByValue(state)
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
        return {'sender': invite.senderFullName,
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
        if not comment:
            return ''
        return makeHtmlString('html_templates:lobby/prebattle', 'inviteComment', {'comment': i18n.makeString(I18N_INVITES.INVITES_COMMENT, comment=html.escape(comment))})

    def getNote(self, invite):
        note = ''
        if self.prbInvites.canAcceptInvite(invite):
            if self.prbDispatcher:
                note = getLeaveOrChangeText(self.prbDispatcher.getFunctionalState(), invite.type, invite.peripheryID)
        else:
            note = getAcceptNotAllowedText(invite.type, invite.peripheryID, invite.isActive(), invite.alreadyJoined)
        if len(note):
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


class PrbFortBattleInviteHtmlTextFormatter(PrbInviteHtmlTextFormatter):

    def getTitle(self, invite):
        extraData = invite.getExtraData()
        regularInviteTitle = super(PrbFortBattleInviteHtmlTextFormatter, self).getTitle(invite)
        if 'enemyClanAbbrev' in extraData:
            enemyClanAbbrev = '[%s]' % extraData['enemyClanAbbrev']
        else:
            enemyClanAbbrev = ''
        return makeHtmlString('html_templates:lobby/prebattle', 'inviteFortTitle', ctx={'inviteRegularTitle': regularInviteTitle,
         'dir': fort_fmt.getDirectionString(extraData['direction']),
         'clanAbbrev': enemyClanAbbrev,
         'time': fort_fmt.getDefencePeriodString(extraData['attackTime'])}, sourceKey='defence' if extraData.get('isDefence') else 'offence')

    def getIconName(self, invite):
        if invite.getExtraData('isDefence'):
            return 'fortBattleDefenceInviteIcon'
        return 'fortBattleOffenceInviteIcon'


class FalloutInviteHtmlTextFormatter(PrbInviteHtmlTextFormatter):

    def getTitle(self, invite):
        if invite.senderFullName:
            creatorName = makeHtmlString('html_templates:lobby/prebattle', 'inviteTitleCreatorName', ctx={'name': invite.senderFullName})
        else:
            creatorName = ''
        return makeHtmlString('html_templates:lobby/prebattle', 'inviteTitle', ctx={'sender': creatorName,
         'battleType': i18n.makeString('#invites:invites/text/fallout/%d' % invite.getExtraData().get('falloutBattleType'))}, sourceKey='FALLOUT')


def getPrbInviteHtmlFormatter(invite):
    if invite.type == PREBATTLE_TYPE.FORT_BATTLE:
        return PrbFortBattleInviteHtmlTextFormatter()
    if invite.getExtraData().get('falloutBattleType'):
        return FalloutInviteHtmlTextFormatter()
    return PrbInviteHtmlTextFormatter()


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
