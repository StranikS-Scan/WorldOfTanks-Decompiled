# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CompaniesWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class CompaniesWindowMeta(AbstractWindowView):

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

    def as_getCompaniesListDPS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getCompaniesListDP()

    def as_showPlayersListS(self, index):
        if self._isDAAPIInited():
            return self.flashObject.as_showPlayersList(index)

    def as_setDefaultFilterS(self, creatorMask, isNotInBattle, division):
        if self._isDAAPIInited():
            return self.flashObject.as_setDefaultFilter(creatorMask, isNotInBattle, division)

    def as_setRefreshCoolDownS(self, time):
        if self._isDAAPIInited():
            return self.flashObject.as_setRefreshCoolDown(time)

    def as_disableCreateButtonS(self, isDisable):
        if self._isDAAPIInited():
            return self.flashObject.as_disableCreateButton(isDisable)
