# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/page.py
import BigWorld
import HBAccountSettings
import SoundGroups
from constants import ARENA_PERIOD
from datetime import date
from debug_utils import LOG_DEBUG
from helpers import dependency
from historical_battles.gui.Scaleform.daapi.view.battle.manager import HistoricalMarkersManager
from shared_utils import CONST_CONTAINER
from PlayerEvents import g_playerEvents
from aih_constants import CTRL_MODE_NAME
from gui.shared import EVENT_BUS_SCOPE, events
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.battle.shared import game_messages_panel
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from gui.Scaleform.daapi.view.battle.classic.page import DynamicAliases
from historical_battles.gui.Scaleform.daapi.settings import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.shared.indicators import createPredictionIndicator
from historical_battles_common.hb_constants import AccountSettingsKeys
from historical_battles_common.hb_constants_extension import ARENA_BONUS_TYPE
from historical_battles.gui.Scaleform.daapi.view.battle import players_panel as event_players_panel
from historical_battles.gui.Scaleform.daapi.view.battle.indicators import createHistoricalBattlesDamageIndicator
from gui.shared.events import LoadViewEvent
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from historical_battles.gui.Scaleform.daapi.view.battle import start_countdown_sound_player
from historical_battles.gui.sounds import sound_battle_players
from historical_battles.gui.sounds.sound_battle_controller import SoundBattleController
from historical_battles.skeletons.gui.game_event_controller import IGameEventController

class HBDynamicAliases(CONST_CONTAINER):
    EQUIPMENT_SOUND_PLAYER = 'equipmentSoundPlayer'


EVENT_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.BATTLE_HINT, BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_BASE_HINT)),
 (BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
   BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
   BATTLE_VIEW_ALIASES.HINT_PANEL,
   BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_PLAYERS_PANEL,
   DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER,
   HBDynamicAliases.EQUIPMENT_SOUND_PLAYER)),
 (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_PLAYERS_PANEL,)),
 (BATTLE_CTRL_ID.CALLOUT, (BATTLE_VIEW_ALIASES.CALLOUT_PANEL,)),
 (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
 (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
 (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,)),
 (BATTLE_CTRL_ID.HIT_DIRECTION, (BATTLE_VIEW_ALIASES.PREDICTION_INDICATOR, BATTLE_VIEW_ALIASES.HIT_DIRECTION)),
 (BATTLE_CTRL_ID.TEAM_BASES, (BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL,))), viewsConfig=((HBDynamicAliases.EQUIPMENT_SOUND_PLAYER, sound_battle_players.EquipmentSoundPlayer),
 (DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, start_countdown_sound_player.StartCountdownSoundPlayer),
 (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.GameMessagesPanel),
 (BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_PLAYERS_PANEL, event_players_panel.HistoricalBattlesPlayersPanel),
 (BATTLE_VIEW_ALIASES.PREDICTION_INDICATOR, createPredictionIndicator),
 (BATTLE_VIEW_ALIASES.HIT_DIRECTION, createHistoricalBattlesDamageIndicator)))
_TUTORIAL_PAGES = ('eventHint1', 'eventHint2', 'eventHint3', 'eventHint4')
_FULL_SCREEN_VIEWS = {BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_STATS_WIDGET, BATTLE_VIEW_ALIASES.RADIAL_MENU, BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_FULL_MAP}
_EVENT_EXTERNAL_COMPONENTS = (CrosshairPanelContainer, HistoricalMarkersManager)

class HistoricalBattlePage(ClassicPage):
    _gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, components=None, external=_EVENT_EXTERNAL_COMPONENTS, fullStatsAlias=None):
        components = EVENT_CONFIG if not components else components + EVENT_CONFIG
        super(HistoricalBattlePage, self).__init__(components=components, external=external, fullStatsAlias=BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_STATS_WIDGET)

    def hasFullScreenView(self, ignoreAlias=None):
        for key in _FULL_SCREEN_VIEWS:
            if key != ignoreAlias and self.as_isComponentVisibleS(key):
                return True

        return False

    def _populate(self):
        super(HistoricalBattlePage, self)._populate()
        self.addListener(events.GameEvent.FULL_MAP_CMD, self._handleToggleFullMap, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__soundBattleController = SoundBattleController()
        self.__soundBattleController.start()
        LOG_DEBUG('Event battle page is created.')

    def _handleToggleFullMap(self, event):
        if self.__checkCanNotToggleFS(BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_FULL_MAP):
            return
        isDown = event.ctx['isDown']
        self._toggleFullMap(isDown)

    def _toggleFullMap(self, isShow):
        messenger = self.getComponent(BATTLE_VIEW_ALIASES.BATTLE_MESSENGER)
        isVisible = self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_FULL_MAP)
        if isShow and not isVisible:
            self._fmToggling = set(self.as_getComponentsVisibilityS())
            self._fmToggling.remove(BATTLE_VIEW_ALIASES.BATTLE_MESSENGER)
            if BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL in self._fmToggling:
                self._fmToggling.remove(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)
            self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_FULL_MAP}, hidden=self._fmToggling)
            messenger.toggleReadingMode(True)
            self.__activateFullMapControlMod()
        elif not isShow and self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_FULL_MAP):
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_FULL_MAP}, visible=self._fmToggling)
            self._fmToggling.clear()
            messenger.toggleReadingMode(False)
            self.__activateFullMapControlMod(False)

    def _dispose(self):
        super(HistoricalBattlePage, self)._dispose()
        self.removeListener(events.GameEvent.FULL_MAP_CMD, self._handleToggleFullMap, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__destroyBattleSoundCtrl()
        LOG_DEBUG('Event battle page is destroyed.')

    def _startBattleSession(self):
        super(HistoricalBattlePage, self)._startBattleSession()
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange

    def _stopBattleSession(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        super(HistoricalBattlePage, self)._stopBattleSession()

    def __activateFullMapControlMod(self, isActive=True):
        if isActive:
            self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_FULL_MAP, cursorVisible=True, enableAiming=False)
        else:
            self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_FULL_MAP)

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_PLAYERS_PANEL})

    def _toggleRadialMenu(self, isShown, allowAction=True):
        radialMenuLinkage = BATTLE_VIEW_ALIASES.RADIAL_MENU
        radialMenu = self.getComponent(radialMenuLinkage)
        if radialMenu is None:
            return
        elif isShown and self.__checkCanNotToggleFS(radialMenuLinkage):
            return
        else:
            if isShown:
                radialMenu.show()
                self.app.enterGuiControlMode(radialMenuLinkage, cursorVisible=False, enableAiming=False)
            else:
                self.app.leaveGuiControlMode(radialMenuLinkage)
                radialMenu.hide(allowAction)
            return

    def _toggleFullStats(self, isShown, permanent=None, tabAlias=None):
        if isShown and self.__checkCanNotToggleFS(self._fullStatsAlias):
            return
        if not isShown and not self._isInPostmortem and BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL in self._fsToggling:
            self._fsToggling.remove(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)
        super(HistoricalBattlePage, self)._toggleFullStats(isShown, permanent=permanent, tabAlias=tabAlias)
        phaseIndicator = BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_PHASE_INDICATOR
        if isShown:
            self._setComponentsVisibility(visible={phaseIndicator})
        elif BigWorld.player().arena.bonusType != ARENA_BONUS_TYPE.HISTORICAL_BATTLES:
            self._setComponentsVisibility(hidden={phaseIndicator})

    def _onBattleLoadingStart(self):
        self.fireEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.HISTORICAL_BATTLE_LOADING)), EVENT_BUS_SCOPE.BATTLE)
        super(HistoricalBattlePage, self)._onBattleLoadingStart()
        voice = BigWorld.player().arena.arenaType.wwmusicSetup.get('wwmusicLoadingVoice')
        mapName = BigWorld.player().arena.arenaType.name
        mapNameToVoiceoverDatestamp = HBAccountSettings.getSettings(AccountSettingsKeys.MAP_LOADING_VOICEOVER_DATESTAMPS)
        currentDay = date.today().day
        if voice is not None and currentDay != mapNameToVoiceoverDatestamp.get(mapName, 0):
            SoundGroups.g_instance.playSound2D(voice)
            mapNameToVoiceoverDatestamp[mapName] = currentDay
            HBAccountSettings.setSettings(AccountSettingsKeys.MAP_LOADING_VOICEOVER_DATESTAMPS, mapNameToVoiceoverDatestamp)
        return

    def _onBattleLoadingFinish(self):
        self.fireEvent(events.DestroyViewEvent(VIEW_ALIAS.HISTORICAL_BATTLE_LOADING), EVENT_BUS_SCOPE.BATTLE)
        super(HistoricalBattlePage, self)._onBattleLoadingFinish()
        if BigWorld.player().arena.period != ARENA_PERIOD.BATTLE:
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_PLAYERS_PANEL})

    def _getBattleLoadingVisibleAliases(self):
        return set()

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        super(HistoricalBattlePage, self)._onPostMortemSwitched(noRespawnPossible, respawnAvailable)
        alias = BATTLE_VIEW_ALIASES.RIBBONS_PANEL
        if self.as_isComponentVisibleS(alias):
            self._setComponentsVisibility(hidden={alias})
        if self._fullStatsAlias and self.as_isComponentVisibleS(self._fullStatsAlias):
            self._toggleFullStats(False)

    def _onRespawnBaseMoving(self):
        super(HistoricalBattlePage, self)._onRespawnBaseMoving()
        alias = BATTLE_VIEW_ALIASES.RIBBONS_PANEL
        if not self.as_isComponentVisibleS(alias):
            self._setComponentsVisibility(visible={alias})

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

    def __checkCanNotToggleFS(self, alias):
        manager = self.app.containerManager
        if manager.isModalViewsIsExists():
            return True
        elif self.getComponent(alias) is None:
            return True
        else:
            return True if self.hasFullScreenView(ignoreAlias=alias) else False

    def __destroyBattleSoundCtrl(self):
        if self.__soundBattleController:
            self.__soundBattleController.finalize()
            self.__soundBattleController = None
        return
