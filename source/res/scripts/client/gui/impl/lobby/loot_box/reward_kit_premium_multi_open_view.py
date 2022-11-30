# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/reward_kit_premium_multi_open_view.py
import logging
from adisp import adisp_process
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer
from gui import SystemMessages
from gui.impl.auxiliary.rewards_helper import getBackportTooltipData, isVideoVehicle, isSpecialStyle, getVehByStyleCD, formatEliteVehicle
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootboxes.components.loot_box_multi_open_renderer_model import LootBoxMultiOpenRendererModel
from gui.impl.gen.view_models.views.lobby.lootboxes.reward_kit_premium_multi_open_view_model import RewardKitPremiumMultiOpenViewModel
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.impl.lobby.loot_box.loot_box_bonuses_helpers import MULTIOPEN_AWARDS_MAX_COUNT, getLootboxBonuses, getNYLootBoxBonusPacker, ORDER_BY_BOX_TYPE
from gui.impl.lobby.loot_box.loot_box_helper import getTooltipContent, fireHideMultiOpenView, isLootboxValid, LootBoxHideableView, LootBoxShowHideCloseHandler, SpecialRewardData, showLootBoxSpecialReward2, SpecialGuestRewardData
from gui.impl.lobby.new_year.tooltips.ny_customizations_statistics_tooltip import NyCustomizationsStatisticsTooltip
from gui.impl.lobby.new_year.tooltips.ny_resource_tooltip import NyResourceTooltip
from gui.impl.lobby.new_year.tooltips.ny_vehicles_statistics_tooltip import NyVehiclesStatisticsTooltip
from gui.impl.lobby.new_year.tooltips.ny_equipments_statistics_tooltip import NyEquipmentsStatisticsTooltip
from gui.impl.lobby.loot_box.loot_box_helper import setGaranteedRewardData
from gui.impl.lobby.loot_box.loot_box_sounds import setOverlayHangarGeneral, LootBoxViewEvents, playSound
from gui.impl.lobby.new_year.ny_reward_kit_statistics import NyRewardKitStatistics
from gui.impl.new_year.new_year_bonus_packer import packBonusModelAndTooltipData
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared import event_dispatcher
from shared_utils import findFirst
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showLootBoxEntry
from gui.shared.events import LootboxesEvent
from gui.shared.gui_items import Vehicle
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from helpers import dependency, int2roman
from new_year.ny_constants import GuestsQuestsTokens
from skeletons.gui.game_control import IFestivityController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.ny.loggers import NyStatisticsPopoverLogger
_logger = logging.getLogger(__name__)

class RewardKitPremiumMultiOpenView(LootBoxHideableView):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __festivityController = dependency.descriptor(IFestivityController)
    __popoverLogger = NyStatisticsPopoverLogger()

    def __init__(self, lootBoxItem, rewards, boxesToOpen, isGuaranteedReward=False):
        settings = ViewSettings(R.views.lobby.new_year.RewardKitPremiumMultiOpenView(), flags=ViewFlags.VIEW, model=RewardKitPremiumMultiOpenViewModel())
        settings.args = (lootBoxItem, rewards, boxesToOpen)
        super(RewardKitPremiumMultiOpenView, self).__init__(settings)
        self.__tooltips = {}
        self.__boxItem = lootBoxItem
        self.__openedCount = 0
        self.__needToOpen = 0
        self.__isOpenNext = True
        self.__currentRewardsPage = 0
        self.__showHideCloseHandler = LootBoxShowHideCloseHandler()
        self.__rewardKitStatistics = NyRewardKitStatistics()
        self.__isGuaranteedReward = isGuaranteedReward
        self.__lastStatisticsResetFailed = False
        self.__specialRewardData = {}

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = BackportTooltipWindow(self.__tooltips[tooltipId], self.getParentWindow(), event=event) if tooltipId is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(RewardKitPremiumMultiOpenView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyVehiclesStatisticsTooltip():
            return NyVehiclesStatisticsTooltip(self.__boxItem.getID())
        if contentID == R.views.lobby.new_year.tooltips.NyCustomizationsStatisticsTooltip():
            return NyCustomizationsStatisticsTooltip(self.__boxItem.getID())
        if contentID == R.views.lobby.new_year.tooltips.NyResourceTooltip():
            return NyResourceTooltip(event.getArgument('type'))
        if contentID == R.views.lobby.new_year.tooltips.NyEquipmentsStatisticsTooltip():
            return NyEquipmentsStatisticsTooltip(self.__boxItem.getID())
        tooltipData = getBackportTooltipData(event, self.__tooltips)
        return getTooltipContent(event, tooltipData)

    @property
    def viewModel(self):
        return super(RewardKitPremiumMultiOpenView, self).getViewModel()

    def _subscribe(self):
        super(RewardKitPremiumMultiOpenView, self)._subscribe()
        self.__showHideCloseHandler.startListen(self.getParentWindow())

    def _getEvents(self):
        model = self.viewModel
        events = super(RewardKitPremiumMultiOpenView, self)._getEvents()
        return events + ((model.onOpenBox, self.__onOpenBox),
         (model.openNextBoxes, self.__openNextBoxes),
         (model.onClose, self.__onWindowClose),
         (model.showSpecialReward, self.__showSpecialReward),
         (model.onViewShowed, self.__onViewShowed),
         (model.guaranteedReward.onShowInfo, self.__onGuaranteedRewardsInfo),
         (model.rewardKitStatistics.onResetStatistics, self.__onResetClick),
         (model.rewardKitStatistics.onUpdateLastSeen, self.__onUpdateLastSeen),
         (self.__itemsCache.onSyncCompleted, self.__onCacheResync),
         (self.__festivityController.onStateChanged, self.__onStateChange),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingChanged))

    def _getListeners(self):
        listeners = super(RewardKitPremiumMultiOpenView, self)._getListeners()
        return listeners + ((LootboxesEvent.ON_SHOW_SPECIAL_REWARDS_CLOSED, self.__onSpecialRewardsClosed, EVENT_BUS_SCOPE.LOBBY), (LootboxesEvent.ON_STATISTICS_RESET, self.__onStatisticsReset, EVENT_BUS_SCOPE.LOBBY))

    def _initialize(self, *args, **kwargs):
        super(RewardKitPremiumMultiOpenView, self)._initialize()
        playSound(LootBoxViewEvents.PREMIUM_MULTI_ENTER)
        setOverlayHangarGeneral(True)
        if args and len(args) == 3:
            self.__boxItem, rewards, self.__needToOpen = args
            self.__currentRewardsPage = 1
            with self.viewModel.transaction() as model:
                model.setIsMemoryRiskySystem(self._isMemoryRiskySystem)
                model.setMaxRewardsInRow(MULTIOPEN_AWARDS_MAX_COUNT)
                self.__updateStatistics()
            self.__update()
            self.__updateBoxesAvailability()
            self.__appendRewards(rewards[0], forceClearPage=True)

    def _finalize(self):
        setOverlayHangarGeneral(False)
        fireHideMultiOpenView()
        self.__showHideCloseHandler.stopListen()
        self.__showHideCloseHandler = None
        self.__rewardKitStatistics = None
        self.__specialRewardData.clear()
        super(RewardKitPremiumMultiOpenView, self)._finalize()
        return

    def __onStatisticsReset(self, event):
        self.__lastStatisticsResetFailed = event.ctx['serverError']

    def __onUpdateLastSeen(self):
        self.__rewardKitStatistics.updateLastSeen()

    def __onResetClick(self):
        self.__rewardKitStatistics.resetStatistics(self.__boxItem.getID())

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
        self.__updateStatistics()

    def __openNextBoxes(self, *_):
        self.viewModel.setIsOnPause(False)
        self.__openedCount = 0
        self.__needToOpen = min(RewardKitPremiumMultiOpenViewModel.WINDOW_MAX_BOX_COUNT, self.__boxItem.getInventoryCount())
        with self.getViewModel().transaction() as tx:
            lootboxes = tx.rewardRows.getItems()
            lootboxes.clear()
            lootboxes.invalidate()
        self.__onOpenBox(None)
        return

    def __updateStatistics(self):
        with self.viewModel.transaction() as model:
            self.__rewardKitStatistics.updateStatistics(model.rewardKitStatistics, self.__boxItem.getID(), self.__lastStatisticsResetFailed)

    def __onOpenBox(self, *_):
        if self.__openedCount < self.__needToOpen:
            self.__isOpenNext = True
            self.__validateNextLootBox()

    def __validateNextLootBox(self):
        if self.__isOpenNext and not self.viewModel.getIsOnPause():
            forceClearPage = False
            if len(self.viewModel.getRewards()) >= RewardKitPremiumMultiOpenViewModel.WINDOW_MAX_BOX_COUNT:
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
            g_eventBus.handleEvent(LootboxesEvent(LootboxesEvent.REMOVE_HIDE_VIEW), EVENT_BUS_SCOPE.LOBBY)
            self._isCanClose = True
            return
        g_eventBus.handleEvent(LootboxesEvent(LootboxesEvent.NEED_STOP_ENTRY_VIDEO), EVENT_BUS_SCOPE.LOBBY)

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
        self.viewModel.setIsRewardKitsEnabled(self.__isBoxesAvailable())

    def __isBoxesAvailable(self):
        serverSettings = self.__lobbyContext.getServerSettings()
        return serverSettings.isLootBoxesEnabled() and serverSettings.isLootBoxEnabled(self.__boxItem.getID())

    @adisp_process
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

    def __bonusOrder(self, bonus):
        order = ORDER_BY_BOX_TYPE.get(self.__boxItem.getCategory())
        name = bonus.getName()
        if name == 'items':
            if findFirst(lambda item: item.isModernized, bonus.getItems()):
                name = 'modernizedEquipment'
        if name == 'currencies':
            name = bonus.getCode()
        key = order.index(name) if name in order else len(order)
        return key

    def __createLootRewardRenderer(self, lootboxRewards):
        lootboxRewardRenderer = LootBoxMultiOpenRendererModel()
        rewardsList = lootboxRewardRenderer.getRewards()
        specialIds = lootboxRewardRenderer.getSpecialIds()
        rewardsList.clear()
        specialIds.clear()
        self.__specialRewardData.clear()
        bonuses, _ = getLootboxBonuses(lootboxRewards, MULTIOPEN_AWARDS_MAX_COUNT, self.__bonusOrder)
        packBonusModelAndTooltipData(bonuses, rewardsList, getNYLootBoxBonusPacker(), self.__tooltips, self.__getBonusCatchers())
        for specialId in self.__specialRewardData:
            specialIds.addNumber(specialId)

        rewardsList.invalidate()
        return lootboxRewardRenderer

    def __onServerSettingChanged(self, diff):
        if 'lootBoxes_config' in diff:
            self.__update()
            self.__updateStatistics()
        self.__updateBoxesAvailability()

    def __onStateChange(self):
        if not self.__festivityController.isEnabled():
            self.destroyWindow()

    @staticmethod
    def __onGuaranteedRewardsInfo(_=None):
        event_dispatcher.showLootBoxGuaranteedRewardsInfo()

    def __getBonusCatchers(self):
        return {'vehicles': self.__vehicleBonusCatcher,
         'customizations': self.__customizationBonusCatcher,
         'battleToken': self.__tokenBattleTokenBonusCatcher}

    def __tokenBattleTokenBonusCatcher(self, bonus, packedBonusList):
        for tokenID in bonus.getTokens().iterkeys():
            model = None
            if tokenID == GuestsQuestsTokens.TOKEN_CAT:
                model = findFirst(lambda model: model.getName() == GuestsQuestsTokens.GUEST_C, packedBonusList)
                if model is not None:
                    self.__specialRewardData[int(model.getIndex())] = self.__createSpecialRewardGuestData()

        return

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

    def __createSpecialRewardGuestData(self):
        return SpecialGuestRewardData(congratsType=LootCongratsTypes.CONGRAT_TYPE_GUEST_C, backToSingleOpening=False)

    def __createSpecialRewardData(self, sourceID, congratsType, vehicle):
        return SpecialRewardData(sourceName=Vehicle.getIconResourceName(Vehicle.getNationLessName(vehicle.name)), congratsType=congratsType, congratsSourceId=sourceID, vehicleName=vehicle.userName, vehicleIsElite=vehicle.isElite, vehicleLvl=int2roman(vehicle.level), vehicleType=formatEliteVehicle(vehicle.isElite, vehicle.type), backToSingleOpening=False, isGuaranteedReward=self.__isGuaranteedReward)


class RewardKitPremiumMultiOpenWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, lootBoxItem, rewards, boxesToOpen, parent=None, guaranteedReward=False):
        super(RewardKitPremiumMultiOpenWindow, self).__init__(content=RewardKitPremiumMultiOpenView(lootBoxItem, rewards, boxesToOpen, guaranteedReward), parent=parent, layer=WindowLayer.TOP_WINDOW, isModal=False)
