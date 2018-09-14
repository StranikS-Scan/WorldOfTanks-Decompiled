# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/invites/ClanPersonalInvitesWindow.py
from gui.clans.clan_helpers import ClanListener
from gui.clans import formatters
from gui.Scaleform.daapi.view.meta.ClanPersonalInvitesWindowMeta import ClanPersonalInvitesWindowMeta
from gui.Scaleform.locale.CLANS import CLANS
from gui.shared.formatters import text_styles
from helpers.i18n import makeString as _ms

class ClanPersonalInvitesWindow(ClanPersonalInvitesWindowMeta, ClanListener):

    def __init__(self, *args):
        super(ClanPersonalInvitesWindow, self).__init__()

    def onClanStateChanged(self, oldStateID, newStateID):
        if not self.clansCtrl.isEnabled():
            self.onWindowClose()
        if not self.clansCtrl.isAvailable():
            pass

    def onAccountClanProfileChanged(self, profile):
        if profile.isInClan():
            self.destroy()

    def onAccountInvitesReceived(self, invites):
        self._updateActualInvites()

    def _populate(self):
        super(ClanPersonalInvitesWindow, self)._populate()
        self.startClanListening()
        self._updateActualInvites()

    def _dispose(self):
        super(ClanPersonalInvitesWindow, self)._dispose()
        self.stopClanListening()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(ClanPersonalInvitesWindow, self)._onRegisterFlashComponent(viewPy, alias)
        viewPy.setParentWindow(self)

    def onWindowClose(self):
        self.destroy()

    def _updateActualInvites(self):
        self.as_setActualInvitesTextS(_ms(CLANS.CLANPERSONALINVITESWINDOW_ACTUALINVITES, count=text_styles.stats(formatters.formatInvitesCount(self.clansCtrl.getAccountProfile().getInvitesCount()))))
