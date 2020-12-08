# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_entry_view.py
import logging
from collections import namedtuple
from functools import partial
import Windowing
from account_helpers.settings_core import settings_constants
from adisp import process
from frameworks.wulf import ViewFlags, WindowFlags, WindowLayer
from frameworks.wulf import ViewSettings
from gui import SystemMessages
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.app_loader import sf_lobby
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.lootboxes.components.loot_box_count_button_model import LootBoxCountButtonModel
from gui.impl.gen.view_models.views.lobby.lootboxes.loot_box_entry_view_model import LootBoxEntryViewModel
from gui.impl.lobby.loot_box.loot_box_helper import showLootBoxReward, showLootBoxPremiumMultiOpen, worldDrawEnabled, MAX_PREMIUM_BOXES_TO_OPEN, showLootBoxMultiOpen, getLootBoxByTypeAndCategory, LootBoxHideableView
from gui.impl.lobby.loot_box.loot_box_notification import LootBoxNotification
from gui.impl.lobby.missions.daily_quests_view import DailyTabs
from gui.impl.lobby.tooltips.loot_box_category_tooltip import LootBoxCategoryTooltipContent
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundsManager, RANDOM_STYLE_BOX
from gui.impl.lobby.loot_box.loot_box_sounds import LootBoxVideoStartStopHandler, LootBoxVideos
from gui.impl.lobby.loot_box.loot_box_sounds import LootBoxViewEvents, playSound
from gui.impl.new_year.views.tabs_controller import LootBoxesEntryViewTabsController
from gui.impl.pub.lobby_window import LobbyWindow
from gui.server_events.events_dispatcher import showDailyQuests
from gui.shared.gui_items.loot_box import NewYearCategories
from items.components.ny_constants import ToySettings
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared import event_dispatcher
from gui.shared import events
from gui.shared.gui_items.loot_box import NewYearLootBoxes
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from helpers import dependency, isPlayerAccount, uniprof
from new_year.ny_constants import AnchorNames
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IFestivityController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.decorators import loggerTarget, loggerEntry, simpleLog, logOnMatch, logProperty
from uilogging.ny.constants import NY_LOG_KEYS, NY_LOG_ACTIONS
from uilogging.ny.loggers import NYLogger
_logger = logging.getLogger(__name__)
_ContentState = namedtuple('_ContentState', ('isOpenBoxBtnVisible',
 'isBackBtnVisible',
 'isBuyBoxBtnVisible',
 'isGiftBuyBtnVisible'))
_MAIN_CONTENT_STATES = {(NewYearLootBoxes.PREMIUM, True): _ContentState(True, False, False, True),
 (NewYearLootBoxes.PREMIUM, False): _ContentState(False, True, True, False),
 (NewYearLootBoxes.COMMON, True): _ContentState(True, False, False, False),
 (NewYearLootBoxes.COMMON, False): _ContentState(False, True, False, False)}
_VIDEO_BUFFER_TIME = 1
_OPEN_BOXES_COUNTERS = (1, 5, 10)
_DEFAULT_BTN_IDX = 0
_ONLY_CB_BTN_IDX = 2

def _getBoxName(boxType, selectedBoxCategory):
    return boxType if boxType == NewYearLootBoxes.COMMON else selectedBoxCategory


@loggerTarget(logKey=NY_LOG_KEYS.NY_LOOT_BOX_VIEW, loggerCls=NYLogger)
class LootBoxEntryView(LootBoxHideableView):
    itemsCache = dependency.descriptor(IItemsCache)
    settingsCore = dependency.descriptor(ISettingsCore)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _festivityController = dependency.descriptor(IFestivityController)
    __LOOT_BOX_CATEGORY_MAPPING = {NewYearCategories.NEWYEAR: ToySettings.NEW_YEAR,
     NewYearCategories.CHRISTMAS: ToySettings.CHRISTMAS,
     NewYearCategories.ORIENTAL: ToySettings.ORIENTAL,
     NewYearCategories.FAIRYTALE: ToySettings.FAIRYTALE}
    __LB_SAVED_BOX_BTN = {NewYearCategories.NEWYEAR: 0,
     NewYearCategories.CHRISTMAS: 0,
     NewYearCategories.ORIENTAL: 0,
     NewYearCategories.FAIRYTALE: 0,
     NewYearLootBoxes.COMMON: 0}

    def __init__(self, layoutID, lootBoxType=NewYearLootBoxes.PREMIUM, category=''):
        settings = ViewSettings(layoutID, flags=ViewFlags.VIEW, model=LootBoxEntryViewModel())
        settings.kwargs = {'initLootBoxType': lootBoxType,
         'initCategory': category}
        super(LootBoxEntryView, self).__init__(settings)
        self.__isVideoOff = False
        self.__lastViewed = -1
        self.__availableBoxes = None
        self.__isViewHidden = False
        self.__isWaitingToHide = False
        self.__videoStartStopHandler = LootBoxVideoStartStopHandler()
        self.__tabsController = LootBoxesEntryViewTabsController()
        self.__openBoxesFunc = None
        return

    @property
    def viewModel(self):
        return super(LootBoxEntryView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return LootBoxCategoryTooltipContent(event.getArgument('category', '')) if contentID == R.views.lobby.tooltips.loot_box_category_tooltip.LootBoxCategoryTooltipContent() else super(LootBoxEntryView, self).createToolTipContent(event, contentID)

    @loggerEntry
    @uniprof.regionDecorator(label='ny.lootbox.entry', scope='enter')
    def _initialize(self, initLootBoxType, initCategory):
        super(LootBoxEntryView, self)._initialize()
        self.viewModel.onOpenBoxHitAreaClick += self.__openBoxFromHitArea
        self.viewModel.onOpenBoxBtnClick += self.__onOpenBoxFromButton
        self.viewModel.onBuyBoxBtnClick += self.__onBuyBox
        self.viewModel.onVideoChangeClick += self.__onVideoChange
        self.viewModel.onWindowClose += self.__onWindowClose
        self.viewModel.onBoxSelected += self.__onBoxSelected
        self.viewModel.onVideoStarted += self.__onVideoStarted
        self.viewModel.onVideoStopped += self.__onVideoStopped
        self.viewModel.onVideoInterrupted += self.__onVideoInterrupted
        self.viewModel.onFadeOutStarted += self.__onFadeOutStarted
        self.viewModel.onFadeInCompleted += self.__onFadeInCompleted
        self.viewModel.onGuaranteedRewardsInfo += self.__onGuaranteedRewardsInfo
        self.viewModel.onCelebrityBtnClick += self.__onCelebrityBtnClick
        self.viewModel.onQuestsBtnClick += self.__onQuestsBtnClick
        self.viewModel.onCountSelected += self.__onCountSelected
        self.viewModel.onDragNDropEnded += self.__onDragNDropEnded
        self.viewModel.onLoadError += self.__onLoadError
        self._festivityController.onStateChanged += self.__onStateChange
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self.settingsCore.onSettingsChanged += self.__updateVideoOff
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self._app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
        Windowing.addWindowAccessibilitynHandler(self.__onWindowAccessibilityChanged)
        with self.viewModel.transaction() as model:
            self.__isVideoOff = self.settingsCore.getSetting(settings_constants.GAME.LOOT_BOX_VIDEO_OFF)
            model.setStreamBufferLength(_VIDEO_BUFFER_TIME)
            model.setIsVideoOff(self.__isVideoOff)
            self.__availableBoxes = self.itemsCache.items.tokens.getLootBoxesCountByType()
            self.__tabsController.updateAvailableBoxes(self.__availableBoxes)
            self.__tabsController.setInitState(initLootBoxType, initCategory)
            self.__tabsController.updateTabModels(model.getBoxTabs())
            model.setCurrentIndex(self.__tabsController.getSelectedTabIdx())
            model.setIsClientFocused(Windowing.isWindowAccessible())
            boxesButtons = model.boxesCountButtons
            for idx, boxesCount in enumerate(_OPEN_BOXES_COUNTERS):
                labelRes = R.strings.lootboxes.entryView.openBoxes.dyn('_'.join(('count', str(boxesCount))))
                boxCountButtonModel = LootBoxCountButtonModel()
                boxCountButtonModel.setIdx(idx)
                boxCountButtonModel.setLabel(labelRes())
                boxCountButtonModel.setIsSelected(_DEFAULT_BTN_IDX == idx)
                boxesButtons.addViewModel(boxCountButtonModel)

            boxesButtons.addSelectedIndex(_DEFAULT_BTN_IDX)
            self.__updateMainContent()
            self.__updateLootBoxViewed()
            self.__updateLootBoxesDeliveryVideo()
        g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_ENTRY_VIEW_LOADED), scope=EVENT_BUS_SCOPE.LOBBY)
        if not self._isMemoryRiskySystem:
            g_eventBus.addListener(events.LootboxesEvent.ON_REWARD_VIEW_CLOSED, self.__handleRewardViewHide, scope=EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.addListener(events.LootboxesEvent.ON_MULTI_OPEN_VIEW_CLOSED, self.__handleRewardViewHide, scope=EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.addListener(events.LootboxesEvent.NEED_SHOW_REWARDS, self.__needShowRewards, scope=EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.addListener(events.LootboxesEvent.NEED_STOP_ENTRY_VIDEO, self.__needStopEntryVideo, scope=EVENT_BUS_SCOPE.LOBBY)
        playSound(LootBoxViewEvents.ENTRY_VIEW_ENTER)

    @uniprof.regionDecorator(label='ny.lootbox.entry', scope='exit')
    def _finalize(self):
        playSound(LootBoxViewEvents.ENTRY_VIEW_EXIT)
        worldDrawEnabled(True)
        if self.__openBoxesFunc is not None:
            self.__openBoxesFunc = None
        if not self._isMemoryRiskySystem:
            g_eventBus.removeListener(events.LootboxesEvent.NEED_STOP_ENTRY_VIDEO, self.__needStopEntryVideo, scope=EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.removeListener(events.LootboxesEvent.NEED_SHOW_REWARDS, self.__needShowRewards, scope=EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.removeListener(events.LootboxesEvent.ON_REWARD_VIEW_CLOSED, self.__handleRewardViewHide, scope=EVENT_BUS_SCOPE.LOBBY)
            g_eventBus.removeListener(events.LootboxesEvent.ON_MULTI_OPEN_VIEW_CLOSED, self.__handleRewardViewHide, scope=EVENT_BUS_SCOPE.LOBBY)
        self.viewModel.onOpenBoxHitAreaClick -= self.__openBoxFromHitArea
        self.viewModel.onOpenBoxBtnClick -= self.__onOpenBoxFromButton
        self.viewModel.onBuyBoxBtnClick -= self.__onBuyBox
        self.viewModel.onVideoChangeClick -= self.__onVideoChange
        self.viewModel.onWindowClose -= self.__onWindowClose
        self.viewModel.onBoxSelected -= self.__onBoxSelected
        self.viewModel.onVideoStarted -= self.__onVideoStarted
        self.viewModel.onVideoStopped -= self.__onVideoStopped
        self.viewModel.onVideoInterrupted -= self.__onVideoInterrupted
        self.viewModel.onFadeOutStarted -= self.__onFadeOutStarted
        self.viewModel.onFadeInCompleted -= self.__onFadeInCompleted
        self.viewModel.onGuaranteedRewardsInfo -= self.__onGuaranteedRewardsInfo
        self.viewModel.onCelebrityBtnClick -= self.__onCelebrityBtnClick
        self.viewModel.onQuestsBtnClick -= self.__onQuestsBtnClick
        self.viewModel.onCountSelected -= self.__onCountSelected
        self.viewModel.onDragNDropEnded -= self.__onDragNDropEnded
        self.viewModel.onLoadError -= self.__onLoadError
        self._festivityController.onStateChanged -= self.__onStateChange
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        self.settingsCore.onSettingsChanged -= self.__updateVideoOff
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self._app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        Windowing.removeWindowAccessibilityHandler(self.__onWindowAccessibilityChanged)
        if isPlayerAccount():
            LootBoxNotification.saveSettings()
            self.settingsCore.applyStorages(False)
        self.__videoStartStopHandler.onVideoDone()
        self.__videoStartStopHandler = None
        super(LootBoxEntryView, self)._finalize()
        return

    @sf_lobby
    def _app(self):
        return None

    def _getVideoOff(self):
        return self.__isVideoOff

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

    def _isSingleOpen(self):
        openCount = _OPEN_BOXES_COUNTERS[self.__getSelectedCountIndx()]
        return openCount == 1

    def _getVideosList(self):
        return ['lootboxes/lootbox_delivery.usm',
         'lootboxes/lootbox_entry.usm',
         'lootboxes/idles/Christmas.usm',
         'lootboxes/idles/Fairytale.usm',
         'lootboxes/idles/newYear_usual.usm',
         'lootboxes/idles/NewYear.usm',
         'lootboxes/idles/Oriental.usm',
         'lootboxes/idles/usual_empty.usm',
         'lootboxes/idles/premium_empty.usm'] if self._isMemoryRiskySystem else ['lootboxes/lootbox_delivery.usm',
         'lootboxes/lootbox_entry.usm',
         'lootboxes/idles/Christmas.usm',
         'lootboxes/idles/Fairytale.usm',
         'lootboxes/idles/newYear_usual.usm',
         'lootboxes/idles/NewYear.usm',
         'lootboxes/idles/Oriental.usm',
         'lootboxes/idles/usual_empty.usm',
         'lootboxes/idles/premium_empty.usm',
         'lootboxes/opening/Christmas.usm',
         'lootboxes/opening/Fairytale.usm',
         'lootboxes/opening/free.usm',
         'lootboxes/opening/NewYear.usm',
         'lootboxes/opening/Oriental.usm',
         'lootboxes/opening/idles/Christmas.usm',
         'lootboxes/opening/idles/Fairytale.usm',
         'lootboxes/opening/idles/free.usm',
         'lootboxes/opening/idles/NewYear.usm',
         'lootboxes/opening/idles/Oriental.usm',
         'StyleLootBoxCongrats/A83_T110E4.usm',
         'StyleLootBoxCongrats/Ch41_WZ_111_5A.usm',
         'StyleLootBoxCongrats/F88_AMX_13_105.usm',
         'StyleLootBoxCongrats/G42_Maus.usm',
         'StyleLootBoxCongrats/G56_E-100.usm',
         'StyleLootBoxCongrats/G72_JagdPz_E100.usm',
         'StyleLootBoxCongrats/GB31_Conqueror_Gun.usm',
         'StyleLootBoxCongrats/J16_ST_B1.usm',
         'StyleLootBoxCongrats/Pl15_60TP_Lewandowskiego.usm',
         'StyleLootBoxCongrats/R97_Object_140.usm',
         'StyleLootBoxCongrats/R148_Object_430_U.usm',
         'VehicleLootBoxCongrats/F116_Bat_Chatillon_Bourrasque.usm',
         'VehicleLootBoxCongrats/It18_Progetto_C45_mod_71.usm',
         'VehicleLootBoxCongrats/R177_ISU_152K_BL10.usm',
         'VehicleLootBoxCongrats/GB109_GSOR_1008.usm']

    def __onBoxSelected(self, args=None):
        tabName = args['tabName']
        self.__tabsController.selectTab(tabName)
        self.__updateCategoryViewed()
        self.__updateMainContent()
        self.__updateLootBoxesDeliveryVideo()
        self.__tabsController.updateTabModels(self.viewModel.getBoxTabs())

    def __onCacheResync(self, *_):
        self.__update()

    def __update(self, isAfterRewardView=False):
        self.__availableBoxes = self.itemsCache.items.tokens.getLootBoxesCountByType()
        if isAfterRewardView:
            self.__isWaitingToHide = False
        if self.__isWaitingToHide:
            return
        if self.__isViewHidden:
            self.__updateEmptySwitch()
            return
        with self.viewModel.transaction():
            self.__updateLootBoxViewed(isAfterRewardView)
            self.__updateMainContent()
            self.__updateLootBoxesDeliveryVideo(isAfterRewardView)
            self.__tabsController.updateAvailableBoxes(self.__availableBoxes)
            self.__tabsController.updateTabModels(self.viewModel.getBoxTabs())

    def __updateLootBoxesDeliveryVideo(self, isAfterRewardView=False):
        if self.viewModel.getIsVideoPlaying():
            return
        else:
            boxCategory = self.__tabsController.getSelectedBoxCategory()
            if boxCategory is not None and LootBoxNotification.hasDeliveredBox(boxCategory):
                if not isAfterRewardView:
                    self.viewModel.setIsVideoPlaying(True)
                    self.__updateLootBoxesDeliveryVideoViewed()
                return
            self.viewModel.setIsNeedSetFocus(True)
            return

    def __updateVideoOff(self, diff):
        if settings_constants.GAME.LOOT_BOX_VIDEO_OFF in diff:
            self.__isVideoOff = diff[settings_constants.GAME.LOOT_BOX_VIDEO_OFF]
            self.viewModel.setIsVideoOff(self.__isVideoOff)

    def __updateLootBoxViewed(self, isAfterRewardView=False):
        totalCount = self.itemsCache.items.tokens.getLootBoxesTotalCount()
        if self.__lastViewed != -1 and self.__lastViewed == totalCount:
            return
        LootBoxNotification.setTotalLootBoxesCount(totalCount)
        self.__lastViewed = totalCount
        self.__updateCategoryViewed(isAfterRewardView)

    def __updateCategoryViewed(self, isAfterRewardView=False):
        selectedCategory = self.__tabsController.getSelectedBoxCategory()
        if selectedCategory is not None:
            LootBoxNotification.setCategoryNewCount(NewYearLootBoxes.PREMIUM, selectedCategory)
            if isAfterRewardView:
                LootBoxNotification.setCategoryDeliveredCount(selectedCategory)
        else:
            LootBoxNotification.setCategoryNewCount(NewYearLootBoxes.COMMON)
        return

    def __updateLootBoxesDeliveryVideoViewed(self):
        for category in NewYearCategories.ALL():
            LootBoxNotification.setCategoryDeliveredCount(category)

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

    def __updateMainContent(self):
        with self.viewModel.transaction() as model:
            hasBoxes = False
            boxNumber = 0
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
            if model.getSelectedBoxName() and model.getSelectedBoxName() != self.__tabsController.getSelectedBoxName():
                playSound(LootBoxViewEvents.LOGISTIC_CENTER_SWITCH)
            model.setSelectedBoxType(boxType)
            model.setSelectedBoxName(self.__tabsController.getSelectedBoxName())
            contentState = _MAIN_CONTENT_STATES[boxType, hasBoxes]
            isBoxEnabled = self.lobbyContext.getServerSettings().isLootBoxEnabled(self.__getSelectedBox(isInInventory=False).getID())
            model.setIsOpenBoxBtnVisible(contentState.isOpenBoxBtnVisible and isBoxEnabled)
            model.setIsBackBtnVisible(contentState.isBackBtnVisible and isBoxEnabled)
            model.setIsBuyBoxBtnVisible(contentState.isBuyBoxBtnVisible and isBoxEnabled)
            model.setIsGiftBuyBtnVisible(contentState.isGiftBuyBtnVisible and isBoxEnabled)
            model.setOpenBoxesCounter(min(MAX_PREMIUM_BOXES_TO_OPEN, boxNumber))
            model.setIsBoxesUnavailable(not isBoxEnabled)
            self.__updateGuaranteedFrequency(model, boxType, boxCategory)
        return

    def __getSelectedCountIndx(self):
        boxType = self.__tabsController.getSelectedBoxType()
        if boxType == NewYearLootBoxes.COMMON:
            return int(self.__LB_SAVED_BOX_BTN.get(boxType, 0))
        boxCategory = self.__tabsController.getSelectedBoxCategory()
        return int(self.__LB_SAVED_BOX_BTN.get(boxCategory, 0))

    @simpleLog(argsIndex=0, resetTime=False, preProcessAction=lambda arg: NY_LOG_ACTIONS.NY_LOOT_BOX_OPEN_COUNT_CHANGED.format(_OPEN_BOXES_COUNTERS[int(arg.get('value', 0))]))
    @logProperty(resetTime=False, objProperty='_getSelectedBoxesCount', needCall=True, postProcessAction=NY_LOG_ACTIONS.NY_LOOT_BOX_COUNT.format)
    def __onCountSelected(self, data):
        indx = data.get('value', 0) if data else 0
        self.__saveSelectedCountBtnIndx(indx)
        self.__setSelectedCountBtn(indx)

    def __saveSelectedCountBtnIndx(self, indx):
        boxType = self.__tabsController.getSelectedBoxType()
        if boxType == NewYearLootBoxes.COMMON:
            self.__LB_SAVED_BOX_BTN[boxType] = indx
            return
        boxCategory = self.__tabsController.getSelectedBoxCategory()
        self.__LB_SAVED_BOX_BTN[boxCategory] = indx

    def __setSelectedCountBtn(self, indx):
        boxesButtons = self.viewModel.boxesCountButtons
        boxesButtonsItems = boxesButtons.getItems()
        for idx, countButton in enumerate(boxesButtonsItems):
            countButton.setIsSelected(idx == indx)

        boxesButtons = self.viewModel.boxesCountButtons
        selectedIndices = boxesButtons.getSelectedIndices()
        selectedIndices.clear()
        boxesButtons.addSelectedIndex(indx)

    @simpleLog(action=NY_LOG_ACTIONS.NY_LOOT_BOX_HIT_OPEN)
    def __openBoxFromHitArea(self, _=None):
        self.__onOpenBox(isSingleOpening=True)

    @logOnMatch(objProperty='_isSingleOpen', needCall=True, matches={True: NY_LOG_ACTIONS.NY_LOOT_BOX_CLICK_OPEN,
     False: NY_LOG_ACTIONS.NY_LOOT_BOX_CLICK_MULTI_OPEN})
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

    def __getSelectedBox(self, isInInventory=True):
        selectedType = self.__tabsController.getSelectedBoxType()
        selectedCategory = self.__tabsController.getSelectedBoxCategory()
        return getLootBoxByTypeAndCategory(selectedType, selectedCategory, isInInventory=isInInventory)

    @simpleLog(action=NY_LOG_ACTIONS.NY_LOOT_BOX_VIEW_BUY_CLICK)
    def __onBuyBox(self, _=None):
        event_dispatcher.showLootBoxBuyWindow(self.__tabsController.getSelectedBoxCategory())

    @staticmethod
    def __onGuaranteedRewardsInfo(_=None):
        event_dispatcher.showLootBoxGuaranteedRewardsInfo()

    def __onWindowClose(self, _=None):
        if self._isMemoryRiskySystem and not self._isCanClose:
            return
        self.destroyWindow()

    def __onVideoStarted(self, _=None):
        self.__videoStartStopHandler.onVideoStart(LootBoxVideos.DELIVERY)

    def __onVideoStopped(self, _=None):
        self.__stopVideoPlaying()

    @logOnMatch(objProperty='_getVideoOff', needCall=True, resetTime=False, matches={False: NY_LOG_ACTIONS.NY_LOOT_BOX_ANIM_OFF,
     True: NY_LOG_ACTIONS.NY_LOOT_BOX_ANIM_ON})
    def __onVideoChange(self, _=None):
        self.__stopVideoPlaying()
        self.settingsCore.applySetting(settings_constants.GAME.LOOT_BOX_VIDEO_OFF, not self.__isVideoOff)

    def __stopVideoPlaying(self):
        self.__videoStartStopHandler.onVideoDone()
        self.viewModel.setIsVideoPlaying(False)
        self.viewModel.setIsNeedSetFocus(True)

    @logProperty(resetTime=False, objProperty='_getSelectedBoxesCount', needCall=True, postProcessAction=NY_LOG_ACTIONS.NY_LOOT_BOX_COUNT.format)
    @process
    def __requestLootBoxOpen(self, boxItem, count):
        isPremiumMulti = boxItem.getType() == NewYearLootBoxes.PREMIUM and count > 1
        openCount = 1 if isPremiumMulti else count
        result = yield LootBoxOpenProcessor(boxItem, openCount).request()
        if result:
            self.viewModel.setIsViewAccessible(False)
            self.__isWaitingToHide = True
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if result.success:
                rewardsList = result.auxData
                if not rewardsList:
                    _logger.error('Lootbox is opened, but no rewards has been received.')
                    self.viewModel.setIsViewAccessible(True)
                    self.__isViewHidden = False
                    self.__isWaitingToHide = False
                    return
                parentWindow = None if self._isMemoryRiskySystem else self.getParentWindow()
                if isPremiumMulti:
                    if self._isMemoryRiskySystem:
                        self.__openBoxesFunc = partial(showLootBoxPremiumMultiOpen, boxItem, rewardsList, count, parentWindow)
                    else:
                        showLootBoxPremiumMultiOpen(boxItem, rewardsList, count, parentWindow)
                elif count == 1:
                    if self._isMemoryRiskySystem:
                        self.__openBoxesFunc = partial(showLootBoxReward, boxItem, rewardsList[0], parentWindow, False)
                    else:
                        showLootBoxReward(lootBoxItem=boxItem, rewards=rewardsList[0], parent=parentWindow, isBackward=False)
                elif self._isMemoryRiskySystem:
                    self.__openBoxesFunc = partial(showLootBoxMultiOpen, boxItem, rewardsList, count, parentWindow)
                else:
                    showLootBoxMultiOpen(boxItem, rewardsList, count, parentWindow)
                    self.__isWaitingToHide = False
                    self.__isViewHidden = True
                if self._isMemoryRiskySystem:
                    self._startFade(self.__openBoxesCallback, withPause=True)
            else:
                self.__markAsCanBeClosed()
                self.viewModel.setIsViewAccessible(True)
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

    def __onViewAddedToContainer(self, _, pyEntity):
        if pyEntity.alias == VIEW_ALIAS.BATTLE_QUEUE:
            self.destroyWindow()

    def __onStateChange(self):
        if not self._festivityController.isEnabled():
            self.destroyWindow()

    def __updateEmptySwitch(self):
        hasBoxesBefore = self.viewModel.getIsOpenBoxBtnVisible()
        if not hasBoxesBefore:
            return
        boxCount = 0
        boxType = self.__tabsController.getSelectedBoxType()
        boxCategory = self.__tabsController.getSelectedBoxCategory()
        if boxType in self.__availableBoxes:
            available = self.__availableBoxes[boxType]
            if boxType == NewYearLootBoxes.PREMIUM:
                categories = available['categories']
                if boxCategory in categories:
                    boxCount = categories[boxCategory]
            else:
                boxCount = available['total']
        if not boxCount:
            self.viewModel.setIsEmptySwitch(not self.viewModel.getIsEmptySwitch())

    def __onFadeOutStarted(self, *_):
        worldDrawEnabled(True)

    def __onFadeInCompleted(self, *_):
        worldDrawEnabled(False)
        self.__markAsCanBeClosed()

    def __markAsCanBeClosed(self):
        if not self._isMemoryRiskySystem:
            return
        g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.REMOVE_HIDE_VIEW), EVENT_BUS_SCOPE.LOBBY)
        self._isCanClose = True

    def __updateGuaranteedFrequency(self, model, boxType, boxCategory):
        box = getLootBoxByTypeAndCategory(boxType, boxCategory, isInInventory=False)
        if box is None:
            return
        else:
            model.setGuaranteedFrequency(box.getGuaranteedFrequency())
            model.setAttemptsToGuaranteed(self.itemsCache.items.tokens.getAttemptsAfterGuaranteedRewards(box))
            return

    def __onWindowAccessibilityChanged(self, isWindowAccessible):
        self.__videoStartStopHandler.setIsNeedPause(not isWindowAccessible)
        if not self.__isViewHidden:
            self.viewModel.setIsClientFocused(isWindowAccessible)

    def __handleRewardViewHide(self, _):
        with self.viewModel.transaction() as model:
            model.setIsClientFocused(True)
            model.setIsViewAccessible(True)
        self.__isViewHidden = False
        self.__update(True)

    @simpleLog(action=NY_LOG_ACTIONS.NY_LOOT_BOX_DRAG_N_DROP)
    def __onDragNDropEnded(self):
        pass

    @simpleLog(action=NY_LOG_ACTIONS.NY_LOOT_BOX_DELIVERY_INTERRUPTED)
    def __onVideoInterrupted(self):
        pass

    def __onCelebrityBtnClick(self):
        NewYearNavigation.switchByAnchorName(AnchorNames.CELEBRITY)
        self.__onWindowClose()

    def __onQuestsBtnClick(self):
        showDailyQuests(subTab=DailyTabs.QUESTS)
        self.__onWindowClose()

    def __needShowRewards(self, _=None):
        self.__disableVideoPlayback()

    def __needStopEntryVideo(self, _=None):
        self.__disableVideoPlayback()

    def __disableVideoPlayback(self):
        self.__isWaitingToHide = False
        self.__isViewHidden = True
        self.viewModel.setIsClientFocused(False)
        self.__updateEmptySwitch()

    def __onLoadError(self):
        g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_VIDEO_LOAD_ERROR), EVENT_BUS_SCOPE.LOBBY)


class LootBoxEntryWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, lootBoxType, category):
        super(LootBoxEntryWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=LootBoxEntryView(R.views.lobby.loot_box.views.loot_box_entry_view.LootBoxEntryView(), lootBoxType=lootBoxType, category=category), layer=WindowLayer.OVERLAY)
