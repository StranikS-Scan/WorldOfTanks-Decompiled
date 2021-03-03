# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/bm2021/market_entry_point.py
from account_helpers.settings_core import settings_constants
from account_helpers.settings_core.options import CarouselTypeSetting, DoubleCarouselTypeSetting
from constants import Configs
from frameworks.wulf import ViewSettings
from frameworks.wulf.gui_constants import ViewFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.bm2021.black_market_entry_point_model import BlackMarketEntryPointModel
from gui.impl.pub import ViewImpl
from gui.Scaleform.daapi.view.common.filter_popover import CAROUSEL_TYPE_SWITCHED_EVENT
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBlackMarketOpenItemWindow
from gui.shared.gui_items.loot_box import BLACK_MARKET_ITEM_TYPE
from helpers import dependency
from helpers.time_utils import getServerUTCTime
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IEventItemsController
from skeletons.gui.lobby_context import ILobbyContext

class MarketEntrancePointWidget(ViewImpl):
    __itemsCtrl = dependency.descriptor(IEventItemsController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __slots__ = ()

    def __init__(self):
        settings = ViewSettings(R.views.lobby.bm2021.BlackMarketEntryWidget(), ViewFlags.COMPONENT, BlackMarketEntryPointModel())
        super(MarketEntrancePointWidget, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MarketEntrancePointWidget, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(MarketEntrancePointWidget, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def _initialize(self):
        super(MarketEntrancePointWidget, self)._initialize()
        self.viewModel.onWidgetClick += self._onWidgetClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        g_eventBus.addListener(CAROUSEL_TYPE_SWITCHED_EVENT, self.__onCarouselTypeChanged, EVENT_BUS_SCOPE.LOBBY)
        self.__settingsCore.onSettingsChanged += self.__onCarouselSettingsChange

    def _finalize(self):
        self.__settingsCore.onSettingsChanged -= self.__onCarouselSettingsChange
        g_eventBus.removeListener(CAROUSEL_TYPE_SWITCHED_EVENT, self.__onCarouselTypeChanged, EVENT_BUS_SCOPE.LOBBY)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.viewModel.onWidgetClick -= self._onWidgetClick
        super(MarketEntrancePointWidget, self)._finalize()

    def _onWidgetClick(self, _=None):
        showBlackMarketOpenItemWindow()

    def __onServerSettingsChanged(self, diff):
        if Configs.LOOT_BOXES_CONFIG.value in diff:
            item = self.__itemsCtrl.getEventItemsByType(BLACK_MARKET_ITEM_TYPE)
            if item:
                self.__updateModel()

    def __onCarouselSettingsChange(self, diff):
        if settings_constants.GAME.DOUBLE_CAROUSEL_TYPE in diff or settings_constants.GAME.CAROUSEL_TYPE in diff:
            self.__updateModel()

    def __onCarouselTypeChanged(self, event):
        self.__updateModel(event.ctx['selectedOption'])

    def __updateModel(self, carouselType=None):
        with self.viewModel.transaction() as model:
            marketItem = self.__itemsCtrl.getEventItemsByType(BLACK_MARKET_ITEM_TYPE)
            if marketItem:
                model.setTimeLeft(marketItem.getAutoOpenTime() - getServerUTCTime())
            carouselTypeSetting = self.__settingsCore.options.getSetting(settings_constants.GAME.CAROUSEL_TYPE)
            doubleCarouselTypeSetting = self.__settingsCore.options.getSetting(settings_constants.GAME.DOUBLE_CAROUSEL_TYPE)
            carouselType = carouselType or CarouselTypeSetting.CAROUSEL_TYPES[carouselTypeSetting.get()]
            isDouble = carouselType == CarouselTypeSetting.OPTIONS.DOUBLE
            isAdaptive = doubleCarouselTypeSetting.get() == DoubleCarouselTypeSetting.DOUBLE_CAROUSEL_TYPES.index(DoubleCarouselTypeSetting.OPTIONS.ADAPTIVE)
            isSmall = not (isDouble and isAdaptive)
            model.setIsSmall(isSmall)
