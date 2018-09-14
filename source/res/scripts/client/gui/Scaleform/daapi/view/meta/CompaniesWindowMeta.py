# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CompaniesWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class CompaniesWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

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
        return self.flashObject.as_getCompaniesListDP() if self._isDAAPIInited() else None

    def as_showPlayersListS(self, index):
        return self.flashObject.as_showPlayersList(index) if self._isDAAPIInited() else None

    def as_setDefaultFilterS(self, creatorMask, isNotInBattle, division):
        return self.flashObject.as_setDefaultFilter(creatorMask, isNotInBattle, division) if self._isDAAPIInited() else None

    def as_setRefreshCoolDownS(self, time):
        return self.flashObject.as_setRefreshCoolDown(time) if self._isDAAPIInited() else None

    def as_disableCreateButtonS(self, isDisable):
        return self.flashObject.as_disableCreateButton(isDisable) if self._isDAAPIInited() else None
