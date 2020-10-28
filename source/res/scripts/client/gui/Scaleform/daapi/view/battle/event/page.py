# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/page.py
import BigWorld
import CommandMapping
from constants import ARENA_PERIOD
from debug_utils import LOG_DEBUG
from shared_utils import CONST_CONTAINER
from adisp import process
from PlayerEvents import g_playerEvents
from frameworks.wulf import WindowLayer
from aih_constants import CTRL_MODE_NAME
from gui.shared import EVENT_BUS_SCOPE, events
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.battle.shared import period_music_listener, game_messages_panel
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from gui.Scaleform.daapi.view.battle.classic.page import DynamicAliases
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.event.manager import EventMarkersManager
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from gui.shared.events import LoadViewEvent
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.daapi.view.battle.event import period_music_player, event_battle_sounds_player, start_countdown_sound_player

class _DynamicAliasesHalloween(CONST_CONTAINER):
    PERIOD_MUSIC_PLAYER = 'PeriodMusicHalloweenPlayer'
    PERIOD_ENV_PLAYER = 'EnvironmentMusicHalloweenPlayer'
    PERIOD_BATTLE_SOUNDS_PLAYER = 'EventBattleSoundsPlayer'
    VEHICLE_HEALTH_SOUNDS_PLAYER = 'VehicleHealthSoundPlayer'


EVENT_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.BATTLE_HINT,)),
 (BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
   BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
   DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER,
   BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
   DynamicAliases.PERIOD_MUSIC_LISTENER,
   _DynamicAliasesHalloween.PERIOD_MUSIC_PLAYER,
   _DynamicAliasesHalloween.PERIOD_ENV_PLAYER,
   _DynamicAliasesHalloween.PERIOD_BATTLE_SOUNDS_PLAYER)),
 (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (_DynamicAliasesHalloween.VEHICLE_HEALTH_SOUNDS_PLAYER,)),
 (BATTLE_CTRL_ID.CALLOUT, (BATTLE_VIEW_ALIASES.CALLOUT_PANEL,)),
 (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
 (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
 (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,))), viewsConfig=((DynamicAliases.PERIOD_MUSIC_LISTENER, period_music_listener.PeriodMusicListener),
 (DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, start_countdown_sound_player.StartCountdownSoundPlayer),
 (_DynamicAliasesHalloween.PERIOD_MUSIC_PLAYER, period_music_player.PeriodMusicHalloweenPlayer),
 (_DynamicAliasesHalloween.PERIOD_ENV_PLAYER, period_music_player.EnvironmentMusicHalloweenPlayer),
 (_DynamicAliasesHalloween.PERIOD_BATTLE_SOUNDS_PLAYER, event_battle_sounds_player.EventBattleSoundsPlayer),
 (_DynamicAliasesHalloween.VEHICLE_HEALTH_SOUNDS_PLAYER, event_battle_sounds_player.VehicleHealthSoundPlayer),
 (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.GameMessagesPanel)))
_TUTORIAL_PAGES = ('eventHint1', 'eventHint2', 'eventHint3', 'eventHint4')
_EVENT_EXTERNAL_COMPONENTS = (CrosshairPanelContainer, EventMarkersManager)

class EventBattlePage(ClassicPage, GameEventGetterMixin):

    def __init__(self, components=None, external=_EVENT_EXTERNAL_COMPONENTS, fullStatsAlias=None):
        components = EVENT_CONFIG if not components else components + EVENT_CONFIG
        super(EventBattlePage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)
        self.__isNearByIndicatorVisible = True

    def _populate(self):
        super(EventBattlePage, self)._populate()
        self.addListener(events.GameEvent.EVENT_STATS, self.__handleToggleEventStats, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.FADE_OUT_AND_IN, self.__handleFadeOutAndIn, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.MINIMAP_CMD, self._handleToggleOverviewMap, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.COLLECTOR_PROGRESS, self._onCollectorProgress, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.COLLECTOR_PROGRESS_STOP, self._onCollectorProgressStop, scope=EVENT_BUS_SCOPE.BATTLE)
        LOG_DEBUG('Event battle page is created.')

    def _onCollectorProgress(self, event):
        ribbonOverlays = event.ctx.get('overlays', {}).get('isRibbonsPanelOverlay', False)
        buffPanelOverlays = event.ctx.get('overlays', {}).get('isBuffsPanelOverlay', False)
        panels = set()
        if ribbonOverlays:
            panels.add(BATTLE_VIEW_ALIASES.RIBBONS_PANEL)
        if buffPanelOverlays:
            panels.add(BATTLE_VIEW_ALIASES.EVENT_BUFFS_PANEL)
        self.as_setComponentsVisibilityS(visible=set(), hidden=panels)

    def _onCollectorProgressStop(self, _):
        panels = {BATTLE_VIEW_ALIASES.EVENT_BUFFS_PANEL, BATTLE_VIEW_ALIASES.RIBBONS_PANEL}
        player = BigWorld.player()
        ownVeh = BigWorld.entity(player.playerVehicleID)
        if ownVeh and ownVeh.isAlive():
            self.as_setComponentsVisibilityS(visible=panels, hidden=set())
        if self.environmentData.getCurrentEnvironmentID() > self.environmentData.getMaxEnvironmentID():
            self._setComponentsVisibility(hidden=panels)

    def _handleToggleOverviewMap(self, event):
        key = event.ctx['key']
        cmdMap = CommandMapping.g_instance
        if cmdMap.isFired(CommandMapping.CMD_MINIMAP_VISIBLE, key):
            self.__isNearByIndicatorVisible = not self.__isNearByIndicatorVisible
            nearByIndicator = self.getComponent(BATTLE_VIEW_ALIASES.BOSS_INDICATOR_PROGRESS)
            nearByIndicator.show(self.__isNearByIndicatorVisible)

    def _dispose(self):
        super(EventBattlePage, self)._dispose()
        self.removeListener(events.GameEvent.EVENT_STATS, self.__handleToggleEventStats, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.FADE_OUT_AND_IN, self.__handleFadeOutAndIn, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.MINIMAP_CMD, self._handleToggleOverviewMap, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.COLLECTOR_PROGRESS, self._onCollectorProgress, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.COLLECTOR_PROGRESS_STOP, self._onCollectorProgressStop, scope=EVENT_BUS_SCOPE.BATTLE)
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

    def _toggleEventStats(self, isShown):
        manager = self.app.containerManager
        if not manager.isContainerShown(WindowLayer.VIEW):
            return
        else:
            eventStats = self.getComponent(BATTLE_VIEW_ALIASES.EVENT_STATS)
            if eventStats is None:
                return
            if manager.isModalViewsIsExists():
                return
            if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.RADIAL_MENU):
                return
            nearByIndicator = self.getComponent(BATTLE_VIEW_ALIASES.BOSS_INDICATOR_PROGRESS)
            nearByIndicator.toggle(not isShown)
            if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EVENT_STATS) != isShown:
                if isShown:
                    self._fsToggling.update(self.as_getComponentsVisibilityS())
                    self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.EVENT_STATS}, hidden=self._fsToggling)
                else:
                    self._setComponentsVisibility(visible=self._fsToggling, hidden={BATTLE_VIEW_ALIASES.EVENT_STATS})
                    self._fsToggling.clear()
            return

    def _onBattleLoadingStart(self):
        data = {'autoStart': False,
         'tutorialPages': _TUTORIAL_PAGES}
        self.fireEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EVENT_LOADING), ctx=data), EVENT_BUS_SCOPE.BATTLE)
        super(EventBattlePage, self)._onBattleLoadingStart()

    def _onBattleLoadingFinish(self):
        self.fireEvent(events.DestroyViewEvent(VIEW_ALIAS.EVENT_LOADING), EVENT_BUS_SCOPE.BATTLE)
        super(EventBattlePage, self)._onBattleLoadingFinish()
        self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.EVENT_STATS})
        if BigWorld.player().arena.period != ARENA_PERIOD.BATTLE:
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.PLAYERS_PANEL_EVENT})

    def __handleToggleEventStats(self, event):
        self._toggleEventStats(event.ctx['isDown'])

    def _getBattleLoadingVisibleAliases(self):
        return None

    def _handleGUIToggled(self, event):
        if not self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EVENT_STATS):
            self._toggleGuiVisible()

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        super(EventBattlePage, self)._onPostMortemSwitched(noRespawnPossible, respawnAvailable)
        alias = BATTLE_VIEW_ALIASES.RIBBONS_PANEL
        if self.as_isComponentVisibleS(alias):
            self._setComponentsVisibility(hidden={alias})

    def _onRespawnBaseMoving(self):
        super(EventBattlePage, self)._onRespawnBaseMoving()
        alias = BATTLE_VIEW_ALIASES.RIBBONS_PANEL
        if not self.as_isComponentVisibleS(alias):
            self._setComponentsVisibility(visible={alias})
        if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EVENT_STATS):
            self._fsToggling.add(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL)
            self._fsToggling.remove(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)

    def _changeCtrlMode(self, ctrlMode):

        def invalidateSiegeVehicle(vehicleType):
            return 'siegeMode' in vehicleType.tags and 'wheeledVehicle' not in vehicleType.tags and 'dualgun' not in vehicleType.tags

        components = {BATTLE_VIEW_ALIASES.DAMAGE_PANEL, BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL, BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL}
        if ctrlMode != CTRL_MODE_NAME.POSTMORTEM:
            ctrl = self.sessionProvider.shared.vehicleState
            vehicle = ctrl.getControllingVehicle()
            if vehicle and invalidateSiegeVehicle(vehicle.typeDescriptor.type):
                components.add(BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR)
        if ctrlMode == CTRL_MODE_NAME.VIDEO:
            self._setComponentsVisibility(hidden=components)
        else:
            self._setComponentsVisibility(visible=components)
