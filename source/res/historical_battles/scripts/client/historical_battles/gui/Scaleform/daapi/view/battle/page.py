# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/battle/page.py
import typing
import BigWorld
import SoundGroups
from datetime import date
from debug_utils import LOG_DEBUG
from helpers import dependency
from shared_utils import CONST_CONTAINER
from aih_constants import CTRL_MODE_NAME
from gui.shared import EVENT_BUS_SCOPE, events
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from gui.Scaleform.daapi.view.battle.classic.page import DynamicAliases
from gui.Scaleform.daapi.view.battle.shared.indicators import createPredictionIndicator
from gui.shared.events import LoadViewEvent
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from helpers.CallbackDelayer import CallbackDelayer
import HBAccountSettings
from historical_battles_common.hb_constants import AccountSettingsKeys
from historical_battles_common.hb_constants_extension import ARENA_BONUS_TYPE
from HBAvatarRespawnComponent import HBAvatarRespawnComponent
from historical_battles.gui.Scaleform.daapi.settings import VIEW_ALIAS
from historical_battles.gui.Scaleform.daapi.view.battle.crosshair import HBCrosshairPanelContainer
from historical_battles.gui.Scaleform.daapi.view.battle.manager import HistoricalMarkersManager
from historical_battles.gui.Scaleform.daapi.view.battle.indicators import createHistoricalBattlesDamageIndicator
from historical_battles.gui.Scaleform.daapi.view.battle import start_countdown_sound_player
from historical_battles.gui.sounds import sound_battle_players
from historical_battles.gui.sounds.sound_battle_controller import SoundBattleController
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
if typing.TYPE_CHECKING:
    from typing import Any, Dict, Tuple
    from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class HBDynamicAliases(CONST_CONTAINER):
    EQUIPMENT_SOUND_PLAYER = 'equipmentSoundPlayer'


EVENT_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.BATTLE_HINT, BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_BASE_HINT)),
 (BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
   BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
   BATTLE_VIEW_ALIASES.HINT_PANEL,
   BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_PLAYERS_PANEL,
   DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER,
   HBDynamicAliases.EQUIPMENT_SOUND_PLAYER,
   BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_ENEMIES_PANEL)),
 (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_PLAYERS_PANEL, BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_ENEMIES_PANEL)),
 (BATTLE_CTRL_ID.CALLOUT, (BATTLE_VIEW_ALIASES.CALLOUT_PANEL,)),
 (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
 (BATTLE_CTRL_ID.RESPAWN, (BATTLE_VIEW_ALIASES.EPIC_RESPAWN_VIEW,)),
 (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
 (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,)),
 (BATTLE_CTRL_ID.HIT_DIRECTION, (BATTLE_VIEW_ALIASES.PREDICTION_INDICATOR, BATTLE_VIEW_ALIASES.HIT_DIRECTION)),
 (BATTLE_CTRL_ID.TEAM_BASES, (BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL,))), viewsConfig=((HBDynamicAliases.EQUIPMENT_SOUND_PLAYER, sound_battle_players.EquipmentSoundPlayer),
 (DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, start_countdown_sound_player.StartCountdownSoundPlayer),
 (BATTLE_VIEW_ALIASES.PREDICTION_INDICATOR, createPredictionIndicator),
 (BATTLE_VIEW_ALIASES.HIT_DIRECTION, createHistoricalBattlesDamageIndicator)))
_TUTORIAL_PAGES = ('eventHint1', 'eventHint2', 'eventHint3', 'eventHint4')
_FULL_SCREEN_VIEWS = {BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_STATS_WIDGET, BATTLE_VIEW_ALIASES.RADIAL_MENU, BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_RESPAWN}
_EVENT_EXTERNAL_COMPONENTS = (HBCrosshairPanelContainer, HistoricalMarkersManager)

class HistoricalBattlePage(ClassicPage):
    _gameEventController = dependency.descriptor(IGameEventController)
    _RESPAWN_WINDOW_DELAY = 4

    def __init__(self, components=None, external=_EVENT_EXTERNAL_COMPONENTS, fullStatsAlias=None):
        components = EVENT_CONFIG if not components else components
        super(HistoricalBattlePage, self).__init__(components=components, external=external, fullStatsAlias=BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_STATS_WIDGET)
        self.__callbackDelayer = CallbackDelayer()

    def hasFullScreenView(self, ignoreAlias=None):
        visibleFullScreenViews = self.__getVisibleFullScreenViews(ignoreAlias)
        return bool(visibleFullScreenViews)

    def _populate(self):
        super(HistoricalBattlePage, self)._populate()
        self.addListener(events.GameEvent.FULL_MAP_CMD, self._handleToggleFullMap, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__soundBattleController = SoundBattleController()
        self.__soundBattleController.start()
        LOG_DEBUG('Event battle page is created.')

    def _handleToggleFullMap(self, event):
        isDown = event.ctx['isDown']
        self._toggleFullMap(isDown)

    def _toggleFullMap(self, isShow):
        messenger = self.getComponent(BATTLE_VIEW_ALIASES.BATTLE_MESSENGER)
        minimapComponent = self.getComponent(BATTLE_VIEW_ALIASES.MINIMAP)
        if isShow and not minimapComponent.isFullViewMode():
            if not self.__checkFullScreenTransition(BATTLE_VIEW_ALIASES.MINIMAP):
                return
            self._fmToggling = set(self.as_getComponentsVisibilityS())
            self._fmToggling.add(BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_PHASE_INDICATOR)
            self._fmToggling.remove(BATTLE_VIEW_ALIASES.BATTLE_MESSENGER)
            if BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL in self._fmToggling:
                self._fmToggling.remove(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)
            if BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_RESPAWN in self._fmToggling:
                self._fmToggling.remove(BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_RESPAWN)
            toShow = {BATTLE_VIEW_ALIASES.MINIMAP}
            self._setComponentsVisibility(visible=toShow, hidden=self._fmToggling - toShow)
            messenger.toggleReadingMode(True)
            self.__activateFullMapControlMod()
            minimapComponent.setFullMapViewMode()
        elif not isShow and minimapComponent.isFullViewMode():
            self._setComponentsVisibility(hidden=None, visible=self._fmToggling)
            self._fmToggling.clear()
            messenger.toggleReadingMode(False)
            self.__activateFullMapControlMod(False)
            minimapComponent.setMiniMapViewMode()
        return

    def _dispose(self):
        super(HistoricalBattlePage, self)._dispose()
        self.removeListener(events.GameEvent.FULL_MAP_CMD, self._handleToggleFullMap, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__destroyBattleSoundCtrl()
        self.__destroyCallbackDelayer()
        LOG_DEBUG('Event battle page is destroyed.')

    def _startBattleSession(self):
        super(HistoricalBattlePage, self)._startBattleSession()
        HBAvatarRespawnComponent.onSpawn += self.__onSpawn
        HBAvatarRespawnComponent.onRespawn += self.__onRespawn

    def __onSpawn(self):
        self.__onRespawnVisibility(True)

    def __onRespawn(self):
        self.__onRespawnVisibility(False)

    def __onRespawnVisibility(self, isVisible):
        if self.sessionProvider.isReplayPlaying:
            return
        else:
            respawnAlias = BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_RESPAWN
            respawn = self.getComponent(respawnAlias)
            if respawn is None:
                return
            if isVisible:
                self._toggleFullMap(False)
                respawn.show()
                self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_RESPAWN, cursorVisible=True, enableAiming=False)
            else:
                respawn.hide()
                self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_RESPAWN)
            return

    def _stopBattleSession(self):
        HBAvatarRespawnComponent.onSpawn -= self.__onSpawn
        HBAvatarRespawnComponent.onRespawn -= self.__onRespawn
        super(HistoricalBattlePage, self)._stopBattleSession()

    def __activateFullMapControlMod(self, isActive=True):
        if isActive:
            self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.MINIMAP, cursorVisible=True, enableAiming=False)
        else:
            self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.MINIMAP)

    def _toggleRadialMenu(self, isShown, allowAction=True):
        radialMenuLinkage = BATTLE_VIEW_ALIASES.RADIAL_MENU
        radialMenu = self.getComponent(radialMenuLinkage)
        if radialMenu is None:
            return
        elif isShown and not self.__checkFullScreenTransition(radialMenuLinkage):
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
        if isShown and not self.__checkFullScreenTransition(self._fullStatsAlias):
            return
        if not isShown and not self._isInPostmortem and BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL in self._fsToggling:
            self._fsToggling.remove(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL)
        super(HistoricalBattlePage, self)._toggleFullStats(isShown, permanent=permanent, tabAlias=tabAlias)
        phaseIndicator = BATTLE_VIEW_ALIASES.HISTORICAL_BATTLES_PHASE_INDICATOR
        if isShown:
            self._setComponentsVisibility(visible={phaseIndicator})
        elif BigWorld.player().arena.bonusType not in ARENA_BONUS_TYPE.HB_RANGE:
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

    def _getBattleLoadingVisibleAliases(self):
        return set()

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        super(HistoricalBattlePage, self)._onPostMortemSwitched(noRespawnPossible, respawnAvailable)
        alias = BATTLE_VIEW_ALIASES.RIBBONS_PANEL
        if self.as_isComponentVisibleS(alias):
            self._setComponentsVisibility(hidden={alias})
        if self._fullStatsAlias and self.as_isComponentVisibleS(self._fullStatsAlias):
            self._toggleFullStats(False)
        self.__callbackDelayer.delayCallback(self._RESPAWN_WINDOW_DELAY, self.__onRespawnVisibility, BigWorld.player().HBAvatarRespawnComponent.respawnPrepared)

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

    def _getOverridedComponentsConfig(self, overrideConfig, overrideViewsConfig):
        config = []
        for ctrlID, aliases in EVENT_CONFIG.getConfig():
            if ctrlID in overrideConfig:
                override = aliases + overrideConfig[ctrlID]
                config.append((ctrlID, override))
            config.append((ctrlID, aliases))

        viewsConfig = EVENT_CONFIG.getViewsConfig() + overrideViewsConfig
        return ComponentsConfig(config=tuple(config), viewsConfig=viewsConfig)

    def __getVisibleFullScreenViews(self, ignoreAlias=None):
        fullScreenViews = set()
        minimapComponent = self.getComponent(BATTLE_VIEW_ALIASES.MINIMAP)
        if minimapComponent is not None and minimapComponent.isFullViewMode():
            fullScreenViews.add(BATTLE_VIEW_ALIASES.MINIMAP)
        fullScreenViews.update(_FULL_SCREEN_VIEWS)
        return {key for key in fullScreenViews if key != ignoreAlias and self.as_isComponentVisibleS(key)}

    def __checkFullScreenTransition(self, alias):
        manager = self.app.containerManager
        if manager.isModalViewsIsExists():
            return False
        elif self.getComponent(alias) is None:
            return False
        else:
            return False if self.hasFullScreenView(ignoreAlias=alias) else True

    def __destroyBattleSoundCtrl(self):
        if self.__soundBattleController:
            self.__soundBattleController.finalize()
            self.__soundBattleController = None
        return

    def __destroyCallbackDelayer(self):
        if self.__callbackDelayer:
            self.__callbackDelayer.destroy()
            self.__callbackDelayer = None
        return
