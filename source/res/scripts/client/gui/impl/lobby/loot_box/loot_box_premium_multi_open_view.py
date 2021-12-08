# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_premium_multi_open_view.py
import logging
from adisp import process
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer
from gui import SystemMessages
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import getBackportTooltipData, isVideoVehicle, isSpecialStyle, getVehByStyleCD, formatEliteVehicle
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootboxes.components.loot_box_multi_open_renderer_model import LootBoxMultiOpenRendererModel
from gui.impl.gen.view_models.views.lobby.lootboxes.loot_box_premium_multi_open_view_model import LootBoxPremiumMultiOpenViewModel
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.impl.lobby.loot_box.loot_box_bonuses_helpers import MULTIOPEN_AWARDS_MAX_COUNT, getLootboxBonuses, getLootBoxBonusPacker
from gui.impl.lobby.loot_box.loot_box_helper import getTooltipContent, fireHideMultiOpenView, isLootboxValid, LootBoxHideableView, LootBoxShowHideCloseHandler, SpecialRewardData, showLootBoxSpecialReward2
from gui.impl.lobby.loot_box.loot_box_helper import setGaranteedRewardData
from gui.impl.lobby.loot_box.loot_box_sounds import setOverlayHangarGeneral, LootBoxViewEvents, playSound
from gui.impl.lobby.new_year.popovers.ny_loot_box_statistics_popover import NyLootBoxStatisticsPopover
from gui.impl.new_year.new_year_bonus_packer import packBonusModelAndTooltipData
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.pub.tooltip_window import SimpleTooltipContent
from gui.shared import event_dispatcher
from gui.shared import events
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showLootBoxEntry
from gui.shared.events import LootboxesEvent
from gui.shared.gui_items import Vehicle
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from helpers import dependency, int2roman
from skeletons.gui.game_control import IFestivityController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.ny.loggers import NyStatisticsPopoverLogger
_logger = logging.getLogger(__name__)

class LootBoxPremiumMultiOpenView(LootBoxHideableView):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _festivityController = dependency.descriptor(IFestivityController)
    __popoverLogger = NyStatisticsPopoverLogger()

    def __init__(self, lootBoxItem, rewards, boxesToOpen, isGuaranteedReward=False):
        settings = ViewSettings(R.views.lobby.new_year.LootBoxPremiumMultiOpenView(), flags=ViewFlags.VIEW, model=LootBoxPremiumMultiOpenViewModel())
        settings.args = (lootBoxItem, rewards, boxesToOpen)
        super(LootBoxPremiumMultiOpenView, self).__init__(settings)
        self.__tooltips = {}
        self.__boxItem = None
        self.__openedCount = 0
        self.__needToOpen = 0
        self.__isOpenNext = True
        self.__currentRewardsPage = 0
        self.__showHideCloseHandler = LootBoxShowHideCloseHandler()
        self.__isGuaranteedReward = isGuaranteedReward
        self.__lastStatisticsResetFailed = False
        self.__specialRewardData = {}
        return

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = BackportTooltipWindow(self.__tooltips[tooltipId], self.getParentWindow()) if tooltipId is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(LootBoxPremiumMultiOpenView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyShardsTooltip():
            tooltipData = self.__tooltips[event.getArgument('tooltipId')]
            return SimpleTooltipContent(contentID=R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent(), body=backport.text(R.strings.ny.fragments.tooltip(), count=tooltipData.specialArgs[0]))
        tooltipData = getBackportTooltipData(event, self.__tooltips)
        return getTooltipContent(event, tooltipData)

    def createPopOverContent(self, event):
        if event.contentID == R.views.lobby.new_year.popovers.NyLootBoxStatisticsPopover():
            self.__popoverLogger.logClickInMultipleOpen()
            return NyLootBoxStatisticsPopover(self.__boxItem.getID(), self.__lastStatisticsResetFailed)
        return super(LootBoxPremiumMultiOpenView, self).createPopOverContent(event)

    @property
    def viewModel(self):
        return super(LootBoxPremiumMultiOpenView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(LootBoxPremiumMultiOpenView, self)._initialize()
        self.__showHideCloseHandler.startListen(self.getParentWindow())
        playSound(LootBoxViewEvents.PREMIUM_MULTI_ENTER)
        setOverlayHangarGeneral(True)
        if args and len(args) == 3:
            self.__boxItem, rewards, self.__needToOpen = args
            self.__currentRewardsPage = 1
            self.viewModel.onOpenBox += self.__onOpenBox
            self.viewModel.openNextBoxes += self.__openNextBoxes
            self.viewModel.onClose += self.__onWindowClose
            self.viewModel.showSpecialReward += self.__showSpecialReward
            self.viewModel.onViewShowed += self.__onViewShowed
            self.viewModel.guaranteedReward.onInfoClick += self.__onGuaranteedRewardsInfo
            self.itemsCache.onSyncCompleted += self.__onCacheResync
            self._festivityController.onStateChanged += self.__onStateChange
            self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
            g_eventBus.addListener(LootboxesEvent.ON_SHOW_SPECIAL_REWARDS_CLOSED, self.__onSpecialRewardsClosed, scope=EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.addListener(events.LootboxesEvent.ON_STATISTICS_RESET, self.__onStatisticsReset, scope=EVENT_BUS_SCOPE.LOBBY)
            with self.viewModel.transaction() as model:
                model.setIsMemoryRiskySystem(self._isMemoryRiskySystem)
            self.__update()
            self.__updateBoxesAvailability()
            self.__appendRewards(rewards[0], forceClearPage=True)

    def _finalize(self):
        setOverlayHangarGeneral(False)
        fireHideMultiOpenView()
        self.__showHideCloseHandler.stopListen()
        self.__showHideCloseHandler = None
        self.viewModel.onOpenBox -= self.__onOpenBox
        self.viewModel.openNextBoxes -= self.__openNextBoxes
        self.viewModel.onViewShowed -= self.__onViewShowed
        self.viewModel.showSpecialReward -= self.__showSpecialReward
        self.viewModel.onClose -= self.__onWindowClose
        self.viewModel.guaranteedReward.onInfoClick -= self.__onGuaranteedRewardsInfo
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        self._festivityController.onStateChanged -= self.__onStateChange
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        g_eventBus.removeListener(LootboxesEvent.ON_SHOW_SPECIAL_REWARDS_CLOSED, self.__onSpecialRewardsClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.LootboxesEvent.ON_STATISTICS_RESET, self.__onStatisticsReset, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__specialRewardData.clear()
        super(LootBoxPremiumMultiOpenView, self)._finalize()
        return

    def __onStatisticsReset(self, event):
        self.__lastStatisticsResetFailed = event.ctx['serverError']

    def __onWindowClose(self, *_):
        if self._isMemoryRiskySystem:
            if not self._isCanClose:
                return
            self._startFade(self.__showEntryAndDestroy, withPause=True)
        else:
            self.destroyWindow()

    def __showEntryAndDestroy(self):
        showLootBoxEntry(category=self.__boxItem.getCategory(), lootBoxType=self.__boxItem.getType())
        self.destroyWindow()

    def __onCacheResync(self, *_):
        self.__update()

    def __openNextBoxes(self, *_):
        self.viewModel.setIsOnPause(False)
        self.__openedCount = 0
        self.__needToOpen = min(LootBoxPremiumMultiOpenViewModel.WINDOW_MAX_BOX_COUNT, self.__boxItem.getInventoryCount())
        with self.getViewModel().transaction() as tx:
            lootboxes = tx.rewardRows.getItems()
            lootboxes.clear()
            lootboxes.invalidate()
        self.__onOpenBox(None)
        return

    def __onOpenBox(self, *_):
        if self.__openedCount < self.__needToOpen:
            self.__isOpenNext = True
            self.__validateNextLootBox()

    def __validateNextLootBox(self):
        if self.__isOpenNext and not self.viewModel.getIsOnPause():
            forceClearPage = False
            if len(self.viewModel.getRewards()) >= LootBoxPremiumMultiOpenViewModel.WINDOW_MAX_BOX_COUNT:
                forceClearPage = True
                self.__currentRewardsPage += 1
            self.__openNextBox(forceClearPage)
            self.__isOpenNext = False

    def __setServerError(self):
        self.viewModel.setIsServerError(True)

    def __showSpecialReward(self, args):
        specialId = args.get('specialId')
        if specialId is None or specialId not in self.__specialRewardData:
            return
        else:
            self.viewModel.setIsPausedForSpecial(True)
            showLootBoxSpecialReward2(self.__specialRewardData[specialId], self.getParentWindow())
            return

    def __onViewShowed(self):
        if self._isMemoryRiskySystem:
            g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.REMOVE_HIDE_VIEW), EVENT_BUS_SCOPE.LOBBY)
            self._isCanClose = True
            return
        g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.NEED_STOP_ENTRY_VIDEO), EVENT_BUS_SCOPE.LOBBY)

    def __onSpecialRewardsClosed(self, _):
        self.viewModel.setIsPausedForSpecial(False)

    def __update(self):
        isValidBox = isLootboxValid(self.__boxItem.getType())
        with self.viewModel.transaction() as tx:
            setGaranteedRewardData(tx.guaranteedReward, self.__boxItem)
            if isValidBox:
                tx.setLeftToOpenCount(self.__needToOpen - self.__openedCount)
                tx.setNeedToOpen(self.__needToOpen)
                tx.setBoxCategory(self.__boxItem.getCategory())
                tx.setBoxesCounter(self.__boxItem.getInventoryCount())
            else:
                tx.setBoxesCounter(0)
                _logger.warning('Lootbox %r is missing on Server!', self.__boxItem)

    def __updateBoxesAvailability(self):
        self.viewModel.setIsLootboxesEnabled(self.__isBoxesAvailable())

    def __isBoxesAvailable(self):
        serverSettings = self.lobbyContext.getServerSettings()
        return serverSettings.isLootBoxesEnabled() and serverSettings.isLootBoxEnabled(self.__boxItem.getID())

    @process
    def __openNextBox(self, forceClearPage=False):
        result = yield LootBoxOpenProcessor(self.__boxItem, 1).request()
        if result:
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if result.success:
                rewardsList = result.auxData['bonus']
                self.__isGuaranteedReward = 'usedLimits' in result.auxData['extData']
                if not rewardsList:
                    _logger.error('Lootbox is opened, but no rewards has been received.')
                    self.__setServerError()
                else:
                    self.__appendRewards(rewardsList[0], forceClearPage)
            else:
                self.__setServerError()
        else:
            self.__setServerError()

    def __appendRewards(self, rewards, forceClearPage=False):
        self.__openedCount += 1
        with self.getViewModel().transaction() as tx:
            tx.setLeftToOpenCount(self.__needToOpen - self.__openedCount)
            lootboxes = tx.rewardRows.getItems()
            if forceClearPage:
                lootboxes.clear()
                tx.setCurrentPage(self.__currentRewardsPage)
                lootboxes.invalidate()
            lootboxes.addViewModel(self.__createLootRewardRenderer(rewards))
            lootboxes.invalidate()

    def __createLootRewardRenderer(self, lootboxRewards):
        lootboxRewardRenderer = LootBoxMultiOpenRendererModel()
        rewardsList = lootboxRewardRenderer.getRewards()
        specialIds = lootboxRewardRenderer.getSpecialIds()
        rewardsList.clear()
        specialIds.clear()
        self.__specialRewardData.clear()
        bonuses, _ = getLootboxBonuses(lootboxRewards, MULTIOPEN_AWARDS_MAX_COUNT)
        packBonusModelAndTooltipData(bonuses, rewardsList, getLootBoxBonusPacker(), self.__tooltips, self.__getBonusCatchers())
        for specialId in self.__specialRewardData:
            specialIds.addNumber(specialId)

        rewardsList.invalidate()
        return lootboxRewardRenderer

    def __onServerSettingChanged(self, diff):
        if 'lootBoxes_config' in diff:
            self.__update()
        self.__updateBoxesAvailability()

    def __onStateChange(self):
        if not self._festivityController.isEnabled():
            self.destroyWindow()

    @staticmethod
    def __onGuaranteedRewardsInfo(_=None):
        event_dispatcher.showLootBoxGuaranteedRewardsInfo()

    def __getBonusCatchers(self):
        return {'vehicles': self.__vehicleBonusCatcher,
         'customizations': self.__customizationBonusCatcher}

    def __vehicleBonusCatcher(self, bonus, packedBonusList):
        for vehicle, _ in bonus.getVehicles():
            if isVideoVehicle(vehicle):
                model = None
                for packedModel in packedBonusList:
                    if packedModel.getValue() == vehicle.shortUserName:
                        model = packedModel
                        break

                if model is not None:
                    self.__specialRewardData[int(model.getIndex())] = self.__createSpecialRewardData(vehicle.intCD, LootCongratsTypes.CONGRAT_TYPE_VEHICLE, vehicle)

        return

    def __customizationBonusCatcher(self, bonus, packedBonusList):
        for bonusData in bonus.getCustomizations():
            item = bonus.getC11nItem(bonusData)
            styleTypes = ('style', 'style_3d')
            if item.itemTypeName in styleTypes and isSpecialStyle(item.intCD):
                model = None
                for packedModel in packedBonusList:
                    if packedModel.getIcon() in styleTypes:
                        model = packedModel
                        break

                if model is not None:
                    vehicle = getVehByStyleCD(item.intCD)
                    self.__specialRewardData[int(model.getIndex())] = self.__createSpecialRewardData(item.intCD, LootCongratsTypes.CONGRAT_TYPE_STYLE, vehicle)

        return

    def __createSpecialRewardData(self, sourceID, congratsType, vehicle):
        return SpecialRewardData(sourceName=Vehicle.getIconResourceName(Vehicle.getNationLessName(vehicle.name)), congratsType=congratsType, congratsSourceId=sourceID, vehicleName=vehicle.userName, vehicleIsElite=vehicle.isElite, vehicleLvl=int2roman(vehicle.level), vehicleType=formatEliteVehicle(vehicle.isElite, vehicle.type), backToSingleOpening=False, isGuaranteedReward=self.__isGuaranteedReward)


class LootBoxPremiumMultiOpenWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, lootBoxItem, rewards, boxesToOpen, parent=None, guaranteedReward=False):
        super(LootBoxPremiumMultiOpenWindow, self).__init__(content=LootBoxPremiumMultiOpenView(lootBoxItem, rewards, boxesToOpen, guaranteedReward), parent=parent, layer=WindowLayer.TOP_WINDOW, isModal=False)
