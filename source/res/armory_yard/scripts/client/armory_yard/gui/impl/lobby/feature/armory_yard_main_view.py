# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_main_view.py
import logging
from account_helpers import AccountSettings
from account_helpers.AccountSettings import ArmoryYard
from armory_yard.gui.impl.lobby.feature.tooltips.reroll_button_tooltip import RerollButtonTooltip
from armory_yard.gui.impl.lobby.feature.tooltips.reroll_info_container_tooltip import RerollInfoContainerTooltip
from armory_yard.gui.window_events import showArmoryYardBuyWindow, showArmoryYardBundlesWindow, showArmoryYardPurchaseStageBuyWindow, showArmoryYardQuestRerollWindow, showYardQuestRerollWindowByTokenQuestID
from armory_yard.managers.sound_manager import setSoundDroneMode
from gui.impl.gui_decorators import args2params
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.events import ArmoryYardEvent
from helpers import dependency
from shared_utils import first
from gui.impl.gen import R
from frameworks.wulf import WindowLayer
from gui.shared.event_dispatcher import showHangar
from armory_yard.gui.window_events import showArmoryYardShopWindow, showArmoryYardShopBuyWindow
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewFlags, ViewSettings
from skeletons.gui.game_control import IArmoryYardController, IArmoryYardShopController, IAwardController
from skeletons.gui.impl import IGuiLoader
from armory_yard.managers.stage_manager import StageManager
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_main_view_model import ArmoryYardMainViewModel, TabId
from armory_yard.gui.impl.lobby.feature.armory_yard_quests_presenter import _QuestsTabPresenter
from armory_yard.gui.impl.lobby.feature.armory_yard_progress_presenter import _ProgressionTabPresenter
from armory_yard.skeletons.armory_yard_reroll_controller import IArmoryYardRerollController
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.framework.entities.View import ViewKeyDynamic
from armory_yard.gui.Scaleform.daapi.view.lobby.hangar.sound_constants import ARMORY_YARD_SOUND_SPACE
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from armory_yard.gui.impl.lobby.feature.tooltips.armory_yard_currency_tooltip_view import ArmoryYardCurrencyTooltipView
from armory_yard.gui.impl.lobby.feature.tooltips.armory_yard_simple_tooltip_view import ArmoryYardSimpleTooltipView
from armory_yard.gui.impl.lobby.feature.tooltips.task_condition_tooltip_view import TaskConditionTooltipView
_logger = logging.getLogger(__name__)
_LOOTBOX_RES = R.views.dyn('gui_lootboxes').dyn('lobby').dyn('gui_lootboxes').dyn('tooltips').dyn('LootboxTooltip')

class ArmoryYardMainView(ViewImpl, IGlobalListener):
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
    __armoryShopCtrl = dependency.descriptor(IArmoryYardShopController)
    __armoryYardRerollCtrl = dependency.descriptor(IArmoryYardRerollController)
    __gui = dependency.descriptor(IGuiLoader)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __itemsCache = dependency.descriptor(IItemsCache)
    __awardController = dependency.descriptor(IAwardController)
    _COMMON_SOUND_SPACE = ARMORY_YARD_SOUND_SPACE

    def __init__(self, layoutID, tabId, onLoadedCallback=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = ArmoryYardMainViewModel()
        self.__onLoadedCallback = onLoadedCallback
        self.__destroyCallback = None
        super(ArmoryYardMainView, self).__init__(settings)
        self.__isClose = False
        self.__stageManager = StageManager()
        self.__tabId = None
        self.__selectedCycleID = 0
        self.__onHoldClose = False
        self.__wantToClose = False
        self.__initedTabId = tabId if tabId is not None else TabId.PROGRESS
        self.__awardController.addMonitoredDynamicViewKey(self.viewKeyDynamic)
        self.__tabs = {TabId.PROGRESS: _ProgressionTabPresenter(self.viewModel, self.__stageManager, self.__closeView),
         TabId.QUESTS: _QuestsTabPresenter(self.viewModel, self.__closeView, self.layer)}
        return

    def onPrbEntitySwitching(self):
        self.__armoryYardCtrl.unloadScene(isReload=False)
        self.__closeView()

    def _initialize(self, *args, **kwargs):
        super(ArmoryYardMainView, self)._initialize(*args, **kwargs)
        self.__armoryYardCtrl.updateVisibilityHangarHeaderMenu()
        self.startGlobalListening()

    def _finalize(self):
        for tab in self.__tabs.values():
            tab.fini()

        self.__tabs.clear()
        self.__stageManager.destroy()
        self.__stageManager = None
        self.__state = None
        self.__onHoldClose = False
        self.__wantToClose = False
        self.__armoryYardCtrl.updateVisibilityHangarHeaderMenu(isVisible=True)
        if not self.__armoryYardCtrl.isVehiclePreview:
            self.__armoryYardCtrl.onLoadingHangar()
        self.stopGlobalListening()
        super(ArmoryYardMainView, self)._finalize()
        if self.__destroyCallback is not None:
            self.__destroyCallback()
        return

    def _onLoading(self, *args, **kwargs):
        super(ArmoryYardMainView, self)._onLoading(*args, **kwargs)
        for tab in self.__tabs.values():
            tab.init(self.getParentWindow())

        self._updateModelData()

    def _onLoaded(self, *args, **kwargs):
        super(ArmoryYardMainView, self)._onLoaded(*args, **kwargs)
        self.__setTab()
        self.__shopUpdate()
        self.__hintUpdate()
        if self.__onLoadedCallback is not None:
            self.__onLoadedCallback()
        return

    def _getEvents(self):
        return super(ArmoryYardMainView, self)._getEvents() + ((self.viewModel.onTabChange, self.__onTabChange),
         (self.viewModel.onQuestReroll, self.__openRerollView),
         (self.viewModel.onChapterSelect, self.__onChapterSelect),
         (self.__armoryYardCtrl.onProgressUpdated, self.__progressUpdated),
         (self.__armoryYardCtrl.serverSettings.onUpdated, self.__onServerSettingsUpdated),
         (self.__armoryYardRerollCtrl.onFreeRerollTokensUpdated, self.__onFreeRerollTokensUpdated),
         (self.__armoryYardCtrl.onTabIdChanged, self.__onTabChange),
         (self.__armoryShopCtrl.onSettingsUpdate, self.__shopUpdate),
         (self.__armoryYardCtrl.onStatusChange, self.__checkStatus))

    def __checkStatus(self):
        if not self.__armoryYardCtrl.isActive():
            self.__closeView()
            return

    def _getListeners(self):
        return ((ArmoryYardEvent.DESTROY_ARMORY_YARD_MAIN_VIEW, self.__destroyWindowEvent),
         (ArmoryYardEvent.SHOW_ARMORY_YARD_BUY_VIEW, self.__showArmoryYardBuyView),
         (ArmoryYardEvent.SHOW_ARMORY_YARD_SHOP_BUY_VIEW, self.__showArmoryYardShopBuyView),
         (ArmoryYardEvent.SHOW_ARMORY_YARD_REROLL_VIEW, self.__showArmoryYardRerollView))

    def _getCurrentPresenter(self):
        return self.__tabs[self.__tabId or self.__initedTabId]

    def _updateModelData(self):
        self.__updateFreeRerollCount()
        with self.viewModel.transaction() as vm:
            if self.__armoryYardRerollCtrl.isRerollEnabled():
                vm.setRerollCountDown(self.__armoryYardRerollCtrl.getFreeRerollCountdown())
            vm.setIsRerollEnabled(self.__armoryYardRerollCtrl.isRerollEnabled())
            vm.setIsPostProgression(self.__armoryYardCtrl.isPostProgressionState)
            maxNumberOfSteps = self.__armoryYardCtrl.maxNumberOfSteps
            receivedTokensCount = self.__armoryYardCtrl.receivedTokensInPostProgressionChapter() if self.__armoryYardCtrl.isPostProgressionState else self.__armoryYardCtrl.getProgressionTokenCount()
            postProgressionTotalTokens = maxNumberOfSteps - self.__armoryYardCtrl.startStepOfPostProgression
            totalTokensCount = postProgressionTotalTokens if self.__armoryYardCtrl.isPostProgressionState else self.__armoryYardCtrl.startStepOfPostProgression
            vm.setReceivedTokensCount(receivedTokensCount)
            vm.setTotalTokensCount(totalTokensCount)
            vm.setMaxNumberOfSteps(maxNumberOfSteps)

    @property
    def viewModel(self):
        return super(ArmoryYardMainView, self).getViewModel()

    @property
    def viewKeyDynamic(self):
        return ViewKeyDynamic(R.views.armory_yard.lobby.feature.ArmoryYardMainView())

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ArmoryYardMainView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.armory_yard.lobby.feature.tooltips.ArmoryYardCurrencyTooltipView():
            currency = event.getArgument('currency')
            if self.getTooltipData(event):
                currency = currency or self.getTooltipData(event).specialArgs[0]
            return ArmoryYardCurrencyTooltipView(currency)
        if contentID == R.views.armory_yard.lobby.feature.tooltips.ArmoryYardSimpleTooltipView():
            return ArmoryYardSimpleTooltipView(event.getArgument('state'), event.getArgument('id'), event.getArgument('step'), stageManager=self.__stageManager)
        if contentID == R.views.armory_yard.lobby.feature.tooltips.TaskConditionTooltipView():
            return TaskConditionTooltipView(event.getArgument('vehicleLevels'), event.getArgument('vehicleTypes'), event.getArgument('battleTypes'), event.getArgument('vehicleNations'))
        if contentID == R.views.armory_yard.lobby.feature.tooltips.RerollInfoContainerTooltip():
            return RerollInfoContainerTooltip()
        if contentID == R.views.armory_yard.lobby.feature.tooltips.RerollButtonTooltip():
            return RerollButtonTooltip(self.__selectedCycleID)
        if _LOOTBOX_RES.exists() and contentID == _LOOTBOX_RES():
            from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
            tooltipData = self.getTooltipData(event)
            lootBoxID = tooltipData.get('lootBoxID')
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
            return LootboxTooltip(lootBox)
        return super(ArmoryYardMainView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        tooltipType = event.getArgument('tooltipType')
        if not tooltipId:
            return None
        else:
            return first([ presenter.getTooltipData(tooltipId, tooltipType) for presenter in self.__tabs.itervalues() ])

    def _destroySubViews(self):
        windows = self.gui.windowsManager.findWindows(lambda w: w.layer == WindowLayer.TOP_SUB_VIEW)
        for window in windows:
            window.destroy()

    def __setTab(self, tabID=None):
        if tabID is None:
            tabID = self.__initedTabId
        if self.__tabId != tabID:
            self._destroySubViews()
            if self.__tabId is not None:
                self.__tabs[self.__tabId].onUnload()
            if tabID == TabId.SHOP:
                self.__tabId = None
                showArmoryYardShopWindow(self.getWindow())
                return
            self.__tabId = tabID
            self.__tabs[self.__tabId].onLoad()
            if self.viewModel:
                self.viewModel.setTabId(self.__tabId)
        return

    @classmethod
    def getInstances(cls):
        return cls.__gui.windowsManager.findViews(cls.__loadedWindowPredicate)

    @classmethod
    def __loadedWindowPredicate(cls, view):
        return view.layoutID == R.views.armory_yard.lobby.feature.ArmoryYardMainView()

    def __onServerSettingsUpdated(self):
        if not self.__armoryYardCtrl.isEnabled():
            self.destroyWindow()
        else:
            self._updateModelData()

    def __onFreeRerollTokensUpdated(self):
        self.__updateFreeRerollCount()

    def __closeView(self, *args):
        if self.__isClose:
            return
        if self.__onHoldClose and not self.__armoryYardCtrl.isPaused:
            self.__wantToClose = True
            return
        self.__isClose = True
        self.destroy()
        showHangar()

    def __destroyWindowEvent(self, event):
        self.__destroyCallback = event.ctx.get('destroyCallback', None)
        self.destroy()
        return

    def setHoldClose(self):
        self.__onHoldClose = True

    def unHoldClose(self):
        self.__onHoldClose = False
        if self.__wantToClose:
            self.__closeView()

    def __onTabChange(self, *args):
        self.__setTab(TabId(first(args).get('tabId')))

    def __shopUpdate(self):
        self.__checkStatus()
        if self.viewModel:
            with self.getViewModel().transaction() as model:
                model.setShopButtonVisible(self.__armoryShopCtrl.isEnabled)

    def __hintUpdate(self):
        if self.getViewModel():
            self.getViewModel().setIsRerollButtonTriggerEnabled(not AccountSettings.getArmoryYard(ArmoryYard.ARMORY_YARD_REROLL_BUTTON_HINT_VIEWED))

    def __showArmoryYardBuyView(self, event):
        if self.__tabId == TabId.PROGRESS and not self.__armoryYardCtrl.isCompleted():
            if self.__armoryYardCtrl.isStarterPackAvailable() and not self.__armoryYardCtrl.isPostProgressionState:
                showArmoryYardBundlesWindow(parent=self.getParentWindow(), onLoadedCallback=event.ctx.get('onLoadedCallback', None))
            elif self.__armoryYardCtrl.isPurchaseStageActive():
                showArmoryYardPurchaseStageBuyWindow(parent=self.getParentWindow(), onLoadedCallback=event.ctx.get('onLoadedCallback', None))
            else:
                showArmoryYardBuyWindow(parent=self.getParentWindow(), onLoadedCallback=event.ctx.get('onLoadedCallback', None))
        return

    def __showArmoryYardShopBuyView(self, event):
        showArmoryYardShopBuyWindow(productId=event.ctx.get('productID'), parent=self.getParentWindow(), onLoadedCallback=event.ctx.get('onLoadedCallback', None))
        return

    def __showArmoryYardRerollView(self, event):
        showYardQuestRerollWindowByTokenQuestID(parent=self.getParentWindow(), tokenQuestID=event.ctx.get('questId', ''), questsToSelect=event.ctx.get('questsToSelect', []), onLoadedCallback=event.ctx.get('onLoadedCallback', None))
        return

    def __progressUpdated(self):
        setSoundDroneMode(self.__armoryYardCtrl.isPostProgressionState)
        self._updateModelData()

    def __updateFreeRerollCount(self):
        with self.viewModel.transaction() as vm:
            vm.setFreeRerollCount(self.__armoryYardRerollCtrl.getFreeRerollsCountByCycleID(int(self.__selectedCycleID)))

    def __onChapterSelect(self, *args):
        self.__selectedCycleID = first(args).get('chapterId')
        self.__updateFreeRerollCount()

    @args2params(str)
    def __openRerollView(self, questId):
        if not AccountSettings.getArmoryYard(ArmoryYard.ARMORY_YARD_REROLL_BUTTON_HINT_VIEWED):
            AccountSettings.setArmoryYard(ArmoryYard.ARMORY_YARD_REROLL_BUTTON_HINT_VIEWED, True)
            self.__hintUpdate()
        showArmoryYardQuestRerollWindow(parent=self.getParentWindow(), conditionQuestID=questId)
