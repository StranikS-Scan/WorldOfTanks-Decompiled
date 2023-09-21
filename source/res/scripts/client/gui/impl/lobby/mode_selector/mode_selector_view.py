# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/mode_selector_view.py
import logging
from functools import partial
import typing
import adisp
from constants import QUEUE_TYPE
from frameworks.wulf import ViewSettings, ViewFlags, WindowLayer, WindowStatus, ViewStatus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl import backport
from gui.impl.auxiliary.tooltips.simple_tooltip import createSimpleTooltip
from gui.impl.backport.backport_tooltip import createAndLoadBackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_model import ModeSelectorModel
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_window_states import ModeSelectorWindowStates
from gui.impl.gen.view_models.views.lobby.mode_selector.tooltips.mode_selector_tooltips_constants import ModeSelectorTooltipsConstants
from gui.impl.lobby.battle_pass.tooltips.battle_pass_completed_tooltip_view import BattlePassCompletedTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_in_progress_tooltip_view import BattlePassInProgressTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_not_started_tooltip_view import BattlePassNotStartedTooltipView
from gui.impl.lobby.comp7.tooltips.main_widget_tooltip import MainWidgetTooltip
from gui.impl.lobby.comp7.tooltips.rank_inactivity_tooltip import RankInactivityTooltip
from gui.impl.lobby.mode_selector.battle_session_view import BattleSessionView
from gui.impl.lobby.mode_selector.items import saveBattlePassStateForItems
from gui.impl.lobby.mode_selector.mode_selector_data_provider import ModeSelectorDataProvider
from gui.impl.lobby.mode_selector.popovers.random_battle_popover import RandomBattlePopover
from gui.impl.lobby.mode_selector.sound_constants import MODE_SELECTOR_SOUND_SPACE
from gui.impl.lobby.mode_selector.tooltips.simply_format_tooltip import SimplyFormatTooltipView
from gui.impl.lobby.winback.popovers.winback_leave_mode_popover_view import WinbackLeaveModePopoverView
from gui.impl.lobby.wt_event.tooltips.wt_event_header_widget_tooltip_view import WtEventHeaderWidgetTooltipView
from gui.impl.lobby.wt_event.tooltips.wt_event_stamp_tooltip_view import WtEventStampTooltipView
from gui.impl.lobby.wt_event.tooltips.wt_event_ticket_tooltip_view import WtEventTicketTooltipView
from gui.impl.pub import ViewImpl
from gui.impl.pub.tooltip_window import SimpleTooltipContent
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.events import FullscreenModeSelectorEvent, ModeSelectorLoadedEvent, ModeSubSelectorEvent, LoadViewEvent
from gui.shared.system_factory import registerModeSelectorTooltips, collectModeSelectorTooltips
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IBootcampController, IWinbackController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from uilogging.deprecated.bootcamp.constants import BC_LOG_KEYS, BC_LOG_ACTIONS
from uilogging.deprecated.bootcamp.loggers import BootcampLogger
from wg_async import wg_await, await_callback, wg_async, BrokenPromiseError, forwardAsFuture
if typing.TYPE_CHECKING:
    from typing import Optional, Callable
    from gui.Scaleform.framework.application import AppEntry
    from frameworks.wulf import View, ViewEvent, Window
    from gui.Scaleform.managers import GameInputMgr
_logger = logging.getLogger(__name__)
_BACKGROUND_ALPHA = 0.7
_R_SIMPLE_TOOLTIP = R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent
_SIMPLE_TOOLTIPS_KEY = 'simpleTooltipIds'
_CONTENT_TOOLTIPS_KEY = 'contentTooltipsMap'
_CLOSE_LAYERS = (WindowLayer.SUB_VIEW, WindowLayer.TOP_SUB_VIEW)
_SIMPLE_TOOLTIP_IDS = [ModeSelectorTooltipsConstants.RANKED_CALENDAR_DAY_INFO_TOOLTIP,
 ModeSelectorTooltipsConstants.RANKED_STEP_TOOLTIP,
 ModeSelectorTooltipsConstants.RANKED_BATTLES_LEAGUE_TOOLTIP,
 ModeSelectorTooltipsConstants.RANKED_BATTLES_EFFICIENCY_TOOLTIP,
 ModeSelectorTooltipsConstants.RANKED_BATTLES_POSITION_TOOLTIP,
 ModeSelectorTooltipsConstants.RANKED_BATTLES_BONUS_TOOLTIP,
 ModeSelectorTooltipsConstants.MAPBOX_CALENDAR_TOOLTIP,
 ModeSelectorTooltipsConstants.EPIC_BATTLE_CALENDAR_TOOLTIP,
 ModeSelectorTooltipsConstants.COMP7_CALENDAR_DAY_EXTENDED_INFO,
 ModeSelectorTooltipsConstants.EVENT_BATTLES_CALENDAR_TOOLTIP]

def _getTooltipByContentIdMap():
    return {R.views.lobby.battle_pass.tooltips.BattlePassNotStartedTooltipView(): BattlePassNotStartedTooltipView,
     R.views.lobby.battle_pass.tooltips.BattlePassCompletedTooltipView(): BattlePassCompletedTooltipView,
     R.views.lobby.battle_pass.tooltips.BattlePassInProgressTooltipView(): partial(BattlePassInProgressTooltipView, battleType=QUEUE_TYPE.RANDOMS),
     R.views.lobby.comp7.tooltips.MainWidgetTooltip(): MainWidgetTooltip,
     R.views.lobby.comp7.tooltips.RankInactivityTooltip(): RankInactivityTooltip,
     R.views.lobby.wt_event.tooltips.WtEventHeaderWidgetTooltipView(): WtEventHeaderWidgetTooltipView,
     R.views.lobby.wt_event.tooltips.WtEventTicketTooltipView(): WtEventTicketTooltipView,
     R.views.lobby.wt_event.tooltips.WtEventStampTooltipView(): WtEventStampTooltipView}


registerModeSelectorTooltips(_SIMPLE_TOOLTIP_IDS, _getTooltipByContentIdMap())

class ModeSelectorView(ViewImpl):
    __slots__ = ('__blur', '__dataProvider', '__prevAppBackgroundAlpha', '__isEventEnabled', '__isClickProcessing', '__prevOptimizationEnabled', '__isGraphicsRestored', '__tooltipConstants', '__subSelectorCallback', '__isContentVisible')
    uiBootcampLogger = BootcampLogger(BC_LOG_KEYS.MS_WINDOW)
    _COMMON_SOUND_SPACE = MODE_SELECTOR_SOUND_SPACE
    __appLoader = dependency.descriptor(IAppLoader)
    __bootcamp = dependency.descriptor(IBootcampController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gui = dependency.descriptor(IGuiLoader)
    __winbackController = dependency.descriptor(IWinbackController)
    layoutID = R.views.lobby.mode_selector.ModeSelectorView()
    _areWidgetsVisible = False

    def __init__(self, layoutId, isEventEnabled=False, provider=None, subSelectorCallback=None):
        super(ModeSelectorView, self).__init__(ViewSettings(layoutId, ViewFlags.LOBBY_TOP_SUB_VIEW, ModeSelectorModel()))
        self.__dataProvider = provider if provider else ModeSelectorDataProvider()
        self.__blur = None
        self.__prevOptimizationEnabled = False
        self.__prevAppBackgroundAlpha = 0.0
        self.__isEventEnabled = isEventEnabled
        self.__isClickProcessing = False
        self.__isGraphicsRestored = False
        self.__subSelectorCallback = subSelectorCallback
        self.__isContentVisible = subSelectorCallback is None
        self.__tooltipConstants = collectModeSelectorTooltips()
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
                return createSimpleTooltip(self.getParentWindow(), event, body=body)
            if tooltipId == ModeSelectorTooltipsConstants.RANDOM_BP_PAUSED_TOOLTIP:
                return createSimpleTooltip(self.getParentWindow(), event, header=backport.text(R.strings.battle_pass.tooltips.entryPoint.disabled.header()), body=backport.text(R.strings.battle_pass.tooltips.entryPoint.disabled.body()))
            if tooltipId in self.__tooltipConstants.get(_SIMPLE_TOOLTIPS_KEY, []):
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
            tooltipClass = self.__tooltipConstants.get(_CONTENT_TOOLTIPS_KEY, {}).get(contentID)
            return tooltipClass() if tooltipClass else None

    def createPopOverContent(self, event):
        if event.contentID == R.views.lobby.mode_selector.popovers.RandomBattlePopover():
            if self.__winbackController.getWinbackBattlesCountLeft() > 0:
                return WinbackLeaveModePopoverView()
            return RandomBattlePopover()
        return super(ModeSelectorView, self).createPopOverContent(event)

    def refresh(self):
        self.__dataProvider.forceRefresh()

    def close(self):
        g_eventBus.handleEvent(events.DestroyGuiImplViewEvent(self.layoutID))

    def _onLoading(self):
        self.__gui.windowsManager.onWindowStatusChanged += self.__windowStatusChanged
        self.__lobbyContext.addHeaderNavigationConfirmator(self.__handleHeaderNavigation)
        g_eventBus.addListener(ModeSubSelectorEvent.CHANGE_VISIBILITY, self.__updateContentVisibility)
        g_eventBus.addListener(ModeSubSelectorEvent.CLICK_PROCESSING, self.__updateClickProcessing)
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
        if self.__subSelectorCallback is not None:
            self.__subSelectorCallback()
            self.__subSelectorCallback = None
        return

    def _initialize(self):
        g_eventBus.handleEvent(FullscreenModeSelectorEvent(FullscreenModeSelectorEvent.NAME, ctx={'showing': True}))

    def _onLoaded(self):
        g_eventBus.handleEvent(ModeSelectorLoadedEvent(ModeSelectorLoadedEvent.NAME))
        self.uiBootcampLogger.logOnlyFromBootcamp(BC_LOG_ACTIONS.OPENED)
        self.inputManager.removeEscapeListener(self.__handleEscape)

    def _finalize(self):
        self.uiBootcampLogger.logOnlyFromBootcamp(BC_LOG_ACTIONS.CLOSED)
        self.__gui.windowsManager.onWindowStatusChanged -= self.__windowStatusChanged
        self.inputManager.removeEscapeListener(self.__handleEscape)
        g_eventBus.removeListener(ModeSubSelectorEvent.CLICK_PROCESSING, self.__updateClickProcessing)
        g_eventBus.removeListener(ModeSubSelectorEvent.CHANGE_VISIBILITY, self.__updateContentVisibility)
        self.__lobbyContext.deleteHeaderNavigationConfirmator(self.__handleHeaderNavigation)
        self.viewModel.onItemClicked -= self.__itemClickHandler
        self.viewModel.onShowMapSelectionClicked -= self.__showMapSelectionClickHandler
        self.viewModel.onShowWidgetsClicked -= self.__showWidgetsClickHandler
        self.viewModel.onInfoClicked -= self.__infoClickHandler
        saveBattlePassStateForItems(self.__dataProvider.itemList)
        self.__dataProvider.onListChanged -= self.__dataProviderListChangeHandler
        self.__dataProvider.dispose()
        self.__tooltipConstants = None
        self.__subSelectorCallback = None
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(FullscreenModeSelectorEvent(FullscreenModeSelectorEvent.NAME, ctx={'showing': False}))
        g_eventBus.handleEvent(events.GameEvent(events.GameEvent.REVEAL_LOBBY_SUB_CONTAINER_ITEMS), scope=EVENT_BUS_SCOPE.GLOBAL)
        self.__restoreGraphics()
        return

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

    def __dataProviderListChangeHandler(self):
        with self.viewModel.transaction() as tx:
            self.__updateViewModel(tx)

    def __updateViewModel(self, vm):
        vm.setIsContentVisible(self.__isContentVisible)
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

    def __updateContentVisibility(self, event):
        isSubSelectorVisible = event.ctx.get('visible', False) if event is not None else False
        self.__isContentVisible = not isSubSelectorVisible
        self.viewModel.setIsContentVisible(self.__isContentVisible)
        return

    def __updateClickProcessing(self, event):
        self.__isClickProcessing = event.ctx.get('isClickProcessing', False) if event is not None else False
        return

    @wg_async
    def __itemClickHandler(self, event):
        self.__isClickProcessing = True
        index = int(event.get('index'))
        modeSelectorItem = self.__dataProvider.getItemByIndex(index)
        if modeSelectorItem is None:
            self.__isClickProcessing = False
            return
        else:
            try:
                if modeSelectorItem.checkHeaderNavigation():
                    navigationPossible = yield await_callback(isHeaderNavigationPossible)()
                    if not navigationPossible:
                        self.__isClickProcessing = False
                        return
                yield wg_await(forwardAsFuture(modeSelectorItem.handleClick()))
            except BrokenPromiseError:
                _logger.debug('%s got BrokenPromiseError during __itemClickHandler.')

            if modeSelectorItem.isSelectable:
                specView = self.__gui.windowsManager.getViewByLayoutID(BattleSessionView.layoutID)
                if modeSelectorItem.modeName != PREBATTLE_ACTION_NAME.SPEC_BATTLES_LIST and specView is not None:
                    specView.destroyWindow()
                self.__dataProvider.select(modeSelectorItem.modeName)
            self.__isClickProcessing = False
            if self.__isContentVisible:
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
        self.uiBootcampLogger.logOnlyFromBootcamp(BC_LOG_ACTIONS.INFO_PAGE_ICON_CLICKED)
        index = int(event.get('index'))
        modeSelectorItem = self.__dataProvider.getItemByIndex(index)
        if modeSelectorItem is None:
            return
        else:
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
            if getattr(window.content, 'isModeSelectorAutoCloseDisabled', False):
                return
            if window.layer in _CLOSE_LAYERS:
                self.__restoreGraphics()
                if not self.__isClickProcessing:
                    self.close()
        return

    @adisp.adisp_async
    def __handleHeaderNavigation(self, callback):
        if self.viewStatus not in (ViewStatus.DESTROYED, ViewStatus.DESTROYING) and not self.__isClickProcessing:
            self.close()
        callback(True)

    def __handleEscape(self):
        if not self.__isClickProcessing:
            self.close()


@adisp.adisp_process
def isHeaderNavigationPossible(callback=None):
    lobbyContext = dependency.instance(ILobbyContext)
    result = yield lobbyContext.isHeaderNavigationPossible()
    callback(result)
