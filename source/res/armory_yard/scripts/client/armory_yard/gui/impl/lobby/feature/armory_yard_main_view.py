# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_main_view.py
import logging
from armory_yard.gui.window_events import showArmoryYardBuyWindow, showArmoryYardBundlesWindow
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared.events import ArmoryYardEvent
from helpers import dependency
from shared_utils import first
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showHangar
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewFlags, ViewSettings
from skeletons.gui.game_control import IArmoryYardController, IAwardController
from skeletons.gui.impl import IGuiLoader
from armory_yard.managers.stage_manager import StageManager
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_main_view_model import ArmoryYardMainViewModel, TabId
from armory_yard.gui.impl.lobby.feature.armory_yard_quests_presenter import _QuestsTabPresenter
from armory_yard.gui.impl.lobby.feature.armory_yard_progress_presenter import _ProgressionTabPresenter
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.framework.entities.View import ViewKeyDynamic
from armory_yard.gui.Scaleform.daapi.view.lobby.hangar.sound_constants import ARMORY_YARD_SOUND_SPACE
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from armory_yard.gui.impl.lobby.feature.tooltips.armory_yard_currency_tooltip_view import ArmoryYardCurrencyTooltipView
from armory_yard.gui.impl.lobby.feature.tooltips.armory_yard_simple_tooltip_view import ArmoryYardSimpleTooltipView
_logger = logging.getLogger(__name__)

class ArmoryYardMainView(ViewImpl, IGlobalListener):
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
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
        self.__stageManager = StageManager()
        self.__tabId = None
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
        self.__updateVisibilityHangarHeaderMenu()
        self.startGlobalListening()

    def _finalize(self):
        for tab in self.__tabs.values():
            tab.fini()

        self.__tabs.clear()
        self.__stageManager.destroy()
        self.__stageManager = None
        self.__state = None
        self.__updateVisibilityHangarHeaderMenu(isVisible=True)
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

    def _onLoaded(self, *args, **kwargs):
        super(ArmoryYardMainView, self)._onLoaded(*args, **kwargs)
        self.__setTab()
        if self.__onLoadedCallback is not None:
            self.__onLoadedCallback()
        return

    def _getEvents(self):
        return super(ArmoryYardMainView, self)._getEvents() + ((self.viewModel.onTabChange, self.__onTabChange), (self.__armoryYardCtrl.serverSettings.onUpdated, self.__onServerSettingsUpdated), (self.__armoryYardCtrl.onTabIdChanged, self.__onTabChange))

    def _getListeners(self):
        return ((ArmoryYardEvent.DESTROY_ARMORY_YARD_MAIN_VIEW, self.__destroyWindowEvent), (ArmoryYardEvent.SHOW_ARMORY_YARD_BUY_VIEW, self.__showArmoryYardBuyView))

    def _getCurrentPresenter(self):
        return self.__tabs[self.__tabId or self.__initedTabId]

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
            return ArmoryYardCurrencyTooltipView()
        return ArmoryYardSimpleTooltipView(event.getArgument('state'), event.getArgument('id')) if contentID == R.views.armory_yard.lobby.feature.tooltips.ArmoryYardSimpleTooltipView() else super(ArmoryYardMainView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        tooltipType = event.getArgument('tooltipType')
        if not tooltipId:
            return None
        else:
            return first([ presenter.getTooltipData(tooltipId, tooltipType) for presenter in self.__tabs.itervalues() ])

    def __setTab(self, tabID=None):
        if tabID is None:
            tabID = self.__initedTabId
        if self.__tabId != tabID:
            if self.__tabId is not None:
                self.__tabs[self.__tabId].onUnload()
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

    def __updateVisibilityHangarHeaderMenu(self, isVisible=False):
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING if not isVisible else HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)

    def __closeView(self, *args):
        self.__armoryYardCtrl.disableVideoStreaming()
        self.destroy()
        showHangar()

    def __destroyWindowEvent(self, event):
        self.__destroyCallback = event.ctx.get('destroyCallback', None)
        self.destroy()
        return

    def __onTabChange(self, *args):
        self.__setTab(TabId(first(args).get('tabId')))

    def __showArmoryYardBuyView(self, event):
        if self.__tabId == TabId.PROGRESS and not self.__armoryYardCtrl.isCompleted():
            if self.__armoryYardCtrl.isStarterPackAvailable():
                showArmoryYardBundlesWindow(parent=self.getParentWindow(), onLoadedCallback=event.ctx.get('onLoadedCallback', None))
            else:
                showArmoryYardBuyWindow(parent=self.getParentWindow(), onLoadedCallback=event.ctx.get('onLoadedCallback', None))
        return
