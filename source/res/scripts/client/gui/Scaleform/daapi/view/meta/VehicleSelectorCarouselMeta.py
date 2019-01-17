# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/VehicleSelectorCarouselMeta.py
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_environment import CarouselEnvironment

class VehicleSelectorCarouselMeta(CarouselEnvironment):

    def setFilter(self, id, selected):
        self._printOverrideError('setFilter')

    def as_initCarouselFilterS(self, data):
        return self.flashObject.as_initCarouselFilter(data) if self._isDAAPIInited() else None
