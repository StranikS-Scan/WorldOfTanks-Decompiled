# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/miniclient/invitations/pointcuts.py
from helpers import aop
import aspects

class PrbDisableAcceptButton(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.prb_control.invites', 'InvitesManager', 'canAcceptInvite', aspects=(aspects.DisableAccept,))


class PrbInvitationText(aop.Pointcut):

    def __init__(self):
        aop.Pointcut.__init__(self, 'gui.prb_control.formatters.invites', 'PrbInviteHtmlTextFormatter', 'getNote', aspects=(aspects.InvitationNote,))
