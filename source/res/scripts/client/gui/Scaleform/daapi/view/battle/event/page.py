# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/page.py
import BigWorld
import ResMgr
import AvatarInputHandler as aih
from AvatarInputHandler.aih_constants import CTRL_MODE_NAME
from constants import ARENA_PERIOD, EVENT
from gui.Scaleform.daapi.view.battle.classic.page import ClassicPage, DynamicAliases
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.Scaleform.daapi.view.battle.event import drone_music_player
from gui.Scaleform.daapi.view.battle.shared import period_music_listener
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.framework import ViewTypes
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control import avatar_getter
from gui.Scaleform.daapi.view.battle.event.manager import EventMarkersManager
from gui.Scaleform.daapi.view.battle.shared.crosshair import CrosshairPanelContainer
from gui.shared import EVENT_BUS_SCOPE, events
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from PlayerEvents import g_playerEvents
from helpers import uniprof
_TUTORIAL_PAGES = ['eventHint1',
 'eventHint2',
 'eventHint3',
 'eventHint4',
 'eventHint5']
EVENT_CONFIG = ComponentsConfig(config=((BATTLE_CTRL_ID.BATTLE_HINTS, (BATTLE_VIEW_ALIASES.BATTLE_HINT,)),
 (BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER, DynamicAliases.DRONE_MUSIC_PLAYER, DynamicAliases.PERIOD_MUSIC_LISTENER)),
 (BATTLE_CTRL_ID.BATTLE_FIELD_CTRL, (DynamicAliases.DRONE_MUSIC_PLAYER,)),
 (BATTLE_CTRL_ID.ARENA_LOAD_PROGRESS, (DynamicAliases.DRONE_MUSIC_PLAYER,)),
 (BATTLE_CTRL_ID.GAME_MESSAGES_PANEL, (BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL,)),
 (BATTLE_CTRL_ID.DEBUG, (BATTLE_VIEW_ALIASES.DEBUG_PANEL,))), viewsConfig=((DynamicAliases.PERIOD_MUSIC_LISTENER, period_music_listener.PeriodMusicListener), (DynamicAliases.DRONE_MUSIC_PLAYER, drone_music_player.EventDroneMusicPlayer)))
_EVENT_EXTERNAL_COMPONENTS = (CrosshairPanelContainer, EventMarkersManager)

class EventBattlePage(ClassicPage):

    def __init__(self, components=None, external=_EVENT_EXTERNAL_COMPONENTS, fullStatsAlias=BATTLE_VIEW_ALIASES.FULL_STATS):
        self._esToggling = set()
        components = EVENT_CONFIG if not components else components + EVENT_CONFIG
        super(EventBattlePage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)

    def _populate(self):
        super(EventBattlePage, self)._populate()
        self.addListener(events.GameEvent.HELP, self.__handleHelpEvent, scope=EVENT_BUS_SCOPE.BATTLE)
        self.addListener(events.GameEvent.EVENT_STATS, self._handleToggleEventStats, scope=EVENT_BUS_SCOPE.BATTLE)
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onGunReloadTimeSet += self.__onGunReloadTimeSet
        self.__cameraTransitionDurations = aih.control_modes.readCameraTransitionSettings(self.__readCameraCfg())
        LOG_DEBUG('Event battle page is created.')
        return

    def _dispose(self):
        super(EventBattlePage, self)._dispose()
        self.removeListener(events.GameEvent.HELP, self.__handleHelpEvent, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.GameEvent.EVENT_STATS, self._handleToggleEventStats, scope=EVENT_BUS_SCOPE.BATTLE)
        self.removeListener(events.RadialMenuEvent.RADIAL_MENU_ACTION, self.__handleRadialAction, scope=EVENT_BUS_SCOPE.BATTLE)
        ammoCtrl = self.sessionProvider.shared.ammo
        if ammoCtrl is not None:
            ammoCtrl.onGunReloadTimeSet -= self.__onGunReloadTimeSet
        LOG_DEBUG('Event battle page is destroyed.')
        return

    def _changeCtrlMode(self, ctrlMode):
        if ctrlMode != CTRL_MODE_NAME.RESPAWN_DEATH:
            super(EventBattlePage, self)._changeCtrlMode(ctrlMode)

    def _startBattleSession(self):
        super(EventBattlePage, self)._startBattleSession()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling += self.__onVehicleControlling
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        handler = avatar_getter.getInputHandler()
        if isinstance(handler, aih.AvatarInputHandler):
            handler.onPostmortemKillerVisionExit += self.__onKillerVisionExit
            handler.onPostmortemKillerVisionEnter += self.__onKillerVisionEnter
        return

    def _stopBattleSession(self):
        super(EventBattlePage, self)._stopBattleSession()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling -= self.__onVehicleControlling
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        handler = avatar_getter.getInputHandler()
        if isinstance(handler, aih.AvatarInputHandler):
            handler.onPostmortemKillerVisionExit -= self.__onKillerVisionExit
            handler.onPostmortemKillerVisionEnter -= self.__onKillerVisionEnter
        return

    def __onKillerVisionEnter(self, killerVehicleID):
        if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.AMMO_INFO):
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.AMMO_INFO})

    def __onVehicleControlling(self, vehicle):
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        if vehicle.isPlayerVehicle and periodCtrl.getPeriod() == ARENA_PERIOD.BATTLE and self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.BATTLE_VEHICLE_SELECTOR):
            self._toggleVehicleSelector(False)

    def _toggleRadialMenu(self, isShown):
        manager = self.app.containerManager
        if not manager.isContainerShown(ViewTypes.DEFAULT):
            return
        elif manager.isModalViewsIsExists():
            return
        else:
            radialMenu = self.getComponent(BATTLE_VIEW_ALIASES.RADIAL_MENU_EVENT)
            if radialMenu is None:
                return
            elif self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EVENT_STATS) or self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.BATTLE_VEHICLE_SELECTOR):
                return
            if isShown:
                self.__enterRadialHUD()
                radialMenu.show()
                self.addListener(events.RadialMenuEvent.RADIAL_MENU_ACTION, self.__handleRadialAction, scope=EVENT_BUS_SCOPE.BATTLE)
            else:
                self.removeListener(events.RadialMenuEvent.RADIAL_MENU_ACTION, self.__handleRadialAction, scope=EVENT_BUS_SCOPE.BATTLE)
                radialMenu.hide()
                self.__exitRadialHUD()
            return

    def _hideRadialMenu(self):
        if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.RADIAL_MENU_EVENT):
            self._toggleRadialMenu(False)

    def _hideEventStats(self):
        if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EVENT_STATS):
            self._toggleEventStats(isShown=False)

    def _isRadialMenuVisible(self):
        return self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.RADIAL_MENU_EVENT)

    def _showLoadingComponent(self):
        self._setComponentsVisibility(hidden=self._blToggling)
        self._blToggling.difference_update([BATTLE_VIEW_ALIASES.QUEST_PROGRESS_TOP_VIEW,
         BATTLE_VIEW_ALIASES.PLAYERS_PANEL,
         BATTLE_VIEW_ALIASES.FULL_STATS,
         BATTLE_VIEW_ALIASES.BATTLE_VEHICLE_SELECTOR,
         BATTLE_VIEW_ALIASES.AMMO_INFO,
         BATTLE_VIEW_ALIASES.RADIAL_MENU_EVENT,
         BATTLE_VIEW_ALIASES.EVENT_STATS])
        data = {'autoStart': False,
         'tutorialPages': _TUTORIAL_PAGES}
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.EVENT_LOADING, ctx=data), EVENT_BUS_SCOPE.BATTLE)

    def _hideLoadingComponent(self):
        self._setComponentsVisibility(visible=self._blToggling)
        self.fireEvent(events.DestroyViewEvent(VIEW_ALIAS.EVENT_LOADING), EVENT_BUS_SCOPE.BATTLE)

    def _onBattleLoadingFinish(self):
        super(EventBattlePage, self)._onBattleLoadingFinish()
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        self._toggleVehicleSelector(False)
        if periodCtrl.getPeriod() not in (ARENA_PERIOD.PREBATTLE, ARENA_PERIOD.BATTLE):
            self._toggleArenaWaitingComponents(True)
        if periodCtrl.getPeriod() == ARENA_PERIOD.PREBATTLE and not self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.BATTLE_VEHICLE_SELECTOR):
            self._toggleArenaWaitingComponents(False)
            self._toggleVehicleSelector(True, False)

    def _toggleArenaWaitingComponents(self, isShow):
        battleHints = self.sessionProvider.dynamic.battleHints
        toggleList = {BATTLE_VIEW_ALIASES.PLAYERS_PANEL_EVENT, BATTLE_VIEW_ALIASES.MAP_SCENARIO_PROGRESS, BATTLE_VIEW_ALIASES.PANEL_VEHICLES}
        if isShow:
            self._setComponentsVisibility(hidden=toggleList)
            if battleHints:
                battleHints.showHint(EVENT.ARENA_WAITING_HINT_NAME)
        else:
            if battleHints:
                battleHints.hideHint(EVENT.ARENA_WAITING_HINT_NAME)
            self._setComponentsVisibility(visible=toggleList)

    def _toggleVehicleSelector(self, isShown, mapTab=True):
        vehicleSelector = self.getComponent(BATTLE_VIEW_ALIASES.BATTLE_VEHICLE_SELECTOR)
        if isShown:
            uniprof.enterToRegion('vehicle_selector.show')
            self._toggleEventStats(False)
            self.__hideAllVisibleComponents(remainVisible={BATTLE_VIEW_ALIASES.BATTLE_VEHICLE_SELECTOR})
            self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.BATTLE_VEHICLE_SELECTOR)
            vehicleSelector.setMapTab(mapTab)
            vehicleSelector.enableCountdownSound()
        else:
            self.__toggleBackHiddenComponents(remainHidden={BATTLE_VIEW_ALIASES.BATTLE_VEHICLE_SELECTOR})
            vehicleSelector.disableCountdownSound()
            self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.BATTLE_VEHICLE_SELECTOR)
            uniprof.exitFromRegion('vehicle_selector.show')

    def _handleToggleEventStats(self, event):
        self._toggleEventStats(event.ctx['isDown'])

    def _toggleEventStats(self, isShown):
        manager = self.app.containerManager
        if not self.getComponent(BATTLE_VIEW_ALIASES.EVENT_STATS) or manager.isModalViewsIsExists() or self._isRadialMenuVisible() or self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.BATTLE_VEHICLE_SELECTOR):
            return
        if self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.EVENT_STATS) != isShown:
            if isShown:
                self.__hideAllVisibleComponents(remainVisible={BATTLE_VIEW_ALIASES.EVENT_STATS})
            else:
                self.__toggleBackHiddenComponents(remainHidden={BATTLE_VIEW_ALIASES.EVENT_STATS})

    def _switchToPostmortem(self):
        self._hideRadialMenu()
        self._hideEventStats()

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self._switchToPostmortem()

    def __hideAllVisibleComponents(self, remainVisible=None):
        self._esToggling.update(self.as_getComponentsVisibilityS())
        self._setComponentsVisibility(visible=remainVisible, hidden=self._esToggling)

    def __toggleBackHiddenComponents(self, remainHidden=None):
        self._setComponentsVisibility(visible=self._esToggling, hidden=remainHidden)
        self._esToggling.clear()

    def __onArenaPeriodChange(self, period, periodEndTime, periodLength, periodAdditionalInfo):
        if period == ARENA_PERIOD.PREBATTLE and not self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.BATTLE_VEHICLE_SELECTOR):
            self._toggleArenaWaitingComponents(False)
            self._toggleVehicleSelector(True, False)
        elif period == ARENA_PERIOD.BATTLE and self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.BATTLE_VEHICLE_SELECTOR):
            BigWorld.player().inputHandler.onControlModeChanged(CTRL_MODE_NAME.ARCADE)
            self._toggleVehicleSelector(False)

    def __enterRadialHUD(self):
        self.__hideAllVisibleComponents()
        self.app.enterGuiControlMode(BATTLE_VIEW_ALIASES.RADIAL_MENU_EVENT, cursorVisible=True, enableAiming=False)

    def __exitRadialHUD(self):
        self.__toggleBackHiddenComponents()
        self.app.leaveGuiControlMode(BATTLE_VIEW_ALIASES.RADIAL_MENU_EVENT)

    def __handleHelpEvent(self, _):
        self._hideRadialMenu()

    def __handleRadialAction(self, _):
        self.__exitRadialHUD()

    def __onGunReloadTimeSet(self, _, state):
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        if state.getActualValue() < 0 and periodCtrl.getPeriod() == ARENA_PERIOD.BATTLE:
            if not self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.AMMO_INFO):
                self._setComponentsVisibility(visible={BATTLE_VIEW_ALIASES.AMMO_INFO})
        elif self.as_isComponentVisibleS(BATTLE_VIEW_ALIASES.AMMO_INFO):
            self._setComponentsVisibility(hidden={BATTLE_VIEW_ALIASES.AMMO_INFO})

    def __onKillerVisionExit(self):
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is None:
            return
        else:
            if ctrl.playerLives <= 0:
                self._toggleVehicleSelector(False)
                transitionDuration = self.__cameraTransitionDurations.get(CTRL_MODE_NAME.DEATH_FREE_CAM, -1)
                BigWorld.player().inputHandler.onControlModeChanged(CTRL_MODE_NAME.DEATH_FREE_CAM, transitionDuration=transitionDuration)
            else:
                self._toggleVehicleSelector(True)
            return

    def __readCameraCfg(self):
        sec = ResMgr.openSection(aih.INPUT_HANDLER_CFG)
        if sec is None:
            LOG_ERROR('can not open <%s>.' % aih.INPUT_HANDLER_CFG)
            return
        else:
            postMortemMode = sec['postMortemMode']
            if postMortemMode is None:
                LOG_ERROR('can not open <%s>.' % aih.INPUT_HANDLER_CFG + '/postMortemMode')
                return
            return postMortemMode['camera']
