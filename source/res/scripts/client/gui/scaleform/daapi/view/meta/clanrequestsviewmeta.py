# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ClanRequestsViewMeta.py
from gui.Scaleform.daapi.view.lobby.clans.invites.ClanInvitesWindowAbstractTabView import ClanInvitesWindowAbstractTabView

class ClanRequestsViewMeta(ClanInvitesWindowAbstractTabView):

    def acceptRequest(self, dbId):
        self._printOverrideError('acceptRequest')

    def declineRequest(self, dbId):
        self._printOverrideError('declineRequest')

    def sendInvite(self, dbId):
        self._printOverrideError('sendInvite')
