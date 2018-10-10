# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/hint_panel/plugins.py
from collections import namedtuple
import CommandMapping
from account_helpers import AccountSettings
from account_helpers.AccountSettings import TRAJECTORY_VIEW_HINT_COUNTER, QUEST_PROGRESS_SHOWS_COUNT
from constants import VEHICLE_SIEGE_STATE as _SIEGE_STATE, ARENA_PERIOD
from debug_utils import LOG_DEBUG
from gui import GUI_SETTINGS
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, CROSSHAIR_VIEW_ID, STRATEGIC_CAMERA_ID
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.utils.key_mapping import getReadableKey
from gui.shared.utils.plugins import IPlugin
from helpers import i18n, dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
HintData = namedtuple('HintData', ['key',
 'messageLeft',
 'messageRight',
 'offsetX',
 'offsetY',
 'priority'])
_TRAJECTORY_VIEW_HINT_POSITION = (0, 120)
_TRAJECTORY_VIEW_HINT_CHECK_STATES = (VEHICLE_VIEW_STATE.DESTROY_TIMER,
 VEHICLE_VIEW_STATE.DEATHZONE_TIMER,
 VEHICLE_VIEW_STATE.RECOVERY,
 VEHICLE_VIEW_STATE.PROGRESS_CIRCLE,
 VEHICLE_VIEW_STATE.UNDER_FIRE,
 VEHICLE_VIEW_STATE.FIRE,
 VEHICLE_VIEW_STATE.STUN)

def createPlugins():
    return {'trajectoryViewHint': TrajectoryViewHintPlugin,
     'siegeIndicatorHint': SiegeIndicatorHintPlugin,
     'questProgressHint': QuestProgressHintPlugin}


class HintPanelPlugin(IPlugin):

    def setPeriod(self, period):
        pass

    def updateMapping(self):
        pass

    def _getHint(self):
        return None


class HintPriority(object):
    QUESTS = 0
    TRAJECTORY = 1
    SIEGE = 2


class TrajectoryViewHintPlugin(HintPanelPlugin):
    __slots__ = ('__hintsLeft', '__isHintShown', '__isObserver', '__isDestroyTimerDisplaying', '__isDeathZoneTimerDisplaying')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, parentObj):
        super(TrajectoryViewHintPlugin, self).__init__(parentObj)
        self.__hintsLeft = 0
        self.__isHintShown = False
        self.__isDestroyTimerDisplaying = False
        self.__isDeathZoneTimerDisplaying = False
        self.__isObserver = False

    def start(self):
        arenaDP = self.sessionProvider.getArenaDP()
        crosshairCtrl = self.sessionProvider.shared.crosshair
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        vInfo = arenaDP.getVehicleInfo()
        self.__isObserver = vInfo.isObserver()
        crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
        crosshairCtrl.onStrategicCameraChanged += self.__onStrategicCameraChanged
        vehicleCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        self.__hintsLeft = AccountSettings.getSettings(TRAJECTORY_VIEW_HINT_COUNTER)
        self.__setup(crosshairCtrl, vehicleCtrl)

    def stop(self):
        ctrl = self.sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
            ctrl.onStrategicCameraChanged -= self.__onStrategicCameraChanged
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        if not self.sessionProvider.isReplayPlaying:
            AccountSettings.setSettings(TRAJECTORY_VIEW_HINT_COUNTER, self.__hintsLeft)
        return

    def updateMapping(self):
        if self.__isHintShown:
            self.__addHint()

    def __setup(self, crosshairCtrl, vehicleCtrl):
        self.__onCrosshairViewChanged(crosshairCtrl.getViewID())
        self.__onStrategicCameraChanged(crosshairCtrl.getStrategicCameraID())
        checkStatesIDs = (VEHICLE_VIEW_STATE.FIRE,
         VEHICLE_VIEW_STATE.DESTROY_TIMER,
         VEHICLE_VIEW_STATE.DEATHZONE_TIMER,
         VEHICLE_VIEW_STATE.STUN)
        for stateID in checkStatesIDs:
            stateValue = vehicleCtrl.getStateValue(stateID)
            if stateValue:
                self.__onVehicleStateUpdated(stateID, stateValue)

    def __onCrosshairViewChanged(self, viewID):
        if viewID == CROSSHAIR_VIEW_ID.STRATEGIC and self.__hintsLeft:
            self.__addHint()
        elif self.__isHintShown:
            self.__removeHint()

    def __onStrategicCameraChanged(self, cameraID):
        if cameraID == STRATEGIC_CAMERA_ID.TRAJECTORY:
            self.__hintsLeft = max(0, self.__hintsLeft - 1)
        if not self.__hintsLeft and self.__isHintShown:
            self.__removeHint()

    def __onVehicleStateUpdated(self, stateID, stateValue):
        if self.__isHintShown or self.__hintsLeft and stateID in _TRAJECTORY_VIEW_HINT_CHECK_STATES:
            if stateID == VEHICLE_VIEW_STATE.DESTROY_TIMER:
                self.__isDestroyTimerDisplaying = stateValue.needToShow()
            elif stateID == VEHICLE_VIEW_STATE.DEATHZONE_TIMER:
                self.__isDeathZoneTimerDisplaying = stateValue.needToShow()
            if self.__isHintShown and self.__isThereAnyIndicators():
                self.__removeHint()
            else:
                ctrl = self.sessionProvider.shared.crosshair
                if ctrl is not None:
                    self.__onCrosshairViewChanged(ctrl.getViewID())
        return

    def __isThereAnyIndicators(self):
        if self.__isDestroyTimerDisplaying or self.__isDeathZoneTimerDisplaying:
            result = True
        else:
            ctrl = self.sessionProvider.shared.vehicleState
            result = ctrl is not None and ctrl.getStateValue(VEHICLE_VIEW_STATE.STUN) or ctrl.getStateValue(VEHICLE_VIEW_STATE.FIRE)
        return result

    def __addHint(self):
        if self.__isObserver:
            return
        if GUI_SETTINGS.spgAlternativeAimingCameraEnabled and not (self.sessionProvider.isReplayPlaying or self.__isThereAnyIndicators()):
            self._parentObj.setBtnHint(CommandMapping.CMD_CM_TRAJECTORY_VIEW, self._getHint())
            self.__isHintShown = True

    def __removeHint(self):
        if self.__isObserver:
            return
        if not self.sessionProvider.isReplayPlaying:
            self._parentObj.removeBtnHint(CommandMapping.CMD_CM_TRAJECTORY_VIEW)
            self.__isHintShown = False

    def _getHint(self):
        hintTextLeft = ''
        keyName = getReadableKey(CommandMapping.CMD_CM_TRAJECTORY_VIEW)
        if keyName:
            hintTextLeft = i18n.makeString(INGAME_GUI.TRAJECTORYVIEW_HINT_ALTERNATEMODELEFT)
            hintTextRight = i18n.makeString(INGAME_GUI.TRAJECTORYVIEW_HINT_ALTERNATEMODERIGHT)
        else:
            hintTextRight = i18n.makeString(INGAME_GUI.TRAJECTORYVIEW_HINT_NOBINDINGKEY)
        return HintData(keyName, hintTextLeft, hintTextRight, _TRAJECTORY_VIEW_HINT_POSITION[0], _TRAJECTORY_VIEW_HINT_POSITION[1], HintPriority.TRAJECTORY)


class SiegeIndicatorHintPlugin(HintPanelPlugin):
    __slots__ = ('__isEnabled', '__siegeState', '__hintsLeft', '__isHintShown', '__isInPostmortem', '__isObserver')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, parentObj):
        super(SiegeIndicatorHintPlugin, self).__init__(parentObj)
        self.__isEnabled = False
        self.__siegeState = _SIEGE_STATE.DISABLED
        self.__hintsLeft = 0
        self.__isHintShown = False
        self.__isInPostmortem = False
        self.__isObserver = False
        self._isInRecovery = False
        self._isInProgressCircle = False
        self._isUnderFire = False

    def start(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        arenaDP = self.sessionProvider.getArenaDP()
        self.__hintsLeft = AccountSettings.getSettings('siegeModeHintCounter')
        if arenaDP is not None:
            self.__isObserver = arenaDP.getVehicleInfo().isObserver()
        else:
            self.__isObserver = False
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling += self.__onVehicleControlling
            vStateCtrl.onPostMortemSwitched += self.__onPostMortemSwitched
            vStateCtrl.onRespawnBaseMoving += self.__onRespawnBaseMoving
            vehicle = vStateCtrl.getControllingVehicle()
            if vehicle is not None:
                self.__onVehicleControlling(vehicle)
        return

    def stop(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
            vStateCtrl.onVehicleControlling -= self.__onVehicleControlling
            vStateCtrl.onPostMortemSwitched -= self.__onPostMortemSwitched
            vStateCtrl.onRespawnBaseMoving -= self.__onRespawnBaseMoving
        AccountSettings.setSettings('siegeModeHintCounter', self.__hintsLeft)
        return

    def updateMapping(self):
        if not self.__isEnabled:
            return
        self.__updateHint()

    def __updateHint(self):
        LOG_DEBUG('Updating siege mode: hint')
        if self.__isInPostmortem or self.__isObserver:
            return
        if self.__siegeState not in _SIEGE_STATE.SWITCHING and self.__hintsLeft and not self.__areOtherIndicatorsShown():
            self._parentObj.setBtnHint(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, self._getHint())
            self.__isHintShown = True
        elif self.__isHintShown or self.__areOtherIndicatorsShown():
            self._parentObj.removeBtnHint(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
            self.__isHintShown = False

    def __onVehicleControlling(self, vehicle):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        vTypeDesc = vehicle.typeDescriptor
        if vehicle.isAlive() and vTypeDesc.hasSiegeMode:
            self.__isEnabled = True
            state = VEHICLE_VIEW_STATE.SIEGE_MODE
            value = vStateCtrl.getStateValue(state)
            if value is not None:
                self.__onVehicleStateUpdated(state, value)
        else:
            self.__siegeState = _SIEGE_STATE.DISABLED
            if self.__isEnabled:
                self._parentObj.removeBtnHint(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
            self.__isEnabled = False
        return

    def __onVehicleStateUpdated(self, state, value):
        if not self.__isEnabled:
            return
        if state == VEHICLE_VIEW_STATE.SIEGE_MODE:
            siegeState, _ = value
            if siegeState == _SIEGE_STATE.SWITCHING_OFF:
                if not self.__isObserver and not self.__isInPostmortem:
                    self.__hintsLeft = max(0, self.__hintsLeft - 1)
            self.__siegeState = siegeState
            self.__updateHint()
        elif state == VEHICLE_VIEW_STATE.RECOVERY:
            self._isInRecovery = value[0]
            if self.__isEnabled:
                self.__updateHint()
        elif state == VEHICLE_VIEW_STATE.PROGRESS_CIRCLE:
            self._isInProgressCircle = value[1]
            if self.__isEnabled:
                self.__updateHint()
        elif state == VEHICLE_VIEW_STATE.UNDER_FIRE:
            self._isUnderFire = value
            if self.__isEnabled:
                self.__updateHint()

    def __onPostMortemSwitched(self, *args):
        self.__isInPostmortem = True
        self._parentObj.removeBtnHint(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        self.__isHintShown = False

    def __onRespawnBaseMoving(self):
        self.__isInPostmortem = False

    def __updateDestroyed(self, _):
        self.__isEnabled = False
        self._parentObj.removeBtnHint(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)

    def _getHint(self):
        keyName = getReadableKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        pressText = ''
        if keyName:
            pressText = INGAME_GUI.SIEGEMODE_HINT_PRESS
            hintText = INGAME_GUI.siegeModeHint(self.__siegeState)
        else:
            hintText = INGAME_GUI.SIEGEMODE_HINT_NOBINDING
        return HintData(keyName, pressText, hintText, 0, 0, HintPriority.SIEGE)

    def __areOtherIndicatorsShown(self):
        return self._isUnderFire or self._isInRecovery or self._isInProgressCircle


class QuestProgressHintPlugin(HintPanelPlugin):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, parentObj):
        super(QuestProgressHintPlugin, self).__init__(parentObj)
        self.__hintsLeft = 0
        self.__isHintInQueue = False
        self.__isActive = False
        self.__wasHintProcessed = False

    def start(self):
        arenaDP = self.sessionProvider.getArenaDP()
        g_eventBus.addListener(GameEvent.SHOW_BTN_HINT, self.__handleShowBtnHint, scope=EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.addListener(GameEvent.FULL_STATS_QUEST_PROGRESS, self.__handlePressHintBtn, scope=EVENT_BUS_SCOPE.BATTLE)
        vInfo = arenaDP.getVehicleInfo()
        self.__isActive = vInfo.vehicleType.level >= 4
        self.__hintsLeft = AccountSettings.getSettings(QUEST_PROGRESS_SHOWS_COUNT)

    def stop(self):
        g_eventBus.removeListener(GameEvent.SHOW_BTN_HINT, self.__handleShowBtnHint, scope=EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.removeListener(GameEvent.FULL_STATS_QUEST_PROGRESS, self.__handlePressHintBtn, scope=EVENT_BUS_SCOPE.BATTLE)
        if self.__wasHintProcessed:
            AccountSettings.setSettings(QUEST_PROGRESS_SHOWS_COUNT, max(self.__hintsLeft - 1, 0))

    def setPeriod(self, period):
        if self.__isActive and self.__hintsLeft > 0:
            if period in (ARENA_PERIOD.PREBATTLE, ARENA_PERIOD.WAITING):
                if not self.__isHintInQueue:
                    self._parentObj.setBtnHint(CommandMapping.CMD_QUEST_PROGRESS_SHOW, self._getHint())
                    self.__isHintInQueue = True
            elif self.__isHintInQueue:
                self._parentObj.removeBtnHint(CommandMapping.CMD_QUEST_PROGRESS_SHOW)
                self.__isHintInQueue = False

    def updateMapping(self):
        if self.__hintsLeft > 0:
            if self.__isHintInQueue:
                self._parentObj.setBtnHint(CommandMapping.CMD_QUEST_PROGRESS_SHOW, self._getHint())

    def _getHint(self):
        keyName = getReadableKey(CommandMapping.CMD_QUEST_PROGRESS_SHOW)
        pressText = ''
        if keyName:
            pressText = INGAME_GUI.BATTLEPROGRESS_HINT_PRESS
            hintText = INGAME_GUI.BATTLEPROGRESS_HINT_DESCRIPTION
        else:
            hintText = INGAME_GUI.BATTLEPROGRESS_HINT_NOBINDINGKEY
        return HintData(keyName, pressText, hintText, 0, 0, HintPriority.QUESTS)

    def __handleShowBtnHint(self, event):
        if event.ctx.get('btnID') == CommandMapping.CMD_QUEST_PROGRESS_SHOW:
            self.__wasHintProcessed = True

    def __handlePressHintBtn(self, event):
        self.__wasHintProcessed = True
