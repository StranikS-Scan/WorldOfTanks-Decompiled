# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VOIP/VOIPManager.py
from __future__ import absolute_import
import logging
import re
from builtins import range
from future.utils import viewitems
import BigWorld
import Event
import Settings
import SoundGroups
from VOIP import VOIPCommon
from VOIP.voip_constants import VOIP_SUPPORTED_API
from VOIP.VOIPFsm import VOIPFsm, VOIP_FSM_STATE as STATE
from VOIP.VOIPHandler import VOIPHandler
from constants import CLIENT_INACTIVITY_TIMEOUT, ARENA_GUI_TYPE
from gui.shared.utils import backoff
from math_common import round_py2_style_int
from messenger.m_constants import PROTO_TYPE
from messenger.m_constants import USER_ACTION_ID, USER_TAG
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.proto.shared_find_criteria import MutedFindCriteria
from messenger.storage import MessengerStorageDescriptor, UsersStorage
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from account_helpers.settings_core.settings_constants import SOUND
from gui.shared.utils import getPlayerDatabaseID
from messenger_common_chat2 import VOIP_CREDS_MODE_CHANNEL_REFRESH
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())
_logger.setLevel(logging.DEBUG)
_BACK_OFF_MIN_DELAY = 1
_BACK_OFF_MAX_DELAY = CLIENT_INACTIVITY_TIMEOUT
_BACK_OFF_MODIFIER = 1
_BACK_OFF_EXP_RANDOM_FACTOR = 0.5
_LOG_REPEAT_WINDOW = 10.0
_LOG_REPEAT_BURST = 3
_LOG_REPEAT_KEYS_MAX = 64
_LOG_DIGITS = re.compile('\\d+')

class VOIPManager(VOIPHandler):
    settingsCore = dependency.descriptor(ISettingsCore)
    usersStorage = MessengerStorageDescriptor(UsersStorage)

    def __init__(self):
        _logger.info('Create')
        super(VOIPManager, self).__init__()
        self.__initialized = False
        self.__enabled = False
        self.__enabledChannelID = None
        self.__voipServer = ''
        self.__voipDomain = ''
        self.__testDomain = ''
        self.__livekitServer = ''
        self.__desiredIsLiveKit = False
        self.__user = ['', '']
        self.__awaitingTestCredentials = False
        self.__awaitingChannelToken = False
        self.__channelTokenTimeoutID = None
        self.__channelTokenRetried = False
        self.__listenerTestToken = ''
        self.__echoTestPublisherHandled = False
        self.__livekitOpusMaxBitrate = None
        self.__livekitOpusRed = None
        self.__channel = ['', '']
        self.__currentChannel = ''
        self.__isChannelRejoin = False
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
        self.__captureDevicesNames = []
        self.__currentCaptureDevice = ''
        self.__channelUsers = {}
        self.__logRepeats = {}
        self.__eventManager = em = Event.EventManager()
        self.onCaptureDevicesUpdated = Event.Event(em)
        self.onCaptureDeviceSet = Event.Event(em)
        self.onPlayerSpeaking = Event.Event(em)
        self.onInitialized = Event.Event(em)
        self.onFailedToConnect = Event.Event(em)
        self.onJoinedChannel = Event.Event(em)
        self.onLeftChannel = Event.Event(em)
        self.onChannelAvailable = Event.Event(em)
        self.onChannelLost = Event.Event(em)
        self.__fsm.onStateChanged += self.__onStateChanged
        return

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    def destroy(self):
        self.__cancelChannelTokenTimeout()
        self.__awaitingChannelToken = False
        self.__fsm.onStateChanged -= self.__onStateChanged
        self.__cancelReloginCallback()
        self.__eventManager.clear()
        if self.__initialized:
            BigWorld.VOIP.finalise()
        _logger.info('Destroy')

    def isEnabled(self):
        return self.__enabled

    def isInitialized(self):
        return self.__initialized

    def isNotInitialized(self):
        return not self.__initialized and self.getState() == STATE.NONE

    def isInitializing(self):
        return self.getState() == STATE.INITIALIZING

    def isInTesting(self):
        return self.__inTesting

    def getVOIPDomain(self):
        return self.__voipDomain

    def getCurrentChannel(self):
        return self.__currentChannel

    def isVoiceSupported(self):
        return (self.getVOIPDomain() != '' or self.__livekitServer != '' and self.isLiveKit()) and self.isInitialized()

    def isChannelAvailable(self):
        return True if self.bwProto.voipProvider.getChannelParams()[0] else False

    def hasDesiredChannel(self):
        channelUrl = self.__channel[0]
        if channelUrl == self.__testDomain:
            return True
        currentChannelID = hash(channelUrl)
        return self.__enabledChannelID == currentChannelID

    def getUser(self):
        return self.__user[0]

    def isInDesiredChannel(self):
        if self.__channel[0] != self.__currentChannel:
            return False
        if self.__currentChannel == self.__testDomain:
            return True
        currentChannelID = hash(self.__currentChannel)
        return self.__enabledChannelID == currentChannelID

    def getCaptureDevices(self):
        return self.__captureDevices

    def getCaptureDevicesNames(self):
        return self.__captureDevicesNames

    def getCurrentCaptureDevice(self):
        return self.__currentCaptureDevice

    def getState(self):
        return self.__fsm.getState()

    def getAPI(self):
        return BigWorld.VOIP.getAPI()

    def isLoggedIn(self):
        return self.__loggedIn

    def onConnected(self):
        _logger.info('Subscribe')
        self.__loginAttemptsRemained = 2
        voipEvents = g_messengerEvents.voip
        voipEvents.onChannelAvailable += self.__me_onChannelAvailable
        voipEvents.onChannelLost += self.__me_onChannelLost
        voipEvents.onCredentialReceived += self.__me_onCredentialReceived
        voipEvents.onCredentialFailed += self.__me_onCredentialFailed
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived += self.__me_onUsersListReceived
        usersEvents.onUserActionReceived += self.__me_onUserActionReceived

    def onDisconnected(self):
        _logger.info('Unsubscribe')
        voipEvents = g_messengerEvents.voip
        voipEvents.onChannelAvailable -= self.__me_onChannelAvailable
        voipEvents.onChannelLost -= self.__me_onChannelLost
        voipEvents.onCredentialReceived -= self.__me_onCredentialReceived
        voipEvents.onCredentialFailed -= self.__me_onCredentialFailed
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived -= self.__me_onUsersListReceived
        usersEvents.onUserActionReceived -= self.__me_onUserActionReceived

    def enable(self, enabled, isInitFromPrefs=False):
        if enabled:
            self.__enable(isInitFromPrefs)
        else:
            dbIDs = set()
            for dbID, data in viewitems(self.__channelUsers):
                if data['talking']:
                    dbIDs.add(dbID)

            self.__disable()
        self.__fsm.update(self)

    def applyChannelSetting(self, isEnabled, channelID):
        self.__enabledChannelID = channelID if isEnabled else None
        self.__fsm.update(self)
        return

    def enableCurrentChannel(self, isEnabled=True, autoEnableVOIP=True):
        if not isEnabled:
            self.__channelTokenRetried = False
        needsEnableVOIP = isEnabled and not self.settingsCore.getSetting(SOUND.VOIP_ENABLE)
        if autoEnableVOIP and needsEnableVOIP:
            self.settingsCore.applySetting(SOUND.VOIP_ENABLE, True)
        params = self.bwProto.voipProvider.getChannelParams()
        channelUrl = params[0]
        if channelUrl:
            _logger.debug("VOIPManager.%s '%s'", 'EnableCurrentChannel' if isEnabled else 'DisabledCurrentChannel', channelUrl)
            channelID = hash(channelUrl)
            self.settingsCore.applySetting(SOUND.VOIP_ENABLE_CHANNEL, (isEnabled, channelID))
        else:
            _logger.error('EnableCurrentChannel: Failed to enable channel. No channel available!')

    def isCurrentChannelEnabled(self):
        params = self.bwProto.voipProvider.getChannelParams()
        channelUrl = params[0]
        if channelUrl:
            channelID = hash(channelUrl)
            return self.__enabledChannelID == channelID
        return False

    def __enable(self, isInitFromPrefs):
        _logger.info('Enable')
        self.__enabled = True
        if self.__channel[0]:
            if not self.__user[0]:
                self.__requestCredentials()
            if not isInitFromPrefs:
                self.enableCurrentChannel(True)

    def __disable(self):
        _logger.info('Disable')
        self.__enabled = False

    def initialize(self, domain, server, livekitServer):
        if self.__initialized:
            _logger.warning('VOIPManager is already initialized')
            return
        _logger.info('Initialize')
        self.__voipServer = server
        self.__voipDomain = domain
        self.__livekitServer = livekitServer
        self.__desiredIsLiveKit = bool(livekitServer)
        if livekitServer:
            self.__testDomain = 'lk_echo_test_%s' % getPlayerDatabaseID()
        else:
            self.__testDomain = 'sip:confctl-2@' + self.__voipDomain
        _logger.debug("voip_server: '%s'", self.__voipServer)
        _logger.debug("voip_domain: '%s'", self.__voipDomain)
        _logger.debug("test_domain: '%s'", self.__testDomain)
        _logger.debug("livekit_server: '%s'", self.__livekitServer)
        self.__fsm.start()
        logLevel = 0
        section = Settings.g_instance.userPrefs
        if section.has_key('development'):
            section = section['development']
            if section.has_key('vivoxLogLevel'):
                logLevel = section['vivoxLogLevel'].asInt
        if self.__livekitServer != '':
            serverSettings = getattr(BigWorld.player(), 'serverSettings', {})
            self.__livekitOpusMaxBitrate = serverSettings.get(VOIPCommon.KEY_SERVER_SETTINGS_LIVEKIT_OPUS_MAX_BITRATE)
            self.__livekitOpusRed = serverSettings.get(VOIPCommon.KEY_SERVER_SETTINGS_LIVEKIT_OPUS_RED)
            vinit = {VOIPCommon.KEY_LIVEKIT_SAMPLE_RATE: serverSettings.get(VOIPCommon.KEY_SERVER_SETTINGS_LIVEKIT_SAMPLE_RATE, ''),
             VOIPCommon.KEY_LIVEKIT_CHANNELS: serverSettings.get(VOIPCommon.KEY_SERVER_SETTINGS_LIVEKIT_CHANNELS, '')}
            initialised = BigWorld.VOIP.initialise(vinit, BigWorld.VOIPBackend.LIVEKIT)
            if initialised is False:
                _logger.error('BigWorld.VOIP.initialise refused to re-initialise the LiveKit backend (returned False); voice will be unavailable this session')
        else:
            vinit = {VOIPCommon.KEY_SERVER: 'http://%s/api2' % self.__voipServer,
             VOIPCommon.KEY_MIN_PORT: '0',
             VOIPCommon.KEY_MAX_PORT: '0',
             VOIPCommon.KEY_LOG_PREFIX: 'voip',
             VOIPCommon.KEY_LOG_SUFFIX: '.txt',
             VOIPCommon.KEY_LOG_FOLDER: '.',
             VOIPCommon.KEY_LOG_LEVEL: str(logLevel)}
            BigWorld.VOIP.initialise(vinit, BigWorld.VOIPBackend.VIVOX)
        BigWorld.VOIP.setHandler(self)

    def __login(self, name, password):
        if not self.__initialized:
            self.__needLogginAfterInit = True
        if self.isLiveKit():
            self.__user = [self.__getPlayerName(''), password]
        else:
            self.__user = [name, password]
        if not self.__needLogginAfterInit:
            self.__fsm.update(self)

    def __loginUser(self):
        _logger.info('Login Request: %s', self.__user[0])
        if self.isLiveKit():
            loginConfig = {VOIPCommon.KEY_LIVEKIT_SERVER_URL: self.__livekitServer,
             VOIPCommon.KEY_LIVEKIT_SELF_IDENTITY: str(getPlayerDatabaseID())}
            BigWorld.VOIP.login(self.__user[0], '', loginConfig)
            return
        cmd = {VOIPCommon.KEY_PARTICIPANT_PROPERTY_FREQUENCY: '100'}
        BigWorld.VOIP.login(self.__user[0], self.__user[1], cmd)

    def __loginUserOnCallback(self):
        self.__reLoginCallbackID = None
        self.__loginUser()
        return

    def __reloginUser(self):
        self.__loginAttemptsRemained -= 1
        _logger.warning('VOIPHandler.ReloginUser. Attempts remained: %d', self.__loginAttemptsRemained)
        if self.__enabled:
            self.__requestCredentials(1)

    def __cancelReloginCallback(self):
        if self.__reLoginCallbackID is not None:
            BigWorld.cancelCallback(self.__reLoginCallbackID)
            self.__reLoginCallbackID = None
        return

    def __setReloginCallback(self):
        delay = self.__expBackOff.nextDelay()
        _logger.info('__setReloginCallback. Next attempt after %d seconds', delay)
        self.__reLoginCallbackID = BigWorld.callback(delay, self.__loginUserOnCallback)

    def __dropPendingRelogin(self):
        if self.__reLoginCallbackID is not None:
            _logger.info('Pending relogin cancelled')
            self.__cancelReloginCallback()
            self.__expBackOff.reset()
        return

    def logout(self):
        _logger.info('Logout')
        self.__cancelChannelTokenTimeout()
        self.__awaitingChannelToken = False
        self.__channelTokenRetried = False
        self.__clearUser()
        self.__clearDesiredChannel()
        self.__fsm.update(self)
        if self.__desiredIsLiveKit:
            self.finalise()

    def finalise(self):
        _logger.info('Finalise')
        self.__dropPendingRelogin()
        self.__cancelChannelTokenTimeout()
        self.__awaitingChannelToken = False
        self.__channelTokenRetried = False
        if self.__initialized:
            BigWorld.VOIP.finalise()
        self.__initialized = False
        self.__fsm.reset()

    def __setAvailableChannel(self, channel, password):
        self.__channelTokenRetried = False
        if not self.__initialized and self.__fsm.inNoneState():
            self.initialize(self.__voipDomain, self.__voipServer, self.__livekitServer)
        if not self.__user[0] and self.isEnabled():
            self.__requestCredentials()
        _logger.info('ReceivedAvailableChannel: %s', channel)
        self.__channel = [channel, password]
        self.__fsm.update(self)
        self.__evaluateAutoJoinChannel(channel)

    def __evaluateAutoJoinChannel(self, newChannel):
        if newChannel == self.__testDomain:
            return
        wasEnabled, channelID = self.settingsCore.getSetting(SOUND.VOIP_ENABLE_CHANNEL)
        newChannelID = hash(newChannel)
        if channelID != newChannelID:
            if self.__isChannelRejoin:
                isEnabled = wasEnabled
            else:
                isEnabled = self.__isAutoJoinChannel()
            self.enableCurrentChannel(isEnabled=isEnabled, autoEnableVOIP=False)
        else:
            _logger.warning('__evaluateAutoJoinChannel: cant use newChannel: %r. id: %r, newId: %r', newChannel, channelID, newChannelID)

    def __joinChannel(self, channel, password):
        _logger.info("JoinChannel '%s'", channel)
        extraData = {}
        if self.isLiveKit():
            if self.__livekitOpusMaxBitrate is not None:
                extraData[VOIPCommon.KEY_LIVEKIT_OPUS_MAX_BITRATE] = self.__livekitOpusMaxBitrate
            if self.__livekitOpusRed is not None:
                extraData[VOIPCommon.KEY_LIVEKIT_OPUS_RED] = self.__livekitOpusRed
            _logger.info('Join LiveKit channel with extra data: %s', extraData)
            extraData[VOIPCommon.KEY_LIVEKIT_TOKEN] = password
            password = ''
        BigWorld.VOIP.joinChannel(channel, password, extraData)
        return

    def __leaveChannel(self):
        if not self.__initialized:
            return
        _logger.info('LeaveChannel')
        self.__clearDesiredChannel()
        self.__fsm.update(self)

    def enterTestChannel(self):
        if self.__inTesting:
            return
        if self.__awaitingChannelToken:
            _logger.info('EnterTestChannel refused: channel-token refresh in progress')
            return
        _logger.info('EnterTestChannel: %s', self.__testDomain)
        self.__inTesting = True
        self.__echoTestPublisherHandled = False
        if self.isLiveKit():
            self.__awaitingTestCredentials = True
            self.__requestCredentials()
            return
        self.__setAvailableChannel(self.__testDomain, '')

    def leaveTestChannel(self):
        if not self.__inTesting:
            return
        _logger.info('LeaveTestChannel')
        self.__inTesting = False
        self.__echoTestPublisherHandled = False
        self.__awaitingTestCredentials = False
        self.__listenerTestToken = ''
        params = self.bwProto.voipProvider.getChannelParams()
        if params[0]:
            self.__setAvailableChannel(*params)
        else:
            self.__leaveChannel()

    def setMasterVolume(self, attenuation):
        BigWorld.VOIP.setMasterVolume(attenuation)

    def setMicrophoneVolume(self, attenuation):
        BigWorld.VOIP.setMicrophoneVolume(attenuation)

    def __setVolume(self):
        self.setMasterVolume(round_py2_style_int(SoundGroups.g_instance.getVolume(VOIPCommon.KEY_VOIP_MASTER) * 100))
        self.setMicrophoneVolume(round_py2_style_int(SoundGroups.g_instance.getVolume(VOIPCommon.KEY_VOIP_MIC) * 100))

    def __muffleMasterVolume(self):
        SoundGroups.g_instance.muffleWWISEVolume()

    def __restoreMasterVolume(self):
        SoundGroups.g_instance.restoreWWISEVolume()

    def setVoiceActivation(self, enabled):
        _logger.debug('SetVoiceActivation: %s', str(enabled))
        self.__activateMicByVoice = enabled
        self.setMicMute(not enabled)

    def setMicMute(self, muted=True):
        if not self.__initialized:
            return
        if muted and self.__activateMicByVoice:
            return
        self.__setMicMute(muted)

    def __setMicMute(self, muted):
        _logger.debug('SetMicMute: %s', str(muted))
        if muted:
            if self.isLiveKit():
                BigWorld.VOIP.command({VOIPCommon.KEY_COMMAND: VOIPCommon.CMD_LIVEKIT_STOP_TALK})
            BigWorld.VOIP.disableMicrophone()
        else:
            BigWorld.VOIP.enableMicrophone()
            if self.isLiveKit():
                BigWorld.VOIP.command({VOIPCommon.KEY_COMMAND: VOIPCommon.CMD_LIVEKIT_START_TALK})

    def requestCaptureDevices(self):
        _logger.debug('RequestCaptureDevices')
        BigWorld.VOIP.getCaptureDevices()

    def setCaptureDevice(self, deviceName):
        _logger.info('SetCaptureDevice: %s', deviceName)
        BigWorld.VOIP.setCaptureDevice(deviceName)

    def isParticipantTalking(self, dbid):
        outcome = self.__channelUsers.get(dbid, {}).get('talking', False)
        return outcome

    def __requestCredentials(self, reset=0):
        _logger.info('RequestUserCredentials')
        self.bwProto.voipProvider.requestCredentials(reset)

    def __requestChannelToken(self):
        _logger.info('RequestChannelToken (LiveKit stale-token rejoin)')
        self.__awaitingChannelToken = True
        self.__armChannelTokenTimeout()
        self.bwProto.voipProvider.requestCredentials(reset=1, mode=VOIP_CREDS_MODE_CHANNEL_REFRESH)

    def __armChannelTokenTimeout(self):
        self.__cancelChannelTokenTimeout()
        self.__channelTokenTimeoutID = BigWorld.callback(5.0, self.__onChannelTokenTimeout)

    def __cancelChannelTokenTimeout(self):
        if self.__channelTokenTimeoutID is not None:
            BigWorld.cancelCallback(self.__channelTokenTimeoutID)
            self.__channelTokenTimeoutID = None
        return

    def __onChannelTokenTimeout(self):
        self.__channelTokenTimeoutID = None
        _logger.warning('Channel token refresh timed out; stale-token rejoin aborted')
        self.__awaitingChannelToken = False
        self.__channelTokenRetried = False
        return

    def __clearDesiredChannel(self):
        self.__channel = ['', '']

    def __clearUser(self):
        self.__user = ['', '']
        self.__awaitingTestCredentials = False

    def __onChatActionMute(self, dbid, muted):
        _logger.debug('OnChatActionMute: dbID = %d, muted = %r', dbid, muted)
        if dbid in self.__channelUsers and self.__channelUsers[dbid]['muted'] != muted:
            self.__muteParticipantForMe(dbid, muted)

    def __muteParticipantForMe(self, dbid, mute):
        _logger.debug('MuteParticipantForMe: %d, %s', dbid, str(mute))
        self.__channelUsers[dbid]['muted'] = mute
        uri = self.__channelUsers[dbid]['uri']
        if self.isLiveKit():
            cmd = {VOIPCommon.KEY_COMMAND: VOIPCommon.CMD_MUTE_PARTICIPANT if mute else VOIPCommon.CMD_UNMUTE_PARTICIPANT,
             VOIPCommon.KEY_PARTICIPANT_URI: uri}
        else:
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
        if self.isLiveKit():
            try:
                return (int(uri), uri)
            except (TypeError, ValueError):
                return (-1, '')

        try:
            domain = self.__voipDomain
            login = uri.partition('sip:')[2].rpartition('@' + domain)[0]
            s = login[login.find('.') + 1:]
            return (int(s), login)
        except Exception:
            return -1

    def __sendLeaveChannelCommand(self, channel):
        _logger.info('Leaving channel %s', channel)
        if channel:
            BigWorld.VOIP.leaveChannel(channel)
        self.__fsm.update(self)

    @staticmethod
    def __getPlayerName(defaultName):
        try:
            player = BigWorld.player()
            if player is None:
                return defaultName
            playerName = getattr(player, 'name', None)
            if playerName is None:
                return defaultName
            return playerName
        except (AttributeError, TypeError):
            return defaultName
        except Exception:
            return defaultName

        return

    def __resetToInitializedState(self):
        _logger.debug('resetToInitializedState')
        if self.__currentChannel != '':
            for dbid in self.__channelUsers:
                self.onPlayerSpeaking(dbid, False)

            self.__channelUsers.clear()
            self.__restoreMasterVolume()
            self.__currentChannel = ''
        if self.__needLogginAfterInit:
            self.__fsm.update(self)
            self.__needLogginAfterInit = False
            if self.__fsm.getState() != STATE.INITIALIZED:
                return
        if self.isLiveKit():
            self.__user = [self.__getPlayerName(''), '']
        self.__fsm.update(self)

    def __onStateChanged(self, oldState, newState):
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
            _logger.info('Joined to channel: %s', self.__currentChannel)
            self.__fsm.update(self)
        elif newState == STATE.LEAVING_CHANNEL:
            if self.__desiredIsLiveKit:
                self.__dropPendingRelogin()
            self.__sendLeaveChannelCommand(self.getCurrentChannel())
        elif newState == STATE.LOGGING_OUT:
            self.__normalLogout = True
            BigWorld.VOIP.logout()

    def onVoipInited(self, data):
        _logger.debug('onVoipInited')
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
            self.onFailedToConnect()

    def onVoipDestroyed(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Voip is not destroyed: %r', data)
        _logger.debug('onVoipDestroyed')

    def onCaptureDevicesArrived(self, data):
        if self.isLiveKit():
            returnCode = int(data.get(VOIPCommon.KEY_RETURN_CODE, VOIPCommon.CODE_ERROR))
            previousDevices = self.__captureDevices
            previousCurrentDevice = self.__currentCaptureDevice
            if returnCode != VOIPCommon.CODE_SUCCESS:
                _logger.warning('LiveKit capture devices refresh failed. Keeping cached devices: %r', previousDevices)
                self.__currentCaptureDevice = previousCurrentDevice
                self.onCaptureDevicesUpdated()
                return
            captureDevices = []
            captureDevicesCount = int(data.get(VOIPCommon.KEY_COUNT, 0))
            for i in range(captureDevicesCount):
                deviceKey = VOIPCommon.KEY_CAPTURE_DEVICES + '_' + str(i)
                device = data.get(deviceKey, '')
                if device:
                    captureDevices.append(str(device))

            self.__captureDevices = captureDevices
            self.__captureDevicesNames = list(captureDevices)
            self.__currentCaptureDevice = str(data.get(VOIPCommon.KEY_CURRENT_CAPTURE_DEVICE, ''))
            self.onCaptureDevicesUpdated()
            return
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Capture devices are not arrived: %r', data)
            return
        captureDevicesCount = int(data[VOIPCommon.KEY_COUNT])
        self.__captureDevices = []
        self.__captureDevicesNames = []
        for i in range(captureDevicesCount):
            self.__captureDevices.append(str(data[VOIPCommon.KEY_CAPTURE_DEVICES + '_' + str(i)]))
            self.__captureDevicesNames.append(str(data[VOIPCommon.KEY_CAPTURE_DEVICES_NAMES + '_' + str(i)]))

        self.__currentCaptureDevice = str(data[VOIPCommon.KEY_CURRENT_CAPTURE_DEVICE])
        self.onCaptureDevicesUpdated()

    def onSetCaptureDevice(self, data):
        returnCode = int(data.get(VOIPCommon.KEY_RETURN_CODE, VOIPCommon.CODE_ERROR))
        deviceName = data.get('device_name', '')
        if returnCode == VOIPCommon.CODE_SUCCESS:
            if deviceName:
                self.__currentCaptureDevice = str(deviceName)
            self.onCaptureDeviceSet(deviceName, True)
        else:
            self.onCaptureDeviceSet(deviceName, False)
            self.requestCaptureDevices()

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
        _logger.debug('onLoginStateChange: Return code %s', returnCode)
        if returnCode == VOIPCommon.CODE_SUCCESS:
            state = int(data[VOIPCommon.KEY_STATE])
            _logger.debug('Return state %s', state)
            if state == VOIPCommon.STATE_LOGGED_IN:
                _logger.debug('onLoginStateChange: LOGGED IN')
                if self.getAPI() == VOIP_SUPPORTED_API.VIVOX:
                    self.bwProto.voipProvider.logVivoxLogin()
                self.__loggedIn = True
                self.__expBackOff.reset()
                if self.__fsm.getState() == STATE.JOINED_CHANNEL:
                    self.__joinChannel(self.__channel[0], self.__channel[1])
                self.__fsm.update(self)
            elif state == VOIPCommon.STATE_LOGGED_OUT:
                _logger.debug('onLoginStateChange: LOGGED OUT %d - %s', statusCode, statusString)
                if self.__normalLogout:
                    _logger.debug('onLoginStateChange: Normal logout')
                    self.__normalLogout = False
                    self.__loggedIn = False
                    self.__fsm.update(self)
                elif self.__desiredIsLiveKit and self.__fsm.getState() != STATE.JOINED_CHANNEL:
                    _logger.info('LiveKit logout ignored in state %d: %s', self.__fsm.getState(), statusString)
                elif self.__reLoginCallbackID is None:
                    _logger.debug('onLoginStateChange: Network lost logout')
                    self.__setReloginCallback()
            elif state == VOIPCommon.STATE_LOGGIN_OUT:
                _logger.debug('onLoginStateChange: LOGGING OUT %d - %s', statusCode, statusString)
        else:
            _logger.info('---------------------------')
            _logger.info("ERROR: '%d' - '%s'", statusCode, statusString)
            _logger.info('---------------------------')
            if statusCode in (VOIPCommon.STATUS_WRONG_CREDENTIALS, VOIPCommon.STATUS_UNKNOWN_ACCOUNT) and self.__loginAttemptsRemained > 0:
                self.__reloginUser()
            else:
                self.onFailedToConnect()
        return

    def onSessionAdded(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Session is not added: %r', data)
            if self.isLiveKit():
                if not self.__channelTokenRetried and not self.__inTesting and not self.__awaitingChannelToken and self.bwProto.voipProvider.getChannelParams()[0]:
                    self.__channelTokenRetried = True
                    self.__requestChannelToken()
                self.__clearDesiredChannel()
                self.__fsm.update(self)
            return
        _logger.debug('Session added: %r', data)
        self.__cancelChannelTokenTimeout()
        self.__awaitingChannelToken = False
        self.__channelTokenRetried = False
        if self.__channelUsers:
            _logger.warning('[VOIP] onSessionAdded: participant cache already contains %d users', len(self.__channelUsers))
        currentChannel = self.__currentChannel = data[VOIPCommon.KEY_URI]
        self.__setVolume()
        self.__fsm.update(self)
        isTestChannel = currentChannel == self.__testDomain
        self.onJoinedChannel(currentChannel, isTestChannel, self.__isChannelRejoin and not isTestChannel)
        if self.isLiveKit():
            if isTestChannel:
                if not self.__echoTestPublisherHandled:
                    self.__echoTestPublisherHandled = True
                    self.setMicMute(False)
                    if self.__listenerTestToken:
                        listenerToken = self.__listenerTestToken
                        self.__listenerTestToken = ''
                        extraData = {VOIPCommon.KEY_LIVEKIT_TOKEN: listenerToken,
                         VOIPCommon.KEY_LIVEKIT_AUTO_PUBLISH: 'false'}
                        _logger.info('Echo test: joining listener on %s', self.__testDomain)
                        BigWorld.VOIP.joinChannel(self.__testDomain, '', extraData)
            elif self.__activateMicByVoice:
                self.setMicMute(False)

    def onSessionRemoved(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Session is not removed: %r', data)
            return
        _logger.debug('Session removed: %r', data)
        for dbid in self.__channelUsers:
            self.onPlayerSpeaking(dbid, False)

        self.__channelUsers.clear()
        self.__restoreMasterVolume()
        leftChannel = self.__currentChannel
        wasTest = leftChannel == self.__testDomain
        self.__currentChannel = ''
        self.__fsm.update(self)
        self.onLeftChannel(leftChannel, wasTest)

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
        isNewUser = dbid not in self.__channelUsers
        if isNewUser:
            self.__channelUsers[dbid] = {'talking': False,
             'uri': uri,
             'muted': False}
            self.onPlayerSpeaking(dbid, False)
        else:
            self.__channelUsers[dbid]['uri'] = uri
        user = self.usersStorage.getUser(dbid)
        if user and user.isMuted():
            self.__muteParticipantForMe(dbid, True)

    def onParticipantRemoved(self, data):
        if int(data[VOIPCommon.KEY_RETURN_CODE]) != VOIPCommon.CODE_SUCCESS:
            _logger.error('Participant is not removed: %r', data)
            return
        uri = data[VOIPCommon.KEY_PARTICIPANT_URI]
        dbid, _ = self.__extractDBIDFromURI(uri)
        if dbid == -1:
            return
        if dbid in self.__channelUsers:
            del self.__channelUsers[dbid]
            if not self.__isAnyoneTalking():
                self.__restoreMasterVolume()
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
                _logger.info('VOIP talking-state transition: dbid=%r talking=%r anyoneTalking=%r', dbid, talking, self.__isAnyoneTalking())
                if self.__isAnyoneTalking():
                    self.__muffleMasterVolume()
                else:
                    self.__restoreMasterVolume()
        self.onPlayerSpeaking(dbid, talking)

    def onLog(self, data):
        message = str(data[VOIPCommon.KEY_STATUS_STRING])
        severity = str(data[VOIPCommon.KEY_LOG_SEVERITY])
        if severity == VOIPCommon.SEVERITY_INFO:
            _logger.info('[LiveKitVOIP]: %s', message)
        elif severity in (VOIPCommon.SEVERITY_WARNING, VOIPCommon.SEVERITY_WARN):
            muted = self.__takeWarningSlot(message)
            if muted:
                _logger.warning('[LiveKitVOIP]: %s (+%d similar muted)', message, muted)
            elif muted is not None:
                _logger.warning('[LiveKitVOIP]: %s', message)
        elif severity == VOIPCommon.SEVERITY_ERROR:
            _logger.error('[LiveKitVOIP]: %s', message)
        else:
            _logger.info('[LiveKitVOIP] %s: %s', severity, message)
        return

    def __takeWarningSlot(self, message):
        key = _LOG_DIGITS.sub('#', message)
        now = BigWorld.time()
        start, seen, muted = self.__logRepeats.get(key, (None, 0, 0))
        if start is not None and now - start < _LOG_REPEAT_WINDOW:
            if seen < _LOG_REPEAT_BURST:
                self.__logRepeats[key] = (start, seen + 1, muted)
                return 0
            self.__logRepeats[key] = (start, seen + 1, muted + 1)
            return
        else:
            if len(self.__logRepeats) >= _LOG_REPEAT_KEYS_MAX:
                self.__logRepeats.clear()
            self.__logRepeats[key] = (now, 1, 0)
            return muted

    @staticmethod
    def __isAutoJoinChannel():
        if hasattr(BigWorld.player(), 'arena'):
            arena = BigWorld.player().arena
            return not (arena is not None and arena.guiType in ARENA_GUI_TYPE.VOIP_SUPPORTED)
        else:
            return True

    def __me_onChannelAvailable(self, uri, pwd, isRejoin):
        self.__isChannelRejoin = isRejoin
        if not self.__inTesting:
            self.__setAvailableChannel(uri, pwd)
            self.onChannelAvailable()

    def __me_onChannelLost(self):
        if not self.__inTesting:
            self.__leaveChannel()
            self.settingsCore.applySetting(SOUND.VOIP_ENABLE_CHANNEL, (False, 0))
            self.onChannelLost()

    def __me_onCredentialReceived(self, name, pwd):
        _logger.debug('OnUserCredentials: %s', name)
        if self.__awaitingChannelToken:
            self.__cancelChannelTokenTimeout()
            self.__awaitingChannelToken = False
            currentRoom = self.bwProto.voipProvider.getChannelParams()[0]
            if name and pwd and name == currentRoom:
                self.__channel = [name, pwd]
                self.applyChannelSetting(True, hash(name))
            else:
                self.__channelTokenRetried = False
            return
        if self.__awaitingTestCredentials:
            self.__awaitingTestCredentials = False
            pubToken, sep, listenerToken = pwd.partition(VOIPCommon.LIVEKIT_TOKEN_DELIMITER)
            self.__listenerTestToken = listenerToken if sep else ''
            self.__setAvailableChannel(self.__testDomain, pubToken)
            return
        self.__login(name, pwd)

    def __me_onCredentialFailed(self):
        self.__cancelChannelTokenTimeout()
        self.__awaitingChannelToken = False
        self.__awaitingTestCredentials = False
        self.__channelTokenRetried = False

    def __me_onUsersListReceived(self, tags):
        if USER_TAG.MUTED not in tags:
            return
        for user in self.usersStorage.getList(MutedFindCriteria()):
            dbID = user.getID()
            if dbID in self.__channelUsers:
                self.__muteParticipantForMe(dbID, True)

    def __me_onUserActionReceived(self, actionID, user, shadowMode):
        if actionID in (USER_ACTION_ID.MUTE_SET, USER_ACTION_ID.MUTE_UNSET):
            self.__onChatActionMute(user.getID(), user.isMuted())

    def isLiveKit(self):
        return self.getAPI() == VOIP_SUPPORTED_API.LIVEKIT
