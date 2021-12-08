# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/ny_loot_box_main_view.py
import logging
import typing
from functools import partial
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from adisp import process
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer, WindowStatus, ViewStatus
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.sf_window import SFWindow
from gui.app_loader import sf_lobby
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.lootboxes.components.loot_box_count_button_model import LootBoxCountButtonModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_loot_box_main_view_model import NyLootBoxMainViewModel
from gui.impl.lobby.loot_box.loot_box_helper import showLootBoxReward, showLootBoxPremiumMultiOpen, MAX_PREMIUM_BOXES_TO_OPEN, showLootBoxMultiOpen, getLootBoxByTypeAndCategory, LootBoxHideableView, setGaranteedRewardData
from gui.impl.lobby.loot_box.loot_box_notification import LootBoxNotification
from gui.impl.lobby.loot_box.loot_box_sounds import LootBoxViewEvents, playSound, LOOTBOXES_SOUND_SPACE
from gui.impl.lobby.missions.daily_quests_view import DailyTabs
from gui.impl.lobby.new_year.popovers.ny_loot_box_statistics_popover import NyLootBoxStatisticsPopover
from gui.impl.lobby.new_year.tooltips.ny_guaranteed_reward_tooltip import NyGuaranteedRewardTooltip
from gui.impl.lobby.tooltips.loot_box_category_tooltip import LootBoxCategoryTooltipContent
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundsManager, RANDOM_STYLE_BOX
from gui.impl.new_year.views.tabs_controller import LootBoxesEntryViewTabsController
from gui.impl.pub.lobby_window import LobbyWindow
from gui.server_events.events_dispatcher import showDailyQuests
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared import event_dispatcher
from gui.shared import events
from gui.shared.gui_items.loot_box import NewYearCategories, NewYearLootBoxes, CATEGORIES_GUI_ORDER
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from messenger.proto.events import g_messengerEvents
from helpers import dependency, isPlayerAccount
from items.components.ny_constants import ToySettings
from new_year.ny_constants import AnchorNames
from realm import CURRENT_REALM
from shared_utils import nextTick
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController
from uilogging.ny.loggers import NyLootBoxesFlowLogger, NyStatisticsPopoverLogger
from gui.impl.lobby.platoon.view.platoon_welcome_view import SelectionWindow
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window
_logger = logging.getLogger(__name__)
_OPEN_BOXES_COUNTERS = (1, 5, 10)
_DEFAULT_BTN_IDX = 0
_ONLY_CB_BTN_IDX = 2
_LOW_PRIORITY_WINDOWS = (VIEW_ALIAS.AWARD_WINDOW, VIEW_ALIAS.AWARD_WINDOW_MODAL, VIEW_ALIAS.ADVENT_CALENDAR)

class NyLootBoxMainView(LootBoxHideableView):
    itemsCache = dependency.descriptor(IItemsCache)
    lobbyContext = dependency.descriptor(ILobbyContext)
    settingsCore = dependency.descriptor(ISettingsCore)
    __nyController = dependency.descriptor(INewYearController)
    __notificationMgr = dependency.descriptor(INotificationWindowController)
    __gui = dependency.descriptor(IGuiLoader)
    __flowlogger = NyLootBoxesFlowLogger()
    __popoverLogger = NyStatisticsPopoverLogger()
    __LOOT_BOX_CATEGORY_MAPPING = {NewYearCategories.NEWYEAR: ToySettings.NEW_YEAR,
     NewYearCategories.CHRISTMAS: ToySettings.CHRISTMAS,
     NewYearCategories.ORIENTAL: ToySettings.ORIENTAL,
     NewYearCategories.FAIRYTALE: ToySettings.FAIRYTALE}
    _COMMON_SOUND_SPACE = LOOTBOXES_SOUND_SPACE
    __slots__ = ('__isVideoOff', '__tabsController', '__availableBoxes', '__isDeliveryVideoPlaying', '__lastViewed', '__isWaitingToHide', '__isViewHidden', '__openBoxesFunc', '__lastStatisticsResetFailed')
    __LB_SAVED_BOX_BTN = {NewYearCategories.NEWYEAR: 0,
     NewYearCategories.CHRISTMAS: 0,
     NewYearCategories.ORIENTAL: 0,
     NewYearCategories.FAIRYTALE: 0,
     NewYearLootBoxes.COMMON: 0}

    def __init__(self, layoutID, lootBoxType=NewYearLootBoxes.PREMIUM, category=''):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.NON_REARRANGE_VIEW
        settings.model = NyLootBoxMainViewModel()
        settings.kwargs = {'initLootBoxType': lootBoxType,
         'initCategory': category}
        super(NyLootBoxMainView, self).__init__(settings)
        self.__isVideoOff = False
        self.__tabsController = LootBoxesEntryViewTabsController()
        self.__availableBoxes = None
        self.__isWaitingToHide = False
        self.__isViewHidden = False
        self.__openBoxesFunc = None
        self.__isDeliveryVideoPlaying = False
        self.__lastViewed = -1
        self.__lastStatisticsResetFailed = False
        return

    @property
    def viewModel(self):
        return super(NyLootBoxMainView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.tooltips.loot_box_category_tooltip.LootBoxCategoryTooltipContent():
            return LootBoxCategoryTooltipContent(event.getArgument('category', ''))
        return NyGuaranteedRewardTooltip() if contentID == R.views.lobby.new_year.tooltips.NyGuaranteedRewardTooltip() else super(NyLootBoxMainView, self).createToolTipContent(event, contentID)

    def createPopOverContent(self, event):
        if event.contentID == R.views.lobby.new_year.popovers.NyLootBoxStatisticsPopover():
            self.__popoverLogger.logClickInBoxes()
            return NyLootBoxStatisticsPopover(self.__tabsController.getSelectedBoxID(), self.__lastStatisticsResetFailed)
        return super(NyLootBoxMainView, self).createPopOverContent(event)

    def externalSelectTab(self, lootBoxType=NewYearLootBoxes.PREMIUM, category=''):
        if self.viewStatus != ViewStatus.LOADED or self.__isDeliveryVideoPlaying:
            return
        tabName = NewYearLootBoxes.COMMON
        if lootBoxType == NewYearLootBoxes.PREMIUM:
            if category in CATEGORIES_GUI_ORDER:
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
        super(NyLootBoxMainView, self)._onLoading(*args, **kwargs)
        self.__subscribeListeners()
        with self.viewModel.transaction() as model:
            self.__isVideoOff = self.settingsCore.getSetting(NewYearStorageKeys.LOOT_BOX_VIDEO_OFF)
            model.setIsVideoOff(self.__isVideoOff)
            self.__availableBoxes = self.itemsCache.items.tokens.getLootBoxesCountByType()
            self.__tabsController.updateAvailableBoxes(self.__availableBoxes)
            self.__tabsController.setInitState(initLootBoxType, initCategory)
            self.__tabsController.updateTabModels(model.sidebar.getItemsTabBar())
            model.sidebar.setStartIndex(self.__tabsController.getSelectedTabIdx())
            boxesButtons = model.boxesCountButtons
            for idx, boxesCount in enumerate(_OPEN_BOXES_COUNTERS):
                labelRes = R.strings.ny.lootBoxMain.entryView.openBoxes.dyn('_'.join(('count', str(boxesCount))))
                boxCountButtonModel = LootBoxCountButtonModel()
                boxCountButtonModel.setIdx(idx)
                boxCountButtonModel.setLabel(labelRes())
                boxCountButtonModel.setIsSelected(_DEFAULT_BTN_IDX == idx)
                boxesButtons.addViewModel(boxCountButtonModel)

            boxesButtons.addSelectedIndex(_DEFAULT_BTN_IDX)
            self.__updateMainContent()
            self.__updateLootBoxViewed()
            self.__updateLootBoxesDeliveryVideo()

    def _initialize(self, *args, **kwargs):
        super(NyLootBoxMainView, self)._initialize()
        g_messengerEvents.onLockPopUpMessages(key=self.__class__.__name__, lockHigh=True, clear=True)
        if self._isMemoryRiskySystem:
            g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.REMOVE_HIDE_VIEW), EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        self.__stopVideo()
        if self.__openBoxesFunc is not None:
            self.__openBoxesFunc = None
        self.__unsubscribeListeners()
        g_messengerEvents.onUnlockPopUpMessages(key=self.__class__.__name__)
        if isPlayerAccount():
            LootBoxNotification.saveSettings()
            self.settingsCore.applyStorages(False)
        super(NyLootBoxMainView, self)._finalize()
        return

    def _getSelectedBoxesCount(self):
        boxNumber = 0
        boxType = self.__tabsController.getSelectedBoxType()
        category = self.__tabsController.getSelectedBoxCategory()
        if boxType in self.__availableBoxes:
            available = self.__availableBoxes[boxType]
            categories = available['categories']
            if boxType == NewYearLootBoxes.PREMIUM:
                boxNumber = categories[category] if category in categories else available['total']
            else:
                boxNumber = available['total']
        return boxNumber

    def _getVideoOff(self):
        return self.__isVideoOff

    def _isSingleOpen(self):
        openCount = _OPEN_BOXES_COUNTERS[self.__getSelectedCountIndx()]
        return openCount == 1

    def _onLoaded(self, *args, **kwargs):
        super(NyLootBoxMainView, self)._onLoaded(*args, **kwargs)
        nextTick(partial(self.__onNyStateUpdated))()

    def __subscribeListeners(self):
        self._app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
        self.viewModel.onWindowClose += self.__onWindowClose
        self.viewModel.onTabClick += self.__onBoxSelectTabClick
        self.viewModel.onCountSelected += self.__onCountSelected
        self.viewModel.onBuyBoxBtnClick += self.__onBuyBox
        self.viewModel.onAnimationSwitchClick += self.__onAnimationSwitch
        self.viewModel.onOpenBoxHitAreaClick += self.__openBoxFromHitArea
        self.viewModel.onOpenBoxBtnClick += self.__onOpenBoxFromButton
        self.viewModel.onCelebrityBtnClick += self.__onCelebrityBtnClick
        self.viewModel.onQuestsBtnClick += self.__onQuestsBtnClick
        self.viewModel.guaranteedReward.onInfoClick += self.__onGuaranteedRewardsInfo
        self.viewModel.onSwitchBoxHover += self.__onSwitchBoxHover
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self.settingsCore.onSettingsChanged += self.__updateVideoOff
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self.__nyController.onStateChanged += self.__onNyStateUpdated
        self.__gui.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged
        g_eventBus.addListener(events.LootboxesEvent.ON_DELIVERY_VIDEO_END, self.__onDeliveryVideoEnd, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.LootboxesEvent.ON_BOX_TRANSITION_END, self.__onBoxTransitionEnd, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.LootboxesEvent.ON_STATISTICS_RESET, self.__onStatisticsReset, scope=EVENT_BUS_SCOPE.LOBBY)
        if not self._isMemoryRiskySystem:
            g_eventBus.addListener(events.LootboxesEvent.ON_REWARD_VIEW_CLOSED, self.__handleRewardViewHide, scope=EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.addListener(events.LootboxesEvent.ON_MULTI_OPEN_VIEW_CLOSED, self.__handleRewardViewHide, scope=EVENT_BUS_SCOPE.LOBBY)

    def __unsubscribeListeners(self):
        self._app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        g_eventBus.removeListener(events.LootboxesEvent.ON_DELIVERY_VIDEO_END, self.__onDeliveryVideoEnd, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.LootboxesEvent.ON_BOX_TRANSITION_END, self.__onBoxTransitionEnd, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.LootboxesEvent.ON_STATISTICS_RESET, self.__onStatisticsReset, scope=EVENT_BUS_SCOPE.LOBBY)
        if not self._isMemoryRiskySystem:
            g_eventBus.removeListener(events.LootboxesEvent.ON_REWARD_VIEW_CLOSED, self.__handleRewardViewHide, scope=EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.removeListener(events.LootboxesEvent.ON_MULTI_OPEN_VIEW_CLOSED, self.__handleRewardViewHide, scope=EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.onWindowClose -= self.__onWindowClose
        self.viewModel.onTabClick -= self.__onBoxSelectTabClick
        self.viewModel.onCountSelected -= self.__onCountSelected
        self.viewModel.onBuyBoxBtnClick -= self.__onBuyBox
        self.viewModel.onAnimationSwitchClick -= self.__onAnimationSwitch
        self.viewModel.onOpenBoxHitAreaClick -= self.__openBoxFromHitArea
        self.viewModel.onOpenBoxBtnClick -= self.__onOpenBoxFromButton
        self.viewModel.onCelebrityBtnClick -= self.__onCelebrityBtnClick
        self.viewModel.onQuestsBtnClick -= self.__onQuestsBtnClick
        self.viewModel.guaranteedReward.onInfoClick -= self.__onGuaranteedRewardsInfo
        self.viewModel.onSwitchBoxHover -= self.__onSwitchBoxHover
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        self.settingsCore.onSettingsChanged -= self.__updateVideoOff
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.__nyController.onStateChanged -= self.__onNyStateUpdated
        self.__gui.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged

    def __onWindowClose(self):
        if self.__isWaitingToHide:
            return
        if not self.__stopVideo():
            g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_MAIN_VIEW_CLOSED), scope=EVENT_BUS_SCOPE.LOBBY)
            self.__flowlogger.logCloseClick(currentObject=NewYearNavigation.getCurrentObject(), currentView=NewYearNavigation.getCurrentViewName())
            self.destroyWindow()

    def __stopVideo(self):
        if self.__isDeliveryVideoPlaying:
            g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.NEED_DELIVERY_VIDEO_STOP), scope=EVENT_BUS_SCOPE.LOBBY)
            self.__isDeliveryVideoPlaying = False
            return True
        return False

    def __onCacheResync(self, *_):
        self.__update()

    def __update(self, isAfterRewardView=False):
        self.__availableBoxes = self.itemsCache.items.tokens.getLootBoxesCountByType()
        if isAfterRewardView:
            self.__isWaitingToHide = False
        if self.__isWaitingToHide:
            return
        with self.viewModel.transaction() as model:
            self.__updateLootBoxViewed(isAfterRewardView)
            self.__updateMainContent()
            self.__updateLootBoxesDeliveryVideo(isAfterRewardView)
            self.__tabsController.updateAvailableBoxes(self.__availableBoxes)
            self.__tabsController.updateTabModels(model.sidebar.getItemsTabBar())

    def __onViewAddedToContainer(self, _, pyEntity):
        if pyEntity.alias == VIEW_ALIAS.BATTLE_QUEUE:
            self.destroyWindow()

    def __onDeliveryVideoEnd(self, event=None):
        self.__isDeliveryVideoPlaying = False
        with self.viewModel.transaction() as model:
            model.setIsViewHidden(False)

    def __onBoxTransitionEnd(self, event=None):
        with self.viewModel.transaction() as model:
            model.setIsBoxChangeAnimation(False)

    def __onStatisticsReset(self, event):
        self.__lastStatisticsResetFailed = event.ctx['serverError']

    def __onBoxSelectTabClick(self, args=None):
        tabName = args['tabName']
        self.__doSelectTab(tabName)

    def __doSelectTab(self, tabName):
        currentTabName = self.__tabsController.getSelectedBoxName()
        prevBoxType = self.__tabsController.getSelectedBoxType()
        prevHasBoxes = self.viewModel.getIsOpenBoxBtnVisible()
        self.__tabsController.selectTab(tabName)
        self.__updateCategoryViewed()
        self.__updateMainContent(currentTabName != tabName, prevBoxType, prevHasBoxes)
        self.__updateLootBoxesDeliveryVideo()
        self.__tabsController.updateTabModels(self.viewModel.sidebar.getItemsTabBar())

    def __updateMainContent(self, isClickTab=False, prevBoxType=None, prevHasBoxes=False):
        with self.viewModel.transaction() as model:
            hasBoxes = False
            boxType = self.__tabsController.getSelectedBoxType()
            boxCategory = self.__tabsController.getSelectedBoxCategory()
            if boxType in self.__availableBoxes:
                available = self.__availableBoxes[boxType]
                if boxType == NewYearLootBoxes.PREMIUM:
                    categories = available['categories']
                    boxNumber = categories[boxCategory] if boxCategory in categories else available['total']
                else:
                    boxNumber = available['total']
                hasBoxes = boxNumber > 0
                if hasBoxes:
                    self.__updateBoxesButtons(boxNumber, boxType == NewYearLootBoxes.PREMIUM)
            setting = self.__LOOT_BOX_CATEGORY_MAPPING.get(boxCategory) if boxCategory is not None else None
            NewYearSoundsManager.setStylesSwitchBox(setting if setting else RANDOM_STYLE_BOX)
            NewYearSoundsManager.setRTPCBoxEntryView(boxType)
            NewYearSoundsManager.setRTPCBoxAvailability(hasBoxes)
            if model.getCurrentName() and model.getCurrentName() != self.__tabsController.getSelectedBoxName():
                playSound(LootBoxViewEvents.LOGISTIC_CENTER_SWITCH)
            model.setSelectedBoxType(boxType)
            model.setCurrentName(self.__tabsController.getSelectedBoxName())
            model.setIsPremiumType(boxType == NewYearLootBoxes.PREMIUM)
            model.setRealm(CURRENT_REALM)
            lootboxItem = getLootBoxByTypeAndCategory(boxType, boxCategory, isInInventory=False)
            isBoxEnabled = lootboxItem is not None and self.lobbyContext.getServerSettings().isLootBoxEnabled(lootboxItem.getID())
            model.setIsOpenBoxBtnVisible(hasBoxes and isBoxEnabled)
            model.setIsBoxesAvailable(isBoxEnabled)
            model.setCurrentCountButton(self.__getSelectedCountIndx())
            nyStorage = self.settingsCore.serverSettings.getNewYearStorage()
            model.setIsStatisticsHintActive(not nyStorage.get(NewYearStorageKeys.NY_STATISTICS_HINT_SHOWN, False) and bool(self.itemsCache.items.tokens.getLootBoxesStats()))
            if isClickTab and (prevBoxType != boxType or hasBoxes or prevHasBoxes and not hasBoxes):
                model.setIsBoxChangeAnimation(True)
            setGaranteedRewardData(model.guaranteedReward, lootboxItem, not self.__isViewHidden, True)
        g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_TAB_SELECTED, ctx={'tabName': self.__tabsController.getSelectedBoxName(),
         'hasBoxes': hasBoxes}), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def __updateBoxesButtons(self, boxNumber, isPremiumBox):
        boxesButtons = self.viewModel.boxesCountButtons
        boxesButtonsItems = boxesButtons.getItems()
        selectedIndex = self.__getSelectedCountIndx()
        for idx, countButton in enumerate(boxesButtonsItems):
            countButton.setIsEnabled(boxNumber >= _OPEN_BOXES_COUNTERS[idx])
            countButton.setIsVisible(not (idx == _ONLY_CB_BTN_IDX and isPremiumBox))

        isNeedSaveIndx = False
        if selectedIndex == _ONLY_CB_BTN_IDX and isPremiumBox:
            selectedIndex -= 1
            isNeedSaveIndx = True
        while selectedIndex > 0 and boxNumber < _OPEN_BOXES_COUNTERS[selectedIndex]:
            selectedIndex -= 1
            isNeedSaveIndx = True

        if isNeedSaveIndx:
            self.__saveSelectedCountBtnIndx(selectedIndex)
        self.__setSelectedCountBtn(selectedIndex)

    def __getSelectedBox(self, isInInventory=True):
        selectedType = self.__tabsController.getSelectedBoxType()
        selectedCategory = self.__tabsController.getSelectedBoxCategory()
        return getLootBoxByTypeAndCategory(selectedType, selectedCategory, isInInventory=isInInventory)

    def __getSelectedCountIndx(self):
        boxType = self.__tabsController.getSelectedBoxType()
        if boxType == NewYearLootBoxes.COMMON:
            return int(self.__LB_SAVED_BOX_BTN.get(boxType, 0))
        boxCategory = self.__tabsController.getSelectedBoxCategory()
        return int(self.__LB_SAVED_BOX_BTN.get(boxCategory, 0))

    def __onCountSelected(self, data):
        indx = data.get('value', 0) if data else 0
        self.__saveSelectedCountBtnIndx(indx)
        self.__setSelectedCountBtn(indx)

    def __saveSelectedCountBtnIndx(self, indx):
        boxType = self.__tabsController.getSelectedBoxType()
        if boxType == NewYearLootBoxes.COMMON:
            self.__LB_SAVED_BOX_BTN[boxType] = indx
            with self.viewModel.transaction() as model:
                model.setCurrentCountButton(self.__getSelectedCountIndx())
            return
        boxCategory = self.__tabsController.getSelectedBoxCategory()
        self.__LB_SAVED_BOX_BTN[boxCategory] = indx
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

    def __onBuyBox(self, _=None):
        self.__flowlogger.logPageButtonsClick()
        event_dispatcher.showLootBoxBuyWindow(self.__tabsController.getSelectedBoxCategory())

    def __updateLootBoxViewed(self, isAfterRewardView=False):
        totalCount = self.itemsCache.items.tokens.getLootBoxesTotalCount()
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
                if box.getType() == NewYearLootBoxes.PREMIUM and openCount > MAX_PREMIUM_BOXES_TO_OPEN:
                    openCount = MAX_PREMIUM_BOXES_TO_OPEN
            invCount = box.getInventoryCount()
            self.__requestLootBoxOpen(box, min(invCount, openCount))
            return

    @process
    def __requestLootBoxOpen(self, boxItem, count):
        self.__isWaitingToHide = True
        self.viewModel.setIsBoxOpenEnabled(False)
        isPremiumMulti = boxItem.getType() == NewYearLootBoxes.PREMIUM and count > 1
        openCount = 1 if isPremiumMulti else count
        result = yield LootBoxOpenProcessor(boxItem, openCount).request()
        if result:
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if result.success:
                rewardsList = result.auxData.get('bonus')
                if not rewardsList:
                    _logger.error('Lootbox is opened, but no rewards has been received.')
                    self.viewModel.setIsBoxOpenEnabled(True)
                    self.__isViewHidden = False
                    self.__isWaitingToHide = False
                    return
                guaranteedReward = 'usedLimits' in result.auxData['extData']
                giftInfo = result.auxData['giftsInfo']
                parentWindow = None if self._isMemoryRiskySystem else self.getParentWindow()
                if isPremiumMulti:
                    openBoxesFunc = partial(showLootBoxPremiumMultiOpen, boxItem, rewardsList, count, parentWindow, guaranteedReward=guaranteedReward)
                elif count == 1:
                    openBoxesFunc = partial(showLootBoxReward, boxItem, rewardsList[0], parentWindow, False, lastStatisticsResetFailed=self.__lastStatisticsResetFailed, guaranteedReward=guaranteedReward, giftsInfo=giftInfo)
                else:
                    openBoxesFunc = partial(showLootBoxMultiOpen, boxItem, rewardsList, count, parentWindow)
                if self._isMemoryRiskySystem:
                    self.__openBoxesFunc = openBoxesFunc
                    self._startFade(self.__openBoxesCallback, withPause=True)
                    self.__isWaitingToHide = False
                    self.__isViewHidden = True
                else:
                    openBoxesFunc()
            else:
                self.viewModel.setIsBoxOpenEnabled(True)
                self.__isWaitingToHide = False
                self.__isViewHidden = False
        return

    def __openBoxesCallback(self):
        if self.__openBoxesFunc is not None:
            self.__openBoxesFunc()
            self.__openBoxesFunc = None
        self.destroyWindow()
        return

    def __onServerSettingChanged(self, diff):
        if 'lootBoxes_config' in diff:
            self.__update()
        if not self.lobbyContext.getServerSettings().isLootBoxesEnabled():
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
        else:
            LootBoxNotification.setCategoryNewCount(NewYearLootBoxes.COMMON)
        return

    def __updateLootBoxesDeliveryVideo(self, isAfterRewardView=False):
        if self.__isDeliveryVideoPlaying:
            return
        else:
            boxCategory = self.__tabsController.getSelectedBoxCategory()
            if boxCategory is not None and LootBoxNotification.hasDeliveredBox(boxCategory):
                if not isAfterRewardView:
                    self.__isDeliveryVideoPlaying = True
                    g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.NEED_DELIVERY_VIDEO_START), scope=EVENT_BUS_SCOPE.LOBBY)
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
        g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.NEED_DELIVERY_VIDEO_STOP), scope=EVENT_BUS_SCOPE.LOBBY)
        self.settingsCore.applySetting(NewYearStorageKeys.LOOT_BOX_VIDEO_OFF, not self.__isVideoOff)

    def __handleRewardViewHide(self, _):
        self.viewModel.setIsBoxOpenEnabled(True)
        self.__isViewHidden = False
        self.__update(True)

    def __onCelebrityBtnClick(self):
        self.__flowlogger.logCelebrityClick()
        NewYearNavigation.switchByAnchorName(AnchorNames.CELEBRITY)
        self.__onWindowClose()

    def __onQuestsBtnClick(self):
        self.__flowlogger.logPageButtonsClick()
        showDailyQuests(subTab=DailyTabs.QUESTS)
        self.__onWindowClose()

    def __onSwitchBoxHover(self, event):
        isBoxHovered = event.get('value', False)
        self.__sendSwitchBoxHoveredEvent(isBoxHovered)

    def __sendSwitchBoxHoveredEvent(self, isBoxHovered):
        g_eventBus.handleEvent(events.LootboxesEvent(eventType=events.LootboxesEvent.SWITCH_BOX_HOVER, ctx={'isBoxHovered': isBoxHovered}), scope=EVENT_BUS_SCOPE.LOBBY)

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

    @staticmethod
    def __onGuaranteedRewardsInfo(_=None):
        event_dispatcher.showLootBoxGuaranteedRewardsInfo()


class NyLootBoxMainViewWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, lootboxType, category, parent=None):
        super(NyLootBoxMainViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=NyLootBoxMainView(R.views.lobby.new_year.views.NyLootBoxMainView(), lootboxType, category), parent=parent, layer=WindowLayer.WINDOW)
