# Embedded file name: scripts/client/VOIP/VOIPManager.py
import BigWorld
import Event
import SoundGroups
import Settings
from VOIP.voip_constants import VOIP_SUPPORTED_API
from VOIPCommon import *
from VOIPFsm import VOIPFsm, VOIP_FSM_STATE as STATE
from VOIPHandler import VOIPHandler
from VOIPLog import LOG_VOIP_INT, closeLog
from messenger.m_constants import USER_ACTION_ID, USER_TAG
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_find_criteria import MutedFindCriteria
from messenger.storage import storage_getter

class VOIPManager(VOIPHandler):

    def __init__(self):
        LOG_VOIP_INT('VOIPManager.Create')
        VOIPHandler.__init__(self)
        self.__initialized = False
        self.__enabled = False
        self.__voipDomain = ''
        self.__testDomain = ''
        self.__user = ['', '']
        self.__channel = ['', '']
        self.__currentChannel = ''
        self.__inTesting = False
        self.__loggedIn = False
        self.__needLogginAfterInit = False
        self.__loginAttemptsRemained = 2
        self.__fsm = VOIPFsm()
        self.__activateMicByVoice = False
        self.__captureDevices = []
        self.__currentCaptureDevice = ''
        self.__channelUsers = {}
        self.OnCaptureDevicesUpdated = Event.Event()
        self.onPlayerSpeaking = Event.Event()
        self.onInitialized = Event.Event()
        self.onStateToggled = Event.Event()
        self.onFailedToConnect = Event.Event()
        self.onJoinedChannel = Event.Event()
        self.onLeftChannel = Event.Event()
        self.__fsm.onStateChanged += self.__onStateChanged

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    def destroy(self):
        self.__fsm.onStateChanged -= self.__onStateChanged
        BigWorld.VOIP.finalise()
        LOG_VOIP_INT('VOIPManager.Destroy')
        closeLog()

    def isEnabled(self):
        return self.__enabled

    def isInitialized(self):
        return self.__initialized

    def isNotInitialized(self):
        return not self.__initialized and self.getState() == STATE.NONE

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
        LOG_VOIP_INT('VOIPManager.Subscribe')
        self.__loginAttemptsRemained = 2
        voipEvents = g_messengerEvents.voip
        voipEvents.onChannelEntered += self.__me_onChannelEntered
        voipEvents.onChannelLeft += self.__me_onChannelLeft
        voipEvents.onCredentialReceived += self.__me_onCredentialReceived
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived += self.__me_onUsersListReceived
        usersEvents.onUserActionReceived += self.__me_onUserActionReceived

    def onDisconnected(self):
        LOG_VOIP_INT('VOIPManager.Unsubscribe')
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
        LOG_VOIP_INT('VOIPManager.Enable')
        self.__enabled = True
        if self.__channel[0] != '' and not self.__user[0]:
            self.__requestCredentials()

    def __disable(self):
        LOG_VOIP_INT('VOIPManager.Disable')
        self.__enabled = False

    def initialize(self, domain):
        LOG_VOIP_INT('VOIPManager.Initialize')
        if not self.__initialized is False:
            raise AssertionError
            self.__voipDomain = domain
            self.__testDomain = 'sip:confctl-2@' + self.__voipDomain.partition('www.')[2]
            LOG_VOIP_INT("voip_domain: '%s'" % self.__voipDomain)
            LOG_VOIP_INT("test_domain: '%s'" % self.__testDomain)
            self.__fsm.update(self)
            logLevel = 0
            section = Settings.g_instance.userPrefs
            if section.has_key('development'):
                section = section['development']
                logLevel = section.has_key('vivoxLogLevel') and section['vivoxLogLevel'].asInt
        vinit = {KEY_SERVER: 'http://%s/api2' % self.__voipDomain,
         KEY_MIN_PORT: '0',
         KEY_MAX_PORT: '0',
         KEY_LOG_PREFIX: 'voip',
         KEY_LOG_SUFFIX: '.txt',
         KEY_LOG_FOLDER: '.',
         KEY_LOG_LEVEL: str(logLevel)}
        BigWorld.VOIP.initialise(vinit)

    def __login(self, name, password):
        if not self.__initialized:
            self.__needLogginAfterInit = True
        self.__user = [name, password]
        self.__fsm.update(self)

    def __loginUser(self, username, password):
        LOG_VOIP_INT("Login Request: '%s', '%s'" % (username, password))
        cmd = {KEY_PARTICIPANT_PROPERTY_FREQUENCY: '100'}
        BigWorld.VOIP.login(username, password, cmd)

    def __reloginUser(self):
        self.__loginAttemptsRemained -= 1
        LOG_VOIP_INT('VOIPHandler.ReloginUser. Attempts remained: %d' % self.__loginAttemptsRemained)
        if self.__enabled:
            self.__requestCredentials(1)

    def logout(self):
        LOG_VOIP_INT('VOIPManager.Logout')
        self.__clearUser()
        self.__clearDesiredChannel()
        self.__fsm.update(self)

    def __enterChannel(self, channel, password):
        if not self.__initialized and self.__fsm.inNoneState():
            self.initialize(self.__voipDomain)
        if not self.__user[0] and self.isEnabled():
            self.__requestCredentials()
        LOG_VOIP_INT("VOIPManager.EnterChannel: '%s' '%s'" % (channel, password))
        self.__channel = [channel, password]
        self.__fsm.update(self)

    def __joinChannel(self, channel, password):
        LOG_VOIP_INT("Joining channel '%s'" % channel)
        BigWorld.VOIP.joinChannel(channel, password)

    def __leaveChannel(self):
        if not self.__initialized:
            return
        LOG_VOIP_INT('VOIPManager.LeaveChannel')
        self.__clearDesiredChannel()
        self.__fsm.update(self)

    def enterTestChannel(self):
        if self.__inTesting:
            return
        LOG_VOIP_INT("VOIPManager.EnterTestChannel: '%s'" % self.__testDomain)
        self.__inTesting = True
        self.__enterChannel(self.__testDomain, '')

    def leaveTestChannel(self):
        if not self.__inTesting:
            return
        LOG_VOIP_INT('VOIPManager.LeaveTestChannel')
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
        self.setMasterVolume(int(round(SoundGroups.g_instance.getVolume(KEY_VOIP_MASTER) * 100)))
        self.setMicrophoneVolume(int(round(SoundGroups.g_instance.getVolume(KEY_VOIP_MIC) * 100)))

    def __muffleMasterVolume(self):
        SoundGroups.g_instance.muffleFMODVolume()

    def __restoreMasterVolume(self):
        SoundGroups.g_instance.restoreFMODVolume()

    def setVoiceActivation(self, enabled):
        LOG_VOIP_INT('VOIPManager.SetVoiceActivation: %s' % str(enabled))
        self.__activateMicByVoice = enabled
        self.setMicMute(not enabled)

    def setMicMute(self, muted = True):
        if not self.__initialized:
            return
        if muted and self.__activateMicByVoice:
            return
        self.__setMicMute(muted)

    def __setMicMute(self, muted):
        LOG_VOIP_INT('VOIPManager.SetMicMute: %s' % str(muted))
        if muted:
            BigWorld.VOIP.disableMicrophone()
        else:
            BigWorld.VOIP.enableMicrophone()

    def requestCaptureDevices(self):
        LOG_VOIP_INT('VOIPManager.RequestCaptureDevices')
        BigWorld.VOIP.getCaptureDevices()

    def setCaptureDevice(self, deviceName):
        LOG_VOIP_INT("VOIPManager.SetCaptureDevice: '%s'" % deviceName)
        BigWorld.VOIP.setCaptureDevice(deviceName)

    def isParticipantTalking(self, dbid):
        outcome = self.__channelUsers.get(dbid, {}).get('talking', False)
        return outcome

    def __requestCredentials(self, reset = 0):
        LOG_VOIP_INT('VOIPManager.RequestUserCredentials')
        self.bwProto.voipProvider.requestCredentials(reset)

    def __clearDesiredChannel(self):
        self.__channel = ['', '']

    def __clearUser(self):
        self.__user = ['', '']

    def __onChatActionMute(self, dbid, muted):
        LOG_VOIP_INT('VOIPManager.OnChatActionMute', dbid, muted)
        if dbid in self.__channelUsers and self.__channelUsers[dbid]['muted'] != muted:
            self.__muteParticipantForMe(dbid, muted)

    def __muteParticipantForMe(self, dbid, mute):
        LOG_VOIP_INT('VOIPManager.MuteParticipantForMe: %d, %s' % (dbid, str(mute)))
        raise dbid in self.__channelUsers or AssertionError
        self.__channelUsers[dbid]['muted'] = mute
        uri = self.__channelUsers[dbid]['uri']
        cmd = {KEY_COMMAND: CMD_SET_PARTICIPANT_MUTE,
         KEY_PARTICIPANT_URI: uri,
         KEY_STATE: str(mute)}
        BigWorld.VOIP.command(cmd)
        return True

    def __isAnyoneTalking(self):
        for info in self.__channelUsers.values():
            if info['talking']:
                return True

        return False

    def __extractDBIDFromURI(self, uri):
        try:
            domain = self.__voipDomain.partition('www.')[2]
            login = uri.partition('sip:')[2].rpartition('@' + domain)[0]
            s = login[login.find('.') + 1:]
            return (int(s), login)
        except:
            return -1

    def __sendLeaveChannelCommand(self, channel):
        LOG_VOIP_INT("Leaving channel '%s'" % channel)
        if channel:
            BigWorld.VOIP.leaveChannel(channel)
        self.__fsm.update(self)

    def __resetToInitializedState(self):
        if self.__currentChannel != '':
            for dbid in self.__channelUsers.keys():
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
            self.__loginUser(self.__user[0], self.__user[1])
        elif newState == STATE.LOGGED_IN:
            self.__fsm.update(self)
        elif newState == STATE.JOINING_CHANNEL:
            muteMic = self.__channel[0] != self.__testDomain and not self.__activateMicByVoice
            self.setMicMute(muteMic)
            self.__joinChannel(self.__channel[0], self.__channel[1])
        elif newState == STATE.JOINED_CHANNEL:
            LOG_VOIP_INT("Joined to channel: '%s'" % self.__currentChannel)
            self.__fsm.update(self)
        elif newState == STATE.LEAVING_CHANNEL:
            self.__sendLeaveChannelCommand(self.getCurrentChannel())
        elif newState == STATE.LOGGING_OUT:
            BigWorld.VOIP.logout()

    def onVoipInited(self, data):
        returnCode = int(data[KEY_RETURN_CODE])
        if returnCode == CODE_SUCCESS:
            self.__initialized = True
            self.__fsm.update(self)
            self.onInitialized(data)
        else:
            self.__initialized = False
            self.__fsm.reset()
            LOG_VOIP_INT('---------------------------')
            LOG_VOIP_INT("ERROR: '%d' - '%s'" % (int(data[KEY_STATUS_CODE]), data[KEY_STATUS_STRING]))
            LOG_VOIP_INT('---------------------------')

    def onVoipDestroyed(self, data):
        raise int(data[KEY_RETURN_CODE]) == CODE_SUCCESS or AssertionError

    def onCaptureDevicesArrived(self, data):
        raise int(data[KEY_RETURN_CODE]) == CODE_SUCCESS or AssertionError
        captureDevicesCount = int(data[KEY_COUNT])
        self.__captureDevices = []
        for i in xrange(captureDevicesCount):
            self.__captureDevices.append(str(data[KEY_CAPTURE_DEVICES + '_' + str(i)]))

        self.__currentCaptureDevice = str(data[KEY_CURRENT_CAPTURE_DEVICE])
        self.OnCaptureDevicesUpdated()

    def onSetCaptureDevice(self, data):
        raise int(data[KEY_RETURN_CODE]) == CODE_SUCCESS or AssertionError

    def onSetLocalSpeakerVolume(self, data):
        raise int(data[KEY_RETURN_CODE]) == CODE_SUCCESS or AssertionError

    def onSetLocalMicVolume(self, data):
        raise int(data[KEY_RETURN_CODE]) == CODE_SUCCESS or AssertionError

    def onMuteLocalMic(self, data):
        raise int(data[KEY_RETURN_CODE]) == CODE_SUCCESS or AssertionError

    def onLoginStateChange(self, data):
        returnCode = int(data[KEY_RETURN_CODE])
        if returnCode == CODE_SUCCESS:
            state = int(data[KEY_STATE])
            if state == STATE_LOGGED_IN:
                if self.getAPI() == VOIP_SUPPORTED_API.VIVOX:
                    self.bwProto.voipProvider.logVivoxLogin()
                self.__loggedIn = True
                self.__fsm.update(self)
            elif state == STATE_LOGGED_OUT:
                self.__loggedIn = False
                self.__fsm.update(self)
        else:
            LOG_VOIP_INT('---------------------------')
            LOG_VOIP_INT("ERROR: '%d' - '%s'" % (int(data[KEY_STATUS_CODE]), data[KEY_STATUS_STRING]))
            LOG_VOIP_INT('---------------------------')
            code = int(data[KEY_STATUS_CODE])
            if (code == STATUS_WRONG_CREDENTIALS or code == STATUS_UNKNOWN_ACCOUNT) and self.__loginAttemptsRemained > 0:
                self.__reloginUser()
            else:
                self.onFailedToConnect()

    def onSessionAdded(self, data):
        raise int(data[KEY_RETURN_CODE]) == CODE_SUCCESS or AssertionError
        raise not self.__channelUsers or AssertionError
        self.__currentChannel = data[KEY_URI]
        self.__setVolume()
        self.__fsm.update(self)
        self.onJoinedChannel(data)

    def onSessionRemoved(self, data):
        raise int(data[KEY_RETURN_CODE]) == CODE_SUCCESS or AssertionError
        for dbid in self.__channelUsers.keys():
            self.onPlayerSpeaking(dbid, False)

        self.__channelUsers.clear()
        self.__restoreMasterVolume()
        self.__currentChannel = ''
        self.__fsm.update(self)
        self.onLeftChannel(data)

    def onNetworkTest(self, data):
        returnCode = int(data[KEY_RETURN_CODE])
        if returnCode == CODE_ERROR:
            LOG_VOIP_INT('---------------------------')
            LOG_VOIP_INT("ERROR: '%d' - '%s'" % (int(data[KEY_STATUS_CODE]), data[KEY_STATUS_STRING]))
            LOG_VOIP_INT('---------------------------')
            self.onFailedToConnect()
            self.__clearDesiredChannel()
            self.__clearUser()

    def onParticipantAdded(self, data):
        if not int(data[KEY_RETURN_CODE]) == CODE_SUCCESS:
            raise AssertionError
            uri = data[KEY_PARTICIPANT_URI]
            dbid, _ = self.__extractDBIDFromURI(uri)
            if dbid == -1:
                return
            self.__channelUsers[dbid] = {'talking': False,
             'uri': uri,
             'muted': False}
            user = self.usersStorage.getUser(dbid)
            user and user.isMuted() and self.__muteParticipantForMe(dbid, True)

    def onParticipantRemoved(self, data):
        if not int(data[KEY_RETURN_CODE]) == CODE_SUCCESS:
            raise AssertionError
            uri = data[KEY_PARTICIPANT_URI]
            dbid, _ = self.__extractDBIDFromURI(uri)
            del dbid in self.__channelUsers and self.__channelUsers[dbid]
        self.onPlayerSpeaking(dbid, False)

    def onParticipantUpdated(self, data):
        if not int(data[KEY_RETURN_CODE]) == CODE_SUCCESS:
            raise AssertionError
            uri = data[KEY_PARTICIPANT_URI]
            dbid, participantLogin = self.__extractDBIDFromURI(uri)
            if dbid == -1:
                return
            talking = int(data[KEY_IS_SPEAKING])
            channelUser = self.__channelUsers[dbid]
            if dbid in self.__channelUsers:
                channelUser['talking'] = channelUser['talking'] != talking and talking
                self.__muffleMasterVolume() if self.__isAnyoneTalking() else self.__restoreMasterVolume()
        self.onPlayerSpeaking(dbid, talking)

    def __me_onChannelEntered(self, uri, pwd):
        if not self.__inTesting:
            self.__enterChannel(uri, pwd)

    def __me_onChannelLeft(self):
        if not self.__inTesting:
            self.__leaveChannel()

    def __me_onCredentialReceived(self, name, pwd):
        LOG_VOIP_INT("VOIPManager.OnUserCredentials: '%s' '%s'" % (name, pwd))
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
