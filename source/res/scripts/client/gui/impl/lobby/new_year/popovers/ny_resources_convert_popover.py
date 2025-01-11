# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/popovers/ny_resources_convert_popover.py
from frameworks.wulf import ViewSettings
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_resource_model import NyResourceModel
from gui.impl.gen.view_models.views.lobby.new_year.popovers.ny_resources_convert_popover_model import NyResourcesConvertPopoverModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_resource_converter_info_tooltip_model import ConverterInfoTooltipType
from gui.impl.lobby.missions.daily_quests_view import DailyTabs
from gui.impl.lobby.new_year.tooltips.ny_resource_converter_info_tooltip import NyResourceConverterInfoTooltip
from gui.impl.new_year.new_year_helper import getRewardKitsCount
from gui.impl.new_year.sounds import NewYearSoundsManager
from gui.impl.pub import PopOverViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.events_dispatcher import showDailyQuests
from gui.shared import g_eventBus
from gui.shared.event_dispatcher import showLootBoxBuyWindow, showLootBoxEntry
from gui.shared.events import NyResourcesConverterPopup
from gui.shared.gui_items.loot_box import NewYearLootBoxes
from gui.shared.utils import decorators
from helpers import dependency, server_settings
from new_year.ny_constants import RESOURCES_ORDER
from new_year.ny_processor import NewYearConvertResourcesProcessor
from ny_common.settings import NY_CONFIG_NAME, NYLootBoxConsts
from skeletons.gui.game_control import IWalletController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
from skeletons.new_year import INewYearController, IFriendServiceController

class NyResourcesConvertPopover(PopOverViewImpl):
    __slots__ = ()
    __nyController = dependency.descriptor(INewYearController)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __wallet = dependency.descriptor(IWalletController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __friendsService = dependency.descriptor(IFriendServiceController)

    def __init__(self):
        settings = ViewSettings(R.views.lobby.new_year.popovers.NyResourcesConvertPopover())
        settings.model = NyResourcesConvertPopoverModel()
        super(NyResourcesConvertPopover, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NyResourcesConvertPopover, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyResourceConverterInfoTooltip():
            tooltipType = ConverterInfoTooltipType(event.getArgument('tooltipType'))
            return NyResourceConverterInfoTooltip(tooltipType)
        return super(NyResourcesConvertPopover, self).createToolTipContent(event, contentID)

    def _initialize(self, *args, **kwargs):
        super(NyResourcesConvertPopover, self)._initialize()
        g_eventBus.handleEvent(NyResourcesConverterPopup(eventType=NyResourcesConverterPopup.SHOW))

    def _onLoading(self, *args, **kwargs):
        super(NyResourcesConvertPopover, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__updateAvailableResources(model=model)
            self.__updateBoxesAvailability(model=model)
            convertRate = model.convertRate
            initialValueCoeff, receivedValueCoeff = self.__nyController.currencies.getResourceConverterCoefficients()
            isExternal = self.__getShopSource() != NYLootBoxConsts.IGB
            lootBoxes = self.__itemsCache.items.tokens.getLootBoxesCountByType()
            if NewYearLootBoxes.PREMIUM in lootBoxes:
                hasBigBoxes = lootBoxes[NewYearLootBoxes.PREMIUM]['total']
            else:
                hasBigBoxes = False
            convertRate.setFrom(initialValueCoeff)
            convertRate.setTo(receivedValueCoeff)
            model.setIsWalletAvailable(self.__wallet.isAvailable)
            model.setResourceTypeFrom(self.__nyController.getResourceTypeFrom())
            model.setResourceTypeTo(self.__nyController.getResourceTypeTo())
            model.setIsExternal(isExternal and not hasBigBoxes)
            model.setIsFriendHangar(self.__friendsService.isInFriendHangar)

    def _finalize(self):
        g_eventBus.handleEvent(NyResourcesConverterPopup(eventType=NyResourcesConverterPopup.HIDE))
        super(NyResourcesConvertPopover, self)._finalize()

    def _getEvents(self):
        serverSettings = self.__lobbyContext.getServerSettings()
        return ((self.viewModel.onConvertClick, self.__onConvertClick),
         (self.viewModel.onGoToQuests, self._onGoToQuests),
         (self.viewModel.onGoToRewardKits, self._onGoToRewardKits),
         (self.viewModel.onChangeResourcesType, self.__onChangeResourcesType),
         (self.__wallet.onWalletStatusChanged, self.__updateWallet),
         (serverSettings.onServerSettingsChange, self.__onServerSettingsChange),
         (self.__nyController.currencies.onBalanceUpdated, self.__updateAvailableResources))

    def _onGoToQuests(self):
        showDailyQuests(DailyTabs.QUESTS)

    def _onGoToRewardKits(self):
        if getRewardKitsCount():
            showLootBoxEntry()
        else:
            showLootBoxBuyWindow()

    def __onConvertClick(self, args):
        fromResourceType = args.get('fromResource')
        toResourceType = args.get('toResource')
        toValue = int(args.get('value'))
        fromValue = int(self.__nyController.currencies.calculateInitialValueByReceived(toValue))
        self._convert(fromResourceType, fromValue, toResourceType, toValue, callback=self.__checkConvertResult)

    @decorators.adisp_process('newYear/resourcesConverter')
    def _convert(self, fromResourceType, fromValue, toResourceType, toValue, callback):
        result = yield NewYearConvertResourcesProcessor(fromResourceType, fromValue, toResourceType, toValue).request()
        callback(result=result)

    @staticmethod
    def __checkConvertResult(result):
        if result.success:
            NewYearSoundsManager.playEvent(backport.sound(R.sounds.hangar_newyear_level_points_anim()))
        elif result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @replaceNoneKwargsModel
    def __updateAvailableResources(self, model=None):
        availableResources = model.getAvailableResources()
        availableResources.clear()
        for resource in RESOURCES_ORDER:
            amount = self.__nyController.currencies.getResouceBalance(resource.value)
            resourceModel = NyResourceModel()
            resourceModel.setType(resource.value)
            resourceModel.setValue(amount)
            availableResources.addViewModel(resourceModel)

        availableResources.invalidate()

    def __updateWallet(self, *args):
        self.viewModel.setIsWalletAvailable(self.__wallet.isAvailable)

    def __onChangeResourcesType(self, args):
        resourceFrom = args.get('resourceFrom')
        resourceTo = args.get('resourceTo')
        if resourceFrom not in [ res.value for res in RESOURCES_ORDER ] or resourceTo not in [ res.value for res in RESOURCES_ORDER ]:
            return
        self.__nyController.setResourceTypeFrom(resourceFrom)
        self.__nyController.setResourceTypeTo(resourceTo)

    @replaceNoneKwargsModel
    def __updateBoxesAvailability(self, model=None):
        model.setIsBoxesAvailable(self.__lobbyContext.getServerSettings().isLootBoxesEnabled())

    @server_settings.serverSettingsChangeListener(NY_CONFIG_NAME)
    def __onServerSettingsChange(self, diff):
        self.__updateBoxesAvailability()

    def __getShopSource(self):
        shopConfig = self.__lobbyContext.getServerSettings().getLootBoxShop()
        return shopConfig.get(NYLootBoxConsts.SOURCE, NYLootBoxConsts.IGB)
