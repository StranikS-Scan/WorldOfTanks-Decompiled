# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ClanInvitesWindowAbstractTabViewMeta.py
from gui.Scaleform.daapi.view.lobby.clans.invites.ClanInvitesViewWithTable import ClanInvitesViewWithTable

class ClanInvitesWindowAbstractTabViewMeta(ClanInvitesViewWithTable):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends ClanInvitesViewWithTable
    null
    """

    def filterBy(self, filterName):
        """
        :param filterName:
        :return :
        """
        self._printOverrideError('filterBy')

    def as_updateFilterStateS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_updateFilterState(data) if self._isDAAPIInited() else None
