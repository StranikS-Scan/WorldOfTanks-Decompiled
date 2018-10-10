# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/epicBattle/tank_carousel.py
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.tank_carousel import TankCarousel
from gui.Scaleform.daapi.view.lobby.hangar.carousels.epicBattle.carousel_data_provider import EpicBattleCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.hangar.carousels.epicBattle.carousel_filter import EpicBattleCarouselFilter
_DISABLED_FILTERS = ['bonus']

class EpicBattleTankCarousel(TankCarousel):

    def __init__(self):
        super(EpicBattleTankCarousel, self).__init__()
        self._carouselDPCls = EpicBattleCarouselDataProvider
        self._carouselFilterCls = EpicBattleCarouselFilter

    def updateHotFilters(self):
        hotFilters = []
        for key in self._usedFilters:
            currFilter = False
            if key not in _DISABLED_FILTERS:
                currFilter = self.filter.get(key)
            hotFilters.append(currFilter)

        self.as_setCarouselFilterS({'hotFilters': hotFilters})

    def _getInitialFilterVO(self, contexts):
        filtersVO = super(EpicBattleTankCarousel, self)._getInitialFilterVO(contexts)
        length = len(filtersVO['hotFilters'])
        for id_ in range(0, length):
            entry = filtersVO['hotFilters'][id_]
            if entry['id'] in _DISABLED_FILTERS:
                entry['enabled'] = False
                entry['selected'] = False

        return filtersVO
