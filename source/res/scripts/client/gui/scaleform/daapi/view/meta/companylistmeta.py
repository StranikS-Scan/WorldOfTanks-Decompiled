# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CompanyListMeta.py
from gui.Scaleform.daapi.view.lobby.prb_windows.BasePrebattleListView import BasePrebattleListView

class CompanyListMeta(BasePrebattleListView):

    def createCompany(self):
        self._printOverrideError('createCompany')

    def joinCompany(self, prbID):
        self._printOverrideError('joinCompany')

    def getDivisionsList(self):
        self._printOverrideError('getDivisionsList')

    def refreshCompaniesList(self, creatorMask, isNotInBattle, division):
        self._printOverrideError('refreshCompaniesList')

    def requestPlayersList(self, prbID):
        self._printOverrideError('requestPlayersList')

    def showFAQWindow(self):
        self._printOverrideError('showFAQWindow')

    def getClientID(self):
        self._printOverrideError('getClientID')

    def as_showPlayersListS(self, index):
        return self.flashObject.as_showPlayersList(index) if self._isDAAPIInited() else None

    def as_setDefaultFilterS(self, creatorMask, isNotInBattle, division):
        return self.flashObject.as_setDefaultFilter(creatorMask, isNotInBattle, division) if self._isDAAPIInited() else None

    def as_setRefreshCoolDownS(self, time):
        return self.flashObject.as_setRefreshCoolDown(time) if self._isDAAPIInited() else None

    def as_disableCreateButtonS(self, isDisable):
        return self.flashObject.as_disableCreateButton(isDisable) if self._isDAAPIInited() else None
