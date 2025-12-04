# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/env_switcher/ny_environment_switcher_controller.py
import SoundGroups
import BigWorld
import Event
from new_year.gui.impl.lobby.new_year.env_switcher.environment_change_view import EnvironmentChangeViewWindow
from new_year.ny_constants import NY_ENVIRONMENT_STATE, NY_ENV_SWITCHER_BTN_TIP_SKIPPED
from new_year.gui.impl.new_year.sounds import EnvSwitcherSounds, EnvSwitcherAnimSounds
from helpers.time_utils import HOURS_IN_DAY, MINUTES_IN_HOUR, hmFloatToHourFloat
from new_year.skeletons.new_year import INewYearEnvironmentSwitchController
from new_year_account_settings import getNYSetting, setNYSettings
from functools import partial
from time import localtime
from enum import Enum

class EnvironmentState(Enum):
    DAY = 'Day'
    AUTO = 'Auto'
    NIGHT = 'Night'
    RACCOON = 'Raccoon'


_TIME_OF_DAY_ENV_STATES = (EnvironmentState.DAY, EnvironmentState.NIGHT, EnvironmentState.AUTO)
ENV_CONFIGS = {EnvironmentState.DAY: {'progress': (9.0, 17.0),
                        'angle': (-103, 0)},
 EnvironmentState.NIGHT: {'progress': (17.0, 9.0),
                          'angle': (0, 103)}}
_ENV_STATES_MAPPING = {EnvironmentState.DAY: EnvSwitcherSounds.DAY,
 EnvironmentState.NIGHT: EnvSwitcherSounds.NIGHT}
_CHOICE_SOUNDS = {EnvironmentState.DAY: EnvSwitcherAnimSounds.DAY_CHOICE,
 EnvironmentState.NIGHT: EnvSwitcherAnimSounds.NIGHT_CHOICE}
_ENTER_SOUNDS = {EnvironmentState.DAY: EnvSwitcherSounds.DAY_ENTER,
 EnvironmentState.NIGHT: EnvSwitcherSounds.NIGHT_ENTER}
_EXIT_SOUNDS = {EnvironmentState.DAY: EnvSwitcherSounds.DAY_EXIT,
 EnvironmentState.NIGHT: EnvSwitcherSounds.NIGHT_EXIT}

def _normalizeEnvConfigs(configs):
    for _, cfg in configs.iteritems():
        s, e = cfg['progress']
        cfg['progress'] = (hmFloatToHourFloat(s), hmFloatToHourFloat(e))


_normalizeEnvConfigs(ENV_CONFIGS)

class NewYearEnvironmentSwitcherController(INewYearEnvironmentSwitchController):
    __slots__ = ('__envState', '__needToShowTip', '__envSwitcher', '__appliedDayNightMode')

    def __init__(self, *args, **kwargs):
        super(NewYearEnvironmentSwitcherController, self).__init__(*args, **kwargs)
        self.onEnvironmentSwitched = Event.Event()
        self.onEnvSwitcherBtnPressed = Event.Event()
        self.__envState = EnvironmentState.AUTO
        self.__appliedDayNightMode = EnvironmentState.DAY
        self.__needToShowTip = False
        self.__envSwitcher = None
        return

    @property
    def userEnvState(self):
        return self.__envState

    @property
    def needToShowTip(self):
        return self.__needToShowTip

    @property
    def currentDayNightMode(self):
        return self.resolveDayNightMode(self.__envState)

    @property
    def currentAppliedDayNightMode(self):
        return self.__appliedDayNightMode

    def onConnected(self):
        self.__envState = self._getAccountEnvState()

    def onLobbyInited(self, event):
        self.__needToShowTip = self._getTipState()

    def skipSwitcherTip(self):
        if not self.__needToShowTip:
            return
        self.__needToShowTip = False
        setNYSettings(NY_ENV_SWITCHER_BTN_TIP_SKIPPED, True)

    def notifyTipShouldClose(self):
        if not self.__needToShowTip:
            return
        self.onEnvSwitcherBtnPressed()

    def applyCurrentEnvironment(self):
        self.switchEnvironment(self.__envState.value, setCallback=False)
        self.__appliedDayNightMode = self.resolveDayNightMode(self.__envState)

    def switchEnvironment(self, newEnv, setCallback=True):
        newEnvState = EnvironmentState(newEnv)
        resolvedEnv = self.__resolveEnvironment(newEnvState)
        self.__envSwitcher = BigWorld.EnvironmentSwitcher(resolvedEnv.value)
        if setCallback:
            self.__envSwitcher.setOnSwitchedCallback(partial(self.__onEnvSwitched, newEnvState))
        self.__envSwitcher.enable(True)
        if resolvedEnv in _ENV_STATES_MAPPING:
            SoundGroups.g_instance.setState(EnvSwitcherSounds.GROUP, _ENV_STATES_MAPPING[resolvedEnv])

    def switchDayNightMode(self, newState):
        newEnvState = EnvironmentState(newState)
        newMode = self.resolveDayNightMode(newEnvState)
        if self.currentDayNightMode == newMode:
            self.__commitEnvState(newEnvState)
            self.onEnvironmentSwitched()
            return
        self.__setSoundState(newMode)
        EnvironmentChangeViewWindow(newEnvState).load()

    def getTimeAngle(self):
        if self.__envState in (EnvironmentState.DAY, EnvironmentState.NIGHT):
            return 0
        config = ENV_CONFIGS.get(self.currentDayNightMode)
        percent = self._getProgressPercent(*config['progress'])
        minAngle, maxAngle = config['angle']
        return minAngle + (maxAngle - minAngle) * percent

    def fini(self):
        self.__envState = None
        self.__needToShowTip = None
        return

    def onDisconnected(self):
        self.__stopSwitchCallback()

    @staticmethod
    def _getTipState():
        return not getNYSetting(NY_ENV_SWITCHER_BTN_TIP_SKIPPED)

    @staticmethod
    def _getAccountEnvState():
        envState = getNYSetting(NY_ENVIRONMENT_STATE)
        if envState is None:
            envState = EnvironmentState.AUTO
            setNYSettings(NY_ENVIRONMENT_STATE, envState)
        return envState

    def _getProgressPercent(self, startHour, endHour):
        current = self.__getCurrentTime()
        span = (endHour - startHour) % HOURS_IN_DAY
        pos = (current - startHour) % HOURS_IN_DAY
        pos = min(max(0, pos), span)
        return pos / float(span) if span else 0

    def __resolveEnvironment(self, envState):
        return self.resolveDayNightMode(envState) if envState in _TIME_OF_DAY_ENV_STATES else envState

    @classmethod
    def resolveDayNightMode(cls, envState):
        if envState in (EnvironmentState.DAY, EnvironmentState.NIGHT):
            return envState
        start, end = ENV_CONFIGS[EnvironmentState.DAY]['progress']
        return EnvironmentState.DAY if start <= cls.__getCurrentTime() < end else EnvironmentState.NIGHT

    @staticmethod
    def __getCurrentTime():
        lt = localtime()
        return lt.tm_hour + lt.tm_min / float(MINUTES_IN_HOUR)

    def __setSoundState(self, newMode):
        SoundGroups.g_instance.setState(EnvSwitcherAnimSounds.GROUP, EnvSwitcherAnimSounds.ON)
        self.__playByMode(_CHOICE_SOUNDS, newMode)

    def __onEnvSwitched(self, newEnvState):
        self.__stopSwitchCallback()
        if newEnvState not in _TIME_OF_DAY_ENV_STATES:
            self.onEnvironmentSwitched()
            return
        self.__playByMode(_EXIT_SOUNDS, self.currentDayNightMode)
        self.__commitEnvState(newEnvState)
        currentMode = self.currentDayNightMode
        self.__appliedDayNightMode = currentMode
        self.__playByMode(_ENTER_SOUNDS, currentMode)
        self.onEnvironmentSwitched()

    def __commitEnvState(self, newEnvState):
        if self.__envState != newEnvState:
            setNYSettings(NY_ENVIRONMENT_STATE, newEnvState)
        self.__envState = newEnvState

    def __stopSwitchCallback(self):
        if self.__envSwitcher is not None:
            self.__envSwitcher.setOnSwitchedCallback(lambda : None)
            self.__envSwitcher = None
        return

    @staticmethod
    def __playByMode(table, mode):
        event = table.get(mode)
        if event:
            SoundGroups.g_instance.playSound2D(event)
