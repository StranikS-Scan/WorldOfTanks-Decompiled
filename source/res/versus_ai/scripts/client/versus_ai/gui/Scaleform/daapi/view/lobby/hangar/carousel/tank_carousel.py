# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: versus_ai/scripts/client/versus_ai/gui/Scaleform/daapi/view/lobby/hangar/carousel/tank_carousel.py
from constants import Configs
from gui.Scaleform.daapi.view.lobby.hangar.carousels import BattlePassTankCarousel
from helpers import dependency, server_settings
from skeletons.gui.lobby_context import ILobbyContext
from versus_ai.gui.Scaleform.daapi.view.lobby.hangar.carousel.carousel_data_provider import VersusAICarouselDataProvider
from versus_ai.gui.Scaleform.daapi.view.lobby.hangar.carousel.carousel_filter import VersusAICarouselFilter

class VersusAITankCarousel(BattlePassTankCarousel):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(VersusAITankCarousel, self).__init__()
        self._carouselDPCls = VersusAICarouselDataProvider
        self._carouselFilterCls = VersusAICarouselFilter

    def _populate(self):
        super(VersusAITankCarousel, self)._populate()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged

    def _dispose(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(VersusAITankCarousel, self)._dispose()

    @server_settings.serverSettingsChangeListener(Configs.VERSUS_AI_CONFIG.value)
    def __onServerSettingChanged(self, *_):
        self.updateVehicles()
