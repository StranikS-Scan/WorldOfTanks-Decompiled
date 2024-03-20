# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/page.py
import BigWorld
from BattleReplay import g_replayEvents
from battle_royale.gui.Scaleform.daapi.view.battle.respawn_message_panel import RespawnMessagePanel
from gui.battle_control.event_dispatcher import toggleCrosshairVisibility
from shared_utils import CONST_CONTAINER
import PlayerEvents
from constants import ARENA_PERIOD
from aih_constants import CTRL_MODE_NAME
from arena_bonus_type_caps import ARENA_BONUS_TYPE, ARENA_BONUS_TYPE_CAPS
from gui.battle_control import avatar_getter
from Event import EventsSubscriber
from battle_royale.gui.Scaleform.daapi.view.battle.markers2d.manager import BattleRoyaleMarkersManager
from battle_royale.gui.Scaleform.daapi.view.battle.player_format import BattleRoyalePlayerFullNameFormatter
from battle_royale.gui.Scaleform.daapi.view.battle.spawned_bot_msg import SpawnedBotMsgPlayerMsgs
from battle_royale.gui.Scaleform.daapi.view.battle.minefield_player_messenger import MinefieldPlayerMessenger
from gui.Scaleform.daapi.view.meta.BattleRoyalePageMeta import BattleRoyalePageMeta
from gui.Scaleform.daapi.view.battle.classic.page import DynamicAliases
from gui.Scaleform.daapi.view.battle.epic import drone_music_player
from gui.Scaleform.daapi.view.battle.shared import crosshair
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, VEHICLE_VIEW_STATE
from battle_royale.gui.battle_control.controllers.spawn_ctrl import ISpawnListener
from battle_royale.gui.br_effect_player import BRUpgradeEffectPlayer
from battle_royale.gui.game_control.br_battle_messages import ProgressionMessagesPlayer
from battle_royale.gui.battle_control.controllers.br_battle_sounds import BRBattleSoundController, RadarSoundPlayer, LevelSoundPlayer, EnemiesAmountSoundPlayer, PhaseSoundPlayer, PostmortemSoundPlayer, InstallModuleSoundPlayer, EquipmentSoundPlayer, SelectRespawnSoundPlayer, ArenaPeriodSoundPlayer

class _DynamicAliases(CONST_CONTAINER):
    SELECT_RESPAWN_SOUND_PLAYER = 'selectRespawnSoundPlayer'
    PROGRESSION_MESSAGES_PLAYER = 'progressionMessagesPlayer'
    RADAR_SOUND_PLAYER = 'radarSoundPlayer'
    LEVEL_SOUND_PLAYER = 'levelSoundPlayer'
    ENEMIES_AMOUNT_SOUND_PLAYER = 'enemiesAmountSoundPlayer'
    PHASE_SOUND_PLAYER = 'phaseSoundPlayer'
    POSTMORTEM_SOUND_PLAYER = 'postmortemSoundPlayer'
    INSTALL_MODULE_SOUND_PLAYER = 'installModuleSoundPlayer'
    ARENA_PERIOD_SOUND_PLAYER = 'arenaPeriodSoundPlayer'
    EQUIPMENT_SOUND_PLAYER = 'equipmentSoundPlayer'
    VEH_UPGRADE_EFFECT_PLAYER = 'vehicleUpgradeEffectPlayer'
    SPAWNED_BOT_MSG_PUBLISHER = 'SpawnedBotMsgPublisher'
    MINEFIELD_MSG_PUBLISHER = 'MinefieldMsgPublisher'
    RESPAWN_PANEL = 'RespawnPanel'


class _BattleRoyaleComponentsConfig(ComponentsConfig):

    def __init__(self):
        super(_BattleRoyaleComponentsConfig, self).__init__(((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
           BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
           BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
           BATTLE_VIEW_ALIASES.HINT_PANEL,
           DynamicAliases.DRONE_MUSIC_PLAYER,
           BATTLE_VIEW_ALIASES.RADAR_BUTTON,
           _DynamicAliases.ARENA_PERIOD_SOUND_PLAYER,
           _DynamicAliases.SELECT_RESPAWN_SOUND_PLAYER,
           BATTLE_VIEW_ALIASES.CORRODING_SHOT_INDICATOR,
           BATTLE_VIEW_ALIASES.BR_TIMERS_PANEL)),
         (BATTLE_CTRL_ID.PERKS, (BATTLE_VIEW_ALIASES.PERKS_PANEL,)),
         (BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.BATTLE_HINT,)),
         (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
         (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (BATTLE_VIEW_ALIASES.BATTLE_TEAM_PANEL, DynamicAliases.DRONE_MUSIC_PLAYER)),
         (BATTLE_CTRL_ID.PROGRESSION_CTRL, (BATTLE_VIEW_ALIASES.BATTLE_LEVEL_PANEL,
           BATTLE_VIEW_ALIASES.UPGRADE_PANEL,
           _DynamicAliases.PROGRESSION_MESSAGES_PLAYER,
           _DynamicAliases.LEVEL_SOUND_PLAYER,
           _DynamicAliases.PHASE_SOUND_PLAYER,
           _DynamicAliases.INSTALL_MODULE_SOUND_PLAYER,
           _DynamicAliases.VEH_UPGRADE_EFFECT_PLAYER,
           _DynamicAliases.SPAWNED_BOT_MSG_PUBLISHER,
           _DynamicAliases.MINEFIELD_MSG_PUBLISHER)),
         (BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS, (DynamicAliases.DRONE_MUSIC_PLAYER,)),
         (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,)),
         (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
         (BATTLE_CTRL_ID.RADAR_CTRL, (BATTLE_VIEW_ALIASES.RADAR_BUTTON, _DynamicAliases.RADAR_SOUND_PLAYER)),
         (BATTLE_CTRL_ID.SPAWN_CTRL, (BATTLE_VIEW_ALIASES.BR_SELECT_RESPAWN,
           BATTLE_VIEW_ALIASES.BR_RESPAWN_MESSAGE_PANEL,
           _DynamicAliases.SELECT_RESPAWN_SOUND_PLAYER,
           BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,
           BATTLE_VIEW_ALIASES.BATTLE_TEAM_PANEL)),
         (BATTLE_CTRL_ID.VEHICLES_COUNT_CTRL, (BATTLE_VIEW_ALIASES.FRAG_PANEL,
           BATTLE_VIEW_ALIASES.FULL_STATS,
           _DynamicAliases.ENEMIES_AMOUNT_SOUND_PLAYER,
           _DynamicAliases.PHASE_SOUND_PLAYER,
           _DynamicAliases.POSTMORTEM_SOUND_PLAYER,
           _DynamicAliases.ARENA_PERIOD_SOUND_PLAYER,
           _DynamicAliases.EQUIPMENT_SOUND_PLAYER)),
         (BATTLE_CTRL_ID.AMMO, (BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,))), ((DynamicAliases.DRONE_MUSIC_PLAYER, drone_music_player.DroneMusicPlayer),
         (_DynamicAliases.SELECT_RESPAWN_SOUND_PLAYER, SelectRespawnSoundPlayer),
         (_DynamicAliases.PROGRESSION_MESSAGES_PLAYER, ProgressionMessagesPlayer),
         (_DynamicAliases.RADAR_SOUND_PLAYER, RadarSoundPlayer),
         (_DynamicAliases.LEVEL_SOUND_PLAYER, LevelSoundPlayer),
         (_DynamicAliases.ENEMIES_AMOUNT_SOUND_PLAYER, EnemiesAmountSoundPlayer),
         (_DynamicAliases.PHASE_SOUND_PLAYER, PhaseSoundPlayer),
         (_DynamicAliases.POSTMORTEM_SOUND_PLAYER, PostmortemSoundPlayer),
         (_DynamicAliases.INSTALL_MODULE_SOUND_PLAYER, InstallModuleSoundPlayer),
         (_DynamicAliases.ARENA_PERIOD_SOUND_PLAYER, ArenaPeriodSoundPlayer),
         (_DynamicAliases.VEH_UPGRADE_EFFECT_PLAYER, BRUpgradeEffectPlayer),
         (_DynamicAliases.EQUIPMENT_SOUND_PLAYER, EquipmentSoundPlayer),
         (_DynamicAliases.SPAWNED_BOT_MSG_PUBLISHER, SpawnedBotMsgPlayerMsgs),
         (_DynamicAliases.MINEFIELD_MSG_PUBLISHER, MinefieldPlayerMessenger),
         (_DynamicAliases.RESPAWN_PANEL, RespawnMessagePanel)))


_BATTLE_ROYALE_CFG = _BattleRoyaleComponentsConfig()

class BattleRoyalePage(BattleRoyalePageMeta, ISpawnListener):
    __PANELS_FOR_SHOW_HIDE = [BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, BATTLE_VIEW_ALIASES.BATTLE_LEVEL_PANEL]

    def __init__(self, components=None):
        if components is None:
            components = _BATTLE_ROYALE_CFG
        self.__selectSpawnToggling = set()
        self.__winScreenToggling = set()
        self.__brSoundControl = None
        self.__isFullStatsShown = False
        self.__isWinnerScreenShown = False
        self.__panelsIsVisible = False
        self.__es = EventsSubscriber()
        self.__isAllowToogleGuiVisible = False
        self.__canShowHUD = True
        self.__hudComponents = set()
        super(BattleRoyalePage, self).__init__(components, external=(crosshair.CrosshairPanelContainer, BattleRoyaleMarkersManager))
        return

    def showSpawnPoints(self):
        visibleComponents = [BATTLE_VIEW_ALIASES.BR_SELECT_RESPAWN]
        if ARENA_BONUS_TYPE_CAPS.checkAny(BigWorld.player().arena.bonusType, ARENA_BONUS_TYPE_CAPS.SQUADS):
            visibleComponents.extend([BATTLE_VIEW_ALIASES.BATTLE_TEAM_PANEL, BATTLE_VIEW_ALIASES.BATTLE_MESSENGER])
        if not self.__selectSpawnToggling:
            self.__selectSpawnToggling.update(set(self.as_getComponentsVisibilityS()) - set(visibleComponents))
        self.__canShowHUD = False
        self._setComponentsVisibility(visible=visibleComponents, hidden=self.__selectSpawnToggling)
        self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.BR_SELECT_RESPAWN, stopVehicle=True)

    def closeSpawnPoints(self):
        self.__isAllowToogleGuiVisible = True
        if self.__selectSpawnToggling or self.__hudComponents:
            self.__canShowHUD = True
            self.__selectSpawnToggling.update(self.__hudComponents)
            self.__hudComponents.clear()
            self._setComponentsVisibility(visible=self.__selectSpawnToggling, hidden=[BATTLE_VIEW_ALIASES.BR_SELECT_RESPAWN])
            self.__selectSpawnToggling.clear()
            self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.BR_SELECT_RESPAWN)

    def isFullStatsShown(self):
        return self.__isFullStatsShown

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self._updatePostmortemTips()
        if not self.sessionProvider.getCtx().isPlayerObserver():
            self._isInPostmortem = True
            self._switchToPostmortem()

    @property
    def isPostmortemTispVisible(self):
        if avatar_getter.isObserverSeesAll():
            return False
        bonusType = BigWorld.player().arenaBonusType
        isTournament = bonusType in (ARENA_BONUS_TYPE.BATTLE_ROYALE_TRN_SOLO, ARENA_BONUS_TYPE.BATTLE_ROYALE_TRN_SQUAD)
        vehicleCountCtrl = self.sessionProvider.dynamic.vehicleCount
        arenaDP = self.sessionProvider.getArenaDP()
        if vehicleCountCtrl and vehicleCountCtrl.getTeamCount() <= 1 and arenaDP.getVehicleInfo().isAlive() or isTournament:
            return False
        if not (self._canShowPostmortemTips() and not self.__isFullStatsShown and not self.__isWinnerScreenShown and BigWorld.player().isFollowWinner()):
            return False
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        if componentSystem and componentSystem.battleRoyaleComponent:
            playerTeam = self.sessionProvider.getArenaDP().getVehicleInfo().team
            defeatedTeams = set(componentSystem.battleRoyaleComponent.defeatedTeams)
            return playerTeam in defeatedTeams
        return False

    def _updatePostmortemTips(self):
        self.as_setPostmortemTipsVisibleS(self.isPostmortemTispVisible)

    def _onDefeatedTeamsUpdated(self, *_):
        self._updatePostmortemTips()

    def _toggleFullStats(self, isShown, permanent=None, tabAlias=None):
        manager = self.app.containerManager
        if manager.isModalViewsIsExists():
            return
        else:
            self.__isFullStatsShown = isShown
            if permanent is None:
                permanent = set()
            permanent.add('minimap')
            if isShown:
                progressionWindow = self.__getProgressionWindowCtrl()
                if progressionWindow:
                    progressionWindow.closeWindow()
            if self.__selectSpawnToggling or self.__isWinnerScreenShown:
                return
            super(BattleRoyalePage, self)._toggleFullStats(isShown, permanent, tabAlias)
            self._updatePostmortemTips()
            return

    def _populate(self):
        super(BattleRoyalePage, self)._populate()
        progressionWindowCtrl = self.__getProgressionWindowCtrl()
        if progressionWindowCtrl:
            self.__es.subscribeToEvent(progressionWindowCtrl.onTriggered, self.__onConfWindowTriggered)
        self.sessionProvider.getCtx().setPlayerFullNameFormatter(BattleRoyalePlayerFullNameFormatter())
        if avatar_getter.isObserverSeesAll():
            self.__es.subscribeToEvent(avatar_getter.getInputHandler().onCameraChanged, self.__onCameraChanged)
        if self.sessionProvider.isReplayPlaying:
            self.__es.subscribeToEvent(g_replayEvents.onTimeWarpStart, self.__onTimeWarpStart)
        self.__brSoundControl = BRBattleSoundController()
        self.__brSoundControl.init()
        crosshairCtrl = self.sessionProvider.shared.crosshair
        if crosshairCtrl:
            self.__es.subscribeToEvent(crosshairCtrl.onCrosshairViewChanged, self.__onCrosshairViewChanged)

    def _onWinScreenReload(self):
        alias = BATTLE_VIEW_ALIASES.BATTLE_ROYALE_WINNER_CONGRATS
        if self.__isWinnerScreenShown:
            self.__isWinnerScreenShown = False
            self._setComponentsVisibility(visible=self.__winScreenToggling, hidden=[alias])
            self.__winScreenToggling.clear()
            toggleCrosshairVisibility()

    def _startBattleSession(self):
        super(BattleRoyalePage, self)._startBattleSession()
        vehStateCtrl = self.sessionProvider.shared.vehicleState
        if vehStateCtrl is not None:
            self._battleSessionES.subscribeToEvent(vehStateCtrl.onVehicleStateUpdated, self.__onVehicleStateUpdated)
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            self._battleSessionES.subscribeToEvent(ammoCtrl.onGunSettingsSet, self.__onGunSettingsSet)
        componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
        if componentSystem and componentSystem.battleRoyaleComponent:
            self._battleSessionES.subscribeToEvent(componentSystem.battleRoyaleComponent.onBattleRoyaleDefeatedTeamsUpdate, self._onDefeatedTeamsUpdated)
        deathScreenCtrl = self.sessionProvider.dynamic.deathScreen
        if deathScreenCtrl:
            self._battleSessionES.subscribeToEvent(deathScreenCtrl.onShowDeathScreen, self.__onShowDeathScreen)
            self._battleSessionES.subscribeToEvent(deathScreenCtrl.onWinnerScreen, self.__onWinnerScreen)
        spawnCtrl = self.sessionProvider.dynamic.spawn
        if spawnCtrl and self not in spawnCtrl.viewComponents:
            spawnCtrl.addRuntimeView(self)
            self._battleSessionES.addCallbackOnUnsubscribe(lambda : spawnCtrl.removeRuntimeView(self))
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(BattleRoyalePage, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == BATTLE_VIEW_ALIASES.BR_SELECT_RESPAWN:
            self._setComponentsVisibility(hidden=[alias])
            return
        if avatar_getter.isObserverSeesAll():
            if alias == BATTLE_VIEW_ALIASES.BATTLE_MESSENGER:
                self._setComponentsVisibility(hidden=[alias])
        elif alias == BATTLE_VIEW_ALIASES.PLAYERS_PANEL:
            self._setComponentsVisibility(hidden=[alias])

    def _onBattleLoadingFinish(self):
        arenaPeriod = self.sessionProvider.shared.arenaPeriod.getPeriod()
        self.__canShowHUD = arenaPeriod not in (ARENA_PERIOD.IDLE, ARENA_PERIOD.WAITING) or BigWorld.player().observerSeesAll()
        super(BattleRoyalePage, self)._onBattleLoadingFinish()
        if not self.__canShowHUD and not BigWorld.player().observerSeesAll():
            self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.BR_SELECT_RESPAWN})

    def _setComponentsVisibility(self, visible=None, hidden=None):
        if self.__isWinnerScreenShown:
            return
        if not self.__canShowHUD and visible:
            hasNoHUD = {BATTLE_VIEW_ALIASES.BR_SELECT_RESPAWN, BATTLE_VIEW_ALIASES.BATTLE_LOADING} & set(visible)
            if not hasNoHUD:
                self.__hudComponents.update(visible)
                super(BattleRoyalePage, self)._setComponentsVisibility(hidden=hidden)
                return
        super(BattleRoyalePage, self)._setComponentsVisibility(visible=visible, hidden=hidden)

    def _toggleGuiVisible(self):
        componentsVisibility = self.as_getComponentsVisibilityS()
        if BATTLE_VIEW_ALIASES.BR_SELECT_RESPAWN in componentsVisibility:
            return
        if not self.__isAllowToogleGuiVisible:
            return
        super(BattleRoyalePage, self)._toggleGuiVisible()

    def _dispose(self):
        if self.__brSoundControl is not None:
            self.__brSoundControl.destroy()
            self.__brSoundControl = None
        self.__selectSpawnToggling.clear()
        self.__es.unsubscribeFromAllEvents()
        super(BattleRoyalePage, self)._dispose()
        return

    def _switchToPostmortem(self):
        BigWorld.player().setIsObserver()

    def __onCrosshairViewChanged(self, viewID):
        self.as_setCrosshairModeS(viewID)

    def __onCameraChanged(self, ctrlMode, _=None):
        teamPanelAliases = (CTRL_MODE_NAME.POSTMORTEM, CTRL_MODE_NAME.VIDEO)
        if ctrlMode in teamPanelAliases:
            args = {'hidden': {BATTLE_VIEW_ALIASES.BATTLE_TEAM_PANEL},
             'visible': {BATTLE_VIEW_ALIASES.PLAYERS_PANEL}}
        else:
            args = {'hidden': {BATTLE_VIEW_ALIASES.PLAYERS_PANEL},
             'visible': {BATTLE_VIEW_ALIASES.BATTLE_TEAM_PANEL}}
        args['hidden' if ctrlMode == CTRL_MODE_NAME.VIDEO else 'visible'].add(BATTLE_VIEW_ALIASES.BATTLE_LEVEL_PANEL)
        self._setComponentsVisibility(**args)

    def __onConfWindowTriggered(self, isOpened):
        if isOpened:
            if not self.as_isComponentVisibleS(self._fullStatsAlias):
                self._fsToggling = set(self.as_getComponentsVisibilityS())
            self._setComponentsVisibility(visible=[], hidden=self._fsToggling)
        elif self._fsToggling:
            self._setComponentsVisibility(visible=self._fsToggling, hidden=[])

    def __getProgressionWindowCtrl(self):
        progression = self.sessionProvider.dynamic.progression
        return progression.getWindowCtrl() if progression else None

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.DEATHZONE_TIMER and value.level is None:
            vehicle = self.sessionProvider.shared.vehicleState.getControllingVehicle()
            isAlive = vehicle is not None and vehicle.isAlive()
            self.as_updateDamageScreenS(value.isCausingDamage and isAlive)
        elif state in (VEHICLE_VIEW_STATE.SWITCHING, VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.CREW_DEACTIVATED):
            self.as_updateDamageScreenS(False)
        vehicle = BigWorld.player().getVehicleAttached()
        if vehicle is None or not vehicle.isAlive() and BigWorld.player().isObserver():
            if self.__panelsIsVisible:
                self._setComponentsVisibility(hidden=self.__PANELS_FOR_SHOW_HIDE)
                self.__panelsIsVisible = False
        elif not self.__panelsIsVisible:
            self._setComponentsVisibility(visible=self.__PANELS_FOR_SHOW_HIDE)
            self.__panelsIsVisible = True
        if vehicle and not vehicle.isAlive():
            if avatar_getter.isBecomeObserverAfterDeath() and BigWorld.player().isObserverBothTeams:
                self._setComponentsVisibility(visible=[BATTLE_VIEW_ALIASES.PLAYERS_PANEL, BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL])
                BigWorld.player().setIsObserver()
        return

    def __onGunSettingsSet(self, _):
        progressionWindowCtrl = self.__getProgressionWindowCtrl()
        if progressionWindowCtrl and progressionWindowCtrl.isWindowOpened():
            isDualGunVehicle = self.sessionProvider.getArenaDP().getVehicleInfo().vehicleType.isDualGunVehicle
            dualGunAlias = BATTLE_VIEW_ALIASES.DUAL_GUN_PANEL
            if not isDualGunVehicle:
                if dualGunAlias in self._fsToggling:
                    self._fsToggling.remove(dualGunAlias)

    def __onShowDeathScreen(self):
        if self.as_isComponentVisibleS(self._fullStatsAlias):
            self._setComponentsVisibility(visible={self._fullStatsAlias}, hidden=[BATTLE_VIEW_ALIASES.BR_PLAYER_STATS_IN_BATTLE])
            self._fsToggling.add(BATTLE_VIEW_ALIASES.BR_PLAYER_STATS_IN_BATTLE)

    def __onWinnerScreen(self, *_):
        if not BigWorld.player().userSeesWorld():
            self.__es.subscribeToEvent(PlayerEvents.g_playerEvents.crosshairPanelInitialized, self.__onWinnerScreen)
            return
        hideSet = set(self.as_getComponentsVisibilityS())
        hideSet.difference_update([BATTLE_VIEW_ALIASES.BATTLE_ROYALE_WINNER_CONGRATS])
        if not self.__winScreenToggling:
            self.__winScreenToggling.update(hideSet)
        self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.BATTLE_ROYALE_WINNER_CONGRATS}, hidden=hideSet)
        self.__isWinnerScreenShown = True
        toggleCrosshairVisibility()
        avatar_getter.setComponentsVisibility(False)

    def __onTimeWarpStart(self):
        self._onWinScreenReload()
