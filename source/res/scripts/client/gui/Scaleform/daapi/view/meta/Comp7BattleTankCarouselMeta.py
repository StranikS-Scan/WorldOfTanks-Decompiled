# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/Comp7BattleTankCarouselMeta.py
from gui.Scaleform.daapi.view.common.vehicle_carousel.carousel_environment import CarouselEnvironment

class Comp7BattleTankCarouselMeta(CarouselEnvironment):

    def setFilter(self, id):
        self._printOverrideError('setFilter')

    def onViewIsHidden(self):
        self._printOverrideError('onViewIsHidden')

    def as_rowCountS(self, value):
        return self.flashObject.as_rowCount(value) if self._isDAAPIInited() else None

    def as_hideS(self, useAnim):
        return self.flashObject.as_hide(useAnim) if self._isDAAPIInited() else None
