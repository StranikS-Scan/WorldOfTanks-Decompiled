# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TankCarouselMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class TankCarouselMeta(BaseDAAPIComponent):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends BaseDAAPIComponent
    """

    def selectVehicle(self, id):
        self._printOverrideError('selectVehicle')

    def buyTank(self):
        self._printOverrideError('buyTank')

    def buySlot(self):
        self._printOverrideError('buySlot')

    def setFilter(self, id):
        self._printOverrideError('setFilter')

    def resetFilters(self):
        self._printOverrideError('resetFilters')

    def updateHotFilters(self):
        self._printOverrideError('updateHotFilters')

    def onChristmasBtnClick(self):
        self._printOverrideError('onChristmasBtnClick')

    def as_getDataProviderS(self):
        return self.flashObject.as_getDataProvider() if self._isDAAPIInited() else None

    def as_setCarouselFilterS(self, data):
        """
        :param data: Represented by TankCarouselFilterSelectedVO (AS)
        """
        return self.flashObject.as_setCarouselFilter(data) if self._isDAAPIInited() else None

    def as_initCarouselFilterS(self, data):
        """
        :param data: Represented by TankCarouselFilterInitVO (AS)
        """
        return self.flashObject.as_initCarouselFilter(data) if self._isDAAPIInited() else None

    def as_showCounterS(self, countText, isAttention):
        return self.flashObject.as_showCounter(countText, isAttention) if self._isDAAPIInited() else None

    def as_rowCountS(self, value):
        return self.flashObject.as_rowCount(value) if self._isDAAPIInited() else None

    def as_hideCounterS(self):
        return self.flashObject.as_hideCounter() if self._isDAAPIInited() else None

    def as_blinkCounterS(self):
        return self.flashObject.as_blinkCounter() if self._isDAAPIInited() else None

    def as_setChristmasBtnDataS(self, data):
        """
        :param data: Represented by ChristmasButtonVO (AS)
        """
        return self.flashObject.as_setChristmasBtnData(data) if self._isDAAPIInited() else None
