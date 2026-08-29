# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VOIP/VOIPManagerWebRTC.py
import logging
import BigWorld
import Event
import SoundGroups
import VOIPCommon
from VOIPFsm import VOIP_FSM_STATE as STATE
from account_helpers import getAccountDatabaseID
from avatar_helpers import getAvatarDatabaseID
from messenger.proto import proto_getter
from VOIPHandler import VOIPHandler
from constants import ARENA_GUI_TYPE
from messenger.m_constants import PROTO_TYPE
from messenger.m_constants import USER_ACTION_ID, USER_TAG
from messenger.proto.shared_find_criteria import MutedFindCriteria
from messenger.storage import storage_getter
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.settings_constants import SOUND
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())
_logger.setLevel(logging.INFO)

class VOIPManagerWebRTC(VOIPHandler):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        _logger.info('Create')
        super(VOIPManagerWebRTC, self).__init__()
        self.__initialized = False
        self.__enabled = False
        self.__enabledChannelID = None
        self.__channel = None
        self.__channelToken = None
        self.__testChannel = None
        self.__currentChannel = ''
        self.__isChannelRejoin = False
        self.__inTesting = False
        self.__waitingTestRequest = False
        self.state = STATE.NONE
        self.__captureDevices = []
        self.__currentCaptureDevice = ''
        self.__channelUsers = {}
        self.__dbid = 0
        self.__eventManager = em = Event.EventManager()
        self.onCaptureDevicesUpdated = Event.Event(em)
        self.onPlayerSpeaking = Event.Event(em)
        self.onInitialized = Event.Event(em)
        self.onFailedToConnect = Event.Event(em)
        self.onJoinedChannel = Event.Event(em)
        self.onLeftChannel = Event.Event(em)
        self.onChannelAvailable = Event.Event(em)
        self.onChannelLost = Event.Event(em)
        return

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    def destroy(self):
        self.__eventManager.clear()
        BigWorld.VOIP.finalise()
        self.__initialized = False
        self.state = STATE.NONE
        _logger.info('Destroy')

    def isEnabled(self):
        return self.__enabled

    def isInitialized(self):
        return self.__initialized

    def isInTesting(self):
        return self.__inTesting

    def getCurrentChannel(self):
        return self.__currentChannel

    def isVoiceSupported(self):
        return self.isInitialized()

    def isChannelAvailable(self):
        return True if self.bwProto.voipProvider.getChannelParams()[0] else False

    def getCaptureDevices(self):
        return self.__captureDevices

    def getCurrentCaptureDevice(self):
        return self.__currentCaptureDevice

    def getAPI(self):
        return BigWorld.VOIP.getAPI()

    def enable(self, enabled, isInitFromPrefs=False):
        if enabled:
            self.__enable(isInitFromPrefs)
        else:
            dbIDs = set()
            for dbID, data in self.__channelUsers.iteritems():
                if data['talking']:
                    dbIDs.add(dbID)

            self.__disable()

    def applyChannelSetting(self, isEnabled, channelID):
        self.__enabledChannelID = channelID if isEnabled else None
        if isEnabled and self.__channel:
            self.__joinChannel(self.__channelToken)
        else:
            self.__leaveChannel()
        return

    def enableCurrentChannel(self, isEnabled=True, autoEnableVOIP=True):
        needsEnableVOIP = isEnabled and not self.settingsCore.getSetting(SOUND.VOIP_ENABLE)
        if autoEnableVOIP and needsEnableVOIP:
            self.settingsCore.applySetting(SOUND.VOIP_ENABLE, True)
        channelID = self.__channel
        if channelID:
            _logger.debug("%s '%s'", 'EnableCurrentChannel' if isEnabled else 'DisabledCurrentChannel', channelID)
            channelID = hash(channelID)
            self.settingsCore.applySetting(SOUND.VOIP_ENABLE_CHANNEL, (isEnabled, channelID))
        else:
            _logger.error('EnableCurrentChannel: Failed to enable channel. No channel available!')

    def isCurrentChannelEnabled(self):
        channelID = self.__channel
        if channelID:
            channelIDHash = hash(channelID)
            return self.__enabledChannelID == channelIDHash
        return False

    def __enable(self, isInitFromPrefs):
        _logger.info('Enable')
        self.__enabled = True
        if self.__channel:
            if not isInitFromPrefs:
                self.enableCurrentChannel(True)
        BigWorld.VOIP.enableVOIP()

    def __disable(self):
        _logger.info('Disable')
        self.__enabled = False
        BigWorld.VOIP.disableVOIP()

    def getState(self):
        return self.state

    def initialize(self, _):
        if self.__initialized:
            _logger.warning('VOIPManagerWebRTC is already initialized')
            return
        _logger.info('Initialize')
        self.state = STATE.INITIALIZING
        BigWorld.VOIP.initialise({})

    def __setAvailableChannel(self, channelID, token, isEchoChannel):
        if self.__currentChannel == channelID:
            _logger.info('ReceivedChannel ignoring request to join same channel were already in.')
            return
        if isEchoChannel and not self.__waitingTestRequest:
            _logger.info('ReceivedChannel ignoring echo channel request')
            return
        if not self.__initialized:
            self.initialize({})
        _logger.info('ReceivedChannel: %s isEchoChannel: %s', channelID, isEchoChannel)
        if self.state in (STATE.JOINED_CHANNEL, STATE.LEAVING_CHANNEL) and not self.__inTesting:
            self.__leaveChannel()
        if isEchoChannel:
            self.__inTesting = True
            self.__testChannel = channelID
            self.__joinChannel(token)
            return
        self.__channel = channelID
        self.__channelToken = token
        self.__evaluateAutoJoinChannel(channelID)

    def __evaluateAutoJoinChannel(self, newChannel):
        wasEnabled, hashedID = self.settingsCore.getSetting(SOUND.VOIP_ENABLE_CHANNEL)
        if hash(newChannel) == hashedID:
            isEnabled = wasEnabled
        else:
            isEnabled = self.__isAutoJoinChannel()
        self.enableCurrentChannel(isEnabled=isEnabled, autoEnableVOIP=False)

    def __joinChannel(self, token):
        _logger.debug("JoinChannel '%s'", token)
        if self.state == STATE.JOINED_CHANNEL:
            _logger.debug('JoinChannel already in channel!')
            return
        if self.state == STATE.INITIALIZED:
            self.state = STATE.JOINING_CHANNEL
            BigWorld.VOIP.joinChannel(token, '')
            self.__currentChannel = self.__channel if not self.__inTesting else self.__testChannel
            self.onJoinedChannel(self.__currentChannel, self.__inTesting, self.__isChannelRejoin and not self.__inTesting)

    def __leaveChannel(self):
        if not self.__initialized or self.state not in (STATE.JOINED_CHANNEL, STATE.JOINING_CHANNEL):
            return
        else:
            _logger.debug('LeaveChannel')
            self.state = STATE.LEAVING_CHANNEL
            BigWorld.VOIP.leaveChannel('')
            self.state = STATE.INITIALIZED
            self.onLeftChannel(self.__currentChannel, self.__inTesting)
            self.__currentChannel = ''
            if self.__inTesting:
                self.__inTesting = False
                self.__testChannel = None
            return

    def enterTestChannel(self):
        if self.__inTesting or self.__waitingTestRequest:
            return
        self.__waitingTestRequest = True
        _logger.info('RequestTestChannel')
        self.bwProto.voipProvider.requestEchoChannel()

    def leaveTestChannel(self):
        if not self.__inTesting and not self.__waitingTestRequest:
            return
        _logger.info('LeaveTestChannel')
        if self.__testChannel:
            self.__leaveChannel()
            if self.isCurrentChannelEnabled():
                self.__joinChannel(self.__channelToken)
        self.__waitingTestRequest = False

    def setMasterVolume(self, attenuation):
        BigWorld.VOIP.setMasterVolume(attenuation)

    def setMicrophoneVolume(self, attenuation):
        BigWorld.VOIP.setMicrophoneVolume(attenuation)

    def __setVolume(self):
        self.setMasterVolume(int(round(SoundGroups.g_instance.getVolume(VOIPCommon.KEY_VOIP_MASTER_WEBRTC) * 100)))
        self.setMicrophoneVolume(int(round(SoundGroups.g_instance.getVolume(VOIPCommon.KEY_VOIP_MIC_WEBRTC) * 100)))

    def __muffleMasterVolume(self):
        SoundGroups.g_instance.muffleWWISEVolume()

    def __restoreMasterVolume(self):
        SoundGroups.g_instance.restoreWWISEVolume()

    def setMicMute(self, muted=True):
        if not self.__initialized:
            return
        self.__setMicMute(muted)

    def __setMicMute(self, muted):
        _logger.debug('SetMicMute: %s', str(muted))
        if muted:
            BigWorld.VOIP.disableMicrophone()
        else:
            BigWorld.VOIP.enableMicrophone()

    def requestCaptureDevices(self):
        _logger.debug('RequestCaptureDevices')
        BigWorld.VOIP.getCaptureDevices()

    def logout(self):
        self.settingsCore.applySetting(SOUND.VOIP_ENABLE_CHANNEL, (False, 0))
        self.__dbid = 0

    def setCaptureDevice(self, deviceName):
        _logger.info('SetCaptureDevice: %s', deviceName)
        BigWorld.VOIP.setCaptureDevice(deviceName)

    def isParticipantTalking(self, dbid):
        outcome = self.__channelUsers.get(dbid, {}).get('talking', False)
        return outcome

    def __onChatActionMute(self, dbid, muted):
        _logger.debug('OnChatActionMute: dbID = %d, muted = %r', dbid, muted)
        if dbid in self.__channelUsers and self.__channelUsers[dbid]['muted'] != muted:
            self.__muteParticipantForMe(dbid, muted)

    def __muteParticipantForMe(self, dbid, mute):
        _logger.debug('MuteParticipantForMe: %s, %s', dbid, str(mute))
        self.__channelUsers[dbid]['muted'] = mute
        cmd = {VOIPCommon.KEY_COMMAND: VOIPCommon.CMD_SET_PARTICIPANT_MUTE,
         VOIPCommon.KEY_PARTICIPANT_URI: str(dbid),
         VOIPCommon.KEY_STATE: str(mute)}
        BigWorld.VOIP.command(cmd)
        return True

    def __isAnyoneTalking(self):
        for info in self.__channelUsers.values():
            if info['talking']:
                return True

        return False

    def __sendLeaveChannelCommand(self, channel):
        _logger.info('Leaving channel %s', channel)
        if channel:
            BigWorld.VOIP.leaveChannel(channel)

    def __resetToInitializedState(self):
        _logger.debug('resetToInitializesState')
        if self.__currentChannel != '':
            for dbid in self.__channelUsers.iterkeys():
                self.onPlayerSpeaking(dbid, False)

            self.__channelUsers.clear()
            self.__restoreMasterVolume()
            self.__currentChannel = ''

    def onVoipInited(self, data):
        _logger.info('onVoipInited')
        returnCode = int(data[VOIPCommon.KEY_RETURN_CODE])
        if returnCode == VOIPCommon.CODE_SUCCESS:
            self.__initialized = True
            self.state = STATE.INITIALIZED
            self.onInitialized(data)
        else:
            self.__initialized = False
            _logger.info('---------------------------')
            _logger.info("ERROR: '%d' - '%s'", int(data[VOIPCommon.KEY_STATUS_CODE]), data[VOIPCommon.KEY_STATUS_STRING])
            _logger.info('---------------------------')

    def onVoipDestroyed(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Voip is not destroyed: %r', data)
        self.__initialized = False
        _logger.info('onVoipDestroyed')

    def onSessionAdded(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Session is not added: %r', data)
            return
        _logger.debug('Session added: %r', data)
        self.state = STATE.JOINED_CHANNEL
        self.__setVolume()

    def onSessionRemoved(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Session is not removed: %r', data)
            return
        _logger.debug('Session removed: %r', data)
        for dbid in self.__channelUsers.iterkeys():
            self.onPlayerSpeaking(dbid, False)

        self.__channelUsers.clear()
        self.__restoreMasterVolume()

    def onCaptureDevicesArrived(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Capture devices list is not ready yet: %r', data)
            self.__captureDevices = []
            self.onCaptureDevicesUpdated()
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

    def onParticipantAdded(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Participant is not added: %r', data)
            return
        dbid = int(data[VOIPCommon.KEY_PARTICIPANT_URI])
        self.__channelUsers[dbid] = {'talking': False,
         'dbid': dbid,
         'muted': False}
        user = self.usersStorage.getUser(dbid)
        muted = False
        if user:
            muted = user.isMuted
        self.__muteParticipantForMe(dbid, muted)

    def onParticipantRemoved(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Participant is not removed: %r', data)
            return
        dbid = data[VOIPCommon.KEY_PARTICIPANT_URI]
        if dbid in self.__channelUsers:
            del self.__channelUsers[dbid]
        self.onPlayerSpeaking(dbid, False)

    def onParticipantUpdated(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Participant is not updated: %r', data)
            return
        dbid = data[VOIPCommon.KEY_PARTICIPANT_URI]
        if dbid == '0':
            dbid = self.__getOwnPlayerDBID()
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

    def __getOwnPlayerDBID(self):
        if self.__dbid != 0:
            return self.__dbid
        self.__dbid = getAccountDatabaseID() or getAvatarDatabaseID()
        return self.__dbid

    @staticmethod
    def __isAutoJoinChannel():
        if hasattr(BigWorld.player(), 'arena'):
            arena = BigWorld.player().arena
            return not (arena is not None and arena.guiType in ARENA_GUI_TYPE.VOIP_SUPPORTED)
        else:
            return True

    def channelAvailable(self, channelID, token, isRejoin, isEchoChannel):
        self.__isChannelRejoin = isRejoin
        self.__setAvailableChannel(channelID, token, isEchoChannel)
        self.onChannelAvailable()

    def channelLost(self):
        _logger.info('Leave VOIP received: %s', self.__channel)
        self.__channel = None
        self.__channelToken = None
        if not self.__inTesting:
            self.__leaveChannel()
            self.settingsCore.applySetting(SOUND.VOIP_ENABLE_CHANNEL, (False, 0))
            self.onChannelLost()
        return

    def usersListReceived(self, tags):
        if USER_TAG.MUTED not in tags:
            return
        for user in self.usersStorage.getList(MutedFindCriteria()):
            dbID = user.getID()
            if dbID in self.__channelUsers:
                self.__muteParticipantForMe(dbID, True)

    def userActionReceived(self, actionID, user, shadowMode):
        if actionID in (USER_ACTION_ID.MUTE_SET, USER_ACTION_ID.MUTE_UNSET):
            self.__onChatActionMute(user.getID(), user.isMuted())

    def isLoggedIn(self):
        pass
