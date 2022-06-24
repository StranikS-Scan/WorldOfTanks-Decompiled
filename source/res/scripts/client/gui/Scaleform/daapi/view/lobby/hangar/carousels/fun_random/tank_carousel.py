# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/carousels/fun_random/tank_carousel.py
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from constants import Configs, ARENA_BONUS_TYPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.hangar.carousels import BattlePassTankCarousel
from gui.Scaleform.daapi.view.lobby.hangar.carousels.fun_random.carousel_data_provider import FunRandomCarouselDataProvider
from gui.Scaleform.daapi.view.lobby.hangar.carousels.fun_random.carousel_filter import FunRandomCarouselFilter
from helpers import dependency, server_settings
from skeletons.gui.lobby_context import ILobbyContext

class FunRandomTankCarousel(BattlePassTankCarousel):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(FunRandomTankCarousel, self).__init__()
        self._carouselDPCls = FunRandomCarouselDataProvider
        self._carouselFilterCls = FunRandomCarouselFilter

    def _populate(self):
        super(FunRandomTankCarousel, self)._populate()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged

    def _dispose(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        super(FunRandomTankCarousel, self)._dispose()

    def _getInitialFilterVO(self, contexts):
        filtersVO = super(FunRandomTankCarousel, self)._getInitialFilterVO(contexts)
        filtersVO['isFunRandom'] = True
        if not self._battlePassController.isGameModeEnabled(ARENA_BONUS_TYPE.FUN_RANDOM):
            filtersVO['popoverAlias'] = VIEW_ALIAS.TANK_CAROUSEL_FILTER_POPOVER
        return filtersVO

    def _getFilters(self):
        filters = super(FunRandomTankCarousel, self)._getFilters()
        if not BONUS_CAPS.checkAny(ARENA_BONUS_TYPE.FUN_RANDOM, BONUS_CAPS.DAILY_MULTIPLIED_XP):
            filters = ('favorite', 'elite', 'premium')
        return filters + ('funRandom',)

    @server_settings.serverSettingsChangeListener(Configs.FUN_RANDOM_CONFIG.value)
    def __onServerSettingChanged(self, *_):
        self.updateVehicles()
