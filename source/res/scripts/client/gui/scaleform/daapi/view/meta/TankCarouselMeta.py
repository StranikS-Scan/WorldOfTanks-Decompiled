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

    def selectTelecomRentalVehicle(self, intCD):
        self._printOverrideError('selectTelecomRentalVehicle')

    def getCarouselAlias(self):
        self._printOverrideError('getCarouselAlias')

    def newYearVehicles(self):
        self._printOverrideError('newYearVehicles')

    def setIsSmall(self, value):
        self._printOverrideError('setIsSmall')

    def setFilter(self, id):
        self._printOverrideError('setFilter')

    def as_rowCountS(self, value):
        return self.flashObject.as_rowCount(value) if self._isDAAPIInited() else None

    def as_setSmallDoubleCarouselS(self, value):
        return self.flashObject.as_setSmallDoubleCarousel(value) if self._isDAAPIInited() else None

    def as_useExtendedCarouselS(self, value):
        return self.flashObject.as_useExtendedCarousel(value) if self._isDAAPIInited() else None

    def as_scrollToSlotS(self, slotIdx):
        return self.flashObject.as_scrollToSlot(slotIdx) if self._isDAAPIInited() else None
