# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/stronghold/tank_carousel.py
from gui.Scaleform.daapi.view.lobby.hangar.carousels import BattlePassTankCarousel
from gui.Scaleform.daapi.view.lobby.hangar.carousels.stronghold.carousel_data_provider import StrongholdCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.hangar.carousels.stronghold.carousel_filter import StrongholdCarouselFilter
from helpers import dependency
from skeletons.gui.game_control import IDebutBoxesController

class StrongholdTankCarousel(BattlePassTankCarousel):
    __debutBoxesController = dependency.descriptor(IDebutBoxesController)

    def __init__(self):
        super(StrongholdTankCarousel, self).__init__()
        self._carouselDPCls = StrongholdCarouselDataProvider
        self._carouselFilterCls = StrongholdCarouselFilter

    def getCustomParams(self):
        data = super(StrongholdTankCarousel, self).getCustomParams()
        if self.__debutBoxesController.isEnabled():
            data.update({'debut_boxes': True})
        return data
