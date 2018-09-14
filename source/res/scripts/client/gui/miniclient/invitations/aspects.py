# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/invitations/aspects.py
from gui import makeHtmlString
from helpers import aop
from helpers.i18n import makeString as _ms
from constants import PREBATTLE_TYPE_NAMES, PREBATTLE_TYPE
from notification.settings import NOTIFICATION_BUTTON_STATE

class DisableAccept(aop.Aspect):

    def atCall(self, cd):
        cd.avoid()
        return False


class InvitationNote(aop.Aspect):

    def atCall(self, cd):
        cd.avoid()
        battle_type = PREBATTLE_TYPE_NAMES[cd.args[0].type]
        return makeHtmlString('html_templates:lobby/prebattle', 'inviteNote', {'note': _ms('#miniclient:invitation/note/{0}'.format(battle_type))})


class DisableAcceptButton(aop.Aspect):

    def atReturn(self, cd):
        original_return_value = cd.returned
        original_buttons = original_return_value['message']['buttonsStates']
        original_buttons['submit'] = original_buttons['submit'] & ~NOTIFICATION_BUTTON_STATE.ENABLED
        return original_return_value


class ClubInvitationComment(aop.Aspect):

    def atCall(self, cd):
        cd.avoid()
        return makeHtmlString('html_templates:lobby/clubs', 'inviteComment')


class ClubInvitationNote(aop.Aspect):

    def atCall(self, cd):
        cd.avoid()
        return makeHtmlString('html_templates:lobby/prebattle', 'inviteNote', {'note': _ms('#miniclient:invitation/note/{0}'.format(PREBATTLE_TYPE_NAMES[PREBATTLE_TYPE.CLUBS]))})
