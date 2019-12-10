# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TankCarouselMeta.py
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_environment import CarouselEnvironment

class TankCarouselMeta(CarouselEnvironment):

    def restoreTank(self):
        self._printOverrideError('restoreTank')

    def buyTank(self):
        self._printOverrideError('buyTank')

    def buySlot(self):
        self._printOverrideError('buySlot')

    def buyRentPromotion(self, intCD):
        self._printOverrideError('buyRentPromotion')

    def newYearVehicles(self):
        self._printOverrideError('newYearVehicles')

    def setFilter(self, id):
        self._printOverrideError('setFilter')

    def updateHotFilters(self):
        self._printOverrideError('updateHotFilters')

    def getCarouselAlias(self):
        self._printOverrideError('getCarouselAlias')

    def as_setCarouselFilterS(self, data):
        return self.flashObject.as_setCarouselFilter(data) if self._isDAAPIInited() else None

    def as_initCarouselFilterS(self, data):
        return self.flashObject.as_initCarouselFilter(data) if self._isDAAPIInited() else None

    def as_rowCountS(self, value):
        return self.flashObject.as_rowCount(value) if self._isDAAPIInited() else None

    def as_setSmallDoubleCarouselS(self, value):
        return self.flashObject.as_setSmallDoubleCarousel(value) if self._isDAAPIInited() else None
