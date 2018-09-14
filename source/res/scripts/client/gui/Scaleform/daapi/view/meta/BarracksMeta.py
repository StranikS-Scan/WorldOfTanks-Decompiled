# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BarracksMeta.py
from gui.Scaleform.framework.entities.View import View

class BarracksMeta(View):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends View
    null
    """

    def invalidateTanksList(self):
        """
        :return :
        """
        self._printOverrideError('invalidateTanksList')

    def setFilter(self, nation, role, tankType, location, nationID):
        """
        :param nation:
        :param role:
        :param tankType:
        :param location:
        :param nationID:
        :return :
        """
        self._printOverrideError('setFilter')

    def onShowRecruitWindowClick(self, rendererData, menuEnabled):
        """
        :param rendererData:
        :param menuEnabled:
        :return :
        """
        self._printOverrideError('onShowRecruitWindowClick')

    def unloadTankman(self, dataCompact):
        """
        :param dataCompact:
        :return :
        """
        self._printOverrideError('unloadTankman')

    def dismissTankman(self, dataCompact):
        """
        :param dataCompact:
        :return :
        """
        self._printOverrideError('dismissTankman')

    def buyBerths(self):
        """
        :return :
        """
        self._printOverrideError('buyBerths')

    def closeBarracks(self):
        """
        :return :
        """
        self._printOverrideError('closeBarracks')

    def setTankmenFilter(self):
        """
        :return :
        """
        self._printOverrideError('setTankmenFilter')

    def openPersonalCase(self, value, tabNumber):
        """
        :param value:
        :param tabNumber:
        :return :
        """
        self._printOverrideError('openPersonalCase')

    def as_setTankmenS(self, tankmenCount, tankmenInSlots, placesCount, tankmenInBarracks, tankmanArr):
        """
        :param tankmenCount:
        :param tankmenInSlots:
        :param placesCount:
        :param tankmenInBarracks:
        :param tankmanArr:
        :return :
        """
        return self.flashObject.as_setTankmen(tankmenCount, tankmenInSlots, placesCount, tankmenInBarracks, tankmanArr) if self._isDAAPIInited() else None

    def as_updateTanksListS(self, provider):
        """
        :param provider:
        :return :
        """
        return self.flashObject.as_updateTanksList(provider) if self._isDAAPIInited() else None

    def as_setTankmenFilterS(self, nation, role, tankType, location, nationID):
        """
        :param nation:
        :param role:
        :param tankType:
        :param location:
        :param nationID:
        :return :
        """
        return self.flashObject.as_setTankmenFilter(nation, role, tankType, location, nationID) if self._isDAAPIInited() else None
