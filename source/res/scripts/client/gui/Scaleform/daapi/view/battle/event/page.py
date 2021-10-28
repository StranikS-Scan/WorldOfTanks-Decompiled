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
from gui.Scaleform.daapi.view.meta.EventBattlePageMeta import EventBattlePageMeta
from gui.Scaleform.daapi.view.battle.shared import period_music_listener, game_messages_panel
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.Scaleform.daapi.view.battle.classic.page import DynamicAliases
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.event.manager import EventMarkersManager
from gui.Scaleform.daapi.view.battle.event.game_event_getter import GameEventGetterMixin
from gui.shared.events import LoadViewEvent
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.Scaleform.daapi.view.battle.event import event_battle_sounds_player, start_countdown_sound_player

class _DynamicAliasesHalloween(CONST_CONTAINER):
    PERIOD_ENV_SOUND = 'PeriodSoundPlayer'
    PERIOD_TIMER_SOUND = 'TimerSoundPlayer'
    BOT_VEHICLE_SOUND = 'BotVehicleSoundPlayer'
    MATTER_COLLECTING_SOUND = 'MatterCollectingSoundPlayer'
    VEHICLE_DEVICE_SOUND = 'VehicleDevicesSoundPlayer'
    TEAM_FIGHT_SOUND = 'TeamFightSoundPlayer'
    PLAYER_VEHICLE_SOUND = 'PlayerVehicleSoundPlayer'
    BOSS_FIGHT_SOUND = 'BossFightSoundPlayer'
    WIN_FIGHT_SOUND = 'WinFightSoundPlayer'


EVENT_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.BATTLE_HINT,)),
 (BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
   BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
   BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
   BATTLE_VIEW_ALIASES.HINT_PANEL,
   BATTLE_VIEW_ALIASES.PLAYERS_PANEL_EVENT,
   DynamicAliases.PERIOD_MUSIC_LISTENER,
   DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER,
   _DynamicAliasesHalloween.PERIOD_ENV_SOUND,
   _DynamicAliasesHalloween.PERIOD_TIMER_SOUND,
   _DynamicAliasesHalloween.BOT_VEHICLE_SOUND,
   _DynamicAliasesHalloween.MATTER_COLLECTING_SOUND,
   _DynamicAliasesHalloween.VEHICLE_DEVICE_SOUND,
   _DynamicAliasesHalloween.TEAM_FIGHT_SOUND,
   _DynamicAliasesHalloween.PLAYER_VEHICLE_SOUND,
   _DynamicAliasesHalloween.BOSS_FIGHT_SOUND,
   _DynamicAliasesHalloween.WIN_FIGHT_SOUND)),
 (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (BATTLE_VIEW_ALIASES.PLAYERS_PANEL_EVENT,)),
 (BATTLE_CTRL_ID.CALLOUT, (BATTLE_VIEW_ALIASES.CALLOUT_PANEL,)),
 (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
 (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
 (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,)),
 (BATTLE_CTRL_ID.AMMO, (BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,))), viewsConfig=((DynamicAliases.PERIOD_MUSIC_LISTENER, period_music_listener.PeriodMusicListener),
 (DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, start_countdown_sound_player.StartCountdownSoundPlayer),
 (_DynamicAliasesHalloween.PERIOD_ENV_SOUND, event_battle_sounds_player.PeriodSoundPlayer),
 (_DynamicAliasesHalloween.PERIOD_TIMER_SOUND, event_battle_sounds_player.TimerSoundPlayer),
 (_DynamicAliasesHalloween.BOT_VEHICLE_SOUND, event_battle_sounds_player.BotVehicleSoundPlayer),
 (_DynamicAliasesHalloween.TEAM_FIGHT_SOUND, event_battle_sounds_player.TeamFightSoundPlayer),
 (_DynamicAliasesHalloween.PLAYER_VEHICLE_SOUND, event_battle_sounds_player.PlayerVehicleSoundPlayer),
 (_DynamicAliasesHalloween.MATTER_COLLECTING_SOUND, event_battle_sounds_player.MatterCollectingSoundPlayer),
 (_DynamicAliasesHalloween.VEHICLE_DEVICE_SOUND, event_battle_sounds_player.VehicleDevicesSoundPlayer),
 (_DynamicAliasesHalloween.BOSS_FIGHT_SOUND, event_battle_sounds_player.BossFightSoundPlayer),
 (_DynamicAliasesHalloween.WIN_FIGHT_SOUND, event_battle_sounds_player.WinFightSoundPlayer),
 (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.GameMessagesPanel)))
_TUTORIAL_PAGES = ('eventHint1', 'eventHint2', 'eventHint3', 'eventHint4')
_EVENT_EXTERNAL_COMPONENTS = (CrosshairPanelContainer, EventMarkersManager)

class EventBattlePage(EventBattlePageMeta, GameEventGetterMixin):

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
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onPlayerFeedbackReceived += self.__onPlayerFeedbackReceived
        LOG_DEBUG('Event battle page is created.')
        return

    def _setComponentsVisibilityDependingStats(self, visible=None, hidden=None):
        if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EVENT_STATS):
            if visible:
                self._fsToggling.update(visible)
            if hidden:
                self._fsToggling.difference_update(hidden)
        else:
            self._setComponentsVisibility(visible=visible, hidden=hidden)

    def _onCollectorProgress(self, event):
        ribbonOverlays = event.ctx.get('overlays', {}).get('isRibbonsPanelOverlay', False)
        buffPanelOverlays = event.ctx.get('overlays', {}).get('isBuffsPanelOverlay', False)
        hiddenPanels = set()
        visiblePanels = set()
        ribbonSet = hiddenPanels if ribbonOverlays else visiblePanels
        ribbonSet.add(BATTLE_VIEW_ALIASES.RIBBONS_PANEL)
        buffSet = hiddenPanels if buffPanelOverlays else visiblePanels
        buffSet.add(BATTLE_VIEW_ALIASES.EVENT_BUFFS_PANEL)
        self._setComponentsVisibilityDependingStats(visible=visiblePanels, hidden=hiddenPanels)

    def _onCollectorProgressStop(self, _):
        panels = {BATTLE_VIEW_ALIASES.RIBBONS_PANEL, BATTLE_VIEW_ALIASES.EVENT_BUFFS_PANEL}
        if self.environmentData.getCurrentEnvironmentID() > self.environmentData.getMaxEnvironmentID():
            self._setComponentsVisibilityDependingStats(hidden=panels)
            return
        player = BigWorld.player()
        ownVeh = BigWorld.entity(player.playerVehicleID)
        if ownVeh and ownVeh.isAlive():
            self._setComponentsVisibilityDependingStats(visible=panels)

    def _handleToggleOverviewMap(self, event):
        key = event.ctx['key']
        cmdMap = CommandMapping.g_instance
        if cmdMap.isFired(CommandMapping.CMD_MINIMAP_VISIBLE, key):
            self.__isNearByIndicatorVisible = not self.__isNearByIndicatorVisible
            nearByIndicator = self.getComponent(BATTLE_VIEW_ALIASES.BOSS_INDICATOR_PROGRESS)
            nearByIndicator.show(self.__isNearByIndicatorVisible)

    def _dispose(self):
        ctrl = self.sessionProvider.shared.feedback
        if ctrl is not None:
            ctrl.onPlayerFeedbackReceived -= self.__onPlayerFeedbackReceived
        self.removeListener(events.GameEvent.EVENT_STATS, self.__handleToggleEventStats, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.FADE_OUT_AND_IN, self.__handleFadeOutAndIn, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.MINIMAP_CMD, self._handleToggleOverviewMap, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.COLLECTOR_PROGRESS, self._onCollectorProgress, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.COLLECTOR_PROGRESS_STOP, self._onCollectorProgressStop, scope=EVENT_BUS_SCOPE.BATTLE)
        LOG_DEBUG('Event battle page is destroyed.')
        super(EventBattlePage, self)._dispose()
        return

    def _startBattleSession(self):
        super(EventBattlePage, self)._startBattleSession()
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange

    def _stopBattleSession(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        super(EventBattlePage, self)._stopBattleSession()

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self._setComponentsVisibilityDependingStats(visible={BATTLE_VIEW_ALIASES.PLAYERS_PANEL_EVENT})

    def __handleFadeOutAndIn(self, event):
        settings = event.ctx.get('settings')
        self.__fadeProcess(settings)

    @process
    def __fadeProcess(self, settings):
        manager = self.app.fadeMgr
        yield manager.startFade(settings=settings)

    def _toggleRadialMenu(self, isShown, allowAction=True):
        radialMenuLinkage = BATTLE_VIEW_ALIASES.RADIAL_MENU
        radialMenu = self.getComponent(radialMenuLinkage)
        if radialMenu is None:
            return
        elif self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EVENT_STATS):
            return
        else:
            if isShown:
                radialMenu.show()
                self.app.enterGuiControlMode(radialMenuLinkage, cursorVisible=False, enableAiming=False)
            else:
                self.app.leaveGuiControlMode(radialMenuLinkage)
                radialMenu.hide(allowAction)
            return

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
        self._setComponentsVisibilityDependingStats(hidden={BATTLE_VIEW_ALIASES.RIBBONS_PANEL})

    def _onRespawnBaseMoving(self):
        super(EventBattlePage, self)._onRespawnBaseMoving()
        self._setComponentsVisibilityDependingStats(visible={BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, BATTLE_VIEW_ALIASES.RIBBONS_PANEL}, hidden={BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL})

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

    def __onPlayerFeedbackReceived(self, feedback):
        for event in feedback:
            eventType = event.getType()
            if eventType == FEEDBACK_EVENT_ID.ENEMY_DAMAGED_HP_PLAYER:
                damageExtra = event.getExtra()
                if damageExtra.isDeathZone():
                    self.as_updateDamageScreenS(True)
