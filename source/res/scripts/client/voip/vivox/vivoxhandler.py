# Embedded file name: scripts/client/VOIP/Vivox/VivoxHandler.py
import BigWorld
from VOIP.ChannelsMgr import ChannelsMgr
from VOIP import messages
from VOIP import constants
from VOIP.VOIPManager import LOG_VOIP_INT
import Settings
import threading
from wotdecorators import noexcept

class VivoxHandler(ChannelsMgr):

    def __init__(self):
        ChannelsMgr.__init__(self)
        self.__loginAttemptsRemained = 2

    def _initialize(self):
        logLevel = 0
        section = Settings.g_instance.userPrefs
        if section.has_key('development'):
            section = section['development']
            if section.has_key('vivoxLogLevel'):
                logLevel = section['vivoxLogLevel'].asInt
        vinit = {'vivox_server': 'http://%s/api2' % self.domain,
         'minimum_port': '0',
         'maximum_port': '0',
         'log_prefix': 'vivox',
         'log_suffix': '.txt',
         'log_folder': '.',
         'log_level': str(logLevel)}
        threading.Thread(target=BigWorld.VOIP.initialise, name='initialization', args=[vinit]).start()

    def onConnected(self):
        self.__loginAttemptsRemained = 2

    def _loginUser(self):
        cmd = {}
        cmd[constants.KEY_PARTICIPANT_PROPERTY_FREQUENCY] = '100'
        BigWorld.VOIP.login(self.user[0], self.user[1], cmd)
        LOG_VOIP_INT("Login Request: '%s', '%s'" % (self.user[0], self.user[1]))

    def __reloginUser(self):
        LOG_VOIP_INT('VivoxHandler.__reloginUser')
        self.__loginAttemptsRemained -= 1
        LOG_VOIP_INT('Requesting user reregistration, attempts remained: %d' % self.__loginAttemptsRemained)
        if self.enabled:
            BigWorld.player().requestVOIPCredentials(1)

    @noexcept
    def __call__(self, message, data = {}):
        LOG_VOIP_INT('Message: %d [%s], Data: %s' % (message, messages.MESSAGE_IDS[message], data))
        if message == messages.vxConnectorCreated:
            if data[constants.KEY_CONNECTOR_HANDLE] != '':
                self.initialized = True
                self.onInitialized(data)
                self._changeState()
        elif message == messages.vxSessionGroupAdded:
            self.loggedIn = True
            self._changeState()
        elif message == messages.vxSessionGroupRemoved:
            LOG_VOIP_INT('vxSessionGroupRemoved')
        elif message == messages.vxMediaStreamUpdated:
            state = int(data[constants.KEY_STATE])
            if state == constants.SESSION_MEDIA_CONNECTED:
                self.currentChannel = data[constants.KEY_CHANNEL_URI]
                self.onJoinedChannel(data)
                self._changeState()
            elif state == constants.SESSION_MEDIA_DISCONNECTED:
                self.__handleSessionMediaDisconnect(data)
        elif message == messages.vxParticipantRemoved:
            self.onParticipantRemoved(data)
        elif message == messages.vxParticipantAdded:
            self.onParticipantAdded(data)
        elif message == messages.vxParticipantUpdated:
            self.onParticipantUpdated(data)
        elif message == messages.vxAuxGetCaptureDevices:
            self.onCaptureDevicesArrived(data)
        elif message == messages.vxSessionAdded:
            pass
        elif message == messages.vxSessionRemoved:
            pass
        elif message == messages.vxAccountLogin:
            if data[constants.KEY_RETURN_CODE] == '0':
                self.onLogined()
            else:
                if data[constants.KEY_STATUS_CODE] == '20200' and self.__loginAttemptsRemained > 0:
                    self.__reloginUser()
                else:
                    self.onFailedToConnect()
                LOG_VOIP_INT("ERROR vxAccountLogin: status_code '%d' = '%s'" % (int(data[constants.KEY_STATUS_CODE]), data[constants.KEY_STATUS_STRING]))
                self.loggedIn = False
                self._clearUser()
                self._changeState(wrongCredentials=True)
        elif message == messages.vxAccountLogout:
            pass
        elif message == messages.vxAccountLoginStateChange:
            if data[constants.KEY_STATE] == '0' and data[constants.KEY_STATUS_CODE] != '20200':
                self.loggedIn = False
                self._changeState()
        elif message == messages.vxAuxGetVADProperties:
            LOG_VOIP_INT('vxAuxGetVADProperties: %s' % str(data))
        elif message == messages.vxAuxConnectivityInfo:
            if data[constants.KEY_STATUS_CODE] == '10007':
                self.onFailedToConnect()
                self.setState(self.STATE_LEAVING_CHANNEL)
                self.sendLeave(self.channel[0])
                self._clearDesiredChannel()
                self.currentChannel = ''
                self._changeState()

    def __handleSessionMediaDisconnect(self, data):
        self.onLeftChannel(data)
        statusCode = int(data[constants.KEY_STATUS_CODE])
        if statusCode > 400:
            LOG_VOIP_INT('vxMediaStreamUpdated, SessionMedia disconnected, code: %d, message: %s' % (statusCode, data[constants.KEY_STATUS_STRING]))
            self.setState(self.STATE_LEAVING_CHANNEL)
            if not self.currentChannel or self.isInDesiredChannel():
                self._clearDesiredChannel()
        self.currentChannel = ''
        self._changeState()
