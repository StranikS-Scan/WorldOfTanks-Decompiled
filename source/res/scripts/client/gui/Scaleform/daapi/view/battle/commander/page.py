# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/page.py
import BigWorld
import BattleReplay
import aih_constants
import WWISE
from gui.Scaleform.daapi.view.battle.commander.six_sence_proxy import SixSenseCommanderVehiclesProxy
from helpers import dependency
from gui.Scaleform.daapi.view.battle.commander.indicators import SixthSenseSound
from gui.battle_control.controllers.commander.spawn_ctrl.interfaces import IRTSSpawnListener
from AvatarInputHandler import AvatarInputHandler, aih_global_binding
from gui.battle_control import avatar_getter
from skeletons.gui.app_loader import IAppLoader
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.Scaleform.daapi.view.battle.commander import markers2d, finish_sound_player
from gui.Scaleform.daapi.view.battle.shared import crosshair
from gui.Scaleform.daapi.view.battle.commander import drone_music_player
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.start_countdown_sound_player import StartCountdownSoundPlayer
from gui.Scaleform.daapi.view.battle.commander.player_formatter import RTSPlayerNameFormatter
from gui.Scaleform.daapi.view.battle.classic.page import DynamicAliases
from gui.Scaleform.daapi.view.meta.CommanderBattlePageMeta import CommanderBattlePageMeta
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.shared import EVENT_BUS_SCOPE, events
from gui.sounds.r4_sound_constants import R4_SOUND
from constants import ARENA_GUI_TYPE
_COMMANDER_EXTERNAL_COMPONENTS = (crosshair.CrosshairPanelContainer, markers2d.CommanderMarkersManager)
_CAMERA_RELATED_CMPS = (BATTLE_VIEW_ALIASES.VEHICLE_MESSAGES, BATTLE_VIEW_ALIASES.SIXTH_SENSE)
_TANKMAN_RELATED_COMPONENTS = (BATTLE_VIEW_ALIASES.BATTLE_MESSENGER,
 BATTLE_VIEW_ALIASES.DAMAGE_PANEL,
 BATTLE_VIEW_ALIASES.RIBBONS_PANEL,
 BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL,
 BATTLE_VIEW_ALIASES.TIMERS_PANEL,
 BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL)
_TANKMAN_HIDDEN_COMPONENTS = (BATTLE_VIEW_ALIASES.COMMANDER_VEHICLE_SELECTION, BATTLE_VIEW_ALIASES.COMMANDER_VEHICLES_PANEL)
_COMMANDER_RELATED_COMPONENTS = (BATTLE_VIEW_ALIASES.COMMANDER_VEHICLE_SELECTION, BATTLE_VIEW_ALIASES.COMMANDER_VEHICLES_PANEL, BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL)
_COMMANDER_HIDDEN_COMPONENTS = (BATTLE_VIEW_ALIASES.BATTLE_MESSENGER,
 BATTLE_VIEW_ALIASES.DAMAGE_PANEL,
 BATTLE_VIEW_ALIASES.RIBBONS_PANEL,
 BATTLE_VIEW_ALIASES.TIMERS_PANEL,
 BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,
 BATTLE_VIEW_ALIASES.COMMANDER_HELP)

class _DynamicAliases(object):
    SIXTH_SENSE_SOUND = 'SixthSenseSound'
    COMMANDER_VEHICLES_MGR_PROXY = 'cmdrVehMgrProxy'


class CommonRTSComponentsConfig(ComponentsConfig):

    def __init__(self):
        super(CommonRTSComponentsConfig, self).__init__(((BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.BATTLE_HINT,)),
         (BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
           BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
           DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER,
           BATTLE_VIEW_ALIASES.PLAYERS_PANEL,
           BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL,
           BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL,
           BATTLE_VIEW_ALIASES.HINT_PANEL,
           DynamicAliases.DRONE_MUSIC_PLAYER,
           BATTLE_VIEW_ALIASES.COMMANDER_SPAWN_MENU)),
         (BATTLE_CTRL_ID.CALLOUT, (BATTLE_VIEW_ALIASES.CALLOUT_PANEL,)),
         (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
         (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
         (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.DRONE_MUSIC_PLAYER, BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR, BATTLE_VIEW_ALIASES.PLAYERS_PANEL)),
         (BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS, (DynamicAliases.DRONE_MUSIC_PLAYER,)),
         (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,)),
         (BATTLE_CTRL_ID.PREBATTLE_SETUPS_CTRL, (BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, BATTLE_VIEW_ALIASES.DAMAGE_PANEL)),
         (BATTLE_CTRL_ID.AMMO, (BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL)),
         (BATTLE_CTRL_ID.SPAWN_CTRL, (BATTLE_VIEW_ALIASES.COMMANDER_SPAWN_MENU,)),
         (BATTLE_CTRL_ID.TEAM_SIXTH_SENSE, (BATTLE_VIEW_ALIASES.SIXTH_SENSE, _DynamicAliases.SIXTH_SENSE_SOUND, _DynamicAliases.COMMANDER_VEHICLES_MGR_PROXY))), viewsConfig=((DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, StartCountdownSoundPlayer), (_DynamicAliases.SIXTH_SENSE_SOUND, SixthSenseSound), (_DynamicAliases.COMMANDER_VEHICLES_MGR_PROXY, SixSenseCommanderVehiclesProxy)))


_COMMANDER_COMPONENTS = CommonRTSComponentsConfig() + ComponentsConfig(viewsConfig=((DynamicAliases.DRONE_MUSIC_PLAYER, drone_music_player.CommanderDroneMusicPlayer),))
_TANKMAN_COMPONENTS = CommonRTSComponentsConfig() + ComponentsConfig(viewsConfig=((DynamicAliases.DRONE_MUSIC_PLAYER, drone_music_player.DroneMusicPlayer),))
BASE_COMMANDER_EXTENDED_CMPNTS = ComponentsConfig(config=((BATTLE_CTRL_ID.ARENA_PERIOD, (DynamicAliases.FINISH_SOUND_PLAYER,)), (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.FINISH_SOUND_PLAYER,))), viewsConfig=((DynamicAliases.FINISH_SOUND_PLAYER, finish_sound_player.FinishSoundPlayer), ('r4FinishSoundPlayer', finish_sound_player.R4FinishSoundPlayer)))

class CommonCommanderBattlePage(CommanderBattlePageMeta, IRTSSpawnListener):
    __appLoader = dependency.descriptor(IAppLoader)
    aihCtrlModeName = aih_global_binding.bindRW(aih_global_binding.BINDING_ID.CTRL_MODE_NAME)
    _TOGGLE_COMPONENTS = {BATTLE_VIEW_ALIASES.COMMANDER_SPAWN_MENU}
    _FORCED_VISIBLE_COMPONENTS = {BATTLE_VIEW_ALIASES.PREBATTLE_TIMER}

    def __init__(self, components, external=_COMMANDER_EXTERNAL_COMPONENTS, fullStatsAlias=BATTLE_VIEW_ALIASES.FULL_STATS):
        super(CommonCommanderBattlePage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)
        self.__spawnMenuToggling = set()
        self.__isFullStatsShown = False
        self.__soundRemappingLabel = None
        self.sessionProvider.getCtx().setPlayerFullNameFormatter(RTSPlayerNameFormatter())
        return

    def getExternals(self):
        return self._external

    def setSpawnPoints(self, _):
        spawnMenuToggling = self.__spawnMenuToggling
        if spawnMenuToggling:
            return
        visibleComponents = self._TOGGLE_COMPONENTS
        spawnMenuToggling.update(set(self.as_getComponentsVisibilityS()) - visibleComponents)
        self._setComponentsVisibility(visible=visibleComponents | self._FORCED_VISIBLE_COMPONENTS, hidden=spawnMenuToggling - self._FORCED_VISIBLE_COMPONENTS)
        self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.COMMANDER_SPAWN_MENU)

    def closeSpawnPoints(self):
        spawnMenuToggling = self.__spawnMenuToggling
        if not spawnMenuToggling:
            return
        self._setComponentsVisibility(visible=spawnMenuToggling | self._FORCED_VISIBLE_COMPONENTS, hidden=self._TOGGLE_COMPONENTS)
        spawnMenuToggling.clear()
        self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.COMMANDER_SPAWN_MENU)

    def onEntitySelected(self):
        pass

    def updatePointsList(self):
        pass

    def _canShowPostmortemTips(self):
        return not self.__isFullStatsShown and super(CommonCommanderBattlePage, self)._canShowPostmortemTips()

    def _populate(self):
        super(CommonCommanderBattlePage, self)._populate()
        spawnCtrl = self.sessionProvider.dynamic.spawn
        if spawnCtrl:
            spawnCtrl.addRuntimeView(self)
        inputHandler = avatar_getter.getInputHandler()
        if isinstance(inputHandler, AvatarInputHandler):
            inputHandler.onCameraChanged += self.__onCameraChanged
        self.addListener(events.GameEvent.COMMANDER_HELP, self.__handleToggleCommanderHelp, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__soundRemappingLabel = self.__getSoundRemappingLabel()
        WWISE.activateRemapping(self.__soundRemappingLabel)

    def _dispose(self):
        self.removeListener(events.GameEvent.COMMANDER_HELP, self.__handleToggleCommanderHelp, scope=EVENT_BUS_SCOPE.BATTLE)
        spawnCtrl = self.sessionProvider.dynamic.spawn
        if spawnCtrl:
            spawnCtrl.removeRuntimeView(self)
        inputHandler = avatar_getter.getInputHandler()
        if isinstance(inputHandler, AvatarInputHandler):
            inputHandler.onCameraChanged -= self.__onCameraChanged
        WWISE.deactivateRemapping(self.__soundRemappingLabel)
        super(CommonCommanderBattlePage, self)._dispose()

    def _toggleRadialMenu(self, isShown, allowAction=True):
        if BigWorld.player().isCommander():
            isShown = False
        super(CommonCommanderBattlePage, self)._toggleRadialMenu(isShown)

    def _toggleFullStats(self, isShown, permanent=None, tabIndex=None):
        manager = self.app.containerManager
        if manager.isModalViewsIsExists():
            return
        elif self.__spawnMenuToggling:
            return
        else:
            self.__isFullStatsShown = isShown
            if isShown:
                contextMenuMgr = self.__appLoader.getApp().contextMenuManager
                if contextMenuMgr is not None:
                    contextMenuMgr.pyHide()
            self.__updateComponentsVisibility()
            super(CommonCommanderBattlePage, self)._toggleFullStats(isShown, permanent, tabIndex)
            return

    def _toggleGuiVisible(self):
        componentsVisibility = self.as_getComponentsVisibilityS()
        if BATTLE_VIEW_ALIASES.COMMANDER_SPAWN_MENU in componentsVisibility:
            return
        self.__updateComponentsVisibility()
        super(CommonCommanderBattlePage, self)._toggleGuiVisible()

    def _setComponentsVisibility(self, visible=None, hidden=None):
        visible = set(visible) if visible else set()
        hidden = set(hidden) if hidden else set()
        if BigWorld.player().isCommander() and BattleReplay.isPlaying() and not BattleReplay.isContollingCamera():
            hidden.add(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL)
        super(CommonCommanderBattlePage, self)._setComponentsVisibility(visible=visible, hidden=hidden)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(CommonCommanderBattlePage, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == BATTLE_VIEW_ALIASES.COMMANDER_SPAWN_MENU:
            self._setComponentsVisibility(hidden=[alias])

    def _onBattleLoadingFinish(self):
        super(CommonCommanderBattlePage, self)._onBattleLoadingFinish()
        self.__updateComponentsVisibility()

    def _onAvatarCtrlModeChanged(self, ctrlMode):
        if not self._isVisible or self._blToggling:
            return
        self._changeCtrlMode(ctrlMode)

    def _changeCtrlMode(self, ctrlMode):
        if self._fsToggling:
            if ctrlMode in aih_constants.CTRL_MODE_NAME.COMMANDER_MODES:
                self._fsToggling.difference_update(_COMMANDER_HIDDEN_COMPONENTS)
                self._fsToggling.update(_COMMANDER_RELATED_COMPONENTS)
                self._setComponentsVisibility(hidden=_COMMANDER_HIDDEN_COMPONENTS)
            else:
                self._fsToggling.difference_update(_TANKMAN_HIDDEN_COMPONENTS)
                self._fsToggling.update(_TANKMAN_RELATED_COMPONENTS)
                self._setComponentsVisibility(hidden=_TANKMAN_HIDDEN_COMPONENTS)
            return
        super(CommonCommanderBattlePage, self)._changeCtrlMode(ctrlMode)
        self.__updateComponentsVisibility(ctrlMode)

    def __handleToggleCommanderHelp(self, event):
        shouldBeShown = event.ctx.get('show')
        if self._isBattleLoading and not shouldBeShown:
            self._blToggling.difference_update((BATTLE_VIEW_ALIASES.COMMANDER_HELP,))
        if self.__isFullStatsShown:
            return
        else:
            if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.COMMANDER_HELP) != shouldBeShown:
                visibleComponents = set(self.as_getComponentsVisibilityS()) if self.as_getComponentsVisibilityS() else set()
                hiddenComponents = None
                if shouldBeShown:
                    visibleComponents.add(BATTLE_VIEW_ALIASES.COMMANDER_HELP)
                else:
                    visibleComponents.difference_update((BATTLE_VIEW_ALIASES.COMMANDER_HELP,))
                    hiddenComponents = {BATTLE_VIEW_ALIASES.COMMANDER_HELP}
                self._setComponentsVisibility(visible=visibleComponents, hidden=hiddenComponents)
            return

    def __onCameraChanged(self, __, _=None):
        if self.aihCtrlModeName in aih_constants.CTRL_MODE_NAME.COMMANDER_MODES:
            self._setComponentsVisibility(hidden=_CAMERA_RELATED_CMPS)
        else:
            self._setComponentsVisibility(visible=_CAMERA_RELATED_CMPS)
            sixthSenseComponent = self.getComponent(BATTLE_VIEW_ALIASES.SIXTH_SENSE)
            sixthSenseComponent.refresh()

    def __updateComponentsVisibility(self, ctrlMode=None):
        if ctrlMode is None:
            ctrlMode = avatar_getter.getInputHandler().ctrlModeName
        if ctrlMode in aih_constants.CTRL_MODE_NAME.COMMANDER_MODES:
            self._setComponentsVisibility(visible=_COMMANDER_RELATED_COMPONENTS, hidden=_COMMANDER_HIDDEN_COMPONENTS)
        else:
            self._setComponentsVisibility(hidden=[BATTLE_VIEW_ALIASES.COMMANDER_HELP])
            self._setComponentsVisibility(visible=_TANKMAN_RELATED_COMPONENTS, hidden=_TANKMAN_HIDDEN_COMPONENTS)
        return

    def __getSoundRemappingLabel(self):
        arenaGuiType = self.sessionProvider.arenaVisitor.getArenaGuiType()
        if arenaGuiType == ARENA_GUI_TYPE.RTS:
            if avatar_getter.isPlayerCommander():
                return R4_SOUND.SOUND_REMAPPING_LABEL_COMMANDER
            return R4_SOUND.SOUND_REMAPPING_LABEL_TANKMAN
        return R4_SOUND.SOUND_REMAPPING_LABEL_RTS_BOOTCAMP


class CommanderBattlePage(CommonCommanderBattlePage):

    def __init__(self):
        components = CommonRTSComponentsConfig() + ComponentsConfig(config=((BATTLE_CTRL_ID.TEAM_BASES, (BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, DynamicAliases.DRONE_MUSIC_PLAYER)),))
        if not self.sessionProvider.isReplayPlaying:
            components += BASE_COMMANDER_EXTENDED_CMPNTS + ComponentsConfig(config=((BATTLE_CTRL_ID.TEAM_BASES, (DynamicAliases.FINISH_SOUND_PLAYER,)),))
        if BigWorld.player().isCommander():
            droneMPClass = drone_music_player.CommanderDroneMusicPlayer
        else:
            droneMPClass = drone_music_player.DroneMusicPlayer
        components += ComponentsConfig(viewsConfig=((DynamicAliases.DRONE_MUSIC_PLAYER, droneMPClass),))
        super(CommanderBattlePage, self).__init__(components)
