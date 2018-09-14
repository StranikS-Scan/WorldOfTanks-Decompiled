# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CompanyListMeta.py
from gui.Scaleform.daapi.view.lobby.prb_windows.BasePrebattleListView import BasePrebattleListView

class CompanyListMeta(BasePrebattleListView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BasePrebattleListView
    null
    """

    def createCompany(self):
        """
        :return :
        """
        self._printOverrideError('createCompany')

    def joinCompany(self, prbID):
        """
        :param prbID:
        :return :
        """
        self._printOverrideError('joinCompany')

    def getDivisionsList(self):
        """
        :return Array:
        """
        self._printOverrideError('getDivisionsList')

    def refreshCompaniesList(self, creatorMask, isNotInBattle, division):
        """
        :param creatorMask:
        :param isNotInBattle:
        :param division:
        :return :
        """
        self._printOverrideError('refreshCompaniesList')

    def requestPlayersList(self, prbID):
        """
        :param prbID:
        :return :
        """
        self._printOverrideError('requestPlayersList')

    def showFAQWindow(self):
        """
        :return :
        """
        self._printOverrideError('showFAQWindow')

    def getClientID(self):
        """
        :return Number:
        """
        self._printOverrideError('getClientID')

    def as_showPlayersListS(self, index):
        """
        :param index:
        :return :
        """
        return self.flashObject.as_showPlayersList(index) if self._isDAAPIInited() else None

    def as_setDefaultFilterS(self, creatorMask, isNotInBattle, division):
        """
        :param creatorMask:
        :param isNotInBattle:
        :param division:
        :return :
        """
        return self.flashObject.as_setDefaultFilter(creatorMask, isNotInBattle, division) if self._isDAAPIInited() else None

    def as_setRefreshCoolDownS(self, time):
        """
        :param time:
        :return :
        """
        return self.flashObject.as_setRefreshCoolDown(time) if self._isDAAPIInited() else None

    def as_disableCreateButtonS(self, isDisable):
        """
        :param isDisable:
        :return :
        """
        return self.flashObject.as_disableCreateButton(isDisable) if self._isDAAPIInited() else None
