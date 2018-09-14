# Embedded file name: scripts/client/VOIP/VOIPFsm.py
import Event
from VOIPLog import LOG_VOIP_INT

class VOIP_FSM_STATE(object):
    NONE = 0
    INITIALIZING = 1
    INITIALIZED = 2
    LOGGING_IN = 3
    LOGGED_IN = 4
    LOGGING_OUT = 5
    JOINING_CHANNEL = 6
    JOINED_CHANNEL = 7
    LEAVING_CHANNEL = 8


_STATE = VOIP_FSM_STATE
_STATE_NAMES = dict([ (v, k) for k, v in VOIP_FSM_STATE.__dict__.iteritems() if not k.startswith('_') ])

class VOIPFsm:

    def __init__(self):
        self.__state = _STATE.NONE
        self.onStateChanged = Event.Event()

    def getState(self):
        return self.__state

    def __setState(self, newState):
        if newState == self.__state:
            return
        LOG_VOIP_INT('%s -> %s' % (_STATE_NAMES[self.__state], _STATE_NAMES[newState]))
        oldState = self.__state
        self.__state = newState
        self.onStateChanged(oldState, newState)

    def inNoneState(self):
        return self.__state == _STATE.NONE

    def reset(self):
        self.__state = _STATE.NONE

    def update(self, voip):
        if self.__state == _STATE.NONE:
            self.__setState(_STATE.INITIALIZING)
        elif self.__state == _STATE.INITIALIZING and voip.isInitialized():
            self.__setState(_STATE.INITIALIZED)
        elif self.__state == _STATE.INITIALIZED and voip.getUser() != '':
            self.__setState(_STATE.LOGGING_IN)
        elif self.__state == _STATE.LOGGING_IN and voip.isLoggedIn():
            self.__setState(_STATE.LOGGED_IN)
        elif self.__state == _STATE.LOGGING_IN and not voip.isLoggedIn():
            self.__setState(_STATE.INITIALIZED)
        elif self.__state == _STATE.LOGGED_IN and voip.hasDesiredChannel() and voip.isEnabled():
            self.__setState(_STATE.JOINING_CHANNEL)
        elif self.__state == _STATE.LOGGED_IN and voip.getUser() == '':
            self.__setState(_STATE.LOGGING_OUT)
        elif self.__state == _STATE.LOGGING_OUT and not voip.isLoggedIn():
            self.__setState(_STATE.INITIALIZED)
        elif self.__state == _STATE.JOINING_CHANNEL and voip.getCurrentChannel():
            self.__setState(_STATE.JOINED_CHANNEL)
        elif self.__state == _STATE.JOINING_CHANNEL and not voip.hasDesiredChannel():
            self.__setState(_STATE.LEAVING_CHANNEL)
        elif self.__state == _STATE.JOINED_CHANNEL and (not voip.isInDesiredChannel() or not voip.isEnabled() or not voip.getCurrentChannel()):
            self.__setState(_STATE.LEAVING_CHANNEL)
        elif self.__state == _STATE.LEAVING_CHANNEL and not voip.getCurrentChannel():
            self.__setState(_STATE.LOGGED_IN)
        else:
            LOG_VOIP_INT('%s not changed' % _STATE_NAMES[self.__state])
