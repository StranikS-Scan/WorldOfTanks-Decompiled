# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/mapbox/tank_carousel.py
from constants import Configs
from gui.Scaleform.daapi.view.lobby.hangar.carousels import BattlePassTankCarousel
from gui.Scaleform.daapi.view.lobby.hangar.carousels.mapbox.carousel_data_provider import MapboxCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.hangar.carousels.mapbox.carousel_filter import MapboxCarouselFilter
from helpers import server_settings

class MapboxTankCarousel(BattlePassTankCarousel):

    def __init__(self):
        super(MapboxTankCarousel, self).__init__()
        self._carouselDPCls = MapboxCarouselDataProvider
        self._carouselFilterCls = MapboxCarouselFilter

    def _onServerSettingChanged(self, diff, skipVehicles=False):
        super(MapboxTankCarousel, self)._onServerSettingChanged(diff, skipVehicles=self.__onServerSettingChanged(diff))

    @server_settings.serverSettingsChangeListener(Configs.MAPBOX_CONFIG.value)
    def __onServerSettingChanged(self, *_):
        self.updateVehicles()
