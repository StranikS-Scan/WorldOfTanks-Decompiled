# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BoostersWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class BoostersWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def requestBoostersArray(self, tabIndex):
        self._printOverrideError('requestBoostersArray')

    def onBoosterActionBtnClick(self, boosterID, questID):
        self._printOverrideError('onBoosterActionBtnClick')

    def onFiltersChange(self, filters):
        self._printOverrideError('onFiltersChange')

    def onResetFilters(self):
        self._printOverrideError('onResetFilters')

    def as_setDataS(self, data):
        """
        :param data: Represented by BoostersWindowVO (AS)
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setStaticDataS(self, data):
        """
        :param data: Represented by BoostersWindowStaticVO (AS)
        """
        return self.flashObject.as_setStaticData(data) if self._isDAAPIInited() else None

    def as_setListDataS(self, boosters, scrollToTop):
        """
        :param boosters: Represented by DataProvider (AS)
        """
        return self.flashObject.as_setListData(boosters, scrollToTop) if self._isDAAPIInited() else None
