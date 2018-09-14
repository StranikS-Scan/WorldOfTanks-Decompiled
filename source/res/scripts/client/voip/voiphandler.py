# Embedded file name: scripts/client/VOIP/VOIPHandler.py
from VOIPLog import LOG_VOIP_INT
from wotdecorators import noexcept
MESSAGE_IDS = {}
MSG_VOIP_INITED = 0
MESSAGE_IDS[MSG_VOIP_INITED] = 'MSG_VOIP_INITED'
MSG_VOIP_DESTROYED = 1
MESSAGE_IDS[MSG_VOIP_DESTROYED] = 'MSG_VOIP_DESTROYED'
MSG_CAPTURE_DEVICES = 10
MESSAGE_IDS[MSG_CAPTURE_DEVICES] = 'MSG_CAPTURE_DEVICES'
MSG_SET_CAPTURE_DEVICE = 11
MESSAGE_IDS[MSG_SET_CAPTURE_DEVICE] = 'MSG_SET_CAPTURE_DEVICE'
MSG_SET_LOCAL_SPEAKER_VOLUME = 20
MESSAGE_IDS[MSG_SET_LOCAL_SPEAKER_VOLUME] = 'MSG_SET_LOCAL_SPEAKER_VOLUME'
MSG_SET_LOCAL_MIC_VOLUME = 21
MESSAGE_IDS[MSG_SET_LOCAL_MIC_VOLUME] = 'MSG_SET_LOCAL_MIC_VOLUME'
MSG_MUTE_LOCAL_MIC = 22
MESSAGE_IDS[MSG_MUTE_LOCAL_MIC] = 'MSG_MUTE_LOCAL_MIC'
MSG_LOGIN_STATE_CHANGE = 30
MESSAGE_IDS[MSG_LOGIN_STATE_CHANGE] = 'MSG_LOGIN_STATE_CHANGE'
MSG_SESSION_ADDED = 42
MESSAGE_IDS[MSG_SESSION_ADDED] = 'MSG_SESSION_ADDED'
MSG_SESSION_REMOVED = 43
MESSAGE_IDS[MSG_SESSION_REMOVED] = 'MSG_SESSION_REMOVED'
MSG_NETWORK_TEST = 50
MESSAGE_IDS[MSG_NETWORK_TEST] = 'MSG_NETWORK_TEST'
MSG_PARTICIPANT_ADDED = 60
MESSAGE_IDS[MSG_PARTICIPANT_ADDED] = 'MSG_PARTICIPANT_ADDED'
MSG_PARTICIPANT_REMOVED = 61
MESSAGE_IDS[MSG_PARTICIPANT_REMOVED] = 'MSG_PARTICIPANT_REMOVED'
MSG_PARTICIPANT_UPDATED = 62
MESSAGE_IDS[MSG_PARTICIPANT_UPDATED] = 'MSG_PARTICIPANT_UPDATED'

class VOIPHandler:

    def __init__(self):
        pass

    def onVoipInited(self, data):
        pass

    def onVoipDestroyed(self, data):
        pass

    def onCaptureDevicesArrived(self, data):
        pass

    def onSetCaptureDevice(self, data):
        pass

    def onSetLocalSpeakerVolume(self, data):
        pass

    def onSetLocalMicVolume(self, data):
        pass

    def onMuteLocalMic(self, data):
        pass

    def onLoginStateChange(self, data):
        pass

    def onSessionAdded(self, data):
        pass

    def onSessionRemoved(self, data):
        pass

    def onNetworkTest(self, data):
        pass

    def onParticipantAdded(self, data):
        pass

    def onParticipantRemoved(self, data):
        pass

    def onParticipantUpdated(self, data):
        pass

    @noexcept
    def __call__(self, message, data = {}):
        if message is not MSG_PARTICIPANT_UPDATED:
            LOG_VOIP_INT('Message: %d [%s], Data: %s' % (message, MESSAGE_IDS[message], data))
        if message == MSG_VOIP_INITED:
            self.onVoipInited(data)
        elif message == MSG_VOIP_DESTROYED:
            self.onVoipDestroyed(data)
        elif message == MSG_CAPTURE_DEVICES:
            self.onCaptureDevicesArrived(data)
        elif message == MSG_SET_CAPTURE_DEVICE:
            self.onSetCaptureDevice(data)
        elif message == MSG_SET_LOCAL_SPEAKER_VOLUME:
            self.onSetLocalSpeakerVolume(data)
        elif message == MSG_SET_LOCAL_MIC_VOLUME:
            self.onSetLocalMicVolume(data)
        elif message == MSG_MUTE_LOCAL_MIC:
            self.onMuteLocalMic(data)
        elif message == MSG_LOGIN_STATE_CHANGE:
            self.onLoginStateChange(data)
        elif message == MSG_SESSION_ADDED:
            self.onSessionAdded(data)
        elif message == MSG_SESSION_REMOVED:
            self.onSessionRemoved(data)
        elif message == MSG_NETWORK_TEST:
            self.onNetworkTest(data)
        elif message == MSG_PARTICIPANT_ADDED:
            self.onParticipantAdded(data)
        elif message == MSG_PARTICIPANT_REMOVED:
            self.onParticipantRemoved(data)
        elif message == MSG_PARTICIPANT_UPDATED:
            self.onParticipantUpdated(data)
