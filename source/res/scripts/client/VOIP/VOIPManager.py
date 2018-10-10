# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VOIP/VOIPManager.py
import logging
import BigWorld
import Event
import Settings
import SoundGroups
import VOIPCommon
from VOIP.voip_constants import VOIP_SUPPORTED_API
from VOIPFsm import VOIPFsm, VOIP_FSM_STATE as STATE
from VOIPHandler import VOIPHandler
from constants import CLIENT_INACTIVITY_TIMEOUT
from gui.shared.utils import backoff
from messenger.m_constants import PROTO_TYPE
from messenger.m_constants import USER_ACTION_ID, USER_TAG
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_find_criteria import MutedFindCriteria
from messenger.storage import storage_getter
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())
_BACK_OFF_MIN_DELAY = 1
_BACK_OFF_MAX_DELAY = CLIENT_INACTIVITY_TIMEOUT
_BACK_OFF_MODIFIER = 1
_BACK_OFF_EXP_RANDOM_FACTOR = 0.5

class VOIPManager(VOIPHandler):

    def __init__(self):
        _logger.debug('VOIPManager.Create')
        super(VOIPManager, self).__init__()
        self.__initialized = False
        self.__enabled = False
        self.__voipServer = ''
        self.__voipDomain = ''
        self.__testDomain = ''
        self.__user = ['', '']
        self.__channel = ['', '']
        self.__currentChannel = ''
        self.__inTesting = False
        self.__loggedIn = False
        self.__needLogginAfterInit = False
        self.__normalLogout = False
        self.__loginAttemptsRemained = 2
        self.__fsm = VOIPFsm()
        self.__expBackOff = backoff.ExpBackoff(_BACK_OFF_MIN_DELAY, _BACK_OFF_MAX_DELAY, _BACK_OFF_MODIFIER, _BACK_OFF_EXP_RANDOM_FACTOR)
        self.__reLoginCallbackID = None
        self.__activateMicByVoice = False
        self.__captureDevices = []
        self.__currentCaptureDevice = ''
        self.__channelUsers = {}
        self.onCaptureDevicesUpdated = Event.Event()
        self.onPlayerSpeaking = Event.Event()
        self.onInitialized = Event.Event()
        self.onStateToggled = Event.Event()
        self.onFailedToConnect = Event.Event()
        self.onJoinedChannel = Event.Event()
        self.onLeftChannel = Event.Event()
        self.__fsm.onStateChanged += self.__onStateChanged
        return

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    def destroy(self):
        self.__fsm.onStateChanged -= self.__onStateChanged
        self.__cancelReloginCallback()
        BigWorld.VOIP.finalise()
        _logger.debug('VOIPManager.Destroy')

    def isEnabled(self):
        return self.__enabled

    def isInitialized(self):
        return self.__initialized

    def isNotInitialized(self):
        return not self.__initialized and self.getState() == STATE.NONE

    def isInTesting(self):
        return self.__inTesting

    def getVOIPDomain(self):
        return self.__voipDomain

    def getCurrentChannel(self):
        return self.__currentChannel

    def hasDesiredChannel(self):
        return self.__channel[0] != ''

    def getUser(self):
        return self.__user[0]

    def isInDesiredChannel(self):
        return self.__channel[0] == self.__currentChannel

    def getCaptureDevices(self):
        return self.__captureDevices

    def getCurrentCaptureDevice(self):
        return self.__currentCaptureDevice

    def getState(self):
        return self.__fsm.getState()

    def getAPI(self):
        return BigWorld.VOIP.getAPI()

    def isLoggedIn(self):
        return self.__loggedIn

    def onConnected(self):
        _logger.debug('VOIPManager.Subscribe')
        self.__loginAttemptsRemained = 2
        voipEvents = g_messengerEvents.voip
        voipEvents.onChannelEntered += self.__me_onChannelEntered
        voipEvents.onChannelLeft += self.__me_onChannelLeft
        voipEvents.onCredentialReceived += self.__me_onCredentialReceived
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived += self.__me_onUsersListReceived
        usersEvents.onUserActionReceived += self.__me_onUserActionReceived

    def onDisconnected(self):
        _logger.debug('VOIPManager.Unsubscribe')
        voipEvents = g_messengerEvents.voip
        voipEvents.onChannelEntered -= self.__me_onChannelEntered
        voipEvents.onChannelLeft -= self.__me_onChannelLeft
        voipEvents.onCredentialReceived -= self.__me_onCredentialReceived
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived -= self.__me_onUsersListReceived
        usersEvents.onUserActionReceived -= self.__me_onUserActionReceived

    def enable(self, enabled):
        if enabled:
            self.__enable()
            self.onStateToggled(True, set())
        else:
            dbIDs = set()
            for dbID, data in self.__channelUsers.iteritems():
                if data['talking']:
                    dbIDs.add(dbID)

            self.__disable()
            self.onStateToggled(False, dbIDs)
        self.__fsm.update(self)

    def __enable(self):
        _logger.debug('VOIPManager.Enable')
        self.__enabled = True
        if self.__channel[0] != '' and not self.__user[0]:
            self.__requestCredentials()

    def __disable(self):
        _logger.debug('VOIPManager.Disable')
        self.__enabled = False

    def initialize(self, domain, server):
        if self.__initialized:
            _logger.warning('VOIPManager is already initialized')
            return
        _logger.debug('VOIPManager.Initialize')
        self.__voipServer = server
        self.__voipDomain = domain
        self.__testDomain = 'sip:confctl-2@' + self.__voipDomain
        _logger.debug("voip_server: '%s'", self.__voipServer)
        _logger.debug("voip_domain: '%s'", self.__voipDomain)
        _logger.debug("test_domain: '%s'", self.__testDomain)
        self.__fsm.update(self)
        logLevel = 0
        section = Settings.g_instance.userPrefs
        if section.has_key('development'):
            section = section['development']
            if section.has_key('vivoxLogLevel'):
                logLevel = section['vivoxLogLevel'].asInt
        vinit = {VOIPCommon.KEY_SERVER: 'http://%s/api2' % self.__voipServer,
         VOIPCommon.KEY_MIN_PORT: '0',
         VOIPCommon.KEY_MAX_PORT: '0',
         VOIPCommon.KEY_LOG_PREFIX: 'voip',
         VOIPCommon.KEY_LOG_SUFFIX: '.txt',
         VOIPCommon.KEY_LOG_FOLDER: '.',
         VOIPCommon.KEY_LOG_LEVEL: str(logLevel)}
        BigWorld.VOIP.initialise(vinit)

    def __login(self, name, password):
        if not self.__initialized:
            self.__needLogginAfterInit = True
        self.__user = [name, password]
        if not self.__needLogginAfterInit:
            self.__fsm.update(self)

    def __loginUser(self):
        _logger.debug('Login Request: %s', self.__user[0])
        cmd = {VOIPCommon.KEY_PARTICIPANT_PROPERTY_FREQUENCY: '100'}
        BigWorld.VOIP.login(self.__user[0], self.__user[1], cmd)

    def __loginUserOnCallback(self):
        self.__reLoginCallbackID = None
        self.__loginUser()
        return

    def __reloginUser(self):
        self.__loginAttemptsRemained -= 1
        _logger.debug('VOIPHandler.ReloginUser. Attempts remained: %d', self.__loginAttemptsRemained)
        if self.__enabled:
            self.__requestCredentials(1)

    def __cancelReloginCallback(self):
        if self.__reLoginCallbackID is not None:
            BigWorld.cancelCallback(self.__reLoginCallbackID)
            self.__reLoginCallbackID = None
        return

    def __setReloginCallback(self):
        delay = self.__expBackOff.next()
        _logger.debug('__setReloginCallback. Next attempt after %d seconds', delay)
        self.__reLoginCallbackID = BigWorld.callback(delay, self.__loginUserOnCallback)

    def logout(self):
        _logger.debug('VOIPManager.Logout')
        self.__clearUser()
        self.__clearDesiredChannel()
        self.__fsm.update(self)

    def __enterChannel(self, channel, password):
        if not self.__initialized and self.__fsm.inNoneState():
            _logger.debug('VOIPManager.__enterChannel and initialize')
            self.initialize(self.__voipDomain, self.__voipServer)
        if not self.__user[0] and self.isEnabled():
            _logger.debug('VOIPManager.__enterChannel and requestCreds')
            self.__requestCredentials()
        _logger.debug('VOIPManager.EnterChannel: %s', channel)
        self.__channel = [channel, password]
        self.__fsm.update(self)

    def __joinChannel(self, channel, password):
        _logger.debug("Joining channel '%s'", channel)
        BigWorld.VOIP.joinChannel(channel, password)

    def __leaveChannel(self):
        if not self.__initialized:
            return
        _logger.debug('VOIPManager.LeaveChannel')
        self.__clearDesiredChannel()
        self.__fsm.update(self)

    def enterTestChannel(self):
        if self.__inTesting:
            return
        _logger.debug('VOIPManager.EnterTestChannel: %s', self.__testDomain)
        self.__inTesting = True
        self.__enterChannel(self.__testDomain, '')

    def leaveTestChannel(self):
        if not self.__inTesting:
            return
        _logger.debug('VOIPManager.LeaveTestChannel')
        self.__inTesting = False
        params = self.bwProto.voipProvider.getChannelParams()
        if params[0]:
            self.__enterChannel(*params)
        else:
            self.__leaveChannel()

    def setMasterVolume(self, attenuation):
        BigWorld.VOIP.setMasterVolume(attenuation)

    def setMicrophoneVolume(self, attenuation):
        BigWorld.VOIP.setMicrophoneVolume(attenuation)

    def __setVolume(self):
        self.setMasterVolume(int(round(SoundGroups.g_instance.getVolume(VOIPCommon.KEY_VOIP_MASTER) * 100)))
        self.setMicrophoneVolume(int(round(SoundGroups.g_instance.getVolume(VOIPCommon.KEY_VOIP_MIC) * 100)))

    def __muffleMasterVolume(self):
        SoundGroups.g_instance.muffleWWISEVolume()

    def __restoreMasterVolume(self):
        SoundGroups.g_instance.restoreWWISEVolume()

    def setVoiceActivation(self, enabled):
        _logger.debug('VOIPManager.SetVoiceActivation: %s', str(enabled))
        self.__activateMicByVoice = enabled
        self.setMicMute(not enabled)

    def setMicMute(self, muted=True):
        if not self.__initialized:
            return
        if muted and self.__activateMicByVoice:
            return
        self.__setMicMute(muted)

    def __setMicMute(self, muted):
        _logger.debug('VOIPManager.SetMicMute: %s', str(muted))
        if muted:
            BigWorld.VOIP.disableMicrophone()
        else:
            BigWorld.VOIP.enableMicrophone()

    def requestCaptureDevices(self):
        _logger.debug('VOIPManager.RequestCaptureDevices')
        BigWorld.VOIP.getCaptureDevices()

    def setCaptureDevice(self, deviceName):
        _logger.debug('VOIPManager.SetCaptureDevice: %s', deviceName)
        BigWorld.VOIP.setCaptureDevice(deviceName)

    def isParticipantTalking(self, dbid):
        outcome = self.__channelUsers.get(dbid, {}).get('talking', False)
        return outcome

    def __requestCredentials(self, reset=0):
        _logger.debug('VOIPManager.RequestUserCredentials')
        self.bwProto.voipProvider.requestCredentials(reset)

    def __clearDesiredChannel(self):
        self.__channel = ['', '']

    def __clearUser(self):
        self.__user = ['', '']

    def __onChatActionMute(self, dbid, muted):
        _logger.debug('VOIPManager.OnChatActionMute: dbID = %d, muted = %r', dbid, muted)
        if dbid in self.__channelUsers and self.__channelUsers[dbid]['muted'] != muted:
            self.__muteParticipantForMe(dbid, muted)

    def __muteParticipantForMe(self, dbid, mute):
        _logger.debug('VOIPManager.MuteParticipantForMe: %d, %s', dbid, str(mute))
        self.__channelUsers[dbid]['muted'] = mute
        uri = self.__channelUsers[dbid]['uri']
        cmd = {VOIPCommon.KEY_COMMAND: VOIPCommon.CMD_SET_PARTICIPANT_MUTE,
         VOIPCommon.KEY_PARTICIPANT_URI: uri,
         VOIPCommon.KEY_STATE: str(mute)}
        BigWorld.VOIP.command(cmd)
        return True

    def __isAnyoneTalking(self):
        for info in self.__channelUsers.values():
            if info['talking']:
                return True

        return False

    def __extractDBIDFromURI(self, uri):
        try:
            domain = self.__voipDomain
            login = uri.partition('sip:')[2].rpartition('@' + domain)[0]
            s = login[login.find('.') + 1:]
            return (int(s), login)
        except Exception:
            return -1

    def __sendLeaveChannelCommand(self, channel):
        _logger.debug('Leaving channel %s', channel)
        if channel:
            BigWorld.VOIP.leaveChannel(channel)
        self.__fsm.update(self)

    def __resetToInitializedState(self):
        _logger.debug('VOIPManager.__resetToInitializesState')
        if self.__currentChannel != '':
            for dbid in self.__channelUsers.iterkeys():
                self.onPlayerSpeaking(dbid, False)

            self.__channelUsers.clear()
            self.__restoreMasterVolume()
            self.__currentChannel = ''
        if self.__needLogginAfterInit:
            self.__fsm.update(self)
            self.__needLogginAfterInit = False

    def __onStateChanged(self, _, newState):
        if newState == STATE.INITIALIZED:
            self.__resetToInitializedState()
        elif newState == STATE.LOGGING_IN:
            self.__loginUser()
        elif newState == STATE.LOGGED_IN:
            self.__fsm.update(self)
        elif newState == STATE.JOINING_CHANNEL:
            muteMic = self.__channel[0] != self.__testDomain and not self.__activateMicByVoice
            self.setMicMute(muteMic)
            self.__joinChannel(self.__channel[0], self.__channel[1])
        elif newState == STATE.JOINED_CHANNEL:
            _logger.debug('Joined to channel: %s', self.__currentChannel)
            self.__fsm.update(self)
        elif newState == STATE.LEAVING_CHANNEL:
            self.__sendLeaveChannelCommand(self.getCurrentChannel())
        elif newState == STATE.LOGGING_OUT:
            self.__normalLogout = True
            BigWorld.VOIP.logout()

    def onVoipInited(self, data):
        _logger.debug('VOIPManager.onVoipInited')
        returnCode = int(data[VOIPCommon.KEY_RETURN_CODE])
        if returnCode == VOIPCommon.CODE_SUCCESS:
            self.__initialized = True
            self.__fsm.update(self)
            self.onInitialized(data)
        else:
            self.__initialized = False
            self.__fsm.reset()
            _logger.info('---------------------------')
            _logger.info("ERROR: '%d' - '%s'", int(data[VOIPCommon.KEY_STATUS_CODE]), data[VOIPCommon.KEY_STATUS_STRING])
            _logger.info('---------------------------')

    def onVoipDestroyed(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Voip is not destroyed: %r', data)

    def onCaptureDevicesArrived(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Capture devices are not arrived: %r', data)
            return
        captureDevicesCount = int(data[VOIPCommon.KEY_COUNT])
        self.__captureDevices = []
        for i in xrange(captureDevicesCount):
            self.__captureDevices.append(str(data[VOIPCommon.KEY_CAPTURE_DEVICES + '_' + str(i)]))

        self.__currentCaptureDevice = str(data[VOIPCommon.KEY_CURRENT_CAPTURE_DEVICE])
        self.onCaptureDevicesUpdated()

    def onSetCaptureDevice(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Capture device is not set: %r', data)

    def onSetLocalSpeakerVolume(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Local speaker volume is not set: %r', data)

    def onSetLocalMicVolume(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Local microphone volume is not set: %r', data)

    def onMuteLocalMic(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Local microphone volume is not muted: %r', data)

    def onLoginStateChange(self, data):
        returnCode = int(data[VOIPCommon.KEY_RETURN_CODE])
        statusCode = int(data[VOIPCommon.KEY_STATUS_CODE])
        statusString = data[VOIPCommon.KEY_STATUS_STRING]
        _logger.debug('VOIPManager.onLoginStateChange: Return code %s', returnCode)
        if returnCode == VOIPCommon.CODE_SUCCESS:
            state = int(data[VOIPCommon.KEY_STATE])
            _logger.debug('Return state %s', state)
            if state == VOIPCommon.STATE_LOGGED_IN:
                _logger.debug('VOIPManager.onLoginStateChange: LOGGED IN')
                if self.getAPI() == VOIP_SUPPORTED_API.VIVOX:
                    self.bwProto.voipProvider.logVivoxLogin()
                self.__loggedIn = True
                self.__expBackOff.reset()
                if self.__fsm.getState() == STATE.JOINED_CHANNEL:
                    self.__joinChannel(self.__channel[0], self.__channel[1])
                self.__fsm.update(self)
            elif state == VOIPCommon.STATE_LOGGED_OUT:
                _logger.debug('VOIPManager.onLoginStateChange: LOGGED OUT %d - %s', statusCode, statusString)
                if self.__normalLogout:
                    _logger.debug('VOIPManager.onLoginStateChange: Normal logout')
                    self.__normalLogout = False
                    self.__loggedIn = False
                    self.__fsm.update(self)
                elif self.__reLoginCallbackID is None:
                    _logger.debug('VOIPManager.onLoginStateChange: Network lost logout')
                    self.__setReloginCallback()
            elif state == VOIPCommon.STATE_LOGGIN_OUT:
                _logger.debug('VOIPManager.onLoginStateChange: LOGGING OUT %d - %s', statusCode, statusString)
        else:
            _logger.info('---------------------------')
            _logger.info("ERROR: '%d' - '%s'", statusCode, statusString)
            _logger.info('---------------------------')
            if (statusCode == VOIPCommon.STATUS_WRONG_CREDENTIALS or statusCode == VOIPCommon.STATUS_UNKNOWN_ACCOUNT) and self.__loginAttemptsRemained > 0:
                self.__reloginUser()
            else:
                self.onFailedToConnect()
        return

    def onSessionAdded(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Session is not added: %r', data)
            return
        self.__currentChannel = data[VOIPCommon.KEY_URI]
        self.__setVolume()
        self.__fsm.update(self)
        self.onJoinedChannel(data)

    def onSessionRemoved(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Session is not removed: %r', data)
            return
        for dbid in self.__channelUsers.iterkeys():
            self.onPlayerSpeaking(dbid, False)

        self.__channelUsers.clear()
        self.__restoreMasterVolume()
        self.__currentChannel = ''
        self.__fsm.update(self)
        self.onLeftChannel(data)

    def onNetworkTest(self, data):
        returnCode = int(data[VOIPCommon.KEY_RETURN_CODE])
        if returnCode == VOIPCommon.CODE_ERROR:
            _logger.info('---------------------------')
            _logger.info("ERROR: '%d' - '%s'", int(data[VOIPCommon.KEY_STATUS_CODE]), data[VOIPCommon.KEY_STATUS_STRING])
            _logger.info('---------------------------')
            self.onFailedToConnect()
            self.__clearDesiredChannel()
            self.__clearUser()

    def onParticipantAdded(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Participant is not added: %r', data)
            return
        uri = data[VOIPCommon.KEY_PARTICIPANT_URI]
        dbid, _ = self.__extractDBIDFromURI(uri)
        if dbid == -1:
            return
        self.__channelUsers[dbid] = {'talking': False,
         'uri': uri,
         'muted': False}
        user = self.usersStorage.getUser(dbid)
        if user and user.isMuted():
            self.__muteParticipantForMe(dbid, True)

    def onParticipantRemoved(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Participant is not removed: %r', data)
            return
        uri = data[VOIPCommon.KEY_PARTICIPANT_URI]
        dbid, _ = self.__extractDBIDFromURI(uri)
        if dbid in self.__channelUsers:
            del self.__channelUsers[dbid]
        self.onPlayerSpeaking(dbid, False)

    def onParticipantUpdated(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Participant is not updated: %r', data)
            return
        uri = data[VOIPCommon.KEY_PARTICIPANT_URI]
        dbid, _ = self.__extractDBIDFromURI(uri)
        if dbid == -1:
            return
        talking = int(data[VOIPCommon.KEY_IS_SPEAKING])
        if dbid in self.__channelUsers:
            channelUser = self.__channelUsers[dbid]
            if channelUser['talking'] != talking:
                channelUser['talking'] = talking
                if self.__isAnyoneTalking():
                    self.__muffleMasterVolume()
                else:
                    self.__restoreMasterVolume()
        self.onPlayerSpeaking(dbid, talking)

    def __me_onChannelEntered(self, uri, pwd, isRejoin):
        if not self.__inTesting:
            self.__enterChannel(uri, pwd)

    def __me_onChannelLeft(self):
        if not self.__inTesting:
            self.__leaveChannel()

    def __me_onCredentialReceived(self, name, pwd):
        _logger.debug('VOIPManager.OnUserCredentials: %s', name)
        self.__login(name, pwd)

    def __me_onUsersListReceived(self, tags):
        if USER_TAG.MUTED not in tags:
            return
        for user in self.usersStorage.getList(MutedFindCriteria()):
            dbID = user.getID()
            if dbID in self.__channelUsers:
                self.__muteParticipantForMe(dbID, True)

    def __me_onUserActionReceived(self, actionID, user):
        if actionID in (USER_ACTION_ID.MUTE_SET, USER_ACTION_ID.MUTE_UNSET):
            self.__onChatActionMute(user.getID(), user.isMuted())
