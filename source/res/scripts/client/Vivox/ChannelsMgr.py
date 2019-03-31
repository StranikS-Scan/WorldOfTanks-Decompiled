# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Vivox/ChannelsMgr.py
# Compiled at: 2011-09-06 16:32:38
import BigWorld
from debug_utils import LOG_DEBUG, LOG_ERROR, verify
from wotdecorators import noexcept
import Event
import messages
import constants
import threading

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

    def __init__(self):
        self.domain = ''
        self.user = ['', '']
        self.channel = ['', '']
        self.enabled = False
        self.loggedIn = False
        self.currentChannel = ''
        self.initialized = False
        self.state = self.STATE_NONE
        self.onCaptureDevicesUpdated = Event.Event()
        self.onParticipantAdded = Event.Event()
        self.onParticipantRemoved = Event.Event()
        self.onParticipantUpdated = Event.Event()
        self.onJoinedChannel = Event.Event()
        self.onLeftChannel = Event.Event()
        self.onInitialized = Event.Event()
        self.onLogined = Event.Event()
        self.onStateChanged = Event.Event()

    def initialize(self, domain):
        verify(self.domain or not self.initialized)
        verify(self.state == self.STATE_NONE)
        self.domain = domain
        self.__changeState()

    def destroy(self):
        BigWorld.VOIP.finalise()

    def login(self, name, password):
        self.user = [name, password]
        self.__changeState()

    def logout(self):
        self.user = ['', '']
        self.channel = ['', '']
        self.__changeState()

    def enterChannel(self, name, password):
        self.channel = [name, password]
        self.__changeState()

    def leaveChannel(self):
        self.channel = ['', '']
        self.__changeState()

    def enable(self, enabled):
        self.enabled = enabled
        self.__changeState()

    def setState(self, newState):
        if newState == self.state:
            return
        LOG_DEBUG('__changeState %s on %s' % (self.states[self.state], self.states[newState]))
        self.state = newState
        self.onStateChanged(self.state, newState)

    def __changeState(self):
        if self.state == self.STATE_NONE and not self.initialized and self.domain != '':
            self.__initialize()
            self.setState(self.STATE_INITIALIZING)
        elif self.state == self.STATE_INITIALIZING and self.initialized:
            self.setState(self.STATE_INITIALIZED)
            if self.user[0] != '':
                self.__changeState()
        elif self.state == self.STATE_INITIALIZED and self.user[0] != '':
            self.setState(self.STATE_LOGGING_IN)
            self.__loginUser()
        elif self.state == self.STATE_LOGGING_IN and self.loggedIn:
            self.setState(self.STATE_LOGGED_IN)
            if self.channel[0] != '':
                self.__changeState()
        elif self.state == self.STATE_LOGGED_IN:
            if self.user[0] == '':
                self.setState(self.STATE_LOGGING_OUT)
                BigWorld.VOIP.logout()
            elif self.channel[0] != '' and self.enabled:
                self.setState(self.STATE_JOINING_CHANNEL)
                self.__joinChannel(self.channel[0], self.channel[0])
        elif self.state == self.STATE_LOGGING_OUT and not self.loggedIn:
            self.setState(self.STATE_INITIALIZED)
            self.__changeState()
        elif self.state == self.STATE_JOINING_CHANNEL and self.currentChannel:
            self.setState(self.STATE_JOINED_CHANNEL)
            if self.channel[0] != self.currentChannel:
                self.setState(self.STATE_LEAVING_CHANNEL)
                self.__leaveChannel(self.currentChannel)
        elif self.state == self.STATE_JOINED_CHANNEL and (self.currentChannel != self.channel[0] or not self.enabled):
            self.setState(self.STATE_LEAVING_CHANNEL)
            self.__leaveChannel(self.currentChannel)
        elif self.state == self.STATE_LEAVING_CHANNEL and not self.currentChannel:
            self.setState(self.STATE_LOGGED_IN)
            self.__changeState()
        else:
            LOG_DEBUG('__changeState  state not changed - ', self.state)

    def __initialize(self):
        vinit = {}
        vinit['vivox_server'] = 'http://%s/api2' % self.domain
        vinit['minimum_port'] = '0'
        vinit['maximum_port'] = '0'
        vinit['log_prefix'] = 'vivox'
        vinit['log_suffix'] = '.txt'
        vinit['log_folder'] = '.'
        vinit['log_level'] = '0'
        threading.Thread(target=BigWorld.VOIP.initialise, name='initialization', args=[vinit]).start()

    def __loginUser(self):
        cmd = {}
        cmd[constants.KEY_PARTICIPANT_PROPERTY_FREQUENCY] = '100'
        BigWorld.VOIP.login(self.user[0], self.user[1], cmd)
        LOG_DEBUG('Login Request:', self.user)

    def __joinChannel(self, channelURI, password):
        BigWorld.VOIP.command({'command': 'hangup'})
        BigWorld.VOIP.joinChannel(channelURI, password, {})
        self.debug("Joining channel '%s'" % channelURI)
        self.__changeState()

    def __leaveChannel(self, channel):
        BigWorld.VOIP.leaveChannel(channel)
        self.debug("Leaving channel '%s'" % channel)
        self.__changeState()

    def debug(self, text):
        prefix = 'VRH: '
        LOG_DEBUG('\n%s%s\n' % (prefix, text))

    @noexcept
    def __call__(self, message, data={}):
        if message not in [messages.vxParticipantUpdated]:
            msg = '::Message: %d [%s], Data: %s' % (message, messages.MESSAGE_IDS[message], data)
            self.debug(msg)
        if message == messages.vxConnectorCreated:
            if data[constants.KEY_CONNECTOR_HANDLE] != '':
                self.initialized = True
                self.onInitialized(data)
                self.__changeState()
        elif message == messages.vxSessionGroupAdded:
            self.loggedIn = True
            self.__changeState()
        elif message == messages.vxSessionGroupRemoved:
            pass
        elif message == messages.vxMediaStreamUpdated:
            state = int(data[constants.KEY_STATE])
            self.debug('CHANNEL DATA: %s' % data)
            if state == constants.SESSION_MEDIA_CONNECTED:
                self.currentChannel = data[constants.KEY_CHANNEL_URI]
                self.onJoinedChannel(data)
                self.__changeState()
            elif state == constants.SESSION_MEDIA_DISCONNECTED:
                self.currentChannel = ''
                self.onLeftChannel(data)
                self.__changeState()
        elif message == messages.vxParticipantRemoved:
            self.onParticipantRemoved(data)
        elif message == messages.vxParticipantAdded:
            self.onParticipantAdded(data)
        elif message == messages.vxParticipantUpdated:
            self.onParticipantUpdated(data)
        elif message == messages.vxAuxGetCaptureDevices:
            self.onCaptureDevicesUpdated(data)
        elif message == messages.vxSessionAdded:
            pass
        elif message == messages.vxSessionRemoved:
            pass
        elif message == messages.vxAccountLogin:
            self.onLogined()
        elif message == messages.vxAccountLogout:
            self.debug('caught vxAccountLogout msg :%s' % data)
            verify(self.currentChannel == '')
            self.loggedIn = False
            self.__changeState()
        elif message == messages.vxAccountLoginStateChange:
            pass
