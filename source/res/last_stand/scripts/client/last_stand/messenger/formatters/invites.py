# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/messenger/formatters/invites.py
from gui.prb_control.formatters.invites import PrbInviteHtmlTextFormatter
from last_stand.skeletons.ls_controller import ILSController
from helpers import dependency

class LSPrbInviteHtmlTextFormatter(PrbInviteHtmlTextFormatter):
    lsCtrl = dependency.descriptor(ILSController)

    def canAcceptInvite(self, invite):
        canAccept = super(LSPrbInviteHtmlTextFormatter, self).canAcceptInvite(invite)
        return canAccept and self.lsCtrl.isAvailable()
