# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/CarouselEnvironmentMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class CarouselEnvironmentMeta(BaseDAAPIComponent):

    def selectVehicle(self, id):
        self._printOverrideError('selectVehicle')

    def resetFilters(self):
        self._printOverrideError('resetFilters')

    def updateHotFilters(self):
        self._printOverrideError('updateHotFilters')

    def as_getDataProviderS(self):
        return self.flashObject.as_getDataProvider() if self._isDAAPIInited() else None

    def as_setInitDataS(self, data):
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_setEnabledS(self, value):
        return self.flashObject.as_setEnabled(value) if self._isDAAPIInited() else None

    def as_showCounterS(self, countText, isAttention):
        return self.flashObject.as_showCounter(countText, isAttention) if self._isDAAPIInited() else None

    def as_hideCounterS(self):
        return self.flashObject.as_hideCounter() if self._isDAAPIInited() else None

    def as_blinkCounterS(self):
        return self.flashObject.as_blinkCounter() if self._isDAAPIInited() else None

    def as_setCarouselFilterS(self, data):
        return self.flashObject.as_setCarouselFilter(data) if self._isDAAPIInited() else None

    def as_initCarouselFilterS(self, data):
        return self.flashObject.as_initCarouselFilter(data) if self._isDAAPIInited() else None
