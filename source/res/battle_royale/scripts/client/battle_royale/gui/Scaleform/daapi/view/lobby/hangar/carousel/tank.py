# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/hangar/carousel/tank.py
from battle_royale.gui.Scaleform.daapi.view.lobby.hangar.carousel.filter import RoyaleCarouselFilter
from gui.Scaleform import getVehicleTypeAssetPath
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.tank_carousel import TankCarousel
from gui.Scaleform.locale.TANK_CAROUSEL_FILTER import TANK_CAROUSEL_FILTER
from gui.shared.utils.functions import makeTooltip
from battle_royale.gui.Scaleform.daapi.view.lobby.hangar.carousel.data_provider import RoyaleCarouselDataProvider

class RoyaleTankCarousel(TankCarousel):
    _CAROUSEL_FILTERS = ('heavyTank', 'mediumTank', 'lightTank')

    def __init__(self):
        super(RoyaleTankCarousel, self).__init__()
        self._carouselDPCls = RoyaleCarouselDataProvider
        self._carouselFilterCls = RoyaleCarouselFilter

    def hasRoles(self):
        return False

    def getCustomParams(self):
        return {'hasBattleRoyleVehicles': self._carouselDP.hasBattleRoyaleVehicles()}

    def _getFiltersVisible(self):
        return False

    def _getInitialFilterVO(self, contexts):
        filtersVO = super(RoyaleTankCarousel, self)._getInitialFilterVO(contexts)
        hotFilters = filtersVO['hotFilters']
        for hotFilter in hotFilters:
            entry = hotFilter['id']
            hotFilter['value'] = getVehicleTypeAssetPath(entry)
            hotFilter['tooltip'] = makeTooltip('#menu:carousel_tank_filter/{}'.format(entry), TANK_CAROUSEL_FILTER.TOOLTIP_VEHICLETYPES_BODY)

        return filtersVO
