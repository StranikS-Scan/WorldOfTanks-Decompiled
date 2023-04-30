# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/comp7/page.py
import BigWorld
import BattleReplay
from aih_constants import CTRL_MODE_NAME
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.comp7.start_countdown_sound_player import Comp7StartTimerSoundPlayer
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from helpers.CallbackDelayer import CallbackDelayer
from shared_utils import CONST_CONTAINER
from constants import ARENA_PERIOD
from gui.Scaleform.daapi.view.battle.classic.page import COMMON_CLASSIC_CONFIG, EXTENDED_CLASSIC_CONFIG, DynamicAliases
from gui.Scaleform.daapi.view.battle.comp7.markers2d.manager import Comp7MarkersManager
from gui.Scaleform.daapi.view.battle.comp7.lobby_notifier import LobbyNotifier
from gui.Scaleform.daapi.view.battle.shared import crosshair
from gui.Scaleform.daapi.view.battle.shared.page import ComponentsConfig
from gui.Scaleform.daapi.view.meta.Comp7BattlePageMeta import Comp7BattlePageMeta
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control import event_dispatcher, avatar_getter
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.shared.gui_items.vehicle_helpers import getRoleMessage
from helpers import dependency, int2roman
from skeletons.gui.battle_session import IBattleSessionProvider

class _DynamicAliases(CONST_CONTAINER):
    LOBBY_NOTIFIER = 'lobbyNotifier'


class _Comp7Config(ComponentsConfig):

    def __init__(self):
        super(_Comp7Config, self).__init__(((BATTLE_CTRL_ID.ARENA_PERIOD, (_DynamicAliases.LOBBY_NOTIFIER, BATTLE_VIEW_ALIASES.COMP7_TANK_CAROUSEL)),), ((_DynamicAliases.LOBBY_NOTIFIER, LobbyNotifier),))


_COMP7_CONFIG = _Comp7Config()
_COMP7_VIEW_OVERRIDES = {DynamicAliases.PREBATTLE_TIMER_SOUND_PLAYER: Comp7StartTimerSoundPlayer}
_COMMON_CONFIG = COMMON_CLASSIC_CONFIG + _COMP7_CONFIG
_EXTENDED_CONFIG = EXTENDED_CLASSIC_CONFIG + _COMP7_CONFIG
_EXTERNAL_COMPONENTS = (crosshair.CrosshairPanelContainer, Comp7MarkersManager)
_FULL_STATS_ALIAS = BATTLE_VIEW_ALIASES.FULL_STATS

class Comp7BattlePage(Comp7BattlePageMeta):
    __TIME_TILL_CAMERA_RETURN = 3.0
    __CALLBACK_UPDATE_PERIOD = 0.2
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, components=None, external=_EXTERNAL_COMPONENTS, fullStatsAlias=_FULL_STATS_ALIAS):
        if components is None:
            components = _COMMON_CONFIG if self.sessionProvider.isReplayPlaying else _EXTENDED_CONFIG
            components.overrideViews(_COMP7_VIEW_OVERRIDES)
        super(Comp7BattlePage, self).__init__(components=components, external=external, fullStatsAlias=fullStatsAlias)
        self.__isCursorDragging = False
        self.__isCursorOver3dScene = False
        self.__returnCameraDelayer = CallbackDelayer()
        self.__visibilityManager = None
        self.__lastCallbackRefresh = 0
        return

    def showHelp(self):
        event_dispatcher.toggleHelpDetailed(ctx={'isComp7': True})

    def moveSpace(self, x, y, delta):
        if self.__isCursorDragging:
            avatar_getter.getInputHandler().ctrl.handleMouseEvent(x, y, delta)
        elif self.__isCursorOver3dScene and delta:
            avatar_getter.getInputHandler().ctrl.handleMouseEvent(0, 0, delta)
            self.__refreshReturnCallback()

    def notifyCursorOver3dScene(self, value):
        self.__isCursorOver3dScene = value

    def notifyCursorDragging(self, value):
        if self.__isCursorDragging != value:
            self.__isCursorDragging = value
            if value:
                self.__returnCameraDelayer.stopCallback(self.__returnCamera)
            else:
                self.__refreshReturnCallback()

    def _populate(self):
        super(Comp7BattlePage, self)._populate()
        g_eventBus.addListener(GameEvent.PREBATTLE_INPUT_STATE_LOCKED, self.__onPrebattleInputStateLocked, scope=EVENT_BUS_SCOPE.BATTLE)
        prebattleCtrl = self.__sessionProvider.dynamic.comp7PrebattleSetup
        isSelectionConfirmed = False
        if prebattleCtrl is not None:
            prebattleCtrl.onVehicleChanged += self.__onVehicleChange
            prebattleCtrl.onSelectionConfirmed += self.__onSelectionConfirmed
            prebattleCtrl.onBattleStarted += self.__onBattleStarted
            isSelectionConfirmed = prebattleCtrl.isSelectionConfirmed()
            if isSelectionConfirmed:
                self.as_onVehicleSelectionConfirmedS()
        vehStateCtrl = self.sessionProvider.shared.vehicleState
        if vehStateCtrl is not None:
            vehStateCtrl.onVehicleControlling += self.__onVehicleControlling
        self.__updateCurrVehicleInfo()
        periodCtrl = self.sessionProvider.shared.arenaPeriod
        arenaPeriod = periodCtrl.getPeriod() if periodCtrl else None
        self.__visibilityManager = _ComponentsVisibilityManager(arenaPeriod, isSelectionConfirmed)
        return

    def _dispose(self):
        g_eventBus.removeListener(GameEvent.PREBATTLE_INPUT_STATE_LOCKED, self.__onPrebattleInputStateLocked, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__returnCameraDelayer.stopCallback(self.__returnCamera)
        prebattleCtrl = self.__sessionProvider.dynamic.comp7PrebattleSetup
        if prebattleCtrl is not None:
            prebattleCtrl.onVehicleChanged -= self.__onVehicleChange
            prebattleCtrl.onSelectionConfirmed -= self.__onSelectionConfirmed
            prebattleCtrl.onBattleStarted -= self.__onBattleStarted
        vehStateCtrl = self.sessionProvider.shared.vehicleState
        if vehStateCtrl is not None:
            vehStateCtrl.onVehicleControlling -= self.__onVehicleControlling
        self.__visibilityManager.clear()
        self.__visibilityManager = None
        super(Comp7BattlePage, self)._dispose()
        return

    def _startBattleSession(self):
        super(Comp7BattlePage, self)._startBattleSession()
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange += self.__onArenaPeriodChange
        return

    def _stopBattleSession(self):
        arena = self.sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange -= self.__onArenaPeriodChange
        super(Comp7BattlePage, self)._stopBattleSession()
        return

    def _onBattleLoadingFinish(self):
        super(Comp7BattlePage, self)._onBattleLoadingFinish()
        arenaPeriod = self.sessionProvider.shared.arenaPeriod.getPeriod()
        if arenaPeriod == ARENA_PERIOD.BATTLE:
            self.as_onBattleStartedS()
        self.__visibilityManager.setBattleLoaded(True)
        self.__updateComponentsVisibility()

    def _switchToPostmortem(self):
        super(Comp7BattlePage, self)._switchToPostmortem()
        BigWorld.player().setIsObserver()
        self.__updateComponentsVisibility()

    def _toggleFullStats(self, isShown, permanent=None, tabAlias=None):
        if self.__visibilityManager is not None:
            self.__visibilityManager.setFullStatsShown(isShown)
            if not isShown:
                self._fsToggling.update(self.__visibilityManager.getVisible())
        super(Comp7BattlePage, self)._toggleFullStats(isShown, permanent=permanent, tabAlias=tabAlias)
        return

    def _onAvatarCtrlModeChanged(self, ctrlMode):
        pass

    def __refreshReturnCallback(self):
        currTime = BigWorld.time()
        if currTime - self.__lastCallbackRefresh > self.__CALLBACK_UPDATE_PERIOD:
            self.__lastCallbackRefresh = currTime
            self.__returnCameraDelayer.delayCallback(self.__TIME_TILL_CAMERA_RETURN, self.__returnCamera)

    def __onArenaPeriodChange(self, period, *_, **__):
        if period == ARENA_PERIOD.BATTLE:
            self.__returnCameraDelayer.stopCallback(self.__returnCamera)
        self.__updateComponentsVisibility(arenaPeriod=period)

    def __updateComponentsVisibility(self, arenaPeriod=None):
        if arenaPeriod is None:
            arenaPeriod = self.sessionProvider.shared.arenaPeriod.getPeriod()
        if not self.sessionProvider.isReplayPlaying:
            if arenaPeriod <= ARENA_PERIOD.PREBATTLE:
                self.app.enterGuiControlMode(VIEW_ALIAS.COMP7_BATTLE_PAGE, enableAiming=False)
            elif arenaPeriod == ARENA_PERIOD.BATTLE:
                self.app.leaveGuiControlMode(VIEW_ALIAS.COMP7_BATTLE_PAGE)
        self.__visibilityManager.updatePeriod(arenaPeriod)
        vehStateCtrl = self.sessionProvider.shared.vehicleState
        if vehStateCtrl is not None:
            self.__visibilityManager.updateControllingVehicle(vehStateCtrl.getControllingVehicleID())
        self._setComponentsVisibility(self.__visibilityManager.getVisible(), self.__visibilityManager.getHidden())
        return

    def __onVehicleChange(self, vehicle):
        self.__updateCurrVehicleInfo(vehicle)

    def __updateCurrVehicleInfo(self, vehicle=None):
        ctrl = self.__sessionProvider.dynamic.comp7PrebattleSetup
        if ctrl is None:
            return
        else:
            if vehicle is None:
                vehicle = ctrl.getCurrentGUIVehicle()
            if vehicle is not None:
                rawData = ctrl.getCurrentVehicleInfo(extendWithDataFromList=True) or {}
                vehicleRole = vehicle.role
                vehicleClass = vehicle.type
                isEliteOrPremium = vehicle.isPremium or bool(rawData.get('isElite', False))
                self.as_updateVehicleStatusS({'tankType': '{}_elite'.format(vehicleClass) if isEliteOrPremium else vehicleClass,
                 'vehicleLevel': int2roman(vehicle.level),
                 'vehicleName': vehicle.userName,
                 'roleId': vehicleRole,
                 'roleMessage': getRoleMessage(vehicleRole),
                 'vehicleCD': vehicle.intCD,
                 'isElite': isEliteOrPremium})
            return

    def __onSelectionConfirmed(self):
        self.__setSelectionConfimed()

    def __onBattleStarted(self):
        self.__setSelectionConfimed()
        self.as_onBattleStartedS()

    def __setSelectionConfimed(self):
        self.__visibilityManager.updateSelectionConfirmed(True)
        self.as_onVehicleSelectionConfirmedS()

    def __onPrebattleInputStateLocked(self, _):
        self.as_onPrebattleInputStateLockedS(False)

    def __onVehicleControlling(self, _):
        self.__updateComponentsVisibility()

    @staticmethod
    def __returnCamera():
        inputHandler = avatar_getter.getInputHandler()
        if inputHandler and inputHandler.ctrl and inputHandler.ctrlModeName == CTRL_MODE_NAME.VEHICLES_SELECTION:
            inputHandler.ctrl.moveCameraToDefault()


class _ComponentsVisibilityManager(object):

    def __init__(self, arenaPeriod, isSelectionConfirmed):
        self.__components = {BATTLE_VIEW_ALIASES.DAMAGE_PANEL: self.__damagePanelPredicate,
         BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL: self.__damageLogPredicate,
         BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR: self.__fragCorrelationBarPredicate,
         BATTLE_VIEW_ALIASES.COMP7_TANK_CAROUSEL: self.__carouselPredicate,
         BATTLE_VIEW_ALIASES.POINT_OF_INTEREST_NOTIFICATIONS_PANEL: self.__POINotificationsPredicate,
         BATTLE_VIEW_ALIASES.RIBBONS_PANEL: self.__ribbonPanelPredicate,
         BATTLE_VIEW_ALIASES.PERKS_PANEL: self.__perksPanelPredicate}
        self.__isSelectionConfirmed = isSelectionConfirmed
        self.__arenaPeriod = arenaPeriod
        self.__isBattleLoaded = False
        self.__isFullStatsShown = False
        self.__controllingVehicleID = None
        self.__visible, self.__hidden = set(), set()
        self.__needUpdateState = True
        self.__updateState()
        return

    def updateSelectionConfirmed(self, value):
        self.__setNeedUpdateState(self.__isSelectionConfirmed != value)
        self.__isSelectionConfirmed = value

    def updatePeriod(self, period):
        self.__setNeedUpdateState(self.__arenaPeriod != period)
        self.__arenaPeriod = period

    def setBattleLoaded(self, isLoaded):
        self.__setNeedUpdateState(self.__isBattleLoaded != isLoaded)
        self.__isBattleLoaded = isLoaded

    def setFullStatsShown(self, isShown):
        self.__setNeedUpdateState(self.__isFullStatsShown != isShown)
        self.__isFullStatsShown = isShown

    def updateControllingVehicle(self, controllingVehicleID):
        self.__setNeedUpdateState(self.__controllingVehicleID != controllingVehicleID)
        self.__controllingVehicleID = controllingVehicleID

    def getVisible(self):
        if self.__needUpdateState:
            self.__updateState()
        return self.__visible

    def getHidden(self):
        if self.__needUpdateState:
            self.__updateState()
        return self.__hidden

    def clear(self):
        self.__components = {}
        self.__hidden = {}
        self.__visible = {}

    def __setNeedUpdateState(self, value):
        if not self.__needUpdateState and value:
            self.__needUpdateState = value

    def __updateState(self):
        for key, predicate in self.__components.iteritems():
            self.__changeState(key, visible=predicate())

        self.__needUpdateState = False

    def __changeState(self, key, visible=True):
        target = self.__visible if visible else self.__hidden
        source = self.__hidden if visible else self.__visible
        target.add(key)
        if key in source:
            source.remove(key)

    def __damagePanelPredicate(self):
        return self.__afterPrebattle()

    def __damageLogPredicate(self):
        return self.__afterPrebattle() and self.__controllingOwnVehicle()

    def __fragCorrelationBarPredicate(self):
        return self.__afterPrebattle()

    def __ribbonPanelPredicate(self):
        return self.__controllingOwnVehicle()

    def __perksPanelPredicate(self):
        return self.__arenaPeriod >= ARENA_PERIOD.BATTLE and self.__isBattleLoaded and avatar_getter.getPlayerTeam() == BigWorld.player().arena.vehicles[self.__controllingVehicleID]['team']

    def __carouselPredicate(self):
        return not BattleReplay.g_replayCtrl.isPlaying and self.__arenaPeriod < ARENA_PERIOD.BATTLE and self.__isBattleLoaded and not self.__isSelectionConfirmed and not self.__isFullStatsShown

    def __POINotificationsPredicate(self):
        return self.__arenaPeriod == ARENA_PERIOD.BATTLE and not self.__isFullStatsShown

    def __afterPrebattle(self):
        return self.__arenaPeriod > ARENA_PERIOD.PREBATTLE and not self.__isFullStatsShown

    def __controllingOwnVehicle(self):
        return avatar_getter.getPlayerVehicleID() == self.__controllingVehicleID
