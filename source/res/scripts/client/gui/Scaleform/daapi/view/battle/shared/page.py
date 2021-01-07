# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/page.py
import logging
import typing
import BattleReplay
import aih_constants
from AvatarInputHandler import aih_global_binding
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.shared import crosshair
from gui.Scaleform.daapi.view.battle.shared import indicators
from gui.Scaleform.daapi.view.battle.shared import markers2d
from gui.Scaleform.daapi.view.meta.BattlePageMeta import BattlePageMeta
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES as _ALIASES
from gui.app_loader import settings as app_settings
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import VIEW_COMPONENT_RULE, BATTLE_CTRL_ID
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import dependency, uniprof
from skeletons.gameplay import IGameplayLogic, PlayerEventID
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.shared.events import LoadViewEvent
_logger = logging.getLogger(__name__)

class IComponentsConfig(object):

    def getConfig(self):
        raise NotImplementedError

    def getViewsConfig(self):
        return None


class ComponentsConfig(IComponentsConfig):

    def __init__(self, config=None, viewsConfig=None):
        super(ComponentsConfig, self).__init__()
        self.__config = config or tuple()
        self.__viewsConfig = viewsConfig or tuple()

    def getConfig(self):
        return self.__config

    def getViewsConfig(self):
        return self.__viewsConfig

    def __iadd__(self, other):
        return self.__doAdd(other)

    def __add__(self, other):
        return self.__doAdd(other)

    def __doAdd(self, other):
        return ComponentsConfig(self.__config + other.getConfig(), self.__viewsConfig + other.getViewsConfig())


class _SharedComponentsConfig(ComponentsConfig):

    def __init__(self):
        super(_SharedComponentsConfig, self).__init__(((BATTLE_CTRL_ID.HIT_DIRECTION, (_ALIASES.HIT_DIRECTION,)),), ((_ALIASES.HIT_DIRECTION, indicators.createDamageIndicator),))


_SHARED_COMPONENTS_CONFIG = _SharedComponentsConfig()

class SharedPage(BattlePageMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    gameplay = dependency.descriptor(IGameplayLogic)

    def __init__(self, components=None, external=None):
        super(SharedPage, self).__init__()
        self._isInPostmortem = False
        self._isBattleLoading = False
        self._isVisible = True
        self._blToggling = set()
        self._fsToggling = set()
        self._destroyTimerToggling = set()
        self._isDestroyTimerShown = False
        if external is None:
            external = (crosshair.CrosshairPanelContainer, markers2d.MarkersManager)
        self._external = [ item() for item in external ]
        if components is None:
            components = _SHARED_COMPONENTS_CONFIG
        else:
            components += _SHARED_COMPONENTS_CONFIG
        self.__componentsConfig = components
        return

    def __del__(self):
        _logger.debug('SharedPage is deleted')

    def isGuiVisible(self):
        return self._isVisible

    def reload(self):
        self._stopBattleSession()
        self.__onPostMortemReload()
        self._startBattleSession()
        self.reloadComponents()
        for component in self._external:
            component.startPlugins()
            if self.sessionProvider.isReplayPlaying:
                component.invokeRegisterComponentForReplay()

    @uniprof.regionDecorator(label='avatar.show_gui', scope='enter')
    def _populate(self):
        self._startBattleSession()
        super(SharedPage, self)._populate()
        for component in self._external:
            component.createExternalComponent()
            component.setOwner(self.app)

        self.addListener(events.GameEvent.RADIAL_MENU_CMD, self._handleRadialMenuCmd, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.FULL_STATS, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.FULL_STATS_QUEST_PROGRESS, self._handleToggleFullStatsQuestProgress, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.TOGGLE_GUI, self._handleGUIToggled, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.SHOW_CURSOR, self.__handleShowCursor, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.SHOW_EXTERNAL_COMPONENTS, self.__handleShowExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(events.GameEvent.HIDE_EXTERNAL_COMPONENTS, self.__handleHideExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(events.GameEvent.SHOW_BTN_HINT, self.__handleShowBtnHint, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(events.GameEvent.HIDE_BTN_HINT, self.__handleHideBtnHint, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(events.GameEvent.CALLOUT_DISPLAY_EVENT, self.__handleCalloutDisplayEvent, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.addListener(events.ViewEventType.LOAD_VIEW, self.__handleLobbyEvent, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.DESTROY_TIMERS_PANEL, self.__destroyTimersListener, scope=EVENT_BUS_SCOPE.BATTLE)
        self.gameplay.postStateEvent(PlayerEventID.AVATAR_SHOW_GUI)

    @uniprof.regionDecorator(label='avatar.show_gui', scope='exit')
    def _dispose(self):
        while self._external:
            component = self._external.pop()
            component.close()

        self.removeListener(events.GameEvent.BATTLE_LOADING, self.__handleBattleLoading, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.RADIAL_MENU_CMD, self._handleRadialMenuCmd, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.FULL_STATS, self._handleToggleFullStats, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.FULL_STATS_QUEST_PROGRESS, self._handleToggleFullStatsQuestProgress, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.TOGGLE_GUI, self._handleGUIToggled, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.SHOW_CURSOR, self.__handleShowCursor, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(events.GameEvent.HIDE_CURSOR, self.__handleHideCursor, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(events.GameEvent.SHOW_EXTERNAL_COMPONENTS, self.__handleShowExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(events.GameEvent.HIDE_EXTERNAL_COMPONENTS, self.__handleHideExternals, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(events.GameEvent.SHOW_BTN_HINT, self.__handleShowBtnHint, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(events.GameEvent.HIDE_BTN_HINT, self.__handleHideBtnHint, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(events.GameEvent.CALLOUT_DISPLAY_EVENT, self.__handleCalloutDisplayEvent, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.removeListener(events.ViewEventType.LOAD_VIEW, self.__handleLobbyEvent, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.DESTROY_TIMERS_PANEL, self.__destroyTimersListener, scope=EVENT_BUS_SCOPE.BATTLE)
        self._stopBattleSession()
        super(SharedPage, self)._dispose()

    def _toggleGuiVisible(self):
        self._isVisible = not self._isVisible
        if self._isVisible:
            self.app.containerManager.showContainers(WindowLayer.VIEW)
        else:
            self.app.containerManager.hideContainers(WindowLayer.VIEW)
        self.fireEvent(events.GameEvent(events.GameEvent.GUI_VISIBILITY, {'visible': self._isVisible}), scope=EVENT_BUS_SCOPE.BATTLE)
        avatar_getter.setComponentsVisibility(self._isVisible)

    def _setComponentsVisibility(self, visible=None, hidden=None):
        if visible is None:
            visible = set()
        if hidden is None:
            hidden = set()
        if visible or hidden:
            _logger.debug('Sets components visibility: visible = %r, hidden = %r', visible, hidden)
            self.as_setComponentsVisibilityS(visible, hidden)
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        self.sessionProvider.addViewComponent(alias, viewPy)

    def _onUnregisterFlashComponent(self, viewPy, alias):
        self.sessionProvider.removeViewComponent(alias)

    def _startBattleSession(self):
        if self.sessionProvider.registerViewComponents(*self.__componentsConfig.getConfig()):
            for alias, objFactory in self.__componentsConfig.getViewsConfig():
                self.sessionProvider.addViewComponent(alias, objFactory(), rule=VIEW_COMPONENT_RULE.NONE)

        else:
            _logger.warning('View components can not be added into battle session provider')
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            if ctrl.isInPostmortem:
                self._onPostMortemSwitched(noRespawnPossible=False, respawnAvailable=False)
            self._isInPostmortem = ctrl.isInPostmortem
            ctrl.onPostMortemSwitched += self._onPostMortemSwitched
            ctrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
        aih_global_binding.subscribe(aih_global_binding.BINDING_ID.CTRL_MODE_NAME, self._onAvatarCtrlModeChanged)
        return

    def _stopBattleSession(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self._onPostMortemSwitched
            ctrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
        aih_global_binding.unsubscribe(aih_global_binding.BINDING_ID.CTRL_MODE_NAME, self._onAvatarCtrlModeChanged)
        for alias, _ in self.__componentsConfig.getViewsConfig():
            self.sessionProvider.removeViewComponent(alias)

        for component in self._external:
            component.stopPlugins()

        return

    def _handleRadialMenuCmd(self, event):
        raise NotImplementedError

    def _handleToggleFullStats(self, event):
        raise NotImplementedError

    def _handleToggleFullStatsQuestProgress(self, event):
        raise NotImplementedError

    def _handleGUIToggled(self, event):
        raise NotImplementedError

    def _handleHelpEvent(self, event):
        raise NotImplementedError

    def _onBattleLoadingStart(self):
        self._isBattleLoading = True
        if not self._blToggling:
            self._blToggling = set(self.as_getComponentsVisibilityS())
        self._blToggling.difference_update([_ALIASES.BATTLE_LOADING])
        self._blToggling.add(_ALIASES.BATTLE_MESSENGER)
        hintPanel = self.getComponent(_ALIASES.HINT_PANEL)
        if hintPanel and hintPanel.getActiveHint():
            self._blToggling.add(_ALIASES.HINT_PANEL)
        self._setComponentsVisibility(visible={_ALIASES.BATTLE_LOADING}, hidden=self._blToggling)

    def _onBattleLoadingFinish(self):
        self._isBattleLoading = False
        self._setComponentsVisibility(visible=self._blToggling, hidden={_ALIASES.BATTLE_LOADING})
        self._blToggling.clear()
        for component in self._external:
            component.active(True)

        self.sessionProvider.shared.hitDirection.setVisible(True)

    def _onDestroyTimerStart(self):
        hintPanel = self.getComponent(_ALIASES.HINT_PANEL)
        if hintPanel and hintPanel.getActiveHint():
            self._destroyTimerToggling.add(_ALIASES.HINT_PANEL)
        self._setComponentsVisibility(hidden=self._destroyTimerToggling)
        self._isDestroyTimerShown = True

    def _onDestroyTimerFinish(self):
        self._setComponentsVisibility(visible=self._destroyTimerToggling)
        self._destroyTimerToggling.clear()
        self._isDestroyTimerShown = False

    def _changeCtrlMode(self, ctrlMode):
        if ctrlMode == ctrlMode == aih_constants.CTRL_MODE_NAME.VIDEO:
            self._setComponentsVisibility(hidden={_ALIASES.DAMAGE_PANEL})
        else:
            self._setComponentsVisibility(visible={_ALIASES.DAMAGE_PANEL})

    def __handleLobbyEvent(self, event):
        if event.alias in (VIEW_ALIAS.INGAME_HELP, VIEW_ALIAS.INGAME_DETAILS_HELP):
            self._handleHelpEvent(event)

    def __handleBattleLoading(self, event):
        if event.ctx['isShown']:
            self._onBattleLoadingStart()
        else:
            self._onBattleLoadingFinish()

    def __destroyTimersListener(self, event):
        isShown = event.ctx['shown']
        if isShown is not None:
            if isShown:
                self._onDestroyTimerStart()
            else:
                self._onDestroyTimerFinish()
        return

    def _switchToPostmortem(self):
        alias = _ALIASES.CONSUMABLES_PANEL
        if self.as_isComponentVisibleS(alias):
            self._setComponentsVisibility(hidden={alias})

    def _reloadPostmortem(self):
        alias = _ALIASES.CONSUMABLES_PANEL
        if not self.as_isComponentVisibleS(alias):
            self._setComponentsVisibility(visible={alias})

    def _processHint(self, needShow):
        alias = _ALIASES.HINT_PANEL
        if needShow:
            if self._isBattleLoading:
                self._blToggling.add(alias)
            elif self._isDestroyTimerShown:
                self._destroyTimerToggling.add(alias)
            elif not self.as_isComponentVisibleS(alias):
                self._setComponentsVisibility(visible={alias})
        elif self._isBattleLoading:
            self._blToggling.discard(alias)
        elif self._isDestroyTimerShown:
            self._destroyTimerToggling.discard(alias)
        elif self.as_isComponentVisibleS(alias):
            self._setComponentsVisibility(hidden={alias})

    def _processCallout(self, needShow):
        alias = _ALIASES.CALLOUT_PANEL
        if needShow:
            if self._isBattleLoading:
                self._blToggling.add(alias)
            elif not self.as_isComponentVisibleS(alias):
                self._setComponentsVisibility(visible={alias})
        elif self._isBattleLoading:
            self._blToggling.discard(alias)
        elif self.as_isComponentVisibleS(alias):
            self._setComponentsVisibility(hidden={alias})

    def _canShowPostmortemTips(self):
        return not self.sessionProvider.getCtx().isPlayerObserver() and not BattleReplay.g_replayCtrl.isPlaying

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        if self._canShowPostmortemTips():
            self.as_setPostmortemTipsVisibleS(True)
        if not self.sessionProvider.getCtx().isPlayerObserver():
            self._isInPostmortem = True
            self._switchToPostmortem()

    def __onRespawnBaseMoving(self):
        if not self.sessionProvider.getCtx().isPlayerObserver() and not BattleReplay.g_replayCtrl.isPlaying:
            self.as_setPostmortemTipsVisibleS(False)
            self._isInPostmortem = False

    def __onPostMortemReload(self):
        self._isInPostmortem = False
        self._reloadPostmortem()

    def __handleShowCursor(self, _):
        self.as_toggleCtrlPressFlagS(True)

    def __handleHideCursor(self, _):
        self.as_toggleCtrlPressFlagS(False)

    def _onAvatarCtrlModeChanged(self, ctrlMode):
        if not self._isVisible or self._fsToggling or self._blToggling:
            return
        self._changeCtrlMode(ctrlMode)

    def __handleShowExternals(self, _):
        for component in self._external:
            component.active(True)

        self.sessionProvider.shared.hitDirection.setVisible(True)

    def __handleHideExternals(self, _):
        for component in self._external:
            component.active(False)

        self.sessionProvider.shared.hitDirection.setVisible(False)

    def __handleShowBtnHint(self, _):
        self._processHint(True)

    def __handleHideBtnHint(self, _):
        self._processHint(False)

    def __handleCalloutDisplayEvent(self, event):
        self._processCallout(needShow=event.ctx['isDown'])


class BattlePageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self, *aliases):
        listeners = [ (alias, self._loadPage) for alias in aliases ]
        super(BattlePageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def _loadPage(self, event):
        page = self.findViewByAlias(WindowLayer.VIEW, event.name)
        if page is not None:
            page.reload()
        else:
            self.loadViewBySharedEvent(event)
        return
