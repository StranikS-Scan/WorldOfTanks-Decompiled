# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/sound_systems/wwise_system.py
import WWISE
import BigWorld
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_WARNING
from gui.sounds.abstract import SoundSystemAbstract
from gui.sounds.sound_constants import SoundSystems, SPEAKERS_CONFIG
_LAPTOP_SOUND_PRESET = 2
_LOGIN = 0
_LOBBY = 1
_QUEUE = 2
_BATTLE_LOADING = 3
_BATTLE = 4
_BATTLE_RESULT = 5
_envTransition = ((None, 0.0, 0.0, 0.0, 0.0, 0.0),
 (0.0, None, 0.0, 0.0, 0.0, 0.0),
 (0.0, 2.0, None, 0.0, 0.0, 0.0),
 (0.0, 0.0, 0.0, None, 0.0, 0.0),
 (0.0, 0.0, 0.0, 0.0, None, 0.0),
 (0.0, 0.0, 0.0, 0.0, 0.0, None))

class _EnvironmentListNode(object):
    __slots__ = ('__prev', '__next', '__environment', '__enterState', '__exitState', '__envID', '__cbkID')

    def __init__(self, environment, start_state, exit_state, envID, previous=None):
        self.__prev = previous
        self.__next = None
        self.__environment = environment
        self.__enterState = start_state
        self.__exitState = exit_state
        self.__envID = envID
        self.__cbkID = None
        return

    def pushEnv(self, nextNode):
        self.__next = nextNode
        nextNode.setPrev(self)
        self.__setExitState()
        nextNode.setDelayedEnter(self.__envID)
        return nextNode

    def setPrev(self, prevState):
        self.__prev = prevState

    def setNext(self, nextState):
        self.__next = nextState

    def popEnv(self):
        self.__setExitState()
        if self.__prev is not None:
            self.__prev.setDelayedEnter(self.__envID)
        prev = self.__prev
        self.__prev = None
        self.__next = None
        if prev is not None:
            prev.setNext(None)
        return prev

    def setDelayedEnter(self, prevID):
        if self.__envID is None:
            return
        else:
            if prevID is None:
                delayT = None
            else:
                delayT = _envTransition[prevID][self.__envID]
            if delayT is None or delayT < 0.01:
                self.__setEnterState()
                return
            self.__cbkID = BigWorld.callback(delayT, self.__setEnterState)
            return

    def __setEnterState(self):
        if self.__enterState:
            LOG_DEBUG('Set Enter UE sound state "{}" for previous finished environment: "{}"'.format(self.__enterState, self.__environment))
            WWISE.WW_eventGlobalSync(self.__enterState)
        self.__cbkID = None
        return

    def __setExitState(self):
        if self.__cbkID is not None:
            BigWorld.cancelCallback(self.__cbkID)
            self.__cbkID = None
            return
        else:
            if self.__exitState:
                LOG_DEBUG('Set Exit UE sound state "{}" for the stopped environment "{}"'.format(self.__exitState, self.__environment))
                WWISE.WW_eventGlobalSync(self.__exitState)
            return


class _EnvironmentStatesSubSys(object):
    _envStateDefs = {'login': ('ue_01_loginscreen_enter', 'ue_01_loginscreen_exit', _LOGIN),
     'lobby': ('ue_02_hangar_enter', 'ue_02_hangar_exit', _LOBBY),
     'queue': ('ue_03_lobby_enter', 'ue_03_lobby_exit', _QUEUE),
     'battleLoading': ('ue_04_loadingscreen_enter', 'ue_04_loadingscreen_exit', _BATTLE_LOADING),
     'battle': ('ue_05_arena_enter', 'ue_05_arena_exit', _BATTLE),
     'battleResults': ('ue_06_result_enter', 'ue_06_result_exit', _BATTLE_RESULT)}

    def __init__(self):
        self._head = _EnvironmentListNode(None, None, None, None)
        return

    def onEnvStart(self, environment):
        state = self._envStateDefs.get(environment)
        if state is not None:
            self._head = self._head.pushEnv(_EnvironmentListNode(environment, *state))
        return

    def onEnvStop(self, newEnvironment):
        state = self._envStateDefs.get(newEnvironment)
        if state is not None:
            if self._head is not None:
                self._head = self._head.popEnv()
            else:
                LOG_WARNING('Unexpected behaviour: list node could not be None in such situation...')
        return


class WWISESoundSystem(SoundSystemAbstract):

    def __init__(self):
        super(WWISESoundSystem, self).__init__()
        self.__envStatesSubSys = _EnvironmentStatesSubSys()

    def getID(self):
        return SoundSystems.WWISE

    def isMSR(self):
        return WWISE.WG_isMSR()

    def enableDynamicPreset(self):
        wwiseEvent = 'ue_set_preset_high_dynamic_range'
        self.sendGlobalEvent(wwiseEvent)
        LOG_DEBUG('WWISE: triggered {0}'.format(wwiseEvent))

    def disableDynamicPreset(self):
        wwiseEvent = 'ue_set_preset_low_dynamic_range'
        self.sendGlobalEvent(wwiseEvent)
        LOG_DEBUG('WWISE: triggered {0}'.format(wwiseEvent))

    def setBassBoost(self, isEnabled):
        if isEnabled:
            wwiseEvent = 'ue_set_preset_bassboost_on'
        else:
            wwiseEvent = 'ue_set_preset_bassboost_off'
        WWISE.WW_eventGlobalSync(wwiseEvent)
        LOG_DEBUG('WWISE: triggered {0}'.format(wwiseEvent))

    def getSystemSpeakersPresetID(self):
        return WWISE.WW_getSystemSpeakersConfig()

    def getUserSpeakersPresetID(self):
        return WWISE.WW_getUserSpeakersConfig()

    def setUserSpeakersPresetID(self, presetID):
        if presetID not in SPEAKERS_CONFIG.RANGE:
            LOG_ERROR('Invalid value of presetID {}'.format(presetID))
            return
        if self.getUserSpeakersPresetID() == presetID:
            LOG_DEBUG('WWISE: Sounds preset is already set. Do nothing')
        else:
            WWISE.WW_setUserSpeakersConfig(presetID)
            LOG_DEBUG('WWISE: New sounds preset is set. New value is {}'.format(presetID))
            WWISE.WW_reinit()
            LOG_DEBUG('WWISE: Sound system is reinitialized')
            BigWorld.reinitVideoSound()

    def setSoundSystem(self, soundSystemID):
        if soundSystemID == _LAPTOP_SOUND_PRESET:
            wwiseEvent = 'ue_set_preset_acoustic_device_laptop'
            soundSystemID = 0
            WWISE.WW_setSoundSystem(soundSystemID)
            WWISE.WW_eventGlobalSync(wwiseEvent)
        else:
            wwiseEvent = 'ue_set_preset_acoustic_device_reset'
            WWISE.WW_eventGlobalSync(wwiseEvent)
            WWISE.WW_setSoundSystem(soundSystemID)
        LOG_DEBUG('WWISE: triggered {0}'.format(wwiseEvent))
        LOG_DEBUG('WWISE: sound system has been applied: %d' % soundSystemID)

    def sendGlobalEvent(self, eventName, **params):
        WWISE.WW_eventGlobalSync(eventName)

    def onEnvStart(self, environment):
        self.__envStatesSubSys.onEnvStart(environment)

    def onEnvStop(self, environment):
        self.__envStatesSubSys.onEnvStop(environment)
