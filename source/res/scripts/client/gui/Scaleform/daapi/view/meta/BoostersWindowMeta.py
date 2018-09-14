# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BoostersWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class BoostersWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def requestBoostersArray(self, tabIndex):
        """
        :param tabIndex:
        :return :
        """
        self._printOverrideError('requestBoostersArray')

    def onBoosterActionBtnClick(self, boosterID, questID):
        """
        :param boosterID:
        :param questID:
        :return :
        """
        self._printOverrideError('onBoosterActionBtnClick')

    def onFiltersChange(self, filters):
        """
        :param filters:
        :return :
        """
        self._printOverrideError('onFiltersChange')

    def onResetFilters(self):
        """
        :return :
        """
        self._printOverrideError('onResetFilters')

    def as_setDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setData(data) if self._isDAAPIInited() else None

    def as_setStaticDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setStaticData(data) if self._isDAAPIInited() else None

    def as_setListDataS(self, boosters, scrollToTop):
        """
        :param boosters:
        :param scrollToTop:
        :return :
        """
        return self.flashObject.as_setListData(boosters, scrollToTop) if self._isDAAPIInited() else None
