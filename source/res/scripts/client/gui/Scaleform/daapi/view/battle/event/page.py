# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/page.py
import BigWorld
from constants import ARENA_PERIOD
from debug_utils import LOG_DEBUG
from adisp import process
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.battle.event import indicators
from gui.Scaleform.daapi.view.battle.shared.start_countdown_sound_player import StartCountdownSoundPlayer
from gui.shared import EVENT_BUS_SCOPE, events
from gui.Scaleform.framework import ViewTypes
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.battle.shared import period_music_listener
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from gui.Scaleform.daapi.view.battle.classic.page import DynamicAliases
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.event.manager import EventMarkersManager
from gui.wt_event.wt_event_helpers import getHunterDescr
EVENT_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.BATTLE_HINT,)),
 (BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER,
   DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER,
   DynamicAliases.PERIOD_MUSIC_LISTENER,
   BATTLE_VIEW_ALIASES.EVENT_PREBATTLE_TIMER,
   BATTLE_VIEW_ALIASES.HINT_PANEL)),
 (BATTLE_CTRL_ID.CALLOUT, (BATTLE_VIEW_ALIASES.CALLOUT_PANEL,)),
 (BATTLE_CTRL_ID.TEAM_HEALTH_BAR, (BATTLE_VIEW_ALIASES.PLAYERS_PANEL_EVENT,)),
 (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
 (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
 (BATTLE_CTRL_ID.HIT_DIRECTION, (BATTLE_VIEW_ALIASES.HIT_DIRECTION,))), viewsConfig=((DynamicAliases.PERIOD_MUSIC_LISTENER, period_music_listener.PeriodMusicListener), (BATTLE_VIEW_ALIASES.HIT_DIRECTION, indicators.createDamageIndicator), (DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER, StartCountdownSoundPlayer)))
_HUNTER_TUTORIAL_PAGES = ('eventHunterHint1', 'eventHunterHint2', 'eventHunterHint3')
_BOSS_TUTORIAL_PAGES = ('eventBossHint1', 'eventBossHint2', 'eventBossHint3')
_EVENT_EXTERNAL_COMPONENTS = (CrosshairPanelContainer, EventMarkersManager)
_HUNTER_VIEWS_COMPONENT = (BATTLE_VIEW_ALIASES.WT_EVENT_REINFORCEMENT_PANEL, BATTLE_VIEW_ALIASES.BATTLE_MESSENGER)

class EventBattlePage(ClassicPage):

    def __init__(self, components=None, external=_EVENT_EXTERNAL_COMPONENTS, fullStatsAlias=BATTLE_VIEW_ALIASES.FULL_STATS):
        components = EVENT_CONFIG if not components else components + EVENT_CONFIG
        self.__isRadialMenuShown = False
        super(EventBattlePage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)
        self.__isRespawnInFullStats = False

    def _populate(self):
        super(EventBattlePage, self)._populate()
        self.addListener(events.GameEvent.EVENT_STATS, self.__handleToggleEventStats, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.FADE_OUT_AND_IN, self.__handleFadeOutAndIn, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.RadialMenuEvent.RADIAL_MENU_ACTION, self.__handleRadialAction, scope=EVENT_BUS_SCOPE.BATTLE)
        LOG_DEBUG('Event battle page is created.')

    def _dispose(self):
        super(EventBattlePage, self)._dispose()
        self.removeListener(events.RadialMenuEvent.RADIAL_MENU_ACTION, self.__handleRadialAction, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.EVENT_STATS, self.__handleToggleEventStats, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.FADE_OUT_AND_IN, self.__handleFadeOutAndIn, scope=EVENT_BUS_SCOPE.BATTLE)
        LOG_DEBUG('Event battle page is destroyed.')

    def _startBattleSession(self):
        super(EventBattlePage, self)._startBattleSession()
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange

    def _stopBattleSession(self):
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        super(EventBattlePage, self)._stopBattleSession()

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.BATTLE:
            info = self.sessionProvider.getCtx().getVehicleInfo(BigWorld.player().playerVehicleID)
            isHunter = getHunterDescr() == info.vehicleType.compactDescr
            visibleComponent = {BATTLE_VIEW_ALIASES.WT_EVENT_BOSS_PROGRESS_WIDGET}
            if isHunter:
                visibleComponent.update(_HUNTER_VIEWS_COMPONENT)
            self._setComponentsVisibility(visible=visibleComponent)

    def __handleFadeOutAndIn(self, event):
        settings = event.ctx.get('settings')
        self.__fadeProcess(settings)

    @process
    def __fadeProcess(self, settings):
        manager = self.app.fadeMgr
        yield manager.startFade(settings=settings)

    def _toggleFullStats(self, isShown, permanent=None, tabIndex=None):
        super(EventBattlePage, self)._toggleFullStats(isShown, permanent, tabIndex)
        if self._isInPostmortem and isShown and not self.__isRespawnInFullStats:
            self.__isRespawnInFullStats = True
        elif not self._isInPostmortem and not isShown and self.__isRespawnInFullStats:
            self.__isRespawnInFullStats = False
            self.as_setPostmortemTipsVisibleS(self._isInPostmortem)
            self._setComponentsVisibility(visible=(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL,))
        elif self.__isRespawnInFullStats and not isShown:
            self.__isRespawnInFullStats = False

    def _toggleRadialMenu(self, isShown, allowAction=True):
        manager = self.app.containerManager
        if not manager.isContainerShown(ViewTypes.DEFAULT):
            return
        elif manager.isModalViewsIsExists():
            return
        else:
            radialMenu = self.getComponent(BATTLE_VIEW_ALIASES.RADIAL_MENU)
            if radialMenu is None:
                return
            elif self._fullStatsAlias and self.as_isComponentVisibleS(self._fullStatsAlias):
                return
            self.__isRadialMenuShown = isShown
            if isShown:
                self.__enterRadialHUD()
                radialMenu.show()
            else:
                radialMenu.hide()
                self.__exitRadialHUD()
            return

    def _onBattleLoadingStart(self):
        info = self.sessionProvider.getCtx().getVehicleInfo(BigWorld.player().playerVehicleID)
        isHunter = getHunterDescr() == info.vehicleType.compactDescr
        data = {'autoStart': False,
         'tutorialPages': _HUNTER_TUTORIAL_PAGES if isHunter else _BOSS_TUTORIAL_PAGES}
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.EVENT_LOADING, ctx=data), EVENT_BUS_SCOPE.BATTLE)
        super(EventBattlePage, self)._onBattleLoadingStart()

    def _onBattleLoadingFinish(self):
        self.fireEvent(events.DestroyViewEvent(VIEW_ALIAS.EVENT_LOADING), EVENT_BUS_SCOPE.BATTLE)
        super(EventBattlePage, self)._onBattleLoadingFinish()
        info = self.sessionProvider.getCtx().getVehicleInfo(BigWorld.player().playerVehicleID)
        isHunter = getHunterDescr() == info.vehicleType.compactDescr
        self._toggleWidget(BATTLE_VIEW_ALIASES.WT_EVENT_BOSS_PROGRESS_WIDGET, True)
        if BigWorld.player().arena.period != ARENA_PERIOD.BATTLE:
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.WT_EVENT_BOSS_PROGRESS_WIDGET, BATTLE_VIEW_ALIASES.WT_EVENT_REINFORCEMENT_PANEL, BATTLE_VIEW_ALIASES.BATTLE_MESSENGER})
        elif isHunter:
            self._setComponentsVisibility(visible=_HUNTER_VIEWS_COMPONENT)

    def __enterRadialHUD(self):
        self._fsToggling.update(self.as_getComponentsVisibilityS())
        self._setComponentsVisibility(hidden=self._fsToggling)
        self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.RADIAL_MENU, cursorVisible=True, enableAiming=False)

    def __exitRadialHUD(self):
        self._setComponentsVisibility(visible=self._fsToggling)
        self._fsToggling.clear()
        self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.RADIAL_MENU)

    def __handleToggleEventStats(self, event):
        self._toggleFullStats(event.ctx['isDown'])

    def __handleRadialAction(self, _):
        if self.__isRadialMenuShown:
            self.__exitRadialHUD()

    def _toggleWidget(self, alias, isShown):
        if isShown:
            if self._isBattleLoading:
                self._blToggling.add(alias)
            elif self._fsToggling:
                self._fsToggling.add(alias)
            elif not self.as_isComponentVisibleS(alias):
                self._setComponentsVisibility(visible={alias})
        elif self._isBattleLoading:
            self._blToggling.discard(alias)
        elif self._fsToggling:
            self._fsToggling.discard(alias)
        elif self.as_isComponentVisibleS(alias):
            self._setComponentsVisibility(hidden={alias})
