# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/page.py
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage, DynamicAliases
from gui.Scaleform.daapi.view.battle.shared.indicators import createPredictionIndicator, createDamageIndicator
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.start_countdown_sound_player import StartCountdownSoundPlayer
from white_tiger.gui.Scaleform.daapi.view.battle.drone_music_player import WTDroneMusicPlayer
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_BATTLE_VIEW_ALIASES import WHITE_TIGER_BATTLE_VIEW_ALIASES
from white_tiger.gui.Scaleform.daapi.view.battle.crosshair import WhiteTigerCrosshairPanelContainer
from white_tiger.skeletons.white_tiger_spawn_listener import ISpawnListener, SpawnType
from white_tiger.gui.Scaleform.daapi.view.battle.markers2d.manager import WhiteTigerMarkersManager
from white_tiger.gui.Scaleform.daapi.view.battle.player_format import WhiteTigerPlayerFullNameFormatter
from white_tiger.gui.shared.events import WhiteTigerEvent
from white_tiger.gui import white_tiger_gui_constants
from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import KillCamMarkersManager
from debug_utils import LOG_DEBUG
from shared_utils import CONST_CONTAINER
from white_tiger.cgf_components.sound_event_managers import WTRespawnSoundPlayer
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from white_tiger.gui.impl.battle.white_tiger_battle_loading import WhiteTigerBattleLoadingWindow
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
import BigWorld
from white_tiger.gui.wt_event_helpers import isBoss

class _SoundPlayerAliases(CONST_CONTAINER):
    WHITE_TIGER_RESPAWN_SOUND_PLAYER = 'wtRespawnSoundPlayer'
    WHITE_TIGER_BATTLE_HINT_SOUND = 'battle_hint_sound'


_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.BATTLE_HINTS, (WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_BATTLE_HINT, BATTLE_VIEW_ALIASES.BATTLE_TIMER)),
 (BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
   BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
   DynamicAliases.DRONE_MUSIC_PLAYER,
   DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER)),
 (BATTLE_CTRL_ID.TEAM_BASES, (BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL,)),
 (white_tiger_gui_constants.BATTLE_CTRL_ID.WT_BATTLE_GUI_CTRL, (WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_HUNTER_RESPAWN, WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_BOSS_TELEPORT, _SoundPlayerAliases.WHITE_TIGER_RESPAWN_SOUND_PLAYER)),
 (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_PLAYERS_PANEL,)),
 (BATTLE_CTRL_ID.HIT_DIRECTION, (BATTLE_VIEW_ALIASES.PREDICTION_INDICATOR, BATTLE_VIEW_ALIASES.HIT_DIRECTION)),
 (BATTLE_CTRL_ID.CALLOUT, (BATTLE_VIEW_ALIASES.CALLOUT_PANEL,)),
 (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
 (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
 (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,)),
 (BATTLE_CTRL_ID.AMMO, (BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,))), viewsConfig=((_SoundPlayerAliases.WHITE_TIGER_RESPAWN_SOUND_PLAYER, WTRespawnSoundPlayer),
 (DynamicAliases.DRONE_MUSIC_PLAYER, WTDroneMusicPlayer),
 (DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, StartCountdownSoundPlayer),
 (BATTLE_VIEW_ALIASES.PREDICTION_INDICATOR, createPredictionIndicator),
 (BATTLE_VIEW_ALIASES.HIT_DIRECTION, createDamageIndicator)))
_EXTERNAL_COMPONENTS = (WhiteTigerMarkersManager, WhiteTigerCrosshairPanelContainer, KillCamMarkersManager)

class WhiteTigerBattlePage(ClassicPage, ISpawnListener):

    def __init__(self, components=None, external=_EXTERNAL_COMPONENTS, fullStatsAlias=BATTLE_VIEW_ALIASES.FULL_STATS):
        self._spawnType = None
        self.__selectSpawnToggling = set()
        components = _CONFIG if not components else components + _CONFIG
        super(WhiteTigerBattlePage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)
        return

    @property
    def _spawnVisibleComponents(self):
        return {BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, BATTLE_VIEW_ALIASES.BATTLE_TIMER} if self._spawnType == SpawnType.TELEPORT else {WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_PLAYERS_PANEL, BATTLE_VIEW_ALIASES.BATTLE_TIMER, BATTLE_VIEW_ALIASES.BATTLE_MESSENGER}

    def _populate(self):
        super(WhiteTigerBattlePage, self)._populate()
        teleport = self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.WT_BATTLE_GUI_CTRL)
        if teleport:
            teleport.addRuntimeView(self)
        self.sessionProvider.getCtx().setPlayerFullNameFormatter(WhiteTigerPlayerFullNameFormatter())
        LOG_DEBUG('White tiger battle page is created.')

    def _dispose(self):
        super(WhiteTigerBattlePage, self)._dispose()
        teleport = self.sessionProvider.dynamic.getControllerByID(BATTLE_CTRL_ID.WT_BATTLE_GUI_CTRL)
        if teleport:
            teleport.removeRuntimeView(self)
        LOG_DEBUG('White tiger battle page is destroyed.')

    def _startBattleSession(self):
        super(WhiteTigerBattlePage, self)._startBattleSession()
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        g_playerEvents.onRoundFinished += self.__onRoundFinished

    def _stopBattleSession(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        super(WhiteTigerBattlePage, self)._stopBattleSession()

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self.__setVisibilityInitBattlePeriod()

    def __onRoundFinished(self, winningTeam, reason):
        hiddenComponents = {WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_HUD, WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_BATTLE_HINT}
        self._setComponentsVisibility(hidden=hiddenComponents)

    def __setVisibilityInitBattlePeriod(self):
        visibleComponents = {WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_PLAYERS_PANEL, WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_HUD}
        hiddenComponents = {BATTLE_VIEW_ALIASES.PREBATTLE_TIMER}
        self._setComponentsVisibility(visible=visibleComponents, hidden=hiddenComponents)

    def setSpawnType(self, spawnType):
        self._spawnType = spawnType

    def showSpawnPoints(self):
        if self.__selectSpawnToggling:
            return
        self._toggleFullStats(isShown=False)
        self.__selectSpawnToggling = set(self.as_getComponentsVisibilityS())
        visibleComponents = {self._spawnViewAlias, BATTLE_VIEW_ALIASES.MINIMAP, WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_HUD} | self._spawnVisibleComponents
        hiddenComponents = self.__selectSpawnToggling - visibleComponents
        self._setComponentsVisibility(visible=visibleComponents, hidden=hiddenComponents)
        self.app.enterGuiControlMode(self._spawnViewAlias)
        g_eventBus.handleEvent(WhiteTigerEvent(WhiteTigerEvent.SHOW_SPAWN_POINTS), scope=EVENT_BUS_SCOPE.GLOBAL)
        self.__toggleExternalComponentsVisibility(externalComponents=self._external, isVisible=False)

    def closeSpawnPoints(self):
        if not self.__selectSpawnToggling:
            return
        self._toggleFullStats(isShown=False)
        hiddenComponents = {self._spawnViewAlias}
        visibleComponents = self.__selectSpawnToggling - hiddenComponents
        self.__selectSpawnToggling = set()
        self._setComponentsVisibility(visible=visibleComponents, hidden=hiddenComponents)
        self.app.leaveGuiControlMode(self._spawnViewAlias)
        g_eventBus.handleEvent(WhiteTigerEvent(WhiteTigerEvent.HIDE_SPAWN_POINTS), scope=EVENT_BUS_SCOPE.GLOBAL)
        self.__toggleExternalComponentsVisibility(externalComponents=self._external, isVisible=True)

    def __toggleExternalComponentsVisibility(self, externalComponents, isVisible):
        for component in externalComponents:
            component.setVisible(isVisible)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(WhiteTigerBattlePage, self)._onRegisterFlashComponent(viewPy, alias)
        if alias in (WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_BOSS_TELEPORT, WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_HUNTER_RESPAWN):
            self._setComponentsVisibility(hidden={alias})

    @property
    def _spawnViewAlias(self):
        return WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_BOSS_TELEPORT if self._spawnType == SpawnType.TELEPORT else WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_HUNTER_RESPAWN

    def _onBattleLoadingStart(self):
        battleLoadingLayoutID = R.views.white_tiger.battle.WhiteTigerBattleLoading()
        self.app.enterGuiControlMode(battleLoadingLayoutID, cursorVisible=True, enableAiming=False)
        self.__showBattlePageGFComponent(battleLoadingLayoutID, WhiteTigerBattleLoadingWindow)
        super(WhiteTigerBattlePage, self)._onBattleLoadingStart()

    def _onBattleLoadingFinish(self):
        battleLoadingLayoutID = R.views.white_tiger.battle.WhiteTigerBattleLoading()
        self.app.leaveGuiControlMode(battleLoadingLayoutID)
        self.__destroyBattlePageGFComponent(battleLoadingLayoutID)
        if self.__isBossPlayer():
            self._blToggling.discard(BATTLE_VIEW_ALIASES.BATTLE_MESSENGER)
        super(WhiteTigerBattlePage, self)._onBattleLoadingFinish()
        self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.FULL_STATS})
        if BigWorld.player().arena.period != ARENA_PERIOD.BATTLE:
            self._setComponentsVisibility(hidden={WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_PLAYERS_PANEL, WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_HUD})
        else:
            self.__setVisibilityInitBattlePeriod()

    def _toggleFullStats(self, isShown, permanent=None, tabAlias=None):
        if permanent is None:
            permanent = set()
        permanent.add(WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_HUD)
        super(WhiteTigerBattlePage, self)._toggleFullStats(isShown, permanent=permanent, tabAlias=tabAlias)
        return

    def _setComponentsVisibility(self, visible=None, hidden=None):
        if visible is not None and BATTLE_VIEW_ALIASES.BATTLE_LOADING in visible:
            visible.remove(BATTLE_VIEW_ALIASES.BATTLE_LOADING)
        if hidden is not None and BATTLE_VIEW_ALIASES.BATTLE_LOADING in hidden:
            hidden.remove(BATTLE_VIEW_ALIASES.BATTLE_LOADING)
        super(WhiteTigerBattlePage, self)._setComponentsVisibility(visible, hidden)
        return

    def __showBattlePageGFComponent(self, layoutID, windowClass):
        guiLoader = dependency.instance(IGuiLoader)
        view = guiLoader.windowsManager.getViewByLayoutID(layoutID)
        if view is not None:
            view.getParentWindow().show()
        else:
            window = windowClass()
            window.load()
        return

    def __destroyBattlePageGFComponent(self, layoutID):
        guiLoader = dependency.instance(IGuiLoader)
        view = guiLoader.windowsManager.getViewByLayoutID(layoutID)
        if view is not None:
            view.destroyWindow()
        return

    def __isBossPlayer(self):
        vInfo = self.sessionProvider.getCtx().getVehicleInfo(BigWorld.player().playerVehicleID)
        tags = vInfo.vehicleType.tags
        return isBoss(tags)
