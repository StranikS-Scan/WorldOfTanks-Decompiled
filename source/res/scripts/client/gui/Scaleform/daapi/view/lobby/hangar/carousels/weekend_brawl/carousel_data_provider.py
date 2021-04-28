# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/weekend_brawl/carousel_data_provider.py
from gui.Scaleform.daapi.view.lobby.hangar.carousels.basic.carousel_data_provider import HangarCarouselDataProvider
from gui.shared.utils.requesters import REQ_CRITERIA

class WeekendBrawlCarouselDataProvider(HangarCarouselDataProvider):

    def __init__(self, carouselFilter, itemsCache, currentVehicle):
        super(WeekendBrawlCarouselDataProvider, self).__init__(carouselFilter, itemsCache, currentVehicle)
        self._baseCriteria = REQ_CRITERIA.INVENTORY
