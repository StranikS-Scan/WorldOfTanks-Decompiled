# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/page.py
from gui.Scaleform.daapi.view.battle.classic.page import DynamicAliases as ClassicDynAliases
from gui.Scaleform.daapi.view.battle.shared.start_countdown_sound_player import StartCountdownSoundPlayer
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.Scaleform.daapi.view.meta.EpicBattlePageMeta import EpicBattlePageMeta
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.shared import EVENT_BUS_SCOPE, events
from gui.Scaleform.genConsts.EPIC_CONSTS import EPIC_CONSTS
from gui.Scaleform.daapi.view.battle.epic import markers2d
from gui.Scaleform.daapi.view.battle.shared import crosshair
from gui.Scaleform.daapi.view.battle.shared import period_music_listener
from gui.Scaleform.daapi.view.battle.epic import finish_sound_player, drone_music_player
from PlayerEvents import g_playerEvents
from gui.Scaleform.managers.battle_input import BattleGUIKeyHandler
import CommandMapping
from constants import ARENA_PERIOD
import BigWorld
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from shared_utils import CONST_CONTAINER

class DynamicAliases(CONST_CONTAINER):
    EPIC_FINISH_SOUND_PLAYER = 'epicFinishSoundPlayer'
    EPIC_DRONE_MUSIC_PLAYER = 'epicDroneMusicPlayer'
    PERIOD_MUSIC_LISTENER = 'periodMusicListener'


class _EpicBattleComponentsConfig(ComponentsConfig):

    def __init__(self):
        super(_EpicBattleComponentsConfig, self).__init__(((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
           BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
           DynamicAliases.EPIC_DRONE_MUSIC_PLAYER,
           DynamicAliases.PERIOD_MUSIC_LISTENER,
           ClassicDynAliases.PREBATTLE_TIMER_SOUND_PLAYER)),
         (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
         (BATTLE_CTRL_ID.RESPAWN, (BATTLE_VIEW_ALIASES.EPIC_RESPAWN_VIEW,)),
         (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.EPIC_OVERVIEW_MAP_SCREEN, BATTLE_VIEW_ALIASES.MINIMAP)),
         (BATTLE_CTRL_ID.SPECTATOR, (BATTLE_VIEW_ALIASES.EPIC_SPECTATOR_VIEW,)),
         (BATTLE_CTRL_ID.GAME_NOTIFICATIONS, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,)),
         (BATTLE_CTRL_ID.EPIC_MISSIONS, (BATTLE_VIEW_ALIASES.EPIC_MISSIONS_PANEL,)),
         (BATTLE_CTRL_ID.TEAM_BASES, (BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, DynamicAliases.EPIC_DRONE_MUSIC_PLAYER)),
         (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.EPIC_DRONE_MUSIC_PLAYER,)),
         (BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS, (DynamicAliases.EPIC_DRONE_MUSIC_PLAYER,)),
         (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,))), ((DynamicAliases.PERIOD_MUSIC_LISTENER, period_music_listener.PeriodMusicListener), (DynamicAliases.EPIC_DRONE_MUSIC_PLAYER, drone_music_player.EpicDroneMusicPlayer), (ClassicDynAliases.PREBATTLE_TIMER_SOUND_PLAYER, StartCountdownSoundPlayer)))


EPIC_BATTLE_CLASSIC_CONFIG = _EpicBattleComponentsConfig()
_EPIC_BATTLE_CLASSICS_COMPONENTS = EPIC_BATTLE_CLASSIC_CONFIG
_EPIC_BATTLE_EXTENDED_COMPONENTS = EPIC_BATTLE_CLASSIC_CONFIG + ComponentsConfig(config=((BATTLE_CTRL_ID.ARENA_PERIOD, (DynamicAliases.EPIC_FINISH_SOUND_PLAYER,)), (BATTLE_CTRL_ID.TEAM_BASES, (DynamicAliases.EPIC_FINISH_SOUND_PLAYER,)), (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.EPIC_FINISH_SOUND_PLAYER,))), viewsConfig=((DynamicAliases.EPIC_FINISH_SOUND_PLAYER, finish_sound_player.EpicFinishSoundPlayer),))

class PageStates(object):
    NONE = -1
    GAME = 0
    LOADING = 1
    TABSCREEN = 2
    OVERVIEWMAP = 3
    RADIAL = 4
    RESPAWN = 5
    COUNTDOWN = 6
    SPECTATOR_FREE = 7
    SPECTATOR_FOLLOW = 8
    SPECTATOR_DEATHCAM = 9
    GAME_OVER = 10


_NEVER_HIDE = {BATTLE_VIEW_ALIASES.SIXTH_SENSE, BATTLE_VIEW_ALIASES.RIBBONS_PANEL, BATTLE_VIEW_ALIASES.DAMAGE_INFO_PANEL}
_GAME_UI = {BATTLE_VIEW_ALIASES.VEHICLE_ERROR_MESSAGES,
 BATTLE_VIEW_ALIASES.DEBUG_PANEL,
 BATTLE_VIEW_ALIASES.PLAYER_MESSAGES,
 BATTLE_VIEW_ALIASES.VEHICLE_MESSAGES,
 BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,
 BATTLE_VIEW_ALIASES.EPIC_SCORE_PANEL,
 BATTLE_VIEW_ALIASES.BATTLE_TIMER,
 BATTLE_VIEW_ALIASES.BATTLE_MESSENGER,
 BATTLE_VIEW_ALIASES.MINIMAP,
 BATTLE_VIEW_ALIASES.DAMAGE_PANEL,
 BATTLE_VIEW_ALIASES.EPIC_REINFORCEMENT_PANEL,
 BATTLE_VIEW_ALIASES.EPIC_MISSIONS_PANEL,
 BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,
 BATTLE_VIEW_ALIASES.RECOVERY_PANEL,
 BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR,
 BATTLE_VIEW_ALIASES.DESTROY_TIMERS_PANEL,
 BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL,
 BATTLE_VIEW_ALIASES.SUPER_PLATOON_PANEL,
 BATTLE_VIEW_ALIASES.EPIC_INGAME_RANK,
 BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL,
 BATTLE_VIEW_ALIASES.DUAL_GUN_PANEL}
_SPECTATOR_UI = {BATTLE_VIEW_ALIASES.EPIC_SPECTATOR_VIEW,
 BATTLE_VIEW_ALIASES.DEBUG_PANEL,
 BATTLE_VIEW_ALIASES.PLAYER_MESSAGES,
 BATTLE_VIEW_ALIASES.EPIC_SCORE_PANEL,
 BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,
 BATTLE_VIEW_ALIASES.MINIMAP,
 BATTLE_VIEW_ALIASES.BATTLE_TIMER,
 BATTLE_VIEW_ALIASES.SUPER_PLATOON_PANEL,
 BATTLE_VIEW_ALIASES.BATTLE_MESSENGER}
_ENABLE_CONTROL_MODE = {PageStates.TABSCREEN,
 PageStates.RESPAWN,
 PageStates.RADIAL,
 PageStates.LOADING}
_PAGE_STATE_TO_CONTROL_PARAMS = {PageStates.TABSCREEN: (BATTLE_VIEW_ALIASES.FULL_STATS, True, True),
 PageStates.RESPAWN: (BATTLE_VIEW_ALIASES.EPIC_RESPAWN_VIEW, True, True),
 PageStates.RADIAL: (BATTLE_VIEW_ALIASES.RADIAL_MENU, False, False),
 PageStates.LOADING: (BATTLE_VIEW_ALIASES.BATTLE_LOADING, True, True)}
_STATE_TO_UI = {PageStates.GAME: _GAME_UI,
 PageStates.LOADING: {BATTLE_VIEW_ALIASES.BATTLE_LOADING, BATTLE_VIEW_ALIASES.EPIC_DEPLOYMENT_MAP},
 PageStates.TABSCREEN: {BATTLE_VIEW_ALIASES.FULL_STATS, BATTLE_VIEW_ALIASES.DEBUG_PANEL, BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL},
 PageStates.OVERVIEWMAP: {BATTLE_VIEW_ALIASES.EPIC_DEPLOYMENT_MAP,
                          BATTLE_VIEW_ALIASES.EPIC_OVERVIEW_MAP_SCREEN,
                          BATTLE_VIEW_ALIASES.EPIC_SCORE_PANEL,
                          BATTLE_VIEW_ALIASES.BATTLE_TIMER,
                          BATTLE_VIEW_ALIASES.DEBUG_PANEL,
                          BATTLE_VIEW_ALIASES.BATTLE_MESSENGER,
                          BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL},
 PageStates.RADIAL: _GAME_UI.union({BATTLE_VIEW_ALIASES.RADIAL_MENU}),
 PageStates.RESPAWN: {BATTLE_VIEW_ALIASES.EPIC_RESPAWN_VIEW,
                      BATTLE_VIEW_ALIASES.DEBUG_PANEL,
                      BATTLE_VIEW_ALIASES.EPIC_DEPLOYMENT_MAP,
                      BATTLE_VIEW_ALIASES.BATTLE_MESSENGER,
                      BATTLE_VIEW_ALIASES.BATTLE_TIMER},
 PageStates.COUNTDOWN: _GAME_UI.difference({BATTLE_VIEW_ALIASES.EPIC_REINFORCEMENT_PANEL, BATTLE_VIEW_ALIASES.EPIC_MISSIONS_PANEL, BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL}).union({BATTLE_VIEW_ALIASES.PREBATTLE_TIMER}),
 PageStates.SPECTATOR_DEATHCAM: _SPECTATOR_UI.union({BATTLE_VIEW_ALIASES.DAMAGE_PANEL,
                                 BATTLE_VIEW_ALIASES.EPIC_REINFORCEMENT_PANEL,
                                 BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,
                                 BATTLE_VIEW_ALIASES.SUPER_PLATOON_PANEL}),
 PageStates.SPECTATOR_FREE: _SPECTATOR_UI.union({BATTLE_VIEW_ALIASES.SUPER_PLATOON_PANEL}),
 PageStates.SPECTATOR_FOLLOW: _SPECTATOR_UI.union({BATTLE_VIEW_ALIASES.DAMAGE_PANEL,
                               BATTLE_VIEW_ALIASES.RECOVERY_PANEL,
                               BATTLE_VIEW_ALIASES.DESTROY_TIMERS_PANEL,
                               BATTLE_VIEW_ALIASES.EPIC_MISSIONS_PANEL,
                               BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL}),
 PageStates.GAME_OVER: _GAME_UI.difference({BATTLE_VIEW_ALIASES.EPIC_REINFORCEMENT_PANEL,
                        BATTLE_VIEW_ALIASES.EPIC_MISSIONS_PANEL,
                        BATTLE_VIEW_ALIASES.BATTLE_TIMER,
                        BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR,
                        BATTLE_VIEW_ALIASES.DUAL_GUN_PANEL})}
_EPIC_EXTERNAL_COMPONENTS = (crosshair.CrosshairPanelContainer, markers2d.EpicMarkersManager)

class EpicBattlePage(EpicBattlePageMeta, BattleGUIKeyHandler):

    def __init__(self, components=None, external=_EPIC_EXTERNAL_COMPONENTS, fullStatsAlias=BATTLE_VIEW_ALIASES.FULL_STATS):
        if components is None:
            components = _EPIC_BATTLE_CLASSICS_COMPONENTS if self.sessionProvider.isReplayPlaying else _EPIC_BATTLE_EXTENDED_COMPONENTS
        super(EpicBattlePage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)
        self.__battleStarted = False
        self.__pageState = PageStates.COUNTDOWN
        self.__topState = PageStates.NONE
        self.__activeState = PageStates.NONE
        return

    def _invalidateState(self):
        targetState = PageStates.NONE
        if self.__topState != PageStates.NONE:
            targetState = self.__topState
        else:
            targetState = self.__pageState
        if targetState == PageStates.NONE or self.__activeState == targetState:
            return
        else:
            if self.__activeState in _ENABLE_CONTROL_MODE and not self.sessionProvider.isReplayPlaying:
                alias, _, _ = _PAGE_STATE_TO_CONTROL_PARAMS[self.__activeState]
                self.app.leaveGuiControlMode(alias)
            self.__activeState = targetState
            if self.__activeState in _ENABLE_CONTROL_MODE and not self.sessionProvider.isReplayPlaying:
                alias, p1, p2 = _PAGE_STATE_TO_CONTROL_PARAMS[self.__activeState]
                self.app.enterGuiControlMode(alias, cursorVisible=p1, enableAiming=p2)
            visibleUI = _STATE_TO_UI[targetState]
            currVis = set(self.as_getComponentsVisibilityS())
            hiddenUI = currVis.difference(visibleUI).difference(_NEVER_HIDE)
            ctrl = self.sessionProvider.shared.vehicleState
            vehicle = ctrl.getControllingVehicle()
            if vehicle is not None:
                if not vehicle.typeDescriptor.hasSiegeMode:
                    if BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR in visibleUI:
                        visibleUI.remove(BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR)
                        hiddenUI.add(BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR)
                elif BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR in hiddenUI:
                    visibleUI.add(BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR)
                    hiddenUI.remove(BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR)
                if not vehicle.typeDescriptor.isDualgunVehicle:
                    if BATTLE_VIEW_ALIASES.DUAL_GUN_PANEL in visibleUI:
                        visibleUI.remove(BATTLE_VIEW_ALIASES.DUAL_GUN_PANEL)
                        hiddenUI.add(BATTLE_VIEW_ALIASES.DUAL_GUN_PANEL)
                elif BATTLE_VIEW_ALIASES.DUAL_GUN_PANEL in hiddenUI:
                    visibleUI.add(BATTLE_VIEW_ALIASES.DUAL_GUN_PANEL)
                    hiddenUI.remove(BATTLE_VIEW_ALIASES.DUAL_GUN_PANEL)
            ctrl = self.sessionProvider.dynamic.maps
            if ctrl and BATTLE_VIEW_ALIASES.EPIC_OVERVIEW_MAP_SCREEN in visibleUI:
                ctrl.setOverviewMapScreenVisibility(True)
            elif ctrl and BATTLE_VIEW_ALIASES.EPIC_OVERVIEW_MAP_SCREEN in hiddenUI:
                ctrl.setOverviewMapScreenVisibility(False)
            self._setComponentsVisibility(visible=visibleUI, hidden=hiddenUI)
            return

    def _populate(self):
        super(EpicBattlePage, self)._populate()
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged += self.__onRespawnVisibility
            self.__onRespawnVisibility(ctrl.isRespawnVisible())
        self.addListener(events.GameEvent.MINIMAP_CMD, self._handleToggleOverviewMap, scope=EVENT_BUS_SCOPE.BATTLE)
        specCtrl = self.sessionProvider.dynamic.spectator
        if specCtrl is not None:
            specCtrl.onSpectatorViewModeChanged += self.__onSpectatorModeChanged
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        self.app.registerGuiKeyHandler(self)
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange += self.__arena_onPeriodChange
            self.__arena_onPeriodChange(arena.period)
        return

    def _dispose(self):
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onRespawnVisibilityChanged -= self.__onRespawnVisibility
        self.removeListener(events.GameEvent.MINIMAP_CMD, self._handleToggleOverviewMap, scope=EVENT_BUS_SCOPE.BATTLE)
        specCtrl = self.sessionProvider.dynamic.spectator
        if specCtrl is not None:
            specCtrl.onSpectatorViewModeChanged -= self.__onSpectatorModeChanged
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange -= self.__arena_onPeriodChange
        super(EpicBattlePage, self)._dispose()
        return

    def __arena_onPeriodChange(self, period, *args):
        if self.__battleStarted:
            return
        if period <= ARENA_PERIOD.PREBATTLE:
            if self.__pageState != PageStates.COUNTDOWN:
                self.__pageState = PageStates.COUNTDOWN
                self._invalidateState()
        if period == ARENA_PERIOD.BATTLE:
            if self.__pageState == PageStates.COUNTDOWN:
                self.__pageState = PageStates.GAME
                self._invalidateState()
            self.__battleStarted = True

    def handleEscKey(self, isDown):
        isMapVisible = self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EPIC_OVERVIEW_MAP_SCREEN)
        if isMapVisible:
            self._setComponentsVisibility(hidden=[BATTLE_VIEW_ALIASES.EPIC_OVERVIEW_MAP_SCREEN, BATTLE_VIEW_ALIASES.EPIC_DEPLOYMENT_MAP])
            self._toggleOverviewMap()
        return isMapVisible

    def _handleToggleOverviewMap(self, event):
        if not self._isVisible:
            return
        cmdMap = CommandMapping.g_instance
        if cmdMap.isFired(CommandMapping.CMD_MINIMAP_VISIBLE, event.ctx['key']):
            self._toggleOverviewMap()

    def _handleToggleFullStats(self, event):
        isDown = event.ctx['isDown']
        self._toggleFullStats(isDown)

    def _onBattleLoadingStart(self):
        self.__topState = PageStates.LOADING
        self._invalidateState()

    def _onBattleLoadingFinish(self):
        if self.__topState == PageStates.LOADING:
            self.__topState = PageStates.NONE
            self._invalidateState()
        for component in self._external:
            component.active(True)

        self.sessionProvider.shared.hitDirection.setVisible(True)

    def _toggleRadialMenu(self, isShown):
        radialMenu = self.getComponent(BATTLE_VIEW_ALIASES.RADIAL_MENU)
        if radialMenu is None:
            return
        else:
            if not isShown and self.__topState == PageStates.RADIAL:
                self.__topState = PageStates.NONE
                radialMenu.hide()
            elif isShown and self.__topState == PageStates.NONE and self.__pageState != PageStates.RESPAWN:
                self.__topState = PageStates.RADIAL
                radialMenu.show()
            else:
                return
            self._invalidateState()
            return

    def _toggleFullStats(self, isShown, permanent=None, tabIndex=None):
        if not isShown and self.__topState == PageStates.TABSCREEN:
            self.__topState = PageStates.NONE
        elif isShown and self.__topState != PageStates.RADIAL:
            self.__checkOverviewmap()
            if self.__pageState == PageStates.RESPAWN:
                BigWorld.worldDrawEnabled(True)
            self.__topState = PageStates.TABSCREEN
        elif not isShown and self.__pageState == PageStates.RESPAWN:
            BigWorld.worldDrawEnabled(False)
        else:
            return
        self._invalidateState()

    def _toggleOverviewMap(self):
        manager = self.app.containerManager
        if manager.isModalViewsIsExists():
            return
        if self.__topState == PageStates.OVERVIEWMAP:
            self.__topState = PageStates.NONE
        elif self.__topState == PageStates.NONE and self.__pageState != PageStates.RESPAWN or self.__topState == PageStates.TABSCREEN and self.__pageState != PageStates.RESPAWN:
            self.__topState = PageStates.OVERVIEWMAP
        else:
            return
        self._invalidateState()

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        super(EpicBattlePage, self)._onPostMortemSwitched(noRespawnPossible, respawnAvailable)
        specCtrl = self.sessionProvider.dynamic.spectator
        if specCtrl is None:
            return
        else:
            self.__checkOverviewmap()
            self.__checkRadialMenu()
            if specCtrl.spectatorViewMode == EPIC_CONSTS.SPECTATOR_MODE_FREECAM:
                self.__pageState = PageStates.SPECTATOR_FREE
            elif specCtrl.spectatorViewMode == EPIC_CONSTS.SPECTATOR_MODE_FOLLOW:
                self.__pageState = PageStates.SPECTATOR_FOLLOW
            elif specCtrl.spectatorViewMode == EPIC_CONSTS.SPECTATOR_MODE_DEATHCAM:
                self.__pageState = PageStates.SPECTATOR_DEATHCAM
            else:
                return
            self._invalidateState()
            return

    def _handleGUIToggled(self, event):
        if not self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.FULL_STATS) and not self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EPIC_RESPAWN_VIEW) and not self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EPIC_OVERVIEW_MAP_SCREEN):
            self._toggleGuiVisible()

    def __onSpectatorModeChanged(self, mode):
        if mode == EPIC_CONSTS.SPECTATOR_MODE_FREECAM:
            self.__pageState = PageStates.SPECTATOR_FREE
        elif mode == EPIC_CONSTS.SPECTATOR_MODE_FOLLOW:
            self.__pageState = PageStates.SPECTATOR_FOLLOW
        elif mode == EPIC_CONSTS.SPECTATOR_MODE_DEATHCAM:
            self.__pageState = PageStates.SPECTATOR_DEATHCAM
        else:
            return
        self._invalidateState()

    def __onRespawnVisibility(self, isVisible, fromTab=False):
        if not self._isVisible and isVisible:
            self._toggleGuiVisible()
        if isVisible and self.__topState == PageStates.TABSCREEN:
            self.__checkOverviewmap()
            self.__checkRadialMenu()
            self.__pageState = PageStates.RESPAWN
        elif isVisible and self.__pageState != PageStates.RESPAWN:
            self.__checkOverviewmap()
            self.__checkRadialMenu()
            self.__pageState = PageStates.RESPAWN
            BigWorld.worldDrawEnabled(False)
            for component in self._external:
                component.active(False)

        elif not isVisible and self.__pageState == PageStates.RESPAWN:
            self.__pageState = PageStates.GAME
            BigWorld.worldDrawEnabled(True)
            for component in self._external:
                component.active(True)

        else:
            return
        self._invalidateState()

    def __onPostmortemDisable(self):
        if not self._isInPostmortem:
            return
        self.__pageState = PageStates.GAME
        self._invalidateState()
        self._isInPostmortem = False

    def _onAvatarCtrlModeChanged(self, ctrlMode):
        pass

    def __onRoundFinished(self, winningTeam, reason):
        self.__pageState = PageStates.GAME_OVER
        self._invalidateState()

    def __checkOverviewmap(self):
        if self.__topState == PageStates.OVERVIEWMAP:
            ctrl = self.sessionProvider.dynamic.maps
            if ctrl:
                ctrl.overviewMapTriggered()

    def __checkRadialMenu(self):
        if self.__topState == PageStates.RADIAL:
            self._toggleRadialMenu(False)
