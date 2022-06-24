# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/mode_selector_view.py
from functools import partial
import typing
import adisp
from adisp import process
from constants import QUEUE_TYPE
from frameworks.wulf import ViewSettings, ViewFlags, WindowLayer, WindowStatus, ViewStatus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl import backport
from gui.impl.backport.backport_tooltip import DecoratedTooltipWindow, createAndLoadBackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_model import ModeSelectorModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_window_states import ModeSelectorWindowStates
from gui.impl.gen.view_models.views.lobby.mode_selector.tooltips.mode_selector_tooltips_constants import ModeSelectorTooltipsConstants
from gui.impl.lobby.battle_pass.tooltips.battle_pass_completed_tooltip_view import BattlePassCompletedTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_in_progress_tooltip_view import BattlePassInProgressTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_not_started_tooltip_view import BattlePassNotStartedTooltipView
from gui.impl.lobby.mode_selector.battle_session_view import BattleSessionView
from gui.impl.lobby.mode_selector.items import saveBattlePassStateForItems
from gui.impl.lobby.mode_selector.mode_selector_data_provider import ModeSelectorDataProvider
from gui.impl.lobby.mode_selector.popovers.random_battle_popover import RandomBattlePopover
from gui.impl.lobby.mode_selector.sound_constants import MODE_SELECTOR_SOUND_SPACE
from gui.impl.lobby.mode_selector.tooltips.simply_format_tooltip import SimplyFormatTooltipView
from gui.impl.pub import ViewImpl
from gui.impl.pub.tooltip_window import SimpleTooltipContent
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.events import FullscreenModeSelectorEvent, LoadViewEvent
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from uilogging.bootcamp.loggers import BootcampLogger
from uilogging.mode_selector.constants import LOG_KEYS, LOG_ACTIONS, LOG_CLOSE_DETAILS
from uilogging.mode_selector.loggers import BaseModeSelectorLogger
if typing.TYPE_CHECKING:
    from typing import Optional, Callable
    from gui.Scaleform.framework.application import AppEntry
    from frameworks.wulf import View, ViewEvent, Window
    from gui.Scaleform.managers import GameInputMgr
_BACKGROUND_ALPHA = 0.7
_R_SIMPLE_TOOLTIP = R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent
_CLOSE_LAYERS = (WindowLayer.SUB_VIEW, WindowLayer.TOP_SUB_VIEW)

class ModeSelectorView(ViewImpl):
    __slots__ = ('__blur', '__dataProvider', '__prevAppBackgroundAlpha', '__isEventEnabled', '__isClickProcessing', '__prevOptimizationEnabled', '__isGraphicsRestored')
    uiLogger = BaseModeSelectorLogger(LOG_KEYS.MS_WINDOW)
    uiBootcampLogger = BootcampLogger(LOG_KEYS.MS_WINDOW)
    _COMMON_SOUND_SPACE = MODE_SELECTOR_SOUND_SPACE
    __appLoader = dependency.descriptor(IAppLoader)
    __bootcamp = dependency.descriptor(IBootcampController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gui = dependency.descriptor(IGuiLoader)
    __tooltipByContentID = {R.views.lobby.battle_pass.tooltips.BattlePassNotStartedTooltipView(): BattlePassNotStartedTooltipView,
     R.views.lobby.battle_pass.tooltips.BattlePassCompletedTooltipView(): BattlePassCompletedTooltipView,
     R.views.lobby.battle_pass.tooltips.BattlePassInProgressTooltipView(): partial(BattlePassInProgressTooltipView, battleType=QUEUE_TYPE.RANDOMS)}
    layoutID = R.views.lobby.mode_selector.ModeSelectorView()
    _areWidgetsVisible = False

    def __init__(self, layoutId, isEventEnabled=False, provider=None):
        super(ModeSelectorView, self).__init__(ViewSettings(layoutId, ViewFlags.LOBBY_TOP_SUB_VIEW, ModeSelectorModel()))
        self.__dataProvider = provider if provider else ModeSelectorDataProvider()
        self.__blur = None
        self.__prevOptimizationEnabled = False
        self.__prevAppBackgroundAlpha = 0.0
        self.__isEventEnabled = isEventEnabled
        self.__isClickProcessing = False
        self.__isGraphicsRestored = False
        self.inputManager.addEscapeListener(self.__handleEscape)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def inputManager(self):
        app = self.__appLoader.getApp()
        return app.gameInputManager

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId in [ModeSelectorTooltipsConstants.DISABLED_TOOLTIP, ModeSelectorTooltipsConstants.CALENDAR_TOOLTIP]:
                index = int(event.getArgument('index'))
                modeSelectorItem = self.__dataProvider.getItemByIndex(index)
                if modeSelectorItem is None:
                    return
                body = modeSelectorItem.disabledTooltipText
                if tooltipId == ModeSelectorTooltipsConstants.CALENDAR_TOOLTIP:
                    if modeSelectorItem.hasExtendedCalendarTooltip:
                        return modeSelectorItem.getExtendedCalendarTooltip(self.getParentWindow())
                    body = modeSelectorItem.calendarTooltipText
                return self.__createSimpleTooltip(event, body=body)
            if tooltipId == ModeSelectorTooltipsConstants.RANDOM_BP_PAUSED_TOOLTIP:
                return self.__createSimpleTooltip(event, header=backport.text(R.strings.battle_pass.tooltips.entryPoint.disabled.header()), body=backport.text(R.strings.battle_pass.tooltips.entryPoint.disabled.body()))
            if tooltipId in [ModeSelectorTooltipsConstants.RANKED_CALENDAR_DAY_INFO_TOOLTIP,
             ModeSelectorTooltipsConstants.RANKED_STEP_TOOLTIP,
             ModeSelectorTooltipsConstants.RANKED_BATTLES_LEAGUE_TOOLTIP,
             ModeSelectorTooltipsConstants.RANKED_BATTLES_EFFICIENCY_TOOLTIP,
             ModeSelectorTooltipsConstants.RANKED_BATTLES_POSITION_TOOLTIP,
             ModeSelectorTooltipsConstants.RANKED_BATTLES_BONUS_TOOLTIP,
             ModeSelectorTooltipsConstants.MAPBOX_CALENDAR_TOOLTIP,
             ModeSelectorTooltipsConstants.EPIC_BATTLE_CALENDAR_TOOLTIP,
             ModeSelectorTooltipsConstants.FUN_RANDOM_CALENDAR_TOOLTIP]:
                return createAndLoadBackportTooltipWindow(self.getParentWindow(), tooltipId=tooltipId, isSpecial=True, specialArgs=(None,))
            if tooltipId == ModeSelectorTooltipsConstants.RANKED_BATTLES_RANK_TOOLTIP:
                rankID = int(event.getArgument('rankID'))
                return createAndLoadBackportTooltipWindow(self.getParentWindow(), tooltipId=tooltipId, isSpecial=True, specialArgs=(rankID,))
            if tooltipId == ModeSelectorTooltipsConstants.EPIC_BATTLE_WIDGET_INFO:
                return createAndLoadBackportTooltipWindow(self.getParentWindow(), tooltipId=tooltipId, isSpecial=True, specialArgs=[])
        return super(ModeSelectorView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == _R_SIMPLE_TOOLTIP():
            return SimpleTooltipContent(contentID, event.getArgument('header', ''), event.getArgument('body', ''), event.getArgument('note', ''), event.getArgument('alert', ''))
        elif contentID == R.views.lobby.mode_selector.tooltips.SimplyFormatTooltip():
            modeName = event.getArgument('modeName', '')
            if modeName is None:
                return
            tooltipLocal = R.strings.mode_selector.mode.dyn(modeName)
            if not tooltipLocal:
                return
            header = backport.text(tooltipLocal.battlePassTooltip.header())
            body = backport.text(tooltipLocal.battlePassTooltip.body())
            if not header:
                return
            return SimplyFormatTooltipView(header, body)
        else:
            tooltipClass = self.__tooltipByContentID.get(contentID)
            return tooltipClass() if tooltipClass else None

    def destroyWindow(self):
        self.uiLogger.log(LOG_ACTIONS.CLOSED, details=LOG_CLOSE_DETAILS.OTHER)
        super(ModeSelectorView, self).destroyWindow()

    def createPopOverContent(self, event):
        return RandomBattlePopover() if event.contentID == R.views.lobby.mode_selector.popovers.RandomBattlePopover() else super(ModeSelectorView, self).createPopOverContent(event)

    def close(self):
        g_eventBus.handleEvent(events.DestroyGuiImplViewEvent(self.layoutID))

    def _onLoading(self):
        self.__gui.windowsManager.onWindowStatusChanged += self.__windowStatusChanged
        self.__lobbyContext.addHeaderNavigationConfirmator(self.__handleHeaderNavigation)
        self.viewModel.onItemClicked += self.__itemClickHandler
        self.viewModel.onShowMapSelectionClicked += self.__showMapSelectionClickHandler
        self.viewModel.onShowWidgetsClicked += self.__showWidgetsClickHandler
        self.viewModel.onInfoClicked += self.__infoClickHandler
        self.__dataProvider.onListChanged += self.__dataProviderListChangeHandler
        self.__updateViewModel(self.viewModel)
        self.__blur = CachedBlur(enabled=True, ownLayer=WindowLayer.MARKER)
        g_eventBus.handleEvent(events.GameEvent(events.GameEvent.HIDE_LOBBY_SUB_CONTAINER_ITEMS), scope=EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), scope=EVENT_BUS_SCOPE.LOBBY)
        app = self.__appLoader.getApp()
        self.__prevAppBackgroundAlpha = app.getBackgroundAlpha()
        app.setBackgroundAlpha(_BACKGROUND_ALPHA)
        self.__prevOptimizationEnabled = app.graphicsOptimizationManager.getEnable()
        if self.__prevOptimizationEnabled:
            app.graphicsOptimizationManager.switchOptimizationEnabled(False)

    def _initialize(self):
        g_eventBus.handleEvent(FullscreenModeSelectorEvent(FullscreenModeSelectorEvent.NAME, ctx={'showing': True}))

    def _onLoaded(self):
        self.uiBootcampLogger.logOnlyFromBootcamp(LOG_ACTIONS.OPENED)
        self.inputManager.removeEscapeListener(self.__handleEscape)
        self.uiLogger.log(LOG_ACTIONS.OPENED, isNew=self.__dataProvider.hasNewIndicator, isWidget=self._areWidgetsVisible, isFeatured=self.__isEventEnabled)

    def _finalize(self):
        self.uiBootcampLogger.logOnlyFromBootcamp(LOG_ACTIONS.CLOSED)
        self.__gui.windowsManager.onWindowStatusChanged -= self.__windowStatusChanged
        self.inputManager.removeEscapeListener(self.__handleEscape)
        self.__lobbyContext.deleteHeaderNavigationConfirmator(self.__handleHeaderNavigation)
        self.viewModel.onItemClicked -= self.__itemClickHandler
        self.viewModel.onShowMapSelectionClicked -= self.__showMapSelectionClickHandler
        self.viewModel.onShowWidgetsClicked -= self.__showWidgetsClickHandler
        self.viewModel.onInfoClicked -= self.__infoClickHandler
        saveBattlePassStateForItems(self.__dataProvider.itemList)
        self.__dataProvider.onListChanged -= self.__dataProviderListChangeHandler
        self.__dataProvider.dispose()
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(FullscreenModeSelectorEvent(FullscreenModeSelectorEvent.NAME, ctx={'showing': False}))
        g_eventBus.handleEvent(events.GameEvent(events.GameEvent.REVEAL_LOBBY_SUB_CONTAINER_ITEMS), scope=EVENT_BUS_SCOPE.GLOBAL)
        self.__restoreGraphics()

    def __restoreGraphics(self):
        if self.__isGraphicsRestored:
            return
        else:
            self.__isGraphicsRestored = True
            if self.__blur:
                self.__blur.fini()
                self.__blur = None
            app = self.__appLoader.getApp()
            if self.__prevOptimizationEnabled:
                app.graphicsOptimizationManager.switchOptimizationEnabled(True)
            app.setBackgroundAlpha(self.__prevAppBackgroundAlpha)
            return

    def __createSimpleTooltip(self, event, header='', body=''):
        window = DecoratedTooltipWindow(content=SimpleTooltipContent(_R_SIMPLE_TOOLTIP(), body=body, header=header), parent=self.getParentWindow())
        window.load()
        window.move(event.mouse.positionX, event.mouse.positionY)
        return window

    def __dataProviderListChangeHandler(self):
        with self.viewModel.transaction() as tx:
            self.__updateViewModel(tx)

    def __updateViewModel(self, vm):
        vm.setIsMapSelectionVisible(self.__dataProvider.isDemonstrator)
        vm.setIsMapSelectionEnabled(self.__dataProvider.isDemoButtonEnabled)
        vm.setAreWidgetsVisible(ModeSelectorView._areWidgetsVisible)
        if self.__bootcamp.isInBootcamp():
            vm.setState(ModeSelectorWindowStates.BOOTCAMP)
        cards = vm.getCardList()
        cards.clear()
        for item in self.__dataProvider.itemList:
            cards.addViewModel(item.viewModel)

        cards.invalidate()

    @process
    def __itemClickHandler(self, event):
        self.__isClickProcessing = True
        navigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
        if not navigationPossible:
            self.__isClickProcessing = False
            return
        else:
            index = int(event.get('index'))
            modeSelectorItem = self.__dataProvider.getItemByIndex(index)
            if modeSelectorItem is None:
                self.__isClickProcessing = False
                return
            self.uiLogger.log(LOG_ACTIONS.CARD_CLICKED, size=event.get('size'), details=event.get('cardMediaSize'), isNew=modeSelectorItem.viewModel.getIsNew(), mode=modeSelectorItem.modeName, isSelected=modeSelectorItem.viewModel.getIsSelected())
            modeSelectorItem.handleClick()
            if modeSelectorItem.isSelectable:
                specView = self.__gui.windowsManager.getViewByLayoutID(BattleSessionView.layoutID)
                if modeSelectorItem.modeName != PREBATTLE_ACTION_NAME.SPEC_BATTLES_LIST and specView is not None:
                    specView.destroyWindow()
                self.__dataProvider.select(modeSelectorItem.modeName)
            self.uiLogger.log(LOG_ACTIONS.CLOSED, details=LOG_CLOSE_DETAILS.CARD_CLICKED)
            self.close()
            return

    def __showMapSelectionClickHandler(self):
        demonstratorWindow = self.__appLoader.getApp().containerManager.getView(WindowLayer.WINDOW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.DEMONSTRATOR_WINDOW})
        if demonstratorWindow is not None:
            demonstratorWindow.onWindowClose()
        else:
            g_eventBus.handleEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.DEMONSTRATOR_WINDOW)), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def __showWidgetsClickHandler(self):
        ModeSelectorView._areWidgetsVisible = not ModeSelectorView._areWidgetsVisible
        self.viewModel.setAreWidgetsVisible(ModeSelectorView._areWidgetsVisible)

    def __infoClickHandler(self, event):
        self.uiBootcampLogger.logOnlyFromBootcamp(LOG_ACTIONS.INFO_PAGE_ICON_CLICKED)
        index = int(event.get('index'))
        modeSelectorItem = self.__dataProvider.getItemByIndex(index)
        if modeSelectorItem is None:
            return
        else:
            self.uiLogger.log(LOG_ACTIONS.INFO_PAGE_ICON_CLICKED, isNew=modeSelectorItem.viewModel.getIsNew(), mode=modeSelectorItem.modeName)
            modeSelectorItem.handleInfoPageClick()
            return

    def __windowStatusChanged(self, uniqueID, newStatus):
        if newStatus == WindowStatus.LOADED:
            window = self.__gui.windowsManager.getWindow(uniqueID)
            parent = None
            if window.parent is not None and window.parent.content is not None:
                parent = window.parent.content
            if window.content == self or parent is not None and parent == self:
                return
            if window.layer in _CLOSE_LAYERS:
                self.__restoreGraphics()
                if not self.__isClickProcessing:
                    self.uiLogger.log(LOG_ACTIONS.CLOSED, details=LOG_CLOSE_DETAILS.OTHER)
                    self.close()
        return

    @adisp.async
    def __handleHeaderNavigation(self, callback):
        if self.viewStatus not in (ViewStatus.DESTROYED, ViewStatus.DESTROYING) and not self.__isClickProcessing:
            self.close()
        callback(True)

    def __handleEscape(self):
        self.close()
