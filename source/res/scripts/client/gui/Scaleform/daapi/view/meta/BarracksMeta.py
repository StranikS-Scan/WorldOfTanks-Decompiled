# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BarracksMeta.py
from gui.Scaleform.framework.entities.View import View

class BarracksMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    """

    def invalidateTanksList(self):
        self._printOverrideError('invalidateTanksList')

    def setFilter(self, nation, role, tankType, location, nationID):
        self._printOverrideError('setFilter')

    def onShowRecruitWindowClick(self, rendererData, menuEnabled):
        self._printOverrideError('onShowRecruitWindowClick')

    def actTankman(self, dataCompact):
        self._printOverrideError('actTankman')

    def buyBerths(self):
        self._printOverrideError('buyBerths')

    def closeBarracks(self):
        self._printOverrideError('closeBarracks')

    def setTankmenFilter(self):
        self._printOverrideError('setTankmenFilter')

    def openPersonalCase(self, value, tabNumber):
        self._printOverrideError('openPersonalCase')

    def as_setTankmenS(self, data):
        """
        :param data: Represented by BarracksTankmenVO (AS)
        """
        return self.flashObject.as_setTankmen(data) if self._isDAAPIInited() else None

    def as_updateTanksListS(self, provider):
        return self.flashObject.as_updateTanksList(provider) if self._isDAAPIInited() else None

    def as_setTankmenFilterS(self, nation, role, tankType, location, nationID):
        return self.flashObject.as_setTankmenFilter(nation, role, tankType, location, nationID) if self._isDAAPIInited() else None
