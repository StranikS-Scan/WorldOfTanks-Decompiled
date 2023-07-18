# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/debut_boxes/tank_carousel.py
from gui.Scaleform.daapi.view.lobby.hangar.carousels import BattlePassTankCarousel

class DebutBoxesTankCarousel(BattlePassTankCarousel):

    def _getFilters(self):
        return super(DebutBoxesTankCarousel, self)._getFilters() + ('debut_boxes',)

    def getCustomParams(self):
        data = super(DebutBoxesTankCarousel, self).getCustomParams()
        data.update({'debut_boxes': True})
        return data
