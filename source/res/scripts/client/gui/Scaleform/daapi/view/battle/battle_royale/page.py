# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/page.py
import BigWorld
from helpers import dependency
from shared_utils import CONST_CONTAINER
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from gui.Scaleform.daapi.view.meta.BattleRoyalePageMeta import BattleRoyalePageMeta
from gui.Scaleform.daapi.view.battle.classic.page import DynamicAliases
from gui.Scaleform.daapi.view.battle.epic import drone_music_player
from gui.Scaleform.daapi.view.battle.shared import period_music_listener, crosshair
from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import MarkersManager
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, VEHICLE_VIEW_STATE
from gui.battle_control.controllers.spawn_ctrl import ISpawnListener
from gui.battle_royale.br_effect_player import BRUpgradeEffectPlayer
from gui.game_control.br_battle_messages import ProgressionMessagesPlayer
from gui.game_control.br_battle_sounds import BRBattleSoundController, RadarSoundPlayer, LevelSoundPlayer, EnemiesAmountSoundPlayer, PhaseSoundPlayer, PostmortemSoundPlayer, InstallModuleSoundPlayer, EquipmentSoundPlayer
from gui.game_control.br_battle_sounds import SelectRespawnSoundPlayer, ArenaPeriodSoundPlayer
from skeletons.gui.battle_session import IBattleSessionProvider

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


class _BattleRoyaleComponentsConfig(ComponentsConfig):

    def __init__(self):
        super(_BattleRoyaleComponentsConfig, self).__init__(((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
           BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
           BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
           BATTLE_VIEW_ALIASES.HINT_PANEL,
           DynamicAliases.DRONE_MUSIC_PLAYER,
           DynamicAliases.PERIOD_MUSIC_LISTENER,
           BATTLE_VIEW_ALIASES.RADAR_BUTTON,
           _DynamicAliases.ARENA_PERIOD_SOUND_PLAYER,
           _DynamicAliases.SELECT_RESPAWN_SOUND_PLAYER)),
         (BATTLE_CTRL_ID.TEAM_BASES, (BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, DynamicAliases.DRONE_MUSIC_PLAYER)),
         (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
         (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (BATTLE_VIEW_ALIASES.BATTLE_TEAM_PANEL, DynamicAliases.DRONE_MUSIC_PLAYER)),
         (BATTLE_CTRL_ID.PROGRESSION_CTRL, (BATTLE_VIEW_ALIASES.BATTLE_LEVEL_PANEL,
           BATTLE_VIEW_ALIASES.UPGRADE_PANEL,
           _DynamicAliases.PROGRESSION_MESSAGES_PLAYER,
           _DynamicAliases.LEVEL_SOUND_PLAYER,
           _DynamicAliases.PHASE_SOUND_PLAYER,
           _DynamicAliases.INSTALL_MODULE_SOUND_PLAYER,
           _DynamicAliases.VEH_UPGRADE_EFFECT_PLAYER)),
         (BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS, (DynamicAliases.DRONE_MUSIC_PLAYER,)),
         (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,)),
         (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
         (BATTLE_CTRL_ID.RADAR_CTRL, (BATTLE_VIEW_ALIASES.RADAR_BUTTON, _DynamicAliases.RADAR_SOUND_PLAYER)),
         (BATTLE_CTRL_ID.SPAWN_CTRL, (BATTLE_VIEW_ALIASES.BR_SELECT_RESPAWN, _DynamicAliases.SELECT_RESPAWN_SOUND_PLAYER)),
         (BATTLE_CTRL_ID.VEHICLES_COUNT_CTRL, (BATTLE_VIEW_ALIASES.FRAG_PANEL,
           _DynamicAliases.ENEMIES_AMOUNT_SOUND_PLAYER,
           _DynamicAliases.PHASE_SOUND_PLAYER,
           _DynamicAliases.POSTMORTEM_SOUND_PLAYER,
           _DynamicAliases.ARENA_PERIOD_SOUND_PLAYER,
           _DynamicAliases.EQUIPMENT_SOUND_PLAYER))), ((DynamicAliases.PERIOD_MUSIC_LISTENER, period_music_listener.PeriodMusicListener),
         (DynamicAliases.DRONE_MUSIC_PLAYER, drone_music_player.DroneMusicPlayer),
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
         (_DynamicAliases.EQUIPMENT_SOUND_PLAYER, EquipmentSoundPlayer)))


_BATTLE_ROYALE_CFG = _BattleRoyaleComponentsConfig()

class BattleRoyalePage(BattleRoyalePageMeta, ISpawnListener):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, components=None):
        if components is None:
            components = _BATTLE_ROYALE_CFG
        self.__selectSpawnToggling = set()
        self.__brSoundControl = None
        super(BattleRoyalePage, self).__init__(components, external=(crosshair.CrosshairPanelContainer, MarkersManager))
        return

    def showSpawnPoints(self):
        visibleComponents = [BATTLE_VIEW_ALIASES.BR_SELECT_RESPAWN]
        if ARENA_BONUS_TYPE_CAPS.checkAny(BigWorld.player().arena.bonusType, ARENA_BONUS_TYPE_CAPS.SQUADS):
            visibleComponents.extend([BATTLE_VIEW_ALIASES.BATTLE_TEAM_PANEL, BATTLE_VIEW_ALIASES.BATTLE_MESSENGER])
        if not self.__selectSpawnToggling:
            self.__selectSpawnToggling.update(set(self.as_getComponentsVisibilityS()) - set(visibleComponents))
        self._setComponentsVisibility(visible=visibleComponents, hidden=self.__selectSpawnToggling)
        self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.BR_SELECT_RESPAWN)

    def closeSpawnPoints(self):
        if self.__selectSpawnToggling:
            self._setComponentsVisibility(visible=self.__selectSpawnToggling, hidden=[BATTLE_VIEW_ALIASES.BR_SELECT_RESPAWN])
            self.__selectSpawnToggling.clear()
            self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.BR_SELECT_RESPAWN)

    def _toggleFullStats(self, isShown, permanent=None, tabIndex=None):
        if permanent is None:
            permanent = set()
        permanent.add('minimap')
        if isShown:
            progressionWindow = self.__getProgressionWindowCtrl()
            if progressionWindow:
                progressionWindow.closeWindow()
        if self.__selectSpawnToggling:
            return
        else:
            super(BattleRoyalePage, self)._toggleFullStats(isShown, permanent, tabIndex)
            return

    def _populate(self):
        super(BattleRoyalePage, self)._populate()
        progressionWindowCtrl = self.__getProgressionWindowCtrl()
        if progressionWindowCtrl:
            progressionWindowCtrl.onTriggered += self.__onConfWindowTriggered
        spawnCtrl = self.guiSessionProvider.dynamic.spawn
        if spawnCtrl:
            spawnCtrl.addRuntimeView(self)
        deathScreenCtrl = self.guiSessionProvider.dynamic.deathScreen
        if deathScreenCtrl:
            deathScreenCtrl.onShowDeathScreen += self.__onShowDeathScreen
        vehStateCtrl = self.sessionProvider.shared.vehicleState
        if vehStateCtrl is not None:
            vehStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vehStateCtrl.onVehicleControlling += self.__onVehicleControlling
        self.__brSoundControl = BRBattleSoundController()
        self.__brSoundControl.init()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(BattleRoyalePage, self)._onRegisterFlashComponent(viewPy, alias)
        if alias in (BATTLE_VIEW_ALIASES.BR_SELECT_RESPAWN, BATTLE_VIEW_ALIASES.BR_SCORE_DEATH_SCREEN):
            self._setComponentsVisibility(hidden=[alias])

    def _toggleGuiVisible(self):
        componentsVisibility = self.as_getComponentsVisibilityS()
        if BATTLE_VIEW_ALIASES.BR_SELECT_RESPAWN in componentsVisibility:
            return
        super(BattleRoyalePage, self)._toggleGuiVisible()

    def _definePostmortemPanel(self):
        self.as_useEventPostmortemPanelS(False)

    def _dispose(self):
        progressionWindowCtrl = self.__getProgressionWindowCtrl()
        if progressionWindowCtrl:
            progressionWindowCtrl.onTriggered -= self.__onConfWindowTriggered
        spawnCtrl = self.guiSessionProvider.dynamic.spawn
        if spawnCtrl:
            spawnCtrl.removeRuntimeView(self)
        deathScreenCtrl = self.guiSessionProvider.dynamic.deathScreen
        if deathScreenCtrl:
            deathScreenCtrl.onShowDeathScreen -= self.__onShowDeathScreen
        vehStateCtrl = self.sessionProvider.shared.vehicleState
        if vehStateCtrl is not None:
            vehStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            vehStateCtrl.onVehicleControlling -= self.__onVehicleControlling
        if self.__brSoundControl is not None:
            self.__brSoundControl.destroy()
            self.__brSoundControl = None
        self.__selectSpawnToggling.clear()
        super(BattleRoyalePage, self)._dispose()
        return

    def __onConfWindowTriggered(self, isOpened):
        if isOpened:
            if not self.as_isComponentVisibleS(self._fullStatsAlias):
                self._fsToggling = set(self.as_getComponentsVisibilityS())
            self._setComponentsVisibility(visible=[], hidden=self._fsToggling)
        elif self._fsToggling:
            self._setComponentsVisibility(visible=self._fsToggling, hidden=[])

    def __getProgressionWindowCtrl(self):
        progression = self.guiSessionProvider.dynamic.progression
        return progression.getWindowCtrl() if progression else None

    def __onShowDeathScreen(self):
        self.as_setPostmortemTipsVisibleS(False)
        self._setComponentsVisibility(hidden=self.as_getComponentsVisibilityS())
        self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.BR_RESULTS_DEATH_SCREEN, cursorVisible=True, enableAiming=False)

    def __onVehicleControlling(self, vehicle):
        ctrl = self.sessionProvider.shared.vehicleState
        checkStatesIDs = (VEHICLE_VIEW_STATE.DEATHZONE_TIMER,)
        for stateID in checkStatesIDs:
            stateValue = ctrl.getStateValue(stateID)
            if stateValue:
                self.__onVehicleStateUpdated(stateID, stateValue)

    def __onVehicleStateUpdated(self, state, value):
        if state == VEHICLE_VIEW_STATE.DEATHZONE_TIMER and value.level is None:
            vehicle = self.sessionProvider.shared.vehicleState.getControllingVehicle()
            isAlive = vehicle is not None and vehicle.isAlive()
            self.as_updateDamageScreenS(value.isCausingDamage and isAlive)
        elif state in (VEHICLE_VIEW_STATE.SWITCHING, VEHICLE_VIEW_STATE.DESTROYED, VEHICLE_VIEW_STATE.CREW_DEACTIVATED):
            self.as_updateDamageScreenS(False)
        return
