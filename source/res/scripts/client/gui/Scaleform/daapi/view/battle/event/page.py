# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/page.py
import BattleReplay
import BigWorld
from aih_constants import CTRL_MODE_NAME
from constants import ARENA_PERIOD
from debug_utils import LOG_DEBUG
from shared_utils import CONST_CONTAINER
from adisp import process
from PlayerEvents import g_playerEvents
from gui.shared import EVENT_BUS_SCOPE, events
from gui.Scaleform.framework import ViewTypes
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.battle.shared import period_music_listener, game_messages_panel
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from gui.Scaleform.daapi.view.battle.classic.page import DynamicAliases
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.event.manager import EventMarkersManager
from gui.Scaleform.daapi.view.battle.event import event_battle_sounds_player
from gui.Scaleform.daapi.view.battle.event import drone_music_player

class _EventDynamicAliases(CONST_CONTAINER):
    EVENT_ARENA_STATE_PLAYER = 'EventArenaStatePlayer'
    VEHICLE_DESTRUCTION_PLAYER = 'VehicleDestroyedSoundPlayer'
    ENEMY_DAMAGE_NOTIFICATIONS_PLAYER = 'EnemyDamageSoundPlayer'
    FINISH_SOUND_PLAYER = 'FinishSoundPlayer'


EVENT_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.BATTLE_HINT,)),
 (BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
   BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
   BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
   DynamicAliases.PERIOD_MUSIC_LISTENER,
   _EventDynamicAliases.EVENT_ARENA_STATE_PLAYER,
   _EventDynamicAliases.VEHICLE_DESTRUCTION_PLAYER,
   _EventDynamicAliases.ENEMY_DAMAGE_NOTIFICATIONS_PLAYER,
   _EventDynamicAliases.FINISH_SOUND_PLAYER,
   DynamicAliases.DRONE_MUSIC_PLAYER)),
 (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.DRONE_MUSIC_PLAYER,)),
 (BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS, (DynamicAliases.DRONE_MUSIC_PLAYER,)),
 (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
 (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,))), viewsConfig=((DynamicAliases.PERIOD_MUSIC_LISTENER, period_music_listener.PeriodMusicListener),
 (_EventDynamicAliases.EVENT_ARENA_STATE_PLAYER, event_battle_sounds_player.EventArenaStatePlayer),
 (_EventDynamicAliases.VEHICLE_DESTRUCTION_PLAYER, event_battle_sounds_player.VehicleDestroyedSoundPlayer),
 (_EventDynamicAliases.ENEMY_DAMAGE_NOTIFICATIONS_PLAYER, event_battle_sounds_player.EnemyDamageSoundPlayer),
 (_EventDynamicAliases.FINISH_SOUND_PLAYER, event_battle_sounds_player.FinishSoundPlayer),
 (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.GameMessagesPanel),
 (DynamicAliases.DRONE_MUSIC_PLAYER, drone_music_player.EventDroneMusicPlayer)))
_TUTORIAL_PAGES = ('eventHint1', 'eventHint2', 'eventHint3', 'eventHint4', 'eventHint5', 'eventHint6')
_EVENT_EXTERNAL_COMPONENTS = (CrosshairPanelContainer, EventMarkersManager)
_TAB_COMPONENTS = {BATTLE_VIEW_ALIASES.EVENT_STATS, BATTLE_VIEW_ALIASES.EVENT_TIMER_TAB}
_FULL_SCREEN_VIEWS = {BATTLE_VIEW_ALIASES.EVENT_STATS, BATTLE_VIEW_ALIASES.RADIAL_MENU, BATTLE_VIEW_ALIASES.EVENT_FULL_MAP}
_END_BATTLE_OVERLAPPING_COMPONENTS = {BATTLE_VIEW_ALIASES.EVENT_TIMER, BATTLE_VIEW_ALIASES.BATTLE_HINT}

class EventBattlePage(ClassicPage):

    def __init__(self, components=None, external=_EVENT_EXTERNAL_COMPONENTS, fullStatsAlias=None):
        components = EVENT_CONFIG if not components else components + EVENT_CONFIG
        super(EventBattlePage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)
        self.__isNearByIndicatorVisible = True
        self._fmToggling = set()

    def hasFullScreenView(self):
        for key in _FULL_SCREEN_VIEWS:
            if self.as_isComponentVisibleS(key):
                return True

        return False

    def _populate(self):
        super(EventBattlePage, self)._populate()
        self.addListener(events.GameEvent.HELP, self.__handleHelpEvent, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.EVENT_STATS, self.__handleToggleEventStats, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.FADE_OUT_AND_IN, self.__handleFadeOutAndIn, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.FULL_MAP_CMD, self._handleToggleFullMap, scope=EVENT_BUS_SCOPE.BATTLE)
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        LOG_DEBUG('Event battle page is created.')

    def _onRegisterFlashComponent(self, viewPy, alias):
        if alias == BATTLE_VIEW_ALIASES.EVENT_TIMER:
            viewPy.allowAnimation()
        super(EventBattlePage, self)._onRegisterFlashComponent(viewPy, alias)

    def _handleToggleFullMap(self, event):
        if self.__checkCanNotToggleFS(BATTLE_VIEW_ALIASES.EVENT_FULL_MAP):
            return
        isDown = event.ctx['isDown']
        self._toggleFullMap(isDown)

    def _toggleFullMap(self, isShow):
        if isShow and not self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EVENT_FULL_MAP):
            self._fmToggling = set(self.as_getComponentsVisibilityS())
            self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.EVENT_FULL_MAP}, hidden=self._fmToggling)
        elif not isShow and self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EVENT_FULL_MAP):
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.EVENT_FULL_MAP}, visible=self._fmToggling)
            self._fmToggling.clear()
        if not BattleReplay.g_replayCtrl.isPlaying:
            self.as_setPostmortemTipsVisibleS(not isShow and self._isInPostmortem)

    def _dispose(self):
        super(EventBattlePage, self)._dispose()
        self.removeListener(events.GameEvent.HELP, self.__handleHelpEvent, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.RadialMenuEvent.RADIAL_MENU_ACTION, self.__handleRadialAction, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.EVENT_STATS, self.__handleToggleEventStats, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.FADE_OUT_AND_IN, self.__handleFadeOutAndIn, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.FULL_MAP_CMD, self._handleToggleFullMap, scope=EVENT_BUS_SCOPE.BATTLE)
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        LOG_DEBUG('Event battle page is destroyed.')

    def _startBattleSession(self):
        super(EventBattlePage, self)._startBattleSession()
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange

    def _stopBattleSession(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        super(EventBattlePage, self)._stopBattleSession()

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.PLAYERS_PANEL_EVENT})

    def __handleFadeOutAndIn(self, event):
        settings = event.ctx.get('settings')
        self.__fadeProcess(settings)

    @process
    def __fadeProcess(self, settings):
        manager = self.app.fadeMgr
        yield manager.startFade(settings=settings)

    def _toggleRadialMenu(self, isShown):
        if self.__checkCanNotToggleFS(BATTLE_VIEW_ALIASES.RADIAL_MENU):
            return
        radialMenu = self.getComponent(BATTLE_VIEW_ALIASES.RADIAL_MENU)
        if isShown:
            self.__enterRadialHUD()
            radialMenu.show()
            self.addListener(events.RadialMenuEvent.RADIAL_MENU_ACTION, self.__handleRadialAction, scope=EVENT_BUS_SCOPE.BATTLE)
        else:
            self.removeListener(events.RadialMenuEvent.RADIAL_MENU_ACTION, self.__handleRadialAction, scope=EVENT_BUS_SCOPE.BATTLE)
            radialMenu.hide()
            self.__exitRadialHUD()

    def _switchToPostmortem(self):
        super(EventBattlePage, self)._switchToPostmortem()
        if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EVENT_STATS):
            self._fsToggling.remove(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL)
            if not BattleReplay.g_replayCtrl.isPlaying:
                self.as_setPostmortemTipsVisibleS(False)

    def _switchFromPostmortem(self):
        super(EventBattlePage, self)._switchFromPostmortem()
        if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EVENT_STATS):
            self._fsToggling.add(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL)

    def _changeCtrlMode(self, ctrlMode):
        if ctrlMode in [CTRL_MODE_NAME.POSTMORTEM, CTRL_MODE_NAME.ARCADE]:
            self._toggleFullMap(False)
        super(EventBattlePage, self)._changeCtrlMode(ctrlMode)

    def _toggleEventStats(self, isShown):
        if self.__checkCanNotToggleFS(BATTLE_VIEW_ALIASES.EVENT_STATS):
            return
        if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EVENT_STATS) != isShown:
            if isShown:
                self._fsToggling.update(self.as_getComponentsVisibilityS())
                self._setComponentsVisibility(visible=_TAB_COMPONENTS, hidden=self._fsToggling)
            else:
                self._setComponentsVisibility(visible=self._fsToggling, hidden=_TAB_COMPONENTS)
                self._fsToggling.clear()
            if not BattleReplay.g_replayCtrl.isPlaying:
                self.as_setPostmortemTipsVisibleS(not isShown and self._isInPostmortem)

    def _onBattleLoadingStart(self):
        data = {'autoStart': False,
         'tutorialPages': _TUTORIAL_PAGES}
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.EVENT_LOADING, ctx=data), EVENT_BUS_SCOPE.BATTLE)
        super(EventBattlePage, self)._onBattleLoadingStart()

    def _onBattleLoadingFinish(self):
        self.fireEvent(events.DestroyViewEvent(VIEW_ALIAS.EVENT_LOADING), EVENT_BUS_SCOPE.BATTLE)
        super(EventBattlePage, self)._onBattleLoadingFinish()
        self._setComponentsVisibility(hidden=_TAB_COMPONENTS)
        if BigWorld.player().arena.period != ARENA_PERIOD.BATTLE:
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.PLAYERS_PANEL_EVENT})

    def __enterRadialHUD(self):
        self._fsToggling.update(self.as_getComponentsVisibilityS())
        self._setComponentsVisibility(hidden=self._fsToggling)
        self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.RADIAL_MENU, cursorVisible=True, enableAiming=False)

    def __exitRadialHUD(self):
        self._setComponentsVisibility(visible=self._fsToggling)
        self._fsToggling.clear()
        self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.RADIAL_MENU)

    def __handleHelpEvent(self, _):
        if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.RADIAL_MENU):
            self._toggleRadialMenu(False)

    def __handleToggleEventStats(self, event):
        self._toggleEventStats(event.ctx['isDown'])

    def __handleRadialAction(self, _):
        self.__exitRadialHUD()

    def _getBattleLoadingVisibleAliases(self):
        return None

    def _handleGUIToggled(self, event):
        if not self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EVENT_STATS):
            self._toggleGuiVisible()

    def __checkCanNotToggleFS(self, alias):
        manager = self.app.containerManager
        if not manager.isContainerShown(ViewTypes.DEFAULT) or manager.isModalViewsIsExists():
            return True
        elif self.getComponent(alias) is None:
            return True
        else:
            for key in _FULL_SCREEN_VIEWS:
                if key != alias and self.as_isComponentVisibleS(key):
                    return True

            return False

    def __onRoundFinished(self, winningTeam, reason):
        self._setComponentsVisibility(hidden=_END_BATTLE_OVERLAPPING_COMPONENTS)
