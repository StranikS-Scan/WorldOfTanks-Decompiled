# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/page.py
import BigWorld
from aih_constants import CTRL_MODE_NAME
from gui.Scaleform.daapi.view.battle.event.crosshair import EventCrosshairPanelContainer
from gui.battle_control.controllers.teleport_spawn_ctrl import ISpawnListener, SpawnType
from gui.Scaleform.daapi.view.battle.event import indicators
from gui.Scaleform.daapi.view.battle.event.wt_battle_sounds_player import BattleHintSoundPlayer
from shared_utils import CONST_CONTAINER
from constants import ARENA_PERIOD
from debug_utils import LOG_DEBUG
from adisp import adisp_process
from PlayerEvents import g_playerEvents
from frameworks.wulf import WindowLayer
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.events import GameEvent
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IEventBattlesController
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from gui.Scaleform.daapi.view.battle.classic.page import DynamicAliases
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.event.manager import EventMarkersManager
from gui.Scaleform.daapi.view.battle.shared.start_countdown_sound_player import StartCountdownSoundPlayer
from gui.Scaleform.daapi.view.battle.event.drone_music_player import EventDroneMusicPlayer
from gui.shared.events import LoadViewEvent
from gui.wt_event.wt_event_helpers import isBoss
from gui.impl.lobby.wt_event.wt_event_sound import playBossWidgetAppears
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from cgf_components.wt_sounds_manager import RespawnSoundPlayer

class _SoundPlayerAliases(CONST_CONTAINER):
    RESPAWN_SOUND_PLAYER = 'respawnSoundPlayer'
    BATTLE_HINT_SOUND = 'battle_hint_sound'


EVENT_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.BATTLE_HINT, BATTLE_VIEW_ALIASES.BATTLE_TIMER, _SoundPlayerAliases.BATTLE_HINT_SOUND)),
 (BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
   BATTLE_VIEW_ALIASES.PREBATTLE_TIMER,
   DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER,
   DynamicAliases.DRONE_MUSIC_PLAYER)),
 (BATTLE_CTRL_ID.HIT_DIRECTION, (BATTLE_VIEW_ALIASES.HIT_DIRECTION,)),
 (BATTLE_CTRL_ID.CALLOUT, (BATTLE_VIEW_ALIASES.CALLOUT_PANEL,)),
 (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
 (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
 (BATTLE_CTRL_ID.TELEPORT_CTRL, (BATTLE_VIEW_ALIASES.EVENT_HUNTER_RESPAWN, BATTLE_VIEW_ALIASES.EVENT_BOSS_TELEPORT, _SoundPlayerAliases.RESPAWN_SOUND_PLAYER)),
 (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (BATTLE_VIEW_ALIASES.PLAYERS_PANEL_EVENT, DynamicAliases.DRONE_MUSIC_PLAYER)),
 (BATTLE_CTRL_ID.PLAYERS_PANEL_CTRL, (BATTLE_VIEW_ALIASES.PLAYERS_PANEL_EVENT,)),
 (BATTLE_CTRL_ID.BOSS_INFO_CTRL, (BATTLE_VIEW_ALIASES.EVENT_BOSS_WIDGET,)),
 (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,)),
 (BATTLE_CTRL_ID.AMMO, (BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,))), viewsConfig=((_SoundPlayerAliases.RESPAWN_SOUND_PLAYER, RespawnSoundPlayer),
 (_SoundPlayerAliases.BATTLE_HINT_SOUND, BattleHintSoundPlayer),
 (BATTLE_VIEW_ALIASES.HIT_DIRECTION, indicators.createDamageIndicator),
 (DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, StartCountdownSoundPlayer),
 (DynamicAliases.DRONE_MUSIC_PLAYER, EventDroneMusicPlayer)))
_HUNTER_PAGES = ('eventHunterHint1', 'eventHunterHint2', 'eventHunterHint3', 'eventHunterHint4', 'eventHunterHint5')
_BOSS_PAGES = ('eventBossHint1', 'eventBossHint2', 'eventBossHint3', 'eventBossHint4', 'eventBossHint5')
_EVENT_EXTERNAL_COMPONENTS = (EventCrosshairPanelContainer, EventMarkersManager)
_HUNTER_VIEW_COMPONENTS = (BATTLE_VIEW_ALIASES.BATTLE_MESSENGER,)

class EventBattlePage(ClassicPage, ISpawnListener):
    __appLoader = dependency.descriptor(IAppLoader)
    __gameEventCtrl = dependency.descriptor(IEventBattlesController)

    def __init__(self, components=None, external=_EVENT_EXTERNAL_COMPONENTS, fullStatsAlias=None):
        self._spawnType = None
        self.__isRadialMenuShown = False
        self.__isEventStatsShown = False
        self.__selectSpawnToggling = set()
        components = EVENT_CONFIG if not components else components + EVENT_CONFIG
        super(EventBattlePage, self).__init__(components, external, fullStatsAlias=fullStatsAlias)
        return

    def setSpawnType(self, spawnType):
        self._spawnType = spawnType

    def showSpawnPoints(self):
        if self.__selectSpawnToggling:
            return
        self._toggleEventStats(isShown=False)
        self.__selectSpawnToggling = set(self.as_getComponentsVisibilityS())
        visibleComponents = {self._spawnViewAlias, BATTLE_VIEW_ALIASES.MINIMAP, BATTLE_VIEW_ALIASES.EVENT_BOSS_WIDGET} | self._spawnVisibleComponents
        hiddenComponents = self.__selectSpawnToggling - visibleComponents
        self._setComponentsVisibility(visible=visibleComponents, hidden=hiddenComponents)
        self.app.enterGuiControlMode(self._spawnViewAlias)
        g_eventBus.handleEvent(GameEvent(GameEvent.SHOW_SPAWN_POINTS), scope=EVENT_BUS_SCOPE.GLOBAL)

    def closeSpawnPoints(self):
        if not self.__selectSpawnToggling:
            return
        self._toggleEventStats(isShown=False)
        hiddenComponents = {self._spawnViewAlias, BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL}
        visibleComponents = self.__selectSpawnToggling - hiddenComponents
        self.__selectSpawnToggling = set()
        self._setComponentsVisibility(visible=visibleComponents, hidden=hiddenComponents)
        self.app.leaveGuiControlMode(self._spawnViewAlias)
        g_eventBus.handleEvent(GameEvent(GameEvent.HIDE_SPAWN_POINTS), scope=EVENT_BUS_SCOPE.GLOBAL)

    @property
    def _spawnViewAlias(self):
        return BATTLE_VIEW_ALIASES.EVENT_BOSS_TELEPORT if self._spawnType == SpawnType.TELEPORT else BATTLE_VIEW_ALIASES.EVENT_HUNTER_RESPAWN

    @property
    def _spawnVisibleComponents(self):
        return {BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, BATTLE_VIEW_ALIASES.BATTLE_TIMER} if self._spawnType == SpawnType.TELEPORT else {BATTLE_VIEW_ALIASES.PLAYERS_PANEL_EVENT, BATTLE_VIEW_ALIASES.BATTLE_TIMER, BATTLE_VIEW_ALIASES.BATTLE_MESSENGER}

    def _populate(self):
        super(EventBattlePage, self)._populate()
        app = self.__appLoader.getDefBattleApp()
        app.cursorMgr.resetMousePosition()
        self.addListener(events.GameEvent.EVENT_STATS, self.__handleToggleEventStats, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.FADE_OUT_AND_IN, self.__handleFadeOutAndIn, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.RadialMenuEvent.RADIAL_MENU_ACTION, self.__handleRadialAction, scope=EVENT_BUS_SCOPE.BATTLE)
        teleport = self.sessionProvider.dynamic.teleport
        if teleport:
            teleport.addRuntimeView(self)
        enterSound = self.__gameEventCtrl.getEnterSound()
        if enterSound:
            enterSound.loadEventCustomSoundBanks()

    def _dispose(self):
        super(EventBattlePage, self)._dispose()
        self.removeListener(events.RadialMenuEvent.RADIAL_MENU_ACTION, self.__handleRadialAction, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.EVENT_STATS, self.__handleToggleEventStats, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.FADE_OUT_AND_IN, self.__handleFadeOutAndIn, scope=EVENT_BUS_SCOPE.BATTLE)
        teleport = self.sessionProvider.dynamic.teleport
        if teleport:
            teleport.removeRuntimeView(self)
        LOG_DEBUG('Event battle page is destroyed.')

    def _startBattleSession(self):
        super(EventBattlePage, self)._startBattleSession()
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        g_playerEvents.onRoundFinished += self.__onRoundFinished

    def _stopBattleSession(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        super(EventBattlePage, self)._stopBattleSession()

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            self.__setVisibilityInitBattlePeriod()

    def __onRoundFinished(self, winningTeam, reason, extraData):
        hiddenComponents = {BATTLE_VIEW_ALIASES.EVENT_BOSS_WIDGET, BATTLE_VIEW_ALIASES.BATTLE_HINT}
        self._setComponentsVisibility(hidden=hiddenComponents)

    def __handleFadeOutAndIn(self, event):
        settings = event.ctx.get('settings')
        self.__fadeProcess(settings)

    @adisp_process
    def __fadeProcess(self, settings):
        manager = self.app.fadeMgr
        yield manager.startFade(settings=settings)

    def _toggleRadialMenu(self, isShown, allowAction=True):
        manager = self.app.containerManager
        if not manager.isContainerShown(WindowLayer.VIEW):
            return
        elif manager.isModalViewsIsExists():
            return
        else:
            radialMenu = self.getComponent(BATTLE_VIEW_ALIASES.RADIAL_MENU)
            if radialMenu is None:
                return
            elif self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EVENT_STATS):
                return
            self.__isRadialMenuShown = isShown
            if isShown:
                self.__enterRadialHUD()
                radialMenu.show()
            else:
                radialMenu.hide()
                self.__exitRadialHUD()
            return

    def _toggleEventStats(self, isShown):
        self.__isEventStatsShown = isShown
        manager = self.app.containerManager
        if not manager.isContainerShown(WindowLayer.VIEW):
            return
        else:
            eventStats = self.getComponent(BATTLE_VIEW_ALIASES.EVENT_STATS)
            if eventStats is None:
                return
            if isShown and manager.isModalViewsIsExists():
                return
            ctrl = self.sessionProvider.shared.calloutCtrl
            if ctrl is not None and ctrl.isRadialMenuOpened():
                return
            if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EVENT_STATS) != isShown:
                if isShown:
                    self._fsToggling.update(self.as_getComponentsVisibilityS())
                    self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.EVENT_STATS}, hidden=self._fsToggling)
                else:
                    self._setComponentsVisibility(visible=self._fsToggling, hidden={BATTLE_VIEW_ALIASES.EVENT_STATS})
                    self._fsToggling.clear()
            if isShown:
                self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.EVENT_STATS, cursorVisible=True, enableAiming=False)
            else:
                self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.EVENT_STATS)
            return

    def _onBattleLoadingStart(self):
        info = self.sessionProvider.getCtx().getVehicleInfo(BigWorld.player().playerVehicleID)
        isHunter = VEHICLE_TAGS.EVENT_HUNTER in info.vehicleType.tags
        data = {'autoStart': False,
         'tutorialPages': _HUNTER_PAGES if isHunter else _BOSS_PAGES}
        self.fireEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EVENT_LOADING), ctx=data), EVENT_BUS_SCOPE.BATTLE)
        super(EventBattlePage, self)._onBattleLoadingStart()

    def _onBattleLoadingFinish(self):
        self.fireEvent(events.DestroyViewEvent(VIEW_ALIAS.EVENT_LOADING), EVENT_BUS_SCOPE.BATTLE)
        if self.__isBoss():
            self._blToggling -= {BATTLE_VIEW_ALIASES.BATTLE_MESSENGER}
        super(EventBattlePage, self)._onBattleLoadingFinish()
        self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.EVENT_STATS})
        if BigWorld.player().arena.period != ARENA_PERIOD.BATTLE:
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.PLAYERS_PANEL_EVENT})
        else:
            self.__setVisibilityInitBattlePeriod()

    def _changeCtrlMode(self, ctrlMode):
        if ctrlMode == CTRL_MODE_NAME.RESPAWN_DEATH:
            return
        super(EventBattlePage, self)._changeCtrlMode(ctrlMode)

    def __setVisibilityInitBattlePeriod(self):
        visibleComponents = {BATTLE_VIEW_ALIASES.PLAYERS_PANEL_EVENT, BATTLE_VIEW_ALIASES.EVENT_BOSS_WIDGET}
        hiddenComponents = {BATTLE_VIEW_ALIASES.PREBATTLE_TIMER}
        if self.__isBoss():
            hiddenComponents.update(_HUNTER_VIEW_COMPONENTS)
        else:
            visibleComponents.update(_HUNTER_VIEW_COMPONENTS)
        playBossWidgetAppears()
        if self.__isEventStatsShown:
            self._fsToggling.update(visibleComponents)
        else:
            self._setComponentsVisibility(visible=visibleComponents, hidden=hiddenComponents)

    def __enterRadialHUD(self):
        self._fsToggling.update(self.as_getComponentsVisibilityS())
        self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.RADIAL_MENU, cursorVisible=False, enableAiming=False)

    def __exitRadialHUD(self):
        self._fsToggling.clear()
        self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.RADIAL_MENU)

    def __handleToggleEventStats(self, event):
        self._toggleEventStats(event.ctx['isDown'])

    def __handleRadialAction(self, _):
        if self.__isRadialMenuShown:
            self.__exitRadialHUD()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(EventBattlePage, self)._onRegisterFlashComponent(viewPy, alias)
        if alias in (BATTLE_VIEW_ALIASES.EVENT_HUNTER_RESPAWN, BATTLE_VIEW_ALIASES.EVENT_BOSS_TELEPORT):
            self._setComponentsVisibility(hidden={alias})

    def _handleGUIToggled(self, event):
        if not self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EVENT_STATS):
            self._toggleGuiVisible()

    def __isBoss(self):
        vInfo = self.sessionProvider.getArenaDP().getVehicleInfo()
        return isBoss(vInfo.vehicleType.tags)
