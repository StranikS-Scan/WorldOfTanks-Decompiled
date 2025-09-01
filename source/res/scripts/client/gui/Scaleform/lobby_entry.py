# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/lobby_entry.py
from collections import namedtuple
import typing
import BigWorld
from PlayerEvents import g_playerEvents
from frameworks.state_machine import BaseStateObserver
from frameworks.wulf import WindowLayer
from frameworks.wulf.gui_constants import ShowingStatus, ViewFlags
from gui.Scaleform.framework import g_entitiesFactories, ScopeTemplates
from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
from gui.lobby_state_machine.states import UntrackedState
from gui.shared.events import NavigationEvent, GUICommonEvent
from gui.shared.system_factory import collectLobbyTooltipsBuilders
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.Scaleform.daapi.settings.config import ADVANCED_COMPLEX_TOOLTIPS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.tooltip_mgr import ToolTip
from gui.Scaleform.framework.ui_logging_manager import UILoggerManager
from gui.Scaleform.framework.application import AppEntry
from gui.Scaleform.framework.managers import LoaderManager, ContainerManager
from gui.Scaleform.framework.managers.CacheManager import CacheManager
from gui.Scaleform.framework.managers.ImageManager import ImageManager
from gui.Scaleform.framework.managers.TutorialManager import ScaleformTutorialManager
from gui.Scaleform.framework.managers.containers import DefaultContainer
from gui.Scaleform.framework.managers.containers import PopUpContainer
from gui.Scaleform.framework.managers.context_menu import ContextMenuManager
from gui.Scaleform.framework.managers.event_logging import EventLogManager
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.framework.managers.optimization_manager import GraphicsOptimizationManager
from gui.Scaleform.managers.ColorSchemeManager import ColorSchemeManager
from gui.Scaleform.managers.cursor_mgr import CursorManager
from gui.Scaleform.managers.GameInputMgr import GameInputMgr
from gui.Scaleform.managers.GlobalVarsManager import GlobalVarsManager
from gui.Scaleform.managers.PopoverManager import PopoverManager
from gui.Scaleform.required_libraries_config import LOBBY_REQUIRED_LIBRARIES
from gui.sounds.SoundManager import SoundManager
from gui.Scaleform.managers.TweenSystem import TweenManager
from gui.Scaleform.managers.UtilsManager import UtilsManager
from gui.Scaleform.managers.voice_chat import LobbyVoiceChatManager
from gui.impl.gen import R
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.subhangar.subhangar_observer import SubhangarObserver
from helpers import uniprof, dependency
from skeletons.gui.app_loader import GuiGlobalSpaceID
from logging import getLogger
_logger = getLogger(__name__)

def getLobbyStateMachine():
    from skeletons.gui.app_loader import IAppLoader
    appLoader = dependency.instance(IAppLoader)
    app = appLoader.getApp()
    return app.stateMachine if app else None


_UntrackedStateForwardedParams = namedtuple('_UntrackedStateForwardedParams', ['loadParams', 'args', 'kwargs'])

class _UntrackedStateObserver(BaseStateObserver):

    def isObservingState(self, state):
        return isinstance(state, UntrackedState)

    def onEnterState(self, state, event):
        from skeletons.gui.app_loader import IAppLoader
        from skeletons.gui.impl import IGuiLoader
        app = dependency.instance(IAppLoader).getApp()
        windowsManager = dependency.instance(IGuiLoader).windowsManager
        viewKey = event.params[UntrackedState.LOAD_PARAMS_KEY].loadParams.viewKey
        view = app.containerManager.getViewByKey(viewKey)
        if view is None and isinstance(viewKey.alias, int):
            view = windowsManager.getViewByLayoutID(viewKey.alias)
        showingStatus = ShowingStatus.HIDDEN
        if view is not None:
            window = view.getParentWindow()
            if window is not None:
                showingStatus = window.showingStatus
        viewAlreadyOpen = showingStatus in (ShowingStatus.SHOWING, ShowingStatus.SHOWN)
        if not viewAlreadyOpen:
            app.loadView(event.params[UntrackedState.LOAD_PARAMS_KEY])
        return


class LobbyEntry(AppEntry):

    def __init__(self, appNS, ctrlModeFlags):
        super(LobbyEntry, self).__init__(R.entries.lobby(), appNS, ctrlModeFlags)
        self.__stateMachine = LobbyStateMachine()
        self.__untrackedStateObserver = _UntrackedStateObserver()
        self.__subhangarObserver = None
        return

    @property
    def stateMachine(self):
        return self.__stateMachine

    @property
    def waitingManager(self):
        return self.__getWaitingFromContainer()

    @uniprof.regionDecorator(label='gui.lobby', scope='enter')
    def afterCreate(self):
        g_eventBus.addListener(GUICommonEvent.LOBBY_VIEW_LOADING, self.__initLSM)
        g_playerEvents.onAccountBecomeNonPlayer += self.__finiLSM
        super(LobbyEntry, self).afterCreate()

    @uniprof.regionDecorator(label='gui.lobby', scope='exit')
    def beforeDelete(self):
        from gui.Scaleform.Waiting import Waiting
        Waiting.close()
        g_playerEvents.onAccountBecomeNonPlayer -= self.__finiLSM
        g_eventBus.removeListener(GUICommonEvent.LOBBY_VIEW_LOADING, self.__initLSM)
        super(LobbyEntry, self).beforeDelete()

    def loadView(self, loadParams, *args, **kwargs):

        def getViewScopeAndLayer(loadParams, *args, **kwargs):
            settings = g_entitiesFactories.getSettings(loadParams.viewKey.alias)
            scope = settings.scope if settings else loadParams.scope
            if settings:
                layer = settings.layer
            else:
                _logger.info('Fake creating view of class %s for LSM to get the layer', loadParams.viewClass.__name__)
                layoutID = loadParams.viewKey.alias
                view = loadParams.viewClass(layoutID, *args, **kwargs)
                layer = ViewFlags.getViewType(view.viewFlags)
                view.destroyWindow()
            if scope == ScopeTemplates.VIEW_SCOPE and layer == WindowLayer.SUB_VIEW:
                scope = ScopeTemplates.LOBBY_SUB_SCOPE
            return (scope, layer)

        if isinstance(loadParams, _UntrackedStateForwardedParams):
            super(LobbyEntry, self).loadView(loadParams.loadParams, *loadParams.args, **loadParams.kwargs)
            return
        matchingState = self.__stateMachine.getStateByViewKey(loadParams.viewKey)
        if matchingState:
            if not self.__stateMachine.isStateEntered(matchingState.getStateID()):
                _logger.warning('View "%s" has a matching state %s, navigate to it instead of direct load. Attempting to extract params and navigate to the matching state.', loadParams.viewKey, matchingState)
                params = dict(kwargs)
                for arg in args:
                    if isinstance(arg, dict):
                        params.update(arg)

                g_eventBus.handleEvent(NavigationEvent(matchingState.getStateID(), params), EVENT_BUS_SCOPE.LOBBY)
                return
        else:
            scope, layer = getViewScopeAndLayer(loadParams, *args, **kwargs)
            untrackedState = self.__stateMachine.getUntrackedStateFor(scope, layer)
            if untrackedState:
                _logger.info('No matching state for view "%s", navigating to untracked state', loadParams.viewKey)
                params = {UntrackedState.LOAD_PARAMS_KEY: _UntrackedStateForwardedParams(loadParams, args, kwargs)}
                self.__stateMachine.post(NavigationEvent(untrackedState.getStateID(), params=params))
                return
        super(LobbyEntry, self).loadView(loadParams, *args, **kwargs)

    def _createLoaderManager(self):
        return LoaderManager(self.proxy)

    def _createContainerManager(self):
        return ContainerManager(self._loaderMgr, DefaultContainer(WindowLayer.HIDDEN_SERVICE_LAYOUT), DefaultContainer(WindowLayer.MARKER), DefaultContainer(WindowLayer.VIEW), DefaultContainer(WindowLayer.CURSOR), DefaultContainer(WindowLayer.WAITING), PopUpContainer(WindowLayer.WINDOW), PopUpContainer(WindowLayer.FULLSCREEN_WINDOW), PopUpContainer(WindowLayer.TOP_WINDOW), PopUpContainer(WindowLayer.OVERLAY), DefaultContainer(WindowLayer.SERVICE_LAYOUT))

    def _createToolTipManager(self):
        builders = collectLobbyTooltipsBuilders()
        tooltip = ToolTip(builders, ADVANCED_COMPLEX_TOOLTIPS, GuiGlobalSpaceID.BATTLE_LOADING)
        tooltip.setEnvironment(self)
        return tooltip

    def _createGlobalVarsManager(self):
        return GlobalVarsManager()

    def _createSoundManager(self):
        return SoundManager()

    def _createCursorManager(self):
        cursor = CursorManager()
        cursor.setEnvironment(self)
        return cursor

    def _createColorSchemeManager(self):
        return ColorSchemeManager()

    def _createEventLogMgr(self):
        return EventLogManager(False)

    def _createContextMenuManager(self):
        return ContextMenuManager(self.proxy)

    def _createPopoverManager(self):
        return PopoverManager(EVENT_BUS_SCOPE.LOBBY)

    def _createVoiceChatManager(self):
        return LobbyVoiceChatManager(self.proxy)

    def _createUtilsManager(self):
        return UtilsManager()

    def _createTweenManager(self):
        return TweenManager()

    def _createGameInputManager(self):
        return GameInputMgr()

    def _createCacheManager(self):
        return CacheManager()

    def _createImageManager(self):
        return ImageManager()

    def _createUILoggerManager(self):
        return UILoggerManager()

    def _createTutorialManager(self):
        return ScaleformTutorialManager()

    def _createGraphicsOptimizationManager(self):
        return GraphicsOptimizationManager()

    def _setup(self):
        self.movie.backgroundAlpha = 0.0
        self.movie.setFocused(SCALEFORM_SWF_PATH_V3)
        BigWorld.wg_setRedefineKeysMode(True)

    def _loadWaiting(self):
        self._containerMgr.load(SFViewLoadParams(VIEW_ALIAS.WAITING))

    def _getRequiredLibraries(self):
        return LOBBY_REQUIRED_LIBRARIES

    def __initLSM(self, _):
        if self.__stateMachine.isRunning():
            return
        self.__stateMachine.configure()
        self.__stateMachine.connect(self.__untrackedStateObserver)
        self.__stateMachine.start()
        self.__subhangarObserver = SubhangarObserver(self.__stateMachine)
        self.__stateMachine.connect(self.__subhangarObserver)

    def __finiLSM(self):
        self.__stateMachine.stop()
        self.__subhangarObserver = None
        return

    def __getWaitingFromContainer(self):
        return self._containerMgr.getView(WindowLayer.WAITING) if self._containerMgr is not None else None
