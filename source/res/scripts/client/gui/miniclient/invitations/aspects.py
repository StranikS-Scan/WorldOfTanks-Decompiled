# Embedded file name: scripts/client/gui/miniclient/invitations/aspects.py
from gui import makeHtmlString
from helpers import aop
from helpers.i18n import makeString as _ms
from constants import PREBATTLE_TYPE_NAMES

class DisableAcceptButton(aop.Aspect):

    def atCall(self, cd):
        cd.avoid()
        return False


class InvitationNote(aop.Aspect):

    def atCall(self, cd):
        cd.avoid()
        battle_type = PREBATTLE_TYPE_NAMES[cd.args[0].type]
        return makeHtmlString('html_templates:lobby/prebattle', 'inviteNote', {'note': _ms('#miniclient:invitation/note/{0}'.format(battle_type))})
