# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BattleTankCarouselMeta.py
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_environment import CarouselEnvironment

class BattleTankCarouselMeta(CarouselEnvironment):

    def setFilter(self, id):
        self._printOverrideError('setFilter')

    def as_useExtendedCarouselS(self, value):
        return self.flashObject.as_useExtendedCarousel(value) if self._isDAAPIInited() else None

    def as_scrollToSlotS(self, slotIdx):
        return self.flashObject.as_scrollToSlot(slotIdx) if self._isDAAPIInited() else None
