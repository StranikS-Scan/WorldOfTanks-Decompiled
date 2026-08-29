# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VOIP/VOIPSingleton.py
import logging
import Event
from VOIPHandler import VOIPHandler
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())
_logger.setLevel(logging.INFO)

class VOIPSingleton(VOIPHandler):

    def __init__(self):
        super(VOIPSingleton, self).__init__()
        from VOIPManagerWebRTC import VOIPManagerWebRTC
        self.__impl = VOIPManagerWebRTC()
        self.__settings = {}
        self.__profile = 'webrtc'
        self.__eventManager = em = Event.EventManager()
        self.onCaptureDevicesUpdated = Event.Event(em)
        self.onPlayerSpeaking = Event.Event(em)
        self.onInitialized = Event.Event(em)
        self.onFailedToConnect = Event.Event(em)
        self.onJoinedChannel = Event.Event(em)
        self.onLeftChannel = Event.Event(em)
        self.onChannelAvailable = Event.Event(em)
        self.onChannelLost = Event.Event(em)

    @property
    def profile(self):
        return self.__profile

    def destroy(self):
        _logger.debug('destroy')
        self.onDisconnected()
        self.__unsubscribe()
        self.__impl.destroy()

    def __subscribe(self):
        _logger.debug('subscribe')
        self.__impl.onCaptureDevicesUpdated += self.onCaptureDevicesUpdated
        self.__impl.onPlayerSpeaking += self.onPlayerSpeaking
        self.__impl.onInitialized += self.onInitialized
        self.__impl.onFailedToConnect += self.onFailedToConnect
        self.__impl.onJoinedChannel += self.onJoinedChannel
        self.__impl.onLeftChannel += self.onLeftChannel
        self.__impl.onChannelAvailable += self.onChannelAvailable
        self.__impl.onChannelLost += self.onChannelLost

    def __unsubscribe(self):
        _logger.debug('unsubscribe')
        self.__impl.onCaptureDevicesUpdated -= self.onCaptureDevicesUpdated
        self.__impl.onPlayerSpeaking -= self.onPlayerSpeaking
        self.__impl.onInitialized -= self.onInitialized
        self.__impl.onFailedToConnect -= self.onFailedToConnect
        self.__impl.onJoinedChannel -= self.onJoinedChannel
        self.__impl.onLeftChannel -= self.onLeftChannel
        self.__impl.onChannelAvailable -= self.onChannelAvailable
        self.__impl.onChannelLost -= self.onChannelLost

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    def isEnabled(self):
        return self.__impl.isEnabled()

    def isInitialized(self):
        return self.__impl.isInitialized()

    def isInTesting(self):
        return self.__impl.isInTesting()

    def getVOIPDomain(self):
        return self.__impl.getVOIPDomain()

    def getCurrentChannel(self):
        return self.__impl.getCurrentChannel()

    def isVoiceSupported(self):
        return self.__impl.isVoiceSupported()

    def isChannelAvailable(self):
        return self.__impl.isChannelAvailable()

    def getCaptureDevices(self):
        return self.__impl.getCaptureDevices()

    def getCurrentCaptureDevice(self):
        return self.__impl.getCurrentCaptureDevice()

    def getState(self):
        return self.__impl.getState()

    def getAPI(self):
        return self.__impl.getAPI()

    def isLoggedIn(self):
        return self.__impl.isLoggedIn()

    def onConnected(self):
        voipEvents = g_messengerEvents.voip
        voipEvents.onChannelAvailable += self.channelAvailable
        voipEvents.onChannelLost += self.channelLost
        voipEvents.onCredentialReceived += self.credentialReceived
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived += self.usersListReceived
        usersEvents.onUserActionReceived += self.userActionReceived

    def onDisconnected(self):
        voipEvents = g_messengerEvents.voip
        voipEvents.onChannelAvailable -= self.channelAvailable
        voipEvents.onChannelLost -= self.channelLost
        voipEvents.onCredentialReceived -= self.credentialReceived
        usersEvents = g_messengerEvents.users
        usersEvents.onUsersListReceived -= self.usersListReceived
        usersEvents.onUserActionReceived -= self.userActionReceived

    def channelAvailable(self, channel, token, isRejoin, isEchoChannel):
        self.__impl.channelAvailable(channel, token, isRejoin, isEchoChannel)

    def channelLost(self):
        self.__impl.channelLost()

    def credentialReceived(self, name, pwd):
        self.__impl.credentialReceived(name, pwd)

    def usersListReceived(self, tags):
        self.__impl.usersListReceived(tags)

    def userActionReceived(self, actionID, user, shadowMode):
        self.__impl.userActionReceived(actionID, user, shadowMode)

    def enable(self, enabled, isInitFromPrefs=False):
        self.__impl.enable(enabled, isInitFromPrefs)

    def applyChannelSetting(self, isEnabled, channelID):
        self.__impl.applyChannelSetting(isEnabled, channelID)

    def enableCurrentChannel(self, isEnabled=True, autoEnableVOIP=True):
        self.__impl.enableCurrentChannel(isEnabled, autoEnableVOIP)

    def isCurrentChannelEnabled(self):
        return self.__impl.isCurrentChannelEnabled()

    def initialize(self, voipSettings):
        _logger.debug('initialize')
        if 'profile' not in voipSettings:
            return
        profile = voipSettings['profile']
        if self.__profile != profile:
            self.__profile = profile
            self.__impl.destroy()
            if voipSettings['profile'] == 'vivox':
                from VOIPManager import VOIPManager
                self.__impl = VOIPManager()
            elif voipSettings['profile'] == 'webrtc':
                from VOIPManagerWebRTC import VOIPManagerWebRTC
                self.__impl = VOIPManagerWebRTC()
        self.onConnected()
        self.__subscribe()
        self.__impl.initialize(voipSettings)

    def logout(self):
        self.__impl.logout()

    def enterTestChannel(self):
        self.__impl.enterTestChannel()

    def leaveTestChannel(self):
        self.__impl.leaveTestChannel()

    def setMasterVolume(self, attenuation):
        self.__impl.setMasterVolume(attenuation)

    def setMicrophoneVolume(self, attenuation):
        self.__impl.setMicrophoneVolume(attenuation)

    def setVoiceActivation(self, enabled):
        self.__impl.setVoiceActivation(enabled)

    def setMicMute(self, muted=True):
        self.__impl.setMicMute(muted)

    def requestCaptureDevices(self):
        self.__impl.requestCaptureDevices()

    def setCaptureDevice(self, deviceName):
        self.__impl.setCaptureDevice(deviceName)

    def isParticipantTalking(self, dbid):
        return self.__impl.isParticipantTalking(dbid)

    def onVoipInited(self, data):
        self.__impl.onVoipInited(data)

    def onVoipDestroyed(self, data):
        self.__impl.onVoipDestroyed(data)

    def onCaptureDevicesArrived(self, data):
        self.__impl.onCaptureDevicesArrived(data)

    def onSetCaptureDevice(self, data):
        self.__impl.onSetCaptureDevice(data)

    def onSetLocalSpeakerVolume(self, data):
        self.__impl.onSetLocalSpeakerVolume(data)

    def onSetLocalMicVolume(self, data):
        self.__impl.onSetLocalMicVolume(data)

    def onMuteLocalMic(self, data):
        self.__impl.onMuteLocalMic(data)

    def onLoginStateChange(self, data):
        self.__impl.onLoginStateChange(data)

    def onSessionAdded(self, data):
        self.__impl.onSessionAdded(data)

    def onSessionRemoved(self, data):
        self.__impl.onSessionRemoved(data)

    def onNetworkTest(self, data):
        self.__impl.onNetworkTest(data)

    def onParticipantAdded(self, data):
        self.__impl.onParticipantAdded(data)

    def onParticipantRemoved(self, data):
        self.__impl.onParticipantRemoved(data)

    def onParticipantUpdated(self, data):
        self.__impl.onParticipantUpdated(data)
