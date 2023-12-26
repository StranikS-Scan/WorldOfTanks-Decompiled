# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/ny_reward_kit_main_view.py
import logging
import typing
from functools import partial
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_REWARD_KIT_OPEN
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from adisp import adisp_process
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer, WindowStatus, ViewStatus
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.sf_window import SFWindow
from gui.app_loader import sf_lobby
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootboxes.components.loot_box_count_button_model import LootBoxCountButtonModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_reward_kit_main_view_model import NyRewardKitMainViewModel
from gui.impl.lobby.loot_box.loot_box_helper import showLootBoxReward, showLootBoxPremiumMultiOpen, MAX_PREMIUM_BOXES_TO_OPEN, getLootBoxByTypeAndCategory, LootBoxHideableView, setGaranteedRewardData
from gui.impl.lobby.loot_box.loot_box_notification import LootBoxNotification
from gui.impl.lobby.loot_box.loot_box_sounds import LootBoxViewEvents, playSound, LOOTBOXES_SOUND_SPACE
from gui.impl.lobby.new_year.tooltips.ny_guaranteed_reward_tooltip import NyGuaranteedRewardTooltip
from gui.impl.lobby.new_year.tooltips.ny_customizations_statistics_tooltip import NyCustomizationsStatisticsTooltip
from gui.impl.lobby.new_year.tooltips.ny_reward_kit_guest_c_tooltip import NyRewardKitGuestCTooltip
from gui.impl.lobby.new_year.tooltips.ny_vehicles_statistics_tooltip import NyVehiclesStatisticsTooltip
from gui.impl.lobby.new_year.tooltips.ny_equipments_statistics_tooltip import NyEquipmentsStatisticsTooltip
from gui.impl.lobby.new_year.tooltips.ny_resource_tooltip import NyResourceTooltip
from gui.impl.lobby.platoon.view.platoon_selection_view import SelectionWindow
from gui.impl.lobby.tooltips.loot_box_category_tooltip import LootBoxCategoryTooltipContent
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundsManager, RANDOM_STYLE_BOX
from gui.impl.new_year.views.tabs_controller import RewardKitsEntryViewTabsController
from gui.impl.pub.lobby_window import LobbyWindow
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared import event_dispatcher
from gui.shared.events import LootboxesEvent
from gui.shared.gui_items.loot_box import NewYearCategories, NewYearLootBoxes, CATEGORIES_GUI_ORDER_NY
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from messenger.proto.events import g_messengerEvents
from helpers import dependency, isPlayerAccount
from items.components.ny_constants import ToySettings
from ny_common.settings import NYLootBoxConsts
from realm import CURRENT_REALM
from shared_utils import nextTick
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from uilogging.ny.loggers import NyLootBoxesFlowLogger, NyStatisticsPopoverLogger
from gui.impl.lobby.new_year.ny_reward_kit_statistics import NyRewardKitStatistics
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window
_logger = logging.getLogger(__name__)
_OPEN_BOXES_COUNTERS = (1, 5)
_DEFAULT_BTN_IDX = 0
_ONLY_CB_BTN_IDX = 2
_LOW_PRIORITY_WINDOWS = (VIEW_ALIAS.AWARD_WINDOW, VIEW_ALIAS.AWARD_WINDOW_MODAL, VIEW_ALIAS.ADVENT_CALENDAR)

class NyRewardKitMainView(LootBoxHideableView):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __nyController = dependency.descriptor(INewYearController)
    __notificationMgr = dependency.descriptor(INotificationWindowController)
    __gui = dependency.descriptor(IGuiLoader)
    __flowlogger = NyLootBoxesFlowLogger()
    __popoverLogger = NyStatisticsPopoverLogger()
    __REWARD_KIT_CATEGORY_MAPPING = {NewYearCategories.NEWYEAR: ToySettings.NEW_YEAR,
     NewYearCategories.CHRISTMAS: ToySettings.CHRISTMAS,
     NewYearCategories.ORIENTAL: ToySettings.ORIENTAL,
     NewYearCategories.FAIRYTALE: ToySettings.FAIRYTALE}
    _COMMON_SOUND_SPACE = LOOTBOXES_SOUND_SPACE
    __slots__ = ('__isVideoOff', '__tabsController', '__availableBoxes', '__isDeliveryVideoPlaying', '__lastViewed', '__isWaitingToHide', '__isViewHidden', '__openBoxesFunc', '__lastStatisticsResetFailed', '__rewardKitStatistics', '__isBuyViewOpen')

    def __init__(self, layoutID, lootBoxType=NewYearLootBoxes.PREMIUM, category=''):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = NyRewardKitMainViewModel()
        settings.kwargs = {'initLootBoxType': lootBoxType,
         'initCategory': category}
        super(NyRewardKitMainView, self).__init__(settings)
        self.__rewardKitStatistics = NyRewardKitStatistics()
        self.__isVideoOff = False
        self.__tabsController = RewardKitsEntryViewTabsController()
        self.__availableBoxes = None
        self.__isWaitingToHide = False
        self.__isViewHidden = False
        self.__openBoxesFunc = None
        self.__isDeliveryVideoPlaying = False
        self.__lastViewed = -1
        self.__lastStatisticsResetFailed = False
        self.__isBuyViewOpen = False
        return

    @property
    def viewModel(self):
        return super(NyRewardKitMainView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.loot_box_category_tooltip.LootBoxCategoryTooltipContent():
            return LootBoxCategoryTooltipContent(event.getArgument('category', ''))
        if contentID == R.views.lobby.new_year.tooltips.NyGuaranteedRewardTooltip():
            return NyGuaranteedRewardTooltip()
        if contentID == R.views.lobby.new_year.tooltips.NyResourceTooltip():
            return NyResourceTooltip(event.getArgument('type'))
        if contentID == R.views.lobby.new_year.tooltips.NyVehiclesStatisticsTooltip():
            return NyVehiclesStatisticsTooltip(self.__tabsController.getSelectedBoxID())
        if contentID == R.views.lobby.new_year.tooltips.NyEquipmentsStatisticsTooltip():
            return NyEquipmentsStatisticsTooltip(self.__tabsController.getSelectedBoxID())
        if contentID == R.views.lobby.new_year.tooltips.NyCustomizationsStatisticsTooltip():
            return NyCustomizationsStatisticsTooltip(self.__tabsController.getSelectedBoxID())
        return NyRewardKitGuestCTooltip() if contentID == R.views.lobby.new_year.tooltips.NyRewardKitGuestCTooltip() else super(NyRewardKitMainView, self).createToolTipContent(event, contentID)

    def externalSelectTab(self, category=''):
        if self.viewStatus != ViewStatus.LOADED or self.__isDeliveryVideoPlaying:
            return
        if category in CATEGORIES_GUI_ORDER_NY:
            tabName = category
        else:
            tabName = self.__tabsController.getInitCategory()
        currentTabName = self.__tabsController.getSelectedBoxName()
        if not tabName or tabName == currentTabName:
            return
        self.__doSelectTab(tabName)

    @sf_lobby
    def _app(self):
        return None

    def _onLoading(self, initLootBoxType, initCategory, *args, **kwargs):
        super(NyRewardKitMainView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__isVideoOff = self.__settingsCore.getSetting(NewYearStorageKeys.LOOT_BOX_VIDEO_OFF)
            model.setIsVideoOff(self.__isVideoOff)
            self.__availableBoxes = self.__itemsCache.items.tokens.getLootBoxesCountByType()
            self.__tabsController.updateAvailableBoxes(self.__availableBoxes)
            self.__tabsController.setInitState(initLootBoxType, initCategory)
            self.__tabsController.updateTabModels(model.sidebar.getItemsTabBar())
            model.sidebar.setStartIndex(self.__tabsController.getSelectedTabIdx())
            boxesButtons = model.boxesCountButtons
            for idx, boxesCount in enumerate(_OPEN_BOXES_COUNTERS):
                labelRes = R.strings.ny.rewardKitMain.entryView.openBoxes.dyn('_'.join(('count', str(boxesCount))))
                boxCountButtonModel = LootBoxCountButtonModel()
                boxCountButtonModel.setIdx(idx)
                boxCountButtonModel.setLabel(labelRes())
                boxCountButtonModel.setIsSelected(_DEFAULT_BTN_IDX == idx)
                boxesButtons.addViewModel(boxCountButtonModel)

            boxesButtons.addSelectedIndex(_DEFAULT_BTN_IDX)
            self.__updateMainContent()
            self.__updateLootBoxViewed()
            self.__updateLootBoxesDeliveryVideo()
            self.__updateStatistics()

    def _initialize(self, *args, **kwargs):
        super(NyRewardKitMainView, self)._initialize()
        AccountSettings.setUIFlag(NY_REWARD_KIT_OPEN, True)
        g_messengerEvents.onLockPopUpMessages(key=self.__class__.__name__, lockHigh=True, clear=True)
        if self._isMemoryRiskySystem:
            g_eventBus.handleEvent(LootboxesEvent(LootboxesEvent.REMOVE_HIDE_VIEW), EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        self.__stopVideo()
        AccountSettings.setUIFlag(NY_REWARD_KIT_OPEN, False)
        if self.__openBoxesFunc is not None:
            self.__openBoxesFunc = None
        g_messengerEvents.onUnlockPopUpMessages(key=self.__class__.__name__)
        self.__rewardKitStatistics = None
        if isPlayerAccount():
            LootBoxNotification.saveSettings()
            self.__settingsCore.applyStorages(False)
        super(NyRewardKitMainView, self)._finalize()
        return

    def _getEvents(self):
        model = self.viewModel
        events = super(NyRewardKitMainView, self)._getEvents()
        return events + ((model.onWindowClose, self.__onWindowClose),
         (model.onChangeTab, self.__onBoxSelectTabClick),
         (model.onCountSelected, self.__onCountSelected),
         (model.onBuyBox, self.__onBuyBox),
         (model.onAnimationSwitch, self.__onAnimationSwitch),
         (model.onOpenBoxFromHitArea, self.__openBoxFromHitArea),
         (model.onOpenBox, self.__onOpenBoxFromButton),
         (model.onSwitchBoxHover, self.__onSwitchBoxHover),
         (model.guaranteedReward.onShowInfo, self.__onBoxesInfoClick),
         (model.rewardKitStatistics.onResetStatistics, self.__onResetStatistics),
         (model.rewardKitStatistics.onUpdateLastSeen, self.__onUpdateLastSeen),
         (self._app.containerManager.onViewAddedToContainer, self.__onViewAddedToContainer),
         (self.__itemsCache.onSyncCompleted, self.__onCacheResync),
         (self.__settingsCore.onSettingsChanged, self.__updateVideoOff),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingChanged),
         (self.__nyController.onStateChanged, self.__onNyStateUpdated),
         (self.__gui.windowsManager.onWindowStatusChanged, self.__onWindowStatusChanged))

    def _getListeners(self):
        listeners = super(NyRewardKitMainView, self)._getListeners()
        if not self._isMemoryRiskySystem:
            listeners += ((LootboxesEvent.ON_REWARD_VIEW_CLOSED, self.__handleRewardViewHide, EVENT_BUS_SCOPE.LOBBY), (LootboxesEvent.ON_MULTI_OPEN_VIEW_CLOSED, self.__handleRewardViewHide, EVENT_BUS_SCOPE.LOBBY))
        return listeners + ((LootboxesEvent.ON_DELIVERY_VIDEO_END, self.__onDeliveryVideoEnd, EVENT_BUS_SCOPE.LOBBY),
         (LootboxesEvent.ON_BOX_TRANSITION_END, self.__onBoxTransitionEnd, EVENT_BUS_SCOPE.LOBBY),
         (LootboxesEvent.ON_STATISTICS_RESET, self.__onStatisticsReset, EVENT_BUS_SCOPE.LOBBY),
         (LootboxesEvent.ON_BUY_VIEW_CLOSED, self.__onBuyViewClosed, EVENT_BUS_SCOPE.LOBBY))

    def _getSelectedBoxesCount(self):
        boxNumber = 0
        category = self.__tabsController.getSelectedBoxCategory()
        if NewYearLootBoxes.PREMIUM in self.__availableBoxes:
            available = self.__availableBoxes[NewYearLootBoxes.PREMIUM]
            categories = available['categories']
            boxNumber = categories[category] if category in categories else available['total']
        return boxNumber

    def _getVideoOff(self):
        return self.__isVideoOff

    def _isSingleOpen(self):
        openCount = _OPEN_BOXES_COUNTERS[self.__getSelectedCountIndx()]
        return openCount == 1

    def _onLoaded(self, *args, **kwargs):
        super(NyRewardKitMainView, self)._onLoaded(*args, **kwargs)
        nextTick(partial(self.__onNyStateUpdated))()

    def __onStatisticsButtonClick(self):
        self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.NY_STATISTICS_HINT_SHOWN: True})

    def __onResetStatistics(self):
        self.__rewardKitStatistics.resetStatistics(self.__tabsController.getSelectedBoxID())

    def __onUpdateLastSeen(self):
        self.__rewardKitStatistics.updateLastSeen()

    def __updateStatistics(self):
        with self.viewModel.transaction() as model:
            self.__rewardKitStatistics.updateStatistics(model.rewardKitStatistics, self.__tabsController.getSelectedBoxID(), self.__lastStatisticsResetFailed)

    def __onWindowClose(self):
        if self.__isWaitingToHide:
            return
        if not self.__stopVideo():
            g_eventBus.handleEvent(LootboxesEvent(LootboxesEvent.ON_MAIN_VIEW_CLOSED), scope=EVENT_BUS_SCOPE.LOBBY)
            self.__flowlogger.logCloseClick(currentObject=NewYearNavigation.getCurrentObject(), currentView=NewYearNavigation.getCurrentViewName())
            self.destroyWindow()

    def __stopVideo(self):
        if self.__isDeliveryVideoPlaying:
            g_eventBus.handleEvent(LootboxesEvent(LootboxesEvent.NEED_DELIVERY_VIDEO_STOP), scope=EVENT_BUS_SCOPE.LOBBY)
            self.__isDeliveryVideoPlaying = False
            return True
        return False

    def __onCacheResync(self, *_):
        self.__update()

    def __update(self, isAfterRewardView=False):
        self.__availableBoxes = self.__itemsCache.items.tokens.getLootBoxesCountByType()
        if isAfterRewardView:
            self.__isWaitingToHide = False
        if self.__isWaitingToHide:
            return
        with self.viewModel.transaction() as model:
            if isAfterRewardView:
                self.viewModel.setIsBoxOpenEnabled(True)
                if self.__getSelectedBoxNumber() > 0:
                    model.setIsBoxChangeAnimation(False)
                else:
                    model.setIsBoxChangeAnimation(True)
            self.__updateLootBoxViewed(isAfterRewardView)
            self.__updateMainContent()
            self.__updateLootBoxesDeliveryVideo(isAfterRewardView)
            self.__tabsController.updateAvailableBoxes(self.__availableBoxes)
            self.__tabsController.updateTabModels(model.sidebar.getItemsTabBar())
        self.__updateStatistics()

    def __getSelectedBoxNumber(self):
        boxNumber = 0
        boxCategory = self.__tabsController.getSelectedBoxCategory()
        if NewYearLootBoxes.PREMIUM in self.__availableBoxes:
            available = self.__availableBoxes[NewYearLootBoxes.PREMIUM]
            categories = available['categories']
            boxNumber = categories[boxCategory] if boxCategory in categories else available['total']
        return boxNumber

    def __onViewAddedToContainer(self, _, pyEntity):
        if pyEntity.alias == VIEW_ALIAS.BATTLE_QUEUE:
            self.destroyWindow()

    def __onDeliveryVideoEnd(self, _=None):
        self.__isDeliveryVideoPlaying = False
        with self.viewModel.transaction() as model:
            model.setIsViewHidden(False)

    def __onBoxTransitionEnd(self, _=None):
        with self.viewModel.transaction() as model:
            model.setIsBoxChangeAnimation(False)

    def __onStatisticsReset(self, event):
        self.__lastStatisticsResetFailed = event.ctx['serverError']

    def __onBoxSelectTabClick(self, args=None):
        if self.viewModel.getIsBoxChangeAnimation():
            return
        tabName = args['tabName']
        self.__doSelectTab(tabName)

    def __doSelectTab(self, tabName):
        currentTabName = self.__tabsController.getSelectedBoxName()
        prevHasBoxes = self.viewModel.getIsOpenBoxBtnVisible()
        self.__tabsController.selectTab(tabName)
        self.__updateCategoryViewed()
        self.__updateMainContent(currentTabName != tabName, prevHasBoxes)
        self.__updateLootBoxesDeliveryVideo()
        self.__tabsController.updateTabModels(self.viewModel.sidebar.getItemsTabBar())

    def __updateMainContent(self, isClickTab=False, prevHasBoxes=False):
        with self.viewModel.transaction() as model:
            boxType = NewYearLootBoxes.PREMIUM
            boxCategory = self.__tabsController.getSelectedBoxCategory()
            boxNumber = self.__getSelectedBoxNumber()
            hasBoxes = boxNumber > 0
            if hasBoxes:
                self.__updateBoxesButtons(boxNumber)
            setting = self.__REWARD_KIT_CATEGORY_MAPPING.get(boxCategory) if boxCategory is not None else None
            NewYearSoundsManager.setStylesSwitchBox(setting if setting else RANDOM_STYLE_BOX)
            NewYearSoundsManager.setRTPCBoxEntryView(boxType)
            NewYearSoundsManager.setRTPCBoxAvailability(hasBoxes)
            if model.getCurrentName() and model.getCurrentName() != self.__tabsController.getSelectedBoxName():
                playSound(LootBoxViewEvents.LOGISTIC_CENTER_SWITCH)
            model.setSelectedBoxType(boxType)
            model.setCurrentName(self.__tabsController.getSelectedBoxName())
            model.setRealm(CURRENT_REALM)
            lootboxItem = getLootBoxByTypeAndCategory(boxType, boxCategory, isInInventory=False)
            isRewardKitsEnable = self.__lobbyContext.getServerSettings().isLootBoxesEnabled()
            shopConfig = self.__lobbyContext.getServerSettings().getLootBoxShop()
            source = shopConfig.get(NYLootBoxConsts.SOURCE, NYLootBoxConsts.EXTERNAL)
            isBoxEnabled = lootboxItem is not None and self.__lobbyContext.getServerSettings().isLootBoxEnabled(lootboxItem.getID())
            model.setIsOpenBoxBtnVisible(hasBoxes and isBoxEnabled)
            model.setIsBoxesAvailable(isBoxEnabled)
            model.setIsRewardKitEnable(isRewardKitsEnable)
            model.setIsExternalLink(source == NYLootBoxConsts.EXTERNAL)
            model.setCurrentCountButton(self.__getSelectedCountIndx())
            nyStorage = self.__settingsCore.serverSettings.getNewYearStorage()
            model.setIsStatisticsHintActive(not nyStorage.get(NewYearStorageKeys.NY_STATISTICS_HINT_SHOWN, False) and bool(self.__itemsCache.items.tokens.getLootBoxesStats()))
            if isClickTab and (hasBoxes or prevHasBoxes and not hasBoxes):
                model.setIsBoxChangeAnimation(True)
            setGaranteedRewardData(model.guaranteedReward, lootboxItem, not self.__isViewHidden, True)
        g_eventBus.handleEvent(LootboxesEvent(LootboxesEvent.ON_TAB_SELECTED, ctx={'tabName': self.__tabsController.getSelectedBoxName(),
         'hasBoxes': hasBoxes}), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def __updateBoxesButtons(self, boxNumber):
        boxesButtons = self.viewModel.boxesCountButtons
        boxesButtonsItems = boxesButtons.getItems()
        selectedIndex = self.__getSelectedCountIndx()
        for idx, countButton in enumerate(boxesButtonsItems):
            countButton.setIsEnabled(boxNumber >= _OPEN_BOXES_COUNTERS[idx])
            countButton.setIsVisible(idx != _ONLY_CB_BTN_IDX)

        isNeedSaveIndx = False
        if selectedIndex == _ONLY_CB_BTN_IDX:
            selectedIndex -= 1
            isNeedSaveIndx = True
        while selectedIndex > 0 and boxNumber < _OPEN_BOXES_COUNTERS[selectedIndex]:
            selectedIndex -= 1
            isNeedSaveIndx = True

        if isNeedSaveIndx:
            self.__saveSelectedCountBtnIndx(selectedIndex)
        self.__setSelectedCountBtn(selectedIndex)

    def __getSelectedBox(self, isInInventory=True):
        selectedType = NewYearLootBoxes.PREMIUM
        selectedCategory = self.__tabsController.getSelectedBoxCategory()
        return getLootBoxByTypeAndCategory(selectedType, selectedCategory, isInInventory=isInInventory)

    def __getSelectedCountIndx(self):
        boxCategory = self.__tabsController.getSelectedBoxCategory()
        return self.__nyController.getSavedBoxesButton(boxCategory)

    def __onCountSelected(self, data):
        indx = int(data.get('value', 0)) if data else 0
        self.__saveSelectedCountBtnIndx(indx)
        self.__setSelectedCountBtn(indx)

    def __saveSelectedCountBtnIndx(self, indx):
        boxCategory = self.__tabsController.getSelectedBoxCategory()
        self.__nyController.setSavedBoxesButton(boxCategory, indx)
        with self.viewModel.transaction() as model:
            model.setCurrentCountButton(self.__getSelectedCountIndx())

    def __setSelectedCountBtn(self, indx):
        boxesButtons = self.viewModel.boxesCountButtons
        boxesButtonsItems = boxesButtons.getItems()
        for idx, countButton in enumerate(boxesButtonsItems):
            countButton.setIsSelected(idx == indx)

        boxesButtons = self.viewModel.boxesCountButtons
        selectedIndices = boxesButtons.getSelectedIndices()
        selectedIndices.clear()
        boxesButtons.addSelectedIndex(indx)

    def __updateLootBoxViewed(self, isAfterRewardView=False):
        totalCount = self.__itemsCache.items.tokens.getLootBoxesTotalCount()
        if self.__lastViewed != -1 and self.__lastViewed == totalCount:
            return
        LootBoxNotification.setTotalLootBoxesCount(totalCount)
        self.__lastViewed = totalCount
        self.__updateCategoryViewed(isAfterRewardView)

    def __openBoxFromHitArea(self, _=None):
        self.__onOpenBox(isSingleOpening=True)

    def __onOpenBoxFromButton(self, _=None):
        self.__onOpenBox()

    def __onOpenBox(self, isSingleOpening=False):
        box = self.__getSelectedBox()
        if box is None:
            _logger.error('Can not open the selected lootbox!')
            return
        else:
            if isSingleOpening:
                openCount = 1
            else:
                openCount = _OPEN_BOXES_COUNTERS[self.__getSelectedCountIndx()]
                if openCount > MAX_PREMIUM_BOXES_TO_OPEN:
                    openCount = MAX_PREMIUM_BOXES_TO_OPEN
            invCount = box.getInventoryCount()
            self.__requestLootBoxOpen(box, min(invCount, openCount))
            return

    @adisp_process
    def __requestLootBoxOpen(self, boxItem, count):
        self.__isWaitingToHide = True
        self.__switchTabsAndButtonsInteraction(interactionEnabled=False)
        result = yield LootBoxOpenProcessor(boxItem, 1).request()
        if result:
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if result.success:
                rewardsList = result.auxData.get('bonus')
                if not rewardsList:
                    _logger.error('Lootbox is opened, but no rewards has been received.')
                    self.__switchTabsAndButtonsInteraction(interactionEnabled=True)
                    self.__isViewHidden = False
                    self.__isWaitingToHide = False
                    return
                guaranteedReward = 'usedLimits' in result.auxData['extData']
                parentWindow = None if self._isMemoryRiskySystem else self.getParentWindow()
                if count > 1:
                    openBoxesFunc = partial(showLootBoxPremiumMultiOpen, boxItem, rewardsList, count, parentWindow, guaranteedReward=guaranteedReward)
                else:
                    openBoxesFunc = partial(showLootBoxReward, boxItem, rewardsList[0], parentWindow, False, lastStatisticsResetFailed=self.__lastStatisticsResetFailed, guaranteedReward=guaranteedReward)
                if self._isMemoryRiskySystem:
                    self.__openBoxesFunc = openBoxesFunc
                    self._startFade(self.__openBoxesCallback, withPause=True)
                    self.__isWaitingToHide = False
                    self.__isViewHidden = True
                else:
                    openBoxesFunc()
            else:
                self.__switchTabsAndButtonsInteraction(interactionEnabled=True)
                self.__isWaitingToHide = False
                self.__isViewHidden = False
        return

    def __switchTabsAndButtonsInteraction(self, interactionEnabled):
        with self.viewModel.transaction() as model:
            model.setIsBoxChangeAnimation(not interactionEnabled)
            model.setIsBoxOpenEnabled(interactionEnabled)

    def __openBoxesCallback(self):
        if self.__openBoxesFunc is not None:
            self.__openBoxesFunc()
            self.__openBoxesFunc = None
        self.destroyWindow()
        return

    def __onServerSettingChanged(self, diff):
        if 'lootBoxes_config' in diff:
            self.__update()
            self.__updateStatistics()
        if not self.__lobbyContext.getServerSettings().isLootBoxesEnabled():
            self.destroyWindow()

    def __onNyStateUpdated(self):
        if not self.__nyController.isEnabled():
            self.destroyWindow()

    def __updateCategoryViewed(self, isAfterRewardView=False):
        selectedCategory = self.__tabsController.getSelectedBoxCategory()
        if selectedCategory is not None:
            LootBoxNotification.setCategoryNewCount(NewYearLootBoxes.PREMIUM, selectedCategory)
            if isAfterRewardView:
                LootBoxNotification.setCategoryDeliveredCount(selectedCategory)
        return

    def __updateLootBoxesDeliveryVideo(self, isAfterRewardView=False):
        if self.__isDeliveryVideoPlaying:
            return
        elif self.__isBuyViewOpen:
            return
        else:
            boxCategory = self.__tabsController.getSelectedBoxCategory()
            if boxCategory is not None and LootBoxNotification.hasDeliveredBox(boxCategory):
                if not isAfterRewardView:
                    self.__isDeliveryVideoPlaying = True
                    g_eventBus.handleEvent(LootboxesEvent(LootboxesEvent.NEED_DELIVERY_VIDEO_START), scope=EVENT_BUS_SCOPE.LOBBY)
                    self.__updateLootBoxesDeliveryVideoViewed()
                    with self.viewModel.transaction() as model:
                        model.setIsViewHidden(True)
            return

    def __updateLootBoxesDeliveryVideoViewed(self):
        for category in NewYearCategories.SETTINGS:
            LootBoxNotification.setCategoryDeliveredCount(category)

    def __updateVideoOff(self, diff):
        if NewYearStorageKeys.LOOT_BOX_VIDEO_OFF in diff:
            self.__isVideoOff = diff[NewYearStorageKeys.LOOT_BOX_VIDEO_OFF]
            self.viewModel.setIsVideoOff(self.__isVideoOff)

    def __onAnimationSwitch(self, _=None):
        g_eventBus.handleEvent(LootboxesEvent(LootboxesEvent.NEED_DELIVERY_VIDEO_STOP), scope=EVENT_BUS_SCOPE.LOBBY)
        self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.LOOT_BOX_VIDEO_OFF: not self.__isVideoOff})

    def __handleRewardViewHide(self, _):
        self.__isViewHidden = False
        self.__update(True)

    def __onSwitchBoxHover(self, event):
        isBoxHovered = event.get('value', False)
        self.__sendSwitchBoxHoveredEvent(isBoxHovered)

    def __sendSwitchBoxHoveredEvent(self, isBoxHovered):
        g_eventBus.handleEvent(LootboxesEvent(eventType=LootboxesEvent.SWITCH_BOX_HOVER, ctx={'isBoxHovered': isBoxHovered}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onWindowStatusChanged(self, uniqueID, newState):
        if newState == WindowStatus.LOADING:
            window = self.__gui.windowsManager.getWindow(uniqueID)
            self.__onWindowOpen(window)

    def __onWindowOpen(self, newWindow):
        layer = newWindow.layer
        if not WindowLayer.VIEW <= layer < WindowLayer.FULLSCREEN_WINDOW:
            return
        else:
            window = self.getParentWindow()
            if window is None:
                return
            needToClose = False
            if window != newWindow and (window.layer > layer or window.layer == layer) and not self.__isParent(window, newWindow) and self.__isAllowed(newWindow):
                if window.canBeClosed():
                    needToClose = True
                else:
                    _logger.info("Window %r hasn't been destroyed by opening window %r", window, newWindow)
            if needToClose:
                if not self.__notificationMgr.hasWindow(newWindow) and self.__isAllowed(newWindow):
                    _logger.info('Notification queue postpones by opening window %r', newWindow)
                    self.__notificationMgr.postponeActive()
                window.destroy()
            return

    @staticmethod
    def __isAllowed(window):
        if isinstance(window, SFWindow):
            alias = window.loadParams.viewKey.alias
            for priority in _LOW_PRIORITY_WINDOWS:
                if alias.startswith(priority):
                    return False

        return False if isinstance(window, SelectionWindow) else True

    @classmethod
    def __isParent(cls, pWindow, window):
        if window.parent is None:
            return False
        else:
            return True if window.parent == pWindow else cls.__isParent(pWindow, window.parent)

    def __onBuyBox(self, _=None):
        if self.__isWaitingToHide:
            return
        self.__flowlogger.logPageButtonsClick()
        self.__switchTabsAndButtonsInteraction(False)
        self.__isBuyViewOpen = True
        event_dispatcher.showLootBoxBuyWindow()

    @staticmethod
    def __onBoxesInfoClick(_=None):
        event_dispatcher.openLootBoxesInfoURL()

    def __onBuyViewClosed(self, _):
        self.__switchTabsAndButtonsInteraction(True)
        self.__isBuyViewOpen = False
        self.__updateLootBoxesDeliveryVideo()


class NyRewardKitViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, lootboxType, category, parent=None):
        super(NyRewardKitViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=NyRewardKitMainView(R.views.lobby.new_year.views.NyRewardKitMainView(), lootboxType, category), parent=parent, layer=WindowLayer.WINDOW)

    @dependency.replace_none_kwargs(notificationManager=INotificationWindowController)
    def load(self, notificationManager=None):
        notificationManager.lock(self.__class__.__name__)
        super(NyRewardKitViewWindow, self).load()

    @dependency.replace_none_kwargs(notificationManager=INotificationWindowController)
    def _finalize(self, notificationManager=None):
        super(NyRewardKitViewWindow, self)._finalize()
        notificationManager.unlock(self.__class__.__name__)
        notificationManager.releasePostponed()
