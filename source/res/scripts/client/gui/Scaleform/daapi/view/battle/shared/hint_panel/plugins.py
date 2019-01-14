# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/hint_panel/plugins.py
from collections import namedtuple
from datetime import datetime
import CommandMapping
from account_helpers import AccountSettings
from account_helpers.AccountSettings import TRAJECTORY_VIEW_HINT_SECTION, QUEST_PROGRESS_HINT_SECTION, HELP_SCREEN_HINT_SECTION, SIEGE_HINT_SECTION, WHEELED_MODE_HINT_SECTION, HINTS_LEFT, NUM_BATTLES, LAST_DISPLAY_DAY
from constants import VEHICLE_SIEGE_STATE as _SIEGE_STATE, ARENA_PERIOD
from debug_utils import LOG_DEBUG
from gui import GUI_SETTINGS
from gui.Scaleform.locale.INGAME_GUI import INGAME_GUI
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, CROSSHAIR_VIEW_ID
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from gui.shared.utils.key_mapping import getReadableKey
from gui.shared.utils.plugins import IPlugin
from helpers import i18n, dependency, time_utils
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
HintData = namedtuple('HintData', ['key',
 'messageLeft',
 'messageRight',
 'offsetX',
 'offsetY',
 'priority'])
_HINT_MIN_VEHICLE_LEVEL = 4
_HINT_TIMEOUT = 6
_HINT_COOLDOWN = 4
_HINT_DISPLAY_COUNT_AFTER_RESET = 1
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
     'prebattleHints': PreBattleHintPlugin}


class HintPanelPlugin(IPlugin):

    def setPeriod(self, period):
        pass

    def updateMapping(self):
        pass

    def _getHint(self):
        return None

    @staticmethod
    def _updateCounterOnUsed(settings):
        settings[LAST_DISPLAY_DAY] = datetime.now().timetuple().tm_yday
        settings[NUM_BATTLES] = 0
        settings[HINTS_LEFT] = max(0, settings[HINTS_LEFT] - 1)

    @staticmethod
    def _updateCounterOnStart(setting, dayCoolDown, battleCoolDown):
        hintsLeft = setting[HINTS_LEFT]
        numBattles = setting[NUM_BATTLES]
        lastDayOfYear = setting[LAST_DISPLAY_DAY]
        dayOfYear = datetime.now().timetuple().tm_yday
        daysLeft = (dayOfYear - lastDayOfYear + time_utils.DAYS_IN_YEAR) % time_utils.DAYS_IN_YEAR
        if hintsLeft == 0 and (daysLeft >= dayCoolDown or numBattles >= battleCoolDown):
            setting[HINTS_LEFT] = _HINT_DISPLAY_COUNT_AFTER_RESET

    @classmethod
    def _updateCounterOnBattle(cls, setting):
        if not cls._haveHintsLeft(setting):
            setting[NUM_BATTLES] = setting[NUM_BATTLES] + 1

    @staticmethod
    def _haveHintsLeft(setting):
        return setting[HINTS_LEFT] > 0


class HintPriority(object):
    TRAJECTORY = 0
    HELP = 1
    QUESTS = 2
    SIEGE = 3


class PRBSettings(object):
    HELP_IDX = 0
    QUEST_IDX = 1
    HINT_DAY_COOLDOWN = 30
    HINT_BATTLES_COOLDOWN = 100


class TrajectoryViewHintPlugin(HintPanelPlugin):
    __slots__ = ('__isHintShown', '__isObserver', '__settings', '__callbackDelayer', '__isDestroyTimerDisplaying', '__isDeathZoneTimerDisplaying', '__wasDisplayed')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _HINT_DAY_COOLDOWN = 30
    _HINT_BATTLES_COOLDOWN = 10

    def __init__(self, parentObj):
        super(TrajectoryViewHintPlugin, self).__init__(parentObj)
        self.__isHintShown = False
        self.__isDestroyTimerDisplaying = False
        self.__isDeathZoneTimerDisplaying = False
        self.__isObserver = False
        self.__settings = {}
        self.__wasDisplayed = False
        self.__callbackDelayer = CallbackDelayer()

    def start(self):
        arenaDP = self.sessionProvider.getArenaDP()
        crosshairCtrl = self.sessionProvider.shared.crosshair
        vehicleCtrl = self.sessionProvider.shared.vehicleState
        vInfo = arenaDP.getVehicleInfo()
        self.__isObserver = vInfo.isObserver()
        crosshairCtrl.onCrosshairViewChanged += self.__onCrosshairViewChanged
        crosshairCtrl.onStrategicCameraChanged += self.__onStrategicCameraChanged
        vehicleCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
        self.__settings = AccountSettings.getSettings(TRAJECTORY_VIEW_HINT_SECTION)
        self._updateCounterOnStart(self.__settings, self._HINT_DAY_COOLDOWN, self._HINT_BATTLES_COOLDOWN)
        self.__setup(crosshairCtrl, vehicleCtrl)

    def stop(self):
        ctrl = self.sessionProvider.shared.crosshair
        if ctrl is not None:
            ctrl.onCrosshairViewChanged -= self.__onCrosshairViewChanged
            ctrl.onStrategicCameraChanged -= self.__onStrategicCameraChanged
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        self.__callbackDelayer.destroy()
        if not self.sessionProvider.isReplayPlaying:
            AccountSettings.setSettings(TRAJECTORY_VIEW_HINT_SECTION, self.__settings)
        return

    def updateMapping(self):
        if self.__isHintShown:
            self.__addHint()

    def setPeriod(self, period):
        if period is ARENA_PERIOD.BATTLE:
            self._updateCounterOnBattle(self.__settings)

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
        haveHintsLeft = self._haveHintsLeft(self.__settings)
        if viewID == CROSSHAIR_VIEW_ID.STRATEGIC and haveHintsLeft:
            self.__addHint()
        elif self.__isHintShown:
            self.__removeHint()

    def __onStrategicCameraChanged(self, cameraID):
        cmdMap = CommandMapping.g_instance
        isUserRequested = cmdMap is not None and cmdMap.isActive(CommandMapping.CMD_CM_TRAJECTORY_VIEW)
        if isUserRequested:
            self._updateCounterOnUsed(self.__settings)
        if isUserRequested and self.__isHintShown:
            self.__removeHint()
        return

    def __onVehicleStateUpdated(self, stateID, stateValue):
        haveHintsLeft = self._haveHintsLeft(self.__settings)
        if self.__isHintShown or haveHintsLeft and stateID in _TRAJECTORY_VIEW_HINT_CHECK_STATES:
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
        if GUI_SETTINGS.spgAlternativeAimingCameraEnabled and not (self.sessionProvider.isReplayPlaying or self.__isThereAnyIndicators()) and not self.__wasDisplayed:
            self._parentObj.setBtnHint(CommandMapping.CMD_CM_TRAJECTORY_VIEW, self._getHint())
            self.__isHintShown = True
            self.__wasDisplayed = True
            self.__callbackDelayer.delayCallback(_HINT_TIMEOUT, self.__onHintTimeOut)

    def __removeHint(self):
        if self.__isObserver:
            return
        if not self.sessionProvider.isReplayPlaying:
            self._parentObj.removeBtnHint(CommandMapping.CMD_CM_TRAJECTORY_VIEW)
            self.__isHintShown = False
            self.__callbackDelayer.stopCallback(self.__onHintTimeOut)

    def __onHintTimeOut(self):
        self.__removeHint()

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
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    settingsCore = dependency.descriptor(ISettingsCore)
    _HINT_DAY_COOLDOWN = 30
    _HINT_BATTLES_COOLDOWN = 10

    def __init__(self, parentObj):
        super(SiegeIndicatorHintPlugin, self).__init__(parentObj)
        self.__isEnabled = False
        self.__siegeState = _SIEGE_STATE.DISABLED
        self.__settings = [{}, {}]
        self.__isHintShown = False
        self.__isInPostmortem = False
        self.__isObserver = False
        self._isInRecovery = False
        self._isInProgressCircle = False
        self._isUnderFire = False
        self.__isWheeledTech = False
        self.__period = None
        self.__isInDisplayPeriod = False
        self.__callbackDelayer = CallbackDelayer()
        return

    def start(self):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        arenaDP = self.sessionProvider.getArenaDP()
        self.__settings = [AccountSettings.getSettings(SIEGE_HINT_SECTION), AccountSettings.getSettings(WHEELED_MODE_HINT_SECTION)]
        self._updateCounterOnStart(self.__settings[0], self._HINT_DAY_COOLDOWN, self._HINT_BATTLES_COOLDOWN)
        self._updateCounterOnStart(self.__settings[1], self._HINT_DAY_COOLDOWN, self._HINT_BATTLES_COOLDOWN)
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
        AccountSettings.setSettings(SIEGE_HINT_SECTION, self.__settings[0])
        AccountSettings.setSettings(WHEELED_MODE_HINT_SECTION, self.__settings[1])
        self.__callbackDelayer.destroy()
        return

    def updateMapping(self):
        if not self.__isEnabled:
            return
        self.__updateHint()

    def setPeriod(self, period):
        if period is ARENA_PERIOD.BATTLE:
            self.__isInDisplayPeriod = self.__period is not None
            self._updateCounterOnBattle(self.__settings[self.__isWheeledTech])
        self.__period = period
        if self.__isEnabled:
            self.__updateHint()
        return

    def __onHintUsed(self):
        self._updateCounterOnUsed(self.__settings[self.__isWheeledTech])

    def __updateHint(self):
        LOG_DEBUG('Updating siege mode: hint')
        if self.__isInPostmortem or self.__isObserver:
            return

        def _showHint():
            self._parentObj.setBtnHint(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION, self._getHint())
            self.__isHintShown = True
            self.__isInDisplayPeriod = False
            self.__callbackDelayer.delayCallback(_HINT_TIMEOUT, self.__onHintTimeOut)

        isInSteadyMode = self.__siegeState not in _SIEGE_STATE.SWITCHING
        haveHintsLeft = self._haveHintsLeft(self.__settings[self.__isWheeledTech])
        if isInSteadyMode and self.__isInDisplayPeriod and haveHintsLeft and not self.__areOtherIndicatorsShown():
            _showHint()
        elif self.__isHintShown or self.__areOtherIndicatorsShown():
            self._parentObj.removeBtnHint(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
            self.__isHintShown = False
            self.__callbackDelayer.destroy()

    def __onVehicleControlling(self, vehicle):
        vStateCtrl = self.sessionProvider.shared.vehicleState
        vTypeDesc = vehicle.typeDescriptor
        self.__isWheeledTech = vTypeDesc.isWheeledVehicle
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
            if siegeState in _SIEGE_STATE.SWITCHING:
                if not self.__isObserver and not self.__isInPostmortem:
                    self.__onHintUsed()
            if self.__siegeState != siegeState:
                self.__siegeState = siegeState
                self.__updateHint()
        elif state == VEHICLE_VIEW_STATE.RECOVERY:
            self._isInRecovery = value[0]
            self.__updateHint()
        elif state == VEHICLE_VIEW_STATE.PROGRESS_CIRCLE:
            self._isInProgressCircle = value[1]
            self.__updateHint()
        elif state == VEHICLE_VIEW_STATE.UNDER_FIRE:
            self._isUnderFire = value
            self.__updateHint()
        elif state == VEHICLE_VIEW_STATE.DESTROYED:
            self.__isInDisplayPeriod = False
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

    def __onHintTimeOut(self):
        self._parentObj.removeBtnHint(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        self.__isHintShown = False

    def _getHint(self):
        keyName = getReadableKey(CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION)
        pressText = ''
        if keyName:
            pressText = INGAME_GUI.SIEGEMODE_HINT_PRESS
            if self.__isWheeledTech:
                hintText = INGAME_GUI.SIEGEMODE_HINT_WHEELED
            else:
                hintText = INGAME_GUI.siegeModeHint(self.__siegeState)
        else:
            hintText = INGAME_GUI.SIEGEMODE_HINT_NOBINDING
        return HintData(keyName, pressText, hintText, 0, 0, HintPriority.SIEGE)

    def __areOtherIndicatorsShown(self):
        return self._isUnderFire or self._isInRecovery or self._isInProgressCircle


class PreBattleHintPlugin(HintPanelPlugin):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, parentObj):
        super(PreBattleHintPlugin, self).__init__(parentObj)
        self.__isActive = False
        self.__hintInQueue = None
        self.__callbackDelayer = CallbackDelayer()
        self.__settings = []
        self.__isInDisplayPeriod = False
        self.__haveReqLevel = False
        return

    def start(self):
        self.__settings = [dict(AccountSettings.getSettings(HELP_SCREEN_HINT_SECTION)), dict(AccountSettings.getSettings(QUEST_PROGRESS_HINT_SECTION))]
        HintPanelPlugin._updateCounterOnStart(self.__settings[PRBSettings.HELP_IDX], PRBSettings.HINT_DAY_COOLDOWN, PRBSettings.HINT_BATTLES_COOLDOWN)
        HintPanelPlugin._updateCounterOnStart(self.__settings[PRBSettings.QUEST_IDX], PRBSettings.HINT_DAY_COOLDOWN, PRBSettings.HINT_BATTLES_COOLDOWN)
        self.__isActive = True
        g_eventBus.addListener(GameEvent.SHOW_BTN_HINT, self.__handleShowBtnHint, scope=EVENT_BUS_SCOPE.GLOBAL)
        g_eventBus.addListener(GameEvent.HELP_DETAILED, self.__handlePressHelpBtn, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(GameEvent.FULL_STATS_QUEST_PROGRESS, self.__handlePressQuestBtn, scope=EVENT_BUS_SCOPE.BATTLE)
        vStateCtrl = self.sessionProvider.shared.vehicleState
        if vStateCtrl is not None:
            vStateCtrl.onVehicleControlling += self.__onVehicleControlling
        return

    def stop(self):
        if not self.isActive():
            return
        else:
            g_eventBus.removeListener(GameEvent.SHOW_BTN_HINT, self.__handleShowBtnHint, scope=EVENT_BUS_SCOPE.GLOBAL)
            g_eventBus.removeListener(GameEvent.HELP_DETAILED, self.__handlePressHelpBtn, scope=EVENT_BUS_SCOPE.BATTLE)
            g_eventBus.removeListener(GameEvent.FULL_STATS_QUEST_PROGRESS, self.__handlePressQuestBtn, scope=EVENT_BUS_SCOPE.BATTLE)
            vStateCtrl = self.sessionProvider.shared.vehicleState
            if vStateCtrl is not None:
                vStateCtrl.onVehicleControlling -= self.__onVehicleControlling
            self.__callbackDelayer.destroy()
            self.__isActive = False
            AccountSettings.setSettings(HELP_SCREEN_HINT_SECTION, self.__settings[PRBSettings.HELP_IDX])
            AccountSettings.setSettings(QUEST_PROGRESS_HINT_SECTION, self.__settings[PRBSettings.QUEST_IDX])
            return

    def isActive(self):
        return self.__isActive

    def setPeriod(self, period):
        self.__isInDisplayPeriod = period in (ARENA_PERIOD.PREBATTLE, ARENA_PERIOD.WAITING)
        if period is ARENA_PERIOD.BATTLE:
            self._updateCounterOnBattle(self.__settings[PRBSettings.HELP_IDX])
            self._updateCounterOnBattle(self.__settings[PRBSettings.QUEST_IDX])

    def updateMapping(self):
        if self.__hintInQueue is not None:
            self._parentObj.setBtnHint(self.__hintInQueue, self._getHint())
        return

    def _getHint(self):
        if self.__hintInQueue is CommandMapping.CMD_SHOW_HELP:
            keyName = getReadableKey(CommandMapping.CMD_SHOW_HELP)
            pressText = INGAME_GUI.HELPSCREEN_HINT_PRESS
            hintText = INGAME_GUI.HELPSCREEN_HINT_DESCRIPTION
            return HintData(keyName, pressText, hintText, 0, 0, HintPriority.HELP)
        if self.__hintInQueue is CommandMapping.CMD_QUEST_PROGRESS_SHOW:
            keyName = getReadableKey(CommandMapping.CMD_QUEST_PROGRESS_SHOW)
            pressText = ''
            hintText = INGAME_GUI.BATTLEPROGRESS_HINT_NOBINDINGKEY
            if keyName:
                pressText = INGAME_GUI.BATTLEPROGRESS_HINT_PRESS
                hintText = INGAME_GUI.BATTLEPROGRESS_HINT_DESCRIPTION
            return HintData(keyName, pressText, hintText, 0, 0, HintPriority.QUESTS)

    def __onVehicleControlling(self, vehicle):
        if not self.isActive():
            return
        elif not vehicle.isAlive():
            return
        else:
            vTypeDesc = vehicle.typeDescriptor
            self.__haveReqLevel = vTypeDesc.level >= _HINT_MIN_VEHICLE_LEVEL
            if self.__canDisplayHelpHint(vTypeDesc):
                self.__displayHint(CommandMapping.CMD_SHOW_HELP)
                return
            elif self.__canDisplayQuestHint():
                self.__displayHint(CommandMapping.CMD_QUEST_PROGRESS_SHOW)
                return
            if self.__hintInQueue is not None:
                self._parentObj.removeBtnHint(CommandMapping.CMD_SHOW_HELP)
                self._parentObj.removeBtnHint(CommandMapping.CMD_QUEST_PROGRESS_SHOW)
                self.__callbackDelayer.destroy()
            return

    def __onHintTimeOut(self):
        self._parentObj.removeBtnHint(self.__hintInQueue)
        if self.__hintInQueue is CommandMapping.CMD_SHOW_HELP:
            self.__callbackDelayer.delayCallback(_HINT_COOLDOWN, self.__onHintTimeCooldown)
        self.__hintInQueue = None
        return

    def __canDisplayHelpHint(self, typeDescriptor):
        return typeDescriptor.isWheeledVehicle and self.__isInDisplayPeriod and self._haveHintsLeft(self.__settings[PRBSettings.HELP_IDX])

    def __canDisplayQuestHint(self):
        return self.__isInDisplayPeriod and self._haveHintsLeft(self.__settings[PRBSettings.QUEST_IDX]) and self.__haveReqLevel

    def __onHintTimeCooldown(self):
        if self.__canDisplayQuestHint():
            self.__displayHint(CommandMapping.CMD_QUEST_PROGRESS_SHOW)

    def __displayHint(self, hintType):
        if self.__isInDisplayPeriod:
            self.__hintInQueue = hintType
            self._parentObj.setBtnHint(hintType, self._getHint())

    def __handleShowBtnHint(self, event):
        if event.ctx.get('btnID') == CommandMapping.CMD_SHOW_HELP or event.ctx.get('btnID') == CommandMapping.CMD_QUEST_PROGRESS_SHOW:
            self.__callbackDelayer.delayCallback(_HINT_TIMEOUT, self.__onHintTimeOut)
        elif self.__callbackDelayer.hasDelayedCallback(self.__onHintTimeOut):
            self.__callbackDelayer.stopCallback(self.__onHintTimeOut)

    def __handlePressHelpBtn(self, event):
        if self.__hintInQueue == CommandMapping.CMD_SHOW_HELP:
            self._parentObj.removeBtnHint(CommandMapping.CMD_SHOW_HELP)
            self.__hintInQueue = None
            self.__callbackDelayer.delayCallback(_HINT_COOLDOWN, self.__onHintTimeCooldown)
        self._updateCounterOnUsed(self.__settings[PRBSettings.HELP_IDX])
        return

    def __handlePressQuestBtn(self, event):
        if self.__hintInQueue == CommandMapping.CMD_QUEST_PROGRESS_SHOW:
            self._parentObj.removeBtnHint(CommandMapping.CMD_QUEST_PROGRESS_SHOW)
            self.__hintInQueue = None
        self._updateCounterOnUsed(self.__settings[PRBSettings.QUEST_IDX])
        return
