# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TankCarouselMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class TankCarouselMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    null
    """

    def selectVehicle(self, id):
        """
        :param id:
        :return :
        """
        self._printOverrideError('selectVehicle')

    def buyTank(self):
        """
        :return :
        """
        self._printOverrideError('buyTank')

    def buySlot(self):
        """
        :return :
        """
        self._printOverrideError('buySlot')

    def setFilter(self, id):
        """
        :param id:
        :return :
        """
        self._printOverrideError('setFilter')

    def resetFilters(self):
        """
        :return :
        """
        self._printOverrideError('resetFilters')

    def as_getDataProviderS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getDataProvider() if self._isDAAPIInited() else None

    def as_setCarouselFilterS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setCarouselFilter(data) if self._isDAAPIInited() else None

    def as_initCarouselFilterS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_initCarouselFilter(data) if self._isDAAPIInited() else None

    def as_showCounterS(self, countText, isAttention):
        """
        :param countText:
        :param isAttention:
        :return :
        """
        return self.flashObject.as_showCounter(countText, isAttention) if self._isDAAPIInited() else None

    def as_hideCounterS(self):
        """
        :return :
        """
        return self.flashObject.as_hideCounter() if self._isDAAPIInited() else None

    def as_blinkCounterS(self):
        """
        :return :
        """
        return self.flashObject.as_blinkCounter() if self._isDAAPIInited() else None
