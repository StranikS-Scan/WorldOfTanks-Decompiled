# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/ranked/tank_carousel.py
from gui.Scaleform.daapi.view.lobby.hangar.carousels.ranked.carousel_data_provider import RankedCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.hangar.carousels.ranked.carousel_filter import RankedCarouselFilter
from gui.Scaleform.daapi.view.lobby.hangar.carousels.battle_pass.tank_carousel import BattlePassTankCarousel
from helpers import dependency
from skeletons.gui.game_control import IDebutBoxesController

class RankedTankCarousel(BattlePassTankCarousel):
    __debutBoxesController = dependency.descriptor(IDebutBoxesController)

    def __init__(self):
        super(RankedTankCarousel, self).__init__()
        self._carouselDPCls = RankedCarouselDataProvider
        self._carouselFilterCls = RankedCarouselFilter

    def _getInitialFilterVO(self, contexts):
        filtersVO = super(RankedTankCarousel, self)._getInitialFilterVO(contexts)
        filtersVO['isRanked'] = True
        return filtersVO

    def _getFilters(self):
        return super(RankedTankCarousel, self)._getFilters() + ('ranked',)

    def getCustomParams(self):
        data = super(RankedTankCarousel, self).getCustomParams()
        if self.__debutBoxesController.isEnabled():
            data.update({'debut_boxes': True})
        return data
