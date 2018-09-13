# Embedded file name: scripts/client/VOIP/ChannelsMgr.py
import BigWorld
from debug_utils import verify
from wotdecorators import noexcept
import Event
from VOIPManager import LOG_VOIP_INT

class ChannelsMgr:
    STATE_NONE = 0
    STATE_INITIALIZING = 1
    STATE_INITIALIZED = 2
    STATE_LOGGING_IN = 3
    STATE_LOGGED_IN = 4
    STATE_LOGGING_OUT = 5
    STATE_JOINING_CHANNEL = 6
    STATE_JOINED_CHANNEL = 7
    STATE_LEAVING_CHANNEL = 8
    states = ('STATE_NONE', 'STATE_INITIALIZING', 'STATE_INITIALIZED', 'STATE_LOGGING_IN', 'STATE_LOGGED_IN', 'STATE_LOGGING_OUT', 'STATE_JOINING_CHANNEL', 'STATE_JOINED_CHANNEL', 'STATE_LEAVING_CHANNEL')
    loginName = property(lambda self: self.user[0])
    password = property(lambda self: self.user[1])

    def __init__(self):
        self.domain = ''
        self.user = ['', '']
        self.channel = ['', '']
        self.enabled = False
        self.loggedIn = False
        self.currentChannel = ''
        self.initialized = False
        self.needLogginAfterInit = False
        self.state = self.STATE_NONE
        self.onCaptureDevicesArrived = Event.Event()
        self.onParticipantAdded = Event.Event()
        self.onParticipantRemoved = Event.Event()
        self.onParticipantUpdated = Event.Event()
        self.onJoinedChannel = Event.Event()
        self.onLeftChannel = Event.Event()
        self.onInitialized = Event.Event()
        self.onLogined = Event.Event()
        self.onStateChanged = Event.Event()
        self.onFailedToConnect = Event.Event()

    def _clearUser(self):
        LOG_VOIP_INT("ChannelsMgr.clearUser '%s' '%s'" % (self.user[0], self.user[1]))
        self.user = ['', '']

    def _clearDesiredChannel(self):
        self.channel = ['', '']

    def isInDesiredChannel(self):
        return self.channel[0] == self.currentChannel

    def onConnected(self):
        pass

    def initialize(self, domain):
        verify(not (self.domain or self.initialized))
        verify(self.state == self.STATE_NONE)
        self.domain = domain
        self._changeState()

    def login(self, name, password):
        if not self.initialized:
            self.needLogginAfterInit = True
        self.user = [name, password]
        self._changeState()

    def logout(self):
        LOG_VOIP_INT('ChannelsMgr.logout')
        self._clearUser()
        self._clearDesiredChannel()
        self._changeState()

    def enterChannel(self, name, password):
        LOG_VOIP_INT("ChannelsMgr.enterChannel: '%s' '%s'" % (name, password))
        self.channel = [name, password]
        self._changeState()

    def leaveChannel(self):
        if not self.initialized:
            return
        LOG_VOIP_INT('ChannelsMgr.leaveChannel')
        self._clearDesiredChannel()
        self._changeState()

    def enable(self, enabled):
        self.enabled = enabled
        if not self.enabled:
            self._clearUser()
        elif self.channel[0] != '':
            BigWorld.player().requestVOIPCredentials()
        self._changeState()

    def setState(self, newState):
        if newState == self.state:
            return
        LOG_VOIP_INT('CHANGE_STATE: %s -> %s' % (self.states[self.state], self.states[newState]))
        self.state = newState
        self.onStateChanged(self.state, newState)

    def __resetToInitializedState(self, isNetworkFailure = False):
        self.setState(self.STATE_INITIALIZED)
        if self.currentChannel != '':
            self.onLeftChannel({})
            self.currentChannel = ''
        if not self.needLogginAfterInit:
            self._clearUser()
        self.needLogginAfterInit = False
        self._changeState()
        if isNetworkFailure and BigWorld.player() is not None:
            BigWorld.player().requestVOIPCredentials()
        return

    def _changeState(self, **args):
        if self.state in (self.STATE_LOGGED_IN,
         self.STATE_JOINING_CHANNEL,
         self.STATE_JOINED_CHANNEL,
         self.STATE_LEAVING_CHANNEL,
         self.STATE_LOGGING_OUT) and not self.loggedIn:
            self.__resetToInitializedState(self.state != self.STATE_LOGGING_OUT)
        elif self.state == self.STATE_NONE and not self.initialized and self.domain != '':
            self.setState(self.STATE_INITIALIZING)
            self._initialize()
        elif self.state == self.STATE_INITIALIZING and self.initialized:
            self.__resetToInitializedState()
        elif self.state == self.STATE_INITIALIZED and self.user[0] != '':
            self.setState(self.STATE_LOGGING_IN)
            self._loginUser()
        elif self.state == self.STATE_LOGGING_IN:
            if self.loggedIn:
                self.setState(self.STATE_LOGGED_IN)
                if self.channel[0] != '':
                    self._changeState()
            elif args.get('wrongCredentials', False):
                self.setState(self.STATE_INITIALIZED)
        elif self.state == self.STATE_LOGGED_IN:
            if self.user[0] == '':
                self.setState(self.STATE_LOGGING_OUT)
                BigWorld.VOIP.logout()
            elif self.channel[0] != '' and self.enabled:
                self.setState(self.STATE_JOINING_CHANNEL)
                self._joinChannel(self.channel[0], self.channel[1])
        elif self.state == self.STATE_JOINING_CHANNEL:
            if self.currentChannel:
                LOG_VOIP_INT("Joined to channel: '%s'" % self.currentChannel)
                self.setState(self.STATE_JOINED_CHANNEL)
                if not self.isInDesiredChannel():
                    self.setState(self.STATE_LEAVING_CHANNEL)
                    self.__sendLeaveChannelCommand(self.currentChannel)
                self._changeState()
            elif not self.channel[0]:
                pass
        elif self.state == self.STATE_JOINED_CHANNEL:
            if not self.isInDesiredChannel() or not self.enabled or not self.currentChannel:
                self.setState(self.STATE_LEAVING_CHANNEL)
                self.__sendLeaveChannelCommand(self.currentChannel)
        elif self.state == self.STATE_LEAVING_CHANNEL:
            if not self.currentChannel:
                self.setState(self.STATE_LOGGED_IN)
                self._changeState()
        else:
            LOG_VOIP_INT('CHANGE_STATE: %s not changed' % self.states[self.state])

    def _initialize(self):
        pass

    def _loginUser(self):
        pass

    def _joinChannel(self, channelURI, password):
        LOG_VOIP_INT("Joining channel '%s'" % channelURI)
        BigWorld.VOIP.command({'command': 'hangup'})
        BigWorld.VOIP.joinChannel(channelURI, password, {})
        self._changeState()

    def sendLeave(self, channel):
        self.__sendLeaveChannelCommand(channel)

    def __sendLeaveChannelCommand(self, channel):
        if channel:
            BigWorld.VOIP.leaveChannel(channel)
        LOG_VOIP_INT("Leaving channel '%s'" % channel)
        self._changeState()

    @noexcept
    def __call__(self, message, data = {}):
        pass
