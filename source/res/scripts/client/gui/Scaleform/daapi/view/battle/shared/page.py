# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/page.py
import logging
import typing
from account_helpers.settings_core.settings_constants import SPGAim
import BigWorld
import BattleReplay
import aih_constants
from AvatarInputHandler import aih_global_binding
from Event import EventsSubscriber
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.shared import crosshair, kill_cam_sound_player
from gui.Scaleform.daapi.view.battle.shared import indicators
from gui.Scaleform.daapi.view.battle.shared import markers2d
from gui.Scaleform.daapi.view.meta.BattlePageMeta import BattlePageMeta
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES as _ALIASES
from gui.app_loader import settings as app_settings
from gui.battle_control import avatar_getter, event_dispatcher
from gui.battle_control.battle_constants import VIEW_COMPONENT_RULE, BATTLE_CTRL_ID, CROSSHAIR_VIEW_ID
from gui.battle_control.controllers.spectator_ctrl import SPECTATOR_MODE
from gui.shared import EVENT_BUS_SCOPE, events
from helpers import dependency, uniprof
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gameplay import IGameplayLogic, PlayerEventID
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.prebattle_hints.controller import IPrebattleHintsController
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

    def overrideViews(self, override):
        newConfig = []
        for componentID, component in self.__viewsConfig:
            newConfig.append((componentID, override.get(componentID, component)))

        self.__viewsConfig = tuple(newConfig)

    def __iadd__(self, other):
        return self.__doAdd(other)

    def __add__(self, other):
        return self.__doAdd(other)

    def __doAdd(self, other):
        return ComponentsConfig(self.__config + other.getConfig(), self.__viewsConfig + other.getViewsConfig())


class _SharedComponentsConfig(ComponentsConfig):

    def __init__(self):
        super(_SharedComponentsConfig, self).__init__(((BATTLE_CTRL_ID.BATTLE_NOTIFIER, (_ALIASES.BATTLE_NOTIFIER,)),
         (BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS, (_ALIASES.BATTLE_NOTIFIER,)),
         (BATTLE_CTRL_ID.PREBATTLE_SETUPS_CTRL, (_ALIASES.DUAL_GUN_PANEL,)),
         (BATTLE_CTRL_ID.KILL_CAM_CTRL, (_ALIASES.KILL_CAM_SOUND_PLAYER,))), ((_ALIASES.KILL_CAM_SOUND_PLAYER, kill_cam_sound_player.KillCamSoundPlayer),))


class _HitDirectionComponentsConfig(ComponentsConfig):

    def __init__(self):
        super(_HitDirectionComponentsConfig, self).__init__(((BATTLE_CTRL_ID.HIT_DIRECTION, (_ALIASES.PREDICTION_INDICATOR, _ALIASES.HIT_DIRECTION)),), ((_ALIASES.PREDICTION_INDICATOR, indicators.createPredictionIndicator), (_ALIASES.HIT_DIRECTION, indicators.createDamageIndicator)))


_SHARED_COMPONENTS_CONFIG = _SharedComponentsConfig()
_HIT_DIRECTION_COMPONENTS_CONFIG = _HitDirectionComponentsConfig()

class SharedPage(BattlePageMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    gameplay = dependency.descriptor(IGameplayLogic)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __prebattleHints = dependency.descriptor(IPrebattleHintsController)

    def __init__(self, components=None, external=None):
        super(SharedPage, self).__init__()
        self._isInPostmortem = False
        self._isBattleLoading = False
        self._isVisible = True
        self._blToggling = set()
        self._fsToggling = set()
        self._deathCamToggling = set()
        self._spectatorModeToggling = set()
        self._destroyTimerToggling = set()
        self._isDestroyTimerShown = False
        if external is None:
            external = (crosshair.CrosshairPanelContainer, markers2d.MarkersManager, markers2d.KillCamMarkersManager)
        self._external = [ item() for item in external ]
        if components is None:
            components = _SHARED_COMPONENTS_CONFIG
        else:
            config = _SHARED_COMPONENTS_CONFIG.getConfig()
            overridedViewAliases = tuple((alias for alias, _ in components.getViewsConfig()))
            viewConfig = tuple(((alias, obj) for alias, obj in _SHARED_COMPONENTS_CONFIG.getViewsConfig() if alias not in overridedViewAliases))
            sharedComponents = ComponentsConfig(config, viewConfig)
            components += sharedComponents
        components = self._addDefaultHitDirectionController(components)
        self.__componentsConfig = components
        self._battleSessionES = EventsSubscriber()
        return

    def __del__(self):
        _logger.debug('SharedPage is deleted')

    def isGuiVisible(self):
        return self._isVisible

    def reload(self):
        self._stopBattleSession()
        self._onPostMortemReload()
        self._startBattleSession()
        self.reloadComponents()
        for component in self._external:
            component.startPlugins()
            if self.sessionProvider.isReplayPlaying:
                component.invokeRegisterComponentForReplay()

    def setComponentsVisibilityWithFade(self, visible=None, hidden=None):
        viewsToShow = {view for view in visible if view in self.components} if visible else None
        viewsToHide = {view for view in hidden if view in self.components} if hidden else None
        if self._fsToggling:
            if viewsToShow:
                self._fsToggling.update(viewsToShow)
            if viewsToHide:
                self._fsToggling.difference_update(viewsToHide)
        if viewsToShow:
            viewsToShow.difference_update(self._fsToggling)
        if viewsToHide:
            viewsToHide.difference_update(self._fsToggling)
        self._setComponentsVisibilityWithFade(visible=viewsToShow, hidden=viewsToHide)
        return

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
        self.addListener(events.GameEvent.FULL_STATS_PERSONAL_RESERVES, self._handleToggleFullStatsPersonalReserves, scope=EVENT_BUS_SCOPE.BATTLE)
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
        self.addListener(events.DeathCamEvent.DEATH_CAM_HIDDEN, self.__handleDeathCamHiddenEvent, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.DeathCamEvent.DEATH_CAM_SPECTATOR_MODE, self.__handleDeathCamSpectatorModeEvent, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.TOGGLE_DEBUG_PIERCING_PANEL, self.__toggleDebugPiercingPanel, scope=EVENT_BUS_SCOPE.BATTLE)
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
        self.removeListener(events.GameEvent.FULL_STATS_PERSONAL_RESERVES, self._handleToggleFullStatsPersonalReserves, scope=EVENT_BUS_SCOPE.BATTLE)
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
        self.removeListener(events.DeathCamEvent.DEATH_CAM_HIDDEN, self.__handleDeathCamHiddenEvent, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.DeathCamEvent.DEATH_CAM_SPECTATOR_MODE, self.__handleDeathCamSpectatorModeEvent, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.TOGGLE_DEBUG_PIERCING_PANEL, self.__toggleDebugPiercingPanel, scope=EVENT_BUS_SCOPE.BATTLE)
        self._stopBattleSession()
        super(SharedPage, self)._dispose()

    def _addDefaultHitDirectionController(self, components):
        if BATTLE_CTRL_ID.HIT_DIRECTION not in dict(components.getConfig()):
            components += _HIT_DIRECTION_COMPONENTS_CONFIG
        return components

    def _toggleGuiVisible(self):
        self._isVisible = not self._isVisible
        if self._isVisible:
            self.app.containerManager.showContainers((WindowLayer.VIEW,))
        else:
            self.app.containerManager.hideContainers((WindowLayer.VIEW,))
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

    def _setComponentsVisibilityWithFade(self, visible=None, hidden=None):
        if visible is None:
            visible = set()
        if hidden is None:
            hidden = set()
        if visible or hidden:
            _logger.debug('Sets components visibility with fade: visible = %r, hidden = %r', visible, hidden)
            self.as_setComponentsVisibilityWithFadeS(visible, hidden)
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
            self._battleSessionES.subscribeToEvent(ctrl.onPostMortemSwitched, self._onPostMortemSwitched)
            self._battleSessionES.subscribeToEvent(ctrl.onRespawnBaseMoving, self._onRespawnBaseMoving)
        killCamCtrl = self.sessionProvider.shared.killCamCtrl
        if killCamCtrl:
            killCamCtrl.onKillCamModeStateChanged += self.__onKillCamStateChanged
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            self._battleSessionES.subscribeToEvent(crosshairCtrl.onCrosshairViewChanged, self.__onCrosshairViewChanged)
            self.__onCrosshairViewChanged(crosshairCtrl.getViewID())
        self._battleSessionES.subscribeToEvent(self.__settingsCore.onSettingsChanged, self.__onSettingsChanged)
        if not self.__settingsCore.isReady:
            self._battleSessionES.subscribeToEvent(self.__settingsCore.onSettingsReady, self.__onSettingsReady)
        aih_global_binding.subscribe(aih_global_binding.BINDING_ID.CTRL_MODE_NAME, self._onAvatarCtrlModeChanged)
        return

    def _stopBattleSession(self):
        self._battleSessionES.unsubscribeFromAllEvents()
        killCamCtrl = self.sessionProvider.shared.killCamCtrl
        if killCamCtrl:
            killCamCtrl.onKillCamModeStateChanged -= self.__onKillCamStateChanged
        aih_global_binding.unsubscribe(aih_global_binding.BINDING_ID.CTRL_MODE_NAME, self._onAvatarCtrlModeChanged)
        for alias, _ in self.__componentsConfig.getViewsConfig():
            self.sessionProvider.removeViewComponent(alias)

        for component in self._external:
            component.stopPlugins()

    def _handleRadialMenuCmd(self, event):
        raise NotImplementedError

    def _handleToggleFullStats(self, event):
        raise NotImplementedError

    def _handleToggleFullStatsQuestProgress(self, event):
        raise NotImplementedError

    def _handleToggleFullStatsPersonalReserves(self, event):
        raise NotImplementedError

    def _handleGUIToggled(self, event):
        raise NotImplementedError

    def _handleHelpEvent(self, event):
        raise NotImplementedError

    def _hasBattleMessenger(self):
        return True

    def _onBattleLoadingStart(self):
        self._isBattleLoading = True
        if not self._blToggling:
            self._blToggling = set(self.as_getComponentsVisibilityS())
        if self._hasBattleMessenger() and not avatar_getter.isObserverSeesAll():
            self._blToggling.add(_ALIASES.BATTLE_MESSENGER)
        hintPanel = self.getComponent(_ALIASES.HINT_PANEL)
        if hintPanel and hintPanel.getActiveHint():
            self._blToggling.add(_ALIASES.HINT_PANEL)
        visible, additionalToggling = set(), set()
        if self.getComponent(_ALIASES.PREBATTLE_AMMUNITION_PANEL) is not None:
            visible.add(_ALIASES.PREBATTLE_AMMUNITION_PANEL)
            additionalToggling.add(_ALIASES.PREBATTLE_AMMUNITION_PANEL)
        if not self.__prebattleHints.isEnabledForCurrentBattleSession():
            additionalToggling.add(_ALIASES.BATTLE_LOADING)
            visible.add(_ALIASES.BATTLE_LOADING)
        self._blToggling.difference_update(additionalToggling)
        self._setComponentsVisibility(visible=visible, hidden=self._blToggling)
        self._blToggling.update(additionalToggling)
        return

    def _onBattleLoadingFinish(self):
        self._isBattleLoading = False
        self._setComponentsVisibility(visible=self._blToggling, hidden={_ALIASES.BATTLE_LOADING})
        self._blToggling.clear()
        for component in self._external:
            component.active(True)

        if self.sessionProvider.shared.hitDirection is not None:
            self.sessionProvider.shared.hitDirection.setVisible(True)
        return

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

    def __isOptionalComponentVisible(self, alias):
        return self.getComponent(alias) is not None and self.as_isComponentVisibleS(alias)

    def __handleBattleLoading(self, event):
        if self.__isOptionalComponentVisible(_ALIASES.DEATH_CAM_HUD):
            return
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

    def __toggleDebugPiercingPanel(self, event):
        self.as_togglePiercingPanelS()

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
        self.as_onPostmortemActiveS(True)
        if not self.sessionProvider.getCtx().isPlayerObserver():
            self._isInPostmortem = True
            self._switchToPostmortem()

    def _onRespawnBaseMoving(self):
        if self._canShowPostmortemTips():
            self.as_onPostmortemActiveS(False)
            self._isInPostmortem = False

    def _onPostMortemReload(self):
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

        if self.sessionProvider.shared.hitDirection is not None:
            self.sessionProvider.shared.hitDirection.setVisible(True)
        return

    def __handleHideExternals(self, _):
        for component in self._external:
            component.active(False)

        if self.sessionProvider.shared.hitDirection is not None:
            self.sessionProvider.shared.hitDirection.setVisible(False)
        return

    def __handleShowBtnHint(self, _):
        self._processHint(True)

    def __handleHideBtnHint(self, _):
        self._processHint(False)

    def __handleCalloutDisplayEvent(self, event):
        self._processCallout(needShow=event.ctx['isDown'])

    def __onKillCamStateChanged(self, state, _):
        if state is events.DeathCamEvent.State.INACTIVE:
            self._onKillCamCtrlModeActivated()
        if state is events.DeathCamEvent.State.STARTING:
            self._onKillCamSimulationStart()
        elif state is events.DeathCamEvent.State.ACTIVE:
            self._setComponentsVisibility(visible={_ALIASES.DEATH_CAM_HUD})
        elif state is events.DeathCamEvent.State.FINISHED:
            self._onKillCamSimulationFinish()

    def _onKillCamCtrlModeActivated(self):
        event_dispatcher.killHelpView()

    def _onKillCamSimulationStart(self):
        self._deathCamToggling = set(self.as_getComponentsVisibilityS())
        self._deathCamToggling.discard(_ALIASES.DEATH_CAM_HUD)
        avatar = BigWorld.player()
        isSimplifiedDC = avatar.isSimpleDeathCam() if avatar else False
        if isSimplifiedDC:
            self._deathCamToggling.discard(_ALIASES.POSTMORTEM_PANEL)
        self._setComponentsVisibility(hidden=self._deathCamToggling)

    def _onKillCamSimulationFinish(self):
        if self.getComponent(_ALIASES.DEATH_CAM_HUD) is not None:
            self._setComponentsVisibility(visible=self._deathCamToggling or None, hidden={_ALIASES.DEATH_CAM_HUD})
        self._deathCamToggling.clear()
        return

    def __onCrosshairViewChanged(self, viewID):
        artyShotIndicatorVisible = self.__settingsCore.isReady and viewID in (CROSSHAIR_VIEW_ID.STRATEGIC,) and self.__settingsCore.getSetting(SPGAim.SHOTS_RESULT_INDICATOR)
        self.__setArtyShotIndicatorFlag(artyShotIndicatorVisible)

    def __handleDeathCamHiddenEvent(self, _):
        self._setComponentsVisibility(hidden={_ALIASES.DEATH_CAM_HUD})

    def __handleDeathCamSpectatorModeEvent(self, event):
        if event.ctx['mode']:
            mode = event.ctx['mode']
            if mode == SPECTATOR_MODE.NONE:
                return
            if mode == SPECTATOR_MODE.FREECAM:
                self._spectatorModeToggling = set(self.as_getComponentsVisibilityS())
                self._setComponentsVisibility(hidden={_ALIASES.DAMAGE_PANEL, _ALIASES.POSTMORTEM_PANEL, _ALIASES.BATTLE_DAMAGE_LOG_PANEL})
            else:
                self._onPostMortemSwitched(False, False)

    def __onSettingsChanged(self, diff):
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if SPGAim.SHOTS_RESULT_INDICATOR in diff and crosshairCtrl is not None:
            viewID = crosshairCtrl.getViewID()
            artyShotIndicatorVisible = viewID in (CROSSHAIR_VIEW_ID.STRATEGIC,) and self.__settingsCore.getSetting(SPGAim.SHOTS_RESULT_INDICATOR)
            self.__setArtyShotIndicatorFlag(artyShotIndicatorVisible)
        return

    def __onSettingsReady(self):
        self.__settingsCore.onSettingsReady -= self.__onSettingsReady
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl is not None:
            viewID = crosshairCtrl.getViewID()
            artyShotIndicatorVisible = viewID in (CROSSHAIR_VIEW_ID.STRATEGIC,) and self.__settingsCore.getSetting(SPGAim.SHOTS_RESULT_INDICATOR)
            self.__setArtyShotIndicatorFlag(artyShotIndicatorVisible)
        return

    def __setArtyShotIndicatorFlag(self, isVisible):
        self.as_setArtyShotIndicatorFlagS(isVisible)


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
