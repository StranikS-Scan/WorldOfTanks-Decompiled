# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ClanPersonalInvitesViewMeta.py
from gui.Scaleform.daapi.view.lobby.clans.invites.ClanInvitesViewWithTable import ClanInvitesViewWithTable

class ClanPersonalInvitesViewMeta(ClanInvitesViewWithTable):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends ClanInvitesViewWithTable
    null
    """

    def acceptInvite(self, dbID):
        """
        :param dbID:
        :return :
        """
        self._printOverrideError('acceptInvite')

    def declineInvite(self, dbID):
        """
        :param dbID:
        :return :
        """
        self._printOverrideError('declineInvite')

    def setInviteSelected(self, dbID, selected):
        """
        :param dbID:
        :param selected:
        :return :
        """
        self._printOverrideError('setInviteSelected')

    def setSelectAllInvitesCheckBoxSelected(self, selected):
        """
        :param selected:
        :return :
        """
        self._printOverrideError('setSelectAllInvitesCheckBoxSelected')

    def declineAllSelectedInvites(self):
        """
        :return :
        """
        self._printOverrideError('declineAllSelectedInvites')

    def as_setDeclineAllSelectedInvitesStateS(self, text, enabled):
        """
        :param text:
        :param enabled:
        :return :
        """
        return self.flashObject.as_setDeclineAllSelectedInvitesState(text, enabled) if self._isDAAPIInited() else None

    def as_setSelectAllCheckboxStateS(self, selected, visible):
        """
        :param selected:
        :param visible:
        :return :
        """
        return self.flashObject.as_setSelectAllCheckboxState(selected, visible) if self._isDAAPIInited() else None
