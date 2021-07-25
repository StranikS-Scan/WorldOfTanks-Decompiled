# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/ranked/tank_carousel.py
from gui.Scaleform.daapi.view.lobby.hangar.carousels.ranked.carousel_data_provider import RankedCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.hangar.carousels.ranked.carousel_filter import RankedCarouselFilter
from gui.Scaleform.daapi.view.lobby.hangar.carousels.battle_pass.tank_carousel import BattlePassTankCarousel

class RankedTankCarousel(BattlePassTankCarousel):

    def __init__(self):
        super(RankedTankCarousel, self).__init__()
        self._carouselDPCls = RankedCarouselDataProvider
        self._carouselFilterCls = RankedCarouselFilter

    def _getInitialFilterVO(self, contexts):
        filtersVO = super(RankedTankCarousel, self)._getInitialFilterVO(contexts)
        filtersVO['isRanked'] = True
        return filtersVO
