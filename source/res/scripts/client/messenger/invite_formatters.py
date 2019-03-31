# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/invite_formatters.py
# Compiled at: 2018-11-29 14:33:44
from constants import PREBATTLE_TYPE, PREBATTLE_INVITE_STATE
from helpers import i18n
from messenger import INVITES_I18N_FILE, getLongDatetimeFormat, g_settings
import types
from predefined_hosts import g_preDefinedHosts
DEFAULT_INVITE_I18N_TEXT_KEY = '#' + INVITES_I18N_FILE + ':invites/%s/invite'
PRB_INVITE_I18N_TEXT_KEYS = {PREBATTLE_INVITE_STATE.ACTIVE: DEFAULT_INVITE_I18N_TEXT_KEY,
 PREBATTLE_INVITE_STATE.ACCEPTED: '#' + INVITES_I18N_FILE + ':invites/%s/accept',
 PREBATTLE_INVITE_STATE.DECLINED: '#' + INVITES_I18N_FILE + ':invites/%s/reject',
 PREBATTLE_INVITE_STATE.EXPIRED: ('#' + INVITES_I18N_FILE + ':invites/%s/invalidInvite/sender-side', '#' + INVITES_I18N_FILE + ':invites/%s/invalidInvite/receiver-side')}
INVITE_I18N_TITLE_KEY = '#' + INVITES_I18N_FILE + ':gui/titles/%s'

class InviteFormatter(object):

    def kArgs(self, invite):
        return {'creator': invite.creator,
         'receiver': invite.receiver}

    def getTypeName(self, _):
        return None

    def getTemplate(self, _):
        return None

    def getNoteText(self, _):
        pass

    def format(self, invite, addNote=True):
        text = str()
        kargs = self.kArgs(invite)
        template = self.getTemplate(invite)
        typeName = self.getTypeName(invite)
        if template and typeName and kargs:
            if type(template) is types.TupleType:
                template = template[0] if invite.isPlayerSender() else template[1]
            template = template % typeName
            text = i18n.makeString(template, **kargs)
        if addNote:
            note = self.getNoteText(invite)
            if len(note):
                text += g_settings.lobbySettings['inviteNoteFormat'] % {'note': note}
        return text

    def link(self, invite, addNote=False):
        link = str()
        text = self.format(invite, addNote=addNote)
        if text:
            link = g_settings.lobbySettings['inviteLinkFormat'] % {'id': invite.id,
             'message': text,
             'sentAt': getLongDatetimeFormat(invite.createTime)}
        return link

    def title(self, invite):
        typeName = self.getTypeName(invite)
        if typeName:
            return i18n.makeString(INVITE_I18N_TITLE_KEY % typeName)
        return str()


class PrebattleInviteFormatter(InviteFormatter):
    __keyTypeMap = {PREBATTLE_TYPE.SQUAD: 'squad',
     PREBATTLE_TYPE.COMPANY: 'company',
     PREBATTLE_TYPE.TRAINING: 'training'}
    __defaultKeyType = 'training'
    __acceptNotAllowedStrs = [i18n.makeString('#{0:>s}:invites/prebattle/acceptNotAllowed/undefinedPeriphery'.format(INVITES_I18N_FILE)), i18n.makeString('#{0:>s}:invites/prebattle/acceptNotAllowed/otherPeriphery'.format(INVITES_I18N_FILE))]

    def getTypeName(self, invite):
        return self.__keyTypeMap.get(invite.type, self.__defaultKeyType)

    def getTemplate(self, invite):
        return PRB_INVITE_I18N_TEXT_KEYS.get(invite.state, DEFAULT_INVITE_I18N_TEXT_KEY)

    def getNoteText(self, invite):
        note = ''
        if invite.anotherPeriphery and invite.isActive():
            host = g_preDefinedHosts.periphery(invite.peripheryID)
            if host is not None:
                note = self.__acceptNotAllowedStrs[1] % host.name
            else:
                note = self.__acceptNotAllowedStrs[0]
        return note
