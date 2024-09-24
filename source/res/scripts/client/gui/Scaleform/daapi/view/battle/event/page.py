# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/page.py
import BigWorld
from constants import ARENA_PERIOD
from debug_utils import LOG_DEBUG
from adisp import adisp_process
from PlayerEvents import g_playerEvents
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.battle.shared.markers2d.manager import KillCamMarkersManager
from gui.shared import EVENT_BUS_SCOPE, events
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.event.manager import EventMarkersManager
from gui.shared.events import LoadViewEvent
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
EVENT_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.BATTLE_HINT,)),
 (BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER, BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL)),
 (BATTLE_CTRL_ID.CALLOUT, (BATTLE_VIEW_ALIASES.CALLOUT_PANEL,)),
 (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,)),
 (BATTLE_CTRL_ID.MAPS, (BATTLE_VIEW_ALIASES.MINIMAP,)),
 (BATTLE_CTRL_ID.PERKS, (BATTLE_VIEW_ALIASES.SITUATION_INDICATORS,))), viewsConfig=())
_TUTORIAL_PAGES = ('eventHint1', 'eventHint2')
_EVENT_EXTERNAL_COMPONENTS = (CrosshairPanelContainer, EventMarkersManager, KillCamMarkersManager)

class EventBattlePage(ClassicPage):

    def __init__(self, components=None, external=_EVENT_EXTERNAL_COMPONENTS, fullStatsAlias=None):
        components = EVENT_CONFIG if not components else components + EVENT_CONFIG
        self.__isRadialMenuShown = False
        super(EventBattlePage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)

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
            self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.PLAYERS_PANEL_EVENT})

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
        manager = self.app.containerManager
        if not manager.isContainerShown(WindowLayer.VIEW):
            return
        else:
            eventStats = self.getComponent(BATTLE_VIEW_ALIASES.EVENT_STATS)
            if eventStats is None:
                return
            if manager.isModalViewsIsExists():
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
            return

    def _onBattleLoadingStart(self):
        data = {'tutorialPages': _TUTORIAL_PAGES}
        self.fireEvent(LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.EVENT_LOADING), ctx=data), EVENT_BUS_SCOPE.BATTLE)
        super(EventBattlePage, self)._onBattleLoadingStart()

    def _onBattleLoadingFinish(self):
        self.fireEvent(events.DestroyViewEvent(VIEW_ALIAS.EVENT_LOADING), EVENT_BUS_SCOPE.BATTLE)
        super(EventBattlePage, self)._onBattleLoadingFinish()
        self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.EVENT_STATS})
        if BigWorld.player().arena.period != ARENA_PERIOD.BATTLE:
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.PLAYERS_PANEL_EVENT})

    def __enterRadialHUD(self):
        self._fsToggling.update(self.as_getComponentsVisibilityS())
        self._setComponentsVisibility(hidden=self._fsToggling)
        self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.RADIAL_MENU, cursorVisible=True, enableAiming=False)

    def __exitRadialHUD(self):
        self._setComponentsVisibility(visible=self._fsToggling)
        self._fsToggling.clear()
        self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.RADIAL_MENU)

    def __handleToggleEventStats(self, event):
        self._toggleEventStats(event.ctx['isDown'])

    def __handleRadialAction(self, _):
        if self.__isRadialMenuShown:
            self.__exitRadialHUD()

    def _handleGUIToggled(self, event):
        if not self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EVENT_STATS):
            self._toggleGuiVisible()
