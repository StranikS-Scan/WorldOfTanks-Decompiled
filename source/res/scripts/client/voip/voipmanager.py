# Embedded file name: scripts/client/VOIP/VOIPManager.py
import BigWorld
import FMOD
import SoundGroups
import Event
import Settings
import constants
from gui.Scaleform import VoiceChatInterface
from debug_utils import LOG_VOIP, LOG_CURRENT_EXCEPTION, verify
from chat_shared import CHAT_ACTIONS, CHAT_RESPONSES, USERS_ROSTER_VOICE_MUTED
from ChatManager import chatManager
import sys
from datetime import datetime
g_useVivoxlog = None
g_vivoxLogFile = None

def LOG_VOIP_INT(msg, *kargs):
    global g_useVivoxlog
    if g_useVivoxlog is None:
        checkUseVivoxLog()
    verify(g_useVivoxlog is not None)
    if g_useVivoxlog:
        _writeLog(msg, kargs)
    elif kargs:
        pass
    return


def checkUseVivoxLog():
    global g_useVivoxlog
    g_useVivoxlog = False
    section = Settings.g_instance.userPrefs
    if section.has_key('development'):
        section = section['development']
        if section.has_key('enableVivoxLog'):
            g_useVivoxlog = section['enableVivoxLog'].asBool
            if g_useVivoxlog:
                _createLog()


def _createLog():
    global g_vivoxLogFile
    if g_vivoxLogFile is None:
        try:
            g_vivoxLogFile = open('vivox.log', 'a')
            g_vivoxLogFile.write('----------------------------\n')
        except:
            LOG_CURRENT_EXCEPTION()

    return


def _closeLog():
    global g_useVivoxlog
    global g_vivoxLogFile
    g_useVivoxlog = None
    if g_vivoxLogFile is not None:
        try:
            g_vivoxLogFile.close()
            g_vivoxLogFile = None
        except:
            LOG_CURRENT_EXCEPTION()

    return


def _writeLog(msg, args):
    try:
        frame = sys._getframe(2)
        dt = datetime.time(datetime.now())
        g_vivoxLogFile.write('%s: (%s, %d):' % (dt, frame.f_code.co_filename, frame.f_lineno))
        g_vivoxLogFile.write(msg)
        if args:
            g_vivoxLogFile.write(args)
        g_vivoxLogFile.write('\n')
        g_vivoxLogFile.flush()
    except:
        LOG_CURRENT_EXCEPTION()


class VOIPManager:

    def __init__(self, channelsMgr):
        self.channelsMgr = channelsMgr
        self.vivoxDomain = ''
        self.testChannel = ''
        self.inTesting = False
        self.channelID = -1
        self.mainChannel = ['', '']
        self.__activateMicByVoice = False
        self.__enableVoiceNormalization = False
        self.usersRoster = {}
        self.channelUsers = {}
        self.captureDevices = []
        self.currentCaptureDevice = ''
        self.OnCaptureDevicesUpdated = Event.Event()
        self.onParticipantMute = Event.Event()
        self.onPlayerSpeaking = Event.Event()
        self.channelsMgr.onCaptureDevicesArrived += self._onCaptureDevicesArrived
        self.channelsMgr.onParticipantAdded += self._onParticipantAdded
        self.channelsMgr.onParticipantRemoved += self._onParticipantRemoved
        self.channelsMgr.onParticipantUpdated += self._onParticipantUpdated
        self.channelsMgr.onJoinedChannel += self._onJoinedChannel
        self.channelsMgr.onLeftChannel += self.onLeftChannel
        self.channelsMgr.onLogined += self.onLogined
        self.channelsMgr.onStateChanged += self.onStateChanged
        self.oldMasterVolume = FMOD.getMasterVolume()
        self.muffled = False

    def destroy(self):
        self.channelsMgr.onParticipantAdded -= self._onParticipantAdded
        self.channelsMgr.onParticipantRemoved -= self._onParticipantRemoved
        self.channelsMgr.onParticipantUpdated -= self._onParticipantUpdated
        self.channelsMgr.onJoinedChannel -= self._onJoinedChannel
        self.channelsMgr.onLeftChannel -= self.onLeftChannel
        self.channelsMgr.onLogined -= self.onLogined
        self.channelsMgr.onStateChanged -= self.onStateChanged
        self.channelsMgr.onCaptureDevicesArrived -= self._onCaptureDevicesArrived
        BigWorld.VOIP.finalise()
        _closeLog()

    def onConnected(self):
        LOG_VOIP_INT('VOIPManager.subscribe')
        chatManager.subscribeChatAction(self.__onEnterChatChannel, CHAT_ACTIONS.VOIPSettings)
        chatManager.subscribeChatAction(self.__onLeftChatChannel, CHAT_ACTIONS.channelDestroyed)
        chatManager.subscribeChatAction(self.__onLeftChatChannel, CHAT_ACTIONS.selfLeave)
        chatManager.subscribeChatAction(self.__onUserCredentials, CHAT_ACTIONS.VOIPCredentials)
        chatManager.subscribeChatAction(self.__onRequestUsersRoster, CHAT_ACTIONS.requestUsersRoster)
        chatManager.subscribeChatAction(self.__onChatActionSetMuted, CHAT_ACTIONS.setMuted)
        chatManager.subscribeChatAction(self.__onChatActionUnsetMuted, CHAT_ACTIONS.unsetMuted)
        chatManager.subscribeChatAction(self.__onChatResponseMutedError, CHAT_RESPONSES.setMutedError)
        chatManager.subscribeChatAction(self.__onChatResponseMutedError, CHAT_RESPONSES.unsetMutedError)
        self.channelsMgr.onConnected()

    def onDisconnected(self):
        LOG_VOIP_INT('VOIPManager.unsubscribe')
        chatManager.unsubscribeChatAction(self.__onEnterChatChannel, CHAT_ACTIONS.VOIPSettings)
        chatManager.unsubscribeChatAction(self.__onLeftChatChannel, CHAT_ACTIONS.channelDestroyed)
        chatManager.unsubscribeChatAction(self.__onLeftChatChannel, CHAT_ACTIONS.selfLeave)
        chatManager.unsubscribeChatAction(self.__onUserCredentials, CHAT_ACTIONS.VOIPCredentials)
        chatManager.unsubscribeChatAction(self.__onRequestUsersRoster, CHAT_ACTIONS.requestUsersRoster)
        chatManager.unsubscribeChatAction(self.__onChatActionSetMuted, CHAT_ACTIONS.setMuted)
        chatManager.unsubscribeChatAction(self.__onChatActionUnsetMuted, CHAT_ACTIONS.unsetMuted)
        chatManager.unsubscribeChatAction(self.__onChatResponseMutedError, CHAT_RESPONSES.setMutedError)
        chatManager.unsubscribeChatAction(self.__onChatResponseMutedError, CHAT_RESPONSES.unsetMutedError)

    def enable(self, enabled):
        LOG_VOIP_INT('VOIPManager.enable: %s' % str(enabled))
        self.channelsMgr.enable(enabled)

    def initialize(self, domain):
        if not domain:
            return
        if self.vivoxDomain:
            verify(domain == self.vivoxDomain)
            return
        LOG_VOIP_INT('VOIPManager.Initialize')
        self.vivoxDomain = domain
        self.testChannel = 'sip:confctl-2@' + domain.partition('www.')[2]
        LOG_VOIP_INT("domain_vivox: '%s'" % self.vivoxDomain)
        LOG_VOIP_INT("domain_test : '%s'" % self.testChannel)
        self.channelsMgr.initialize(domain)

    def __enterChannel(self, name, password):
        if not self.channelsMgr.user[0] and self.channelsMgr.enabled:
            self.requestVOIPCredentials()
        self.channelsMgr.enterChannel(name, password)

    def __leaveChannel(self):
        self.channelsMgr.leaveChannel()

    def __onEnterChatChannel(self, data):
        if not data['channel'] or data['data']['URL'] == '' or data['data']['password'] == '':
            return
        if self.mainChannel[0] == data['data']['URL']:
            return
        self.channelID = data['channel']
        self.mainChannel = [data['data']['URL'], data['data']['password']]
        if not self.inTesting:
            self.__enterChannel(self.mainChannel[0], self.mainChannel[1])

    def __onLeftChatChannel(self, data):
        if self.channelID != data['channel']:
            return
        verify(self.mainChannel[0])
        if not self.inTesting:
            self.__leaveChannel()
        self.channelID = -1
        self.mainChannel = ['', '']

    def enterTestChannel(self):
        if self.inTesting:
            return
        LOG_VOIP_INT("VOIPManager.enterTestChannel: '%s'" % self.testChannel)
        self.inTesting = True
        self.__enterChannel(self.testChannel, '')

    def leaveTestChannel(self):
        if not self.inTesting:
            return
        LOG_VOIP_INT('VOIPManager.leaveTestChannel')
        self.inTesting = False
        if self.mainChannel[0]:
            verify(self.channelID != -1)
            self.__enterChannel(self.mainChannel[0], self.mainChannel[1])
        else:
            verify(self.channelID == -1)
            self.__leaveChannel()

    def requestVOIPCredentials(self):
        LOG_VOIP_INT('VOIPManager.requestVOIPCredentials')
        BigWorld.player().requestVOIPCredentials()

    def __onUserCredentials(self, data):
        LOG_VOIP_INT("VOIPManager.onUserCredentials: '%s' '%s'" % (data['data'][0], data['data'][1]))
        self.channelsMgr.login(data['data'][0], data['data'][1])
        BigWorld.player().requestUsersRoster(USERS_ROSTER_VOICE_MUTED)

    def logout(self):
        LOG_VOIP_INT('VOIPManager.logout')
        self.usersRoster.clear()
        self.channelsMgr.logout()

    def setMicMute(self, muted = True):
        if not self.channelsMgr.initialized:
            return
        if muted and self.__activateMicByVoice:
            return
        self._setMicMute(muted)

    def _setMicMute(self, muted):
        pass

    def setVoiceActivation(self, enabled):
        LOG_VOIP_INT('VOIPManager.setVoiceActivation: ', enabled)
        self.__activateMicByVoice = enabled
        self.setMicMute(not enabled)

    def setMasterVolume(self, attenuation):
        BigWorld.VOIP.setMasterVolume(attenuation, {})

    def setMicrophoneVolume(self, attenuation):
        BigWorld.VOIP.setMicrophoneVolume(attenuation, {})

    def setVolume(self):
        self.setMasterVolume(int(round(SoundGroups.g_instance.getVolume('masterVivox') * 100)))
        self.setMicrophoneVolume(int(round(SoundGroups.g_instance.getVolume('micVivox') * 100)))

    def getVADProperties(self):
        LOG_VOIP_INT('VOIPManager.getVADProperties is not implemented!')

    def setVADProperties(self, hangover, sensitivity):
        LOG_VOIP_INT('VOIPManager.setVADProperties is not implemented!')

    def muteParticipantForMe(self, dbid, mute, name = ''):
        LOG_VOIP_INT('VOIPManager.muteParticipantForMe')
        if dbid not in self.channelUsers:
            LOG_VOIP_INT("mute_for_me: User not found in participant's list")
            return False
        p = BigWorld.player()
        p.setMuted(dbid, name) if mute else p.unsetMuted(dbid)
        self._muteParticipantForMe(dbid, mute)

    def _muteParticipantForMe(self, dbid, mute):
        LOG_VOIP_INT('VOIPManager._muteParticipantForMe is not implemented!')
        return False

    def __onChatActionSetMuted(self, data):
        LOG_VOIP_INT('VOIPManager.__onChatActionSetMuted')
        self.__onChatActionMute(data['data'][0], True)

    def __onChatActionUnsetMuted(self, data):
        LOG_VOIP_INT('VOIPManager.__onChatActionUnsetMuted')
        self.__onChatActionMute(data['data'], False)

    def __onChatActionMute(self, dbid, muted):
        LOG_VOIP_INT('VOIPManager.__onChatActionMute', dbid, muted)
        self.usersRoster[dbid] = muted
        if dbid in self.channelUsers and self.channelUsers[dbid]['muted'] != muted:
            self._muteParticipantForMe(dbid, muted)

    def __onChatResponseMutedError(self, data):
        LOG_VOIP_INT('VOIPManager.__onChatResponseMutedError', data.items())
        verify(False and data)

    def __onRequestUsersRoster(self, data):
        for dbid, name, flags in data['data']:
            muted = bool(flags & USERS_ROSTER_VOICE_MUTED)
            self.usersRoster[dbid] = muted
            if muted and dbid in self.channelUsers:
                self._muteParticipantForMe(dbid, True)

    def requestCaptureDevices(self):
        LOG_VOIP_INT('VOIPManager.requestCaptureDevices')
        BigWorld.VOIP.wg_getCaptureDevices()

    def setCaptureDevice(self, deviceName):
        LOG_VOIP_INT("VOIPManager.setCaptureDevice: '%s'" % deviceName)
        BigWorld.VOIP.wg_setCaptureDevice(deviceName)
        self.requestCaptureDevices()

    def _onCaptureDevicesArrived(self, data):
        LOG_VOIP_INT('VOIPManager.onCaptureDevicesArrived')
        captureDevicesCount = int(data[constants.KEY_COUNT])
        self.captureDevices = []
        for i in xrange(captureDevicesCount):
            self.captureDevices.append(str(data[constants.KEY_CAPTURE_DEVICES + '_' + str(i)]))

        self.currentCaptureDevice = str(data[constants.KEY_CURRENT_CAPTURE_DEVICE])
        self.OnCaptureDevicesUpdated()

    def setParticipantVolume(self, uri, volume):
        LOG_VOIP_INT('VOIPManager.setParticipantVolume is not implemented')

    def isParticipantTalking(self, dbid):
        outcome = self.channelUsers.get(dbid, {}).get('talking', False)
        return outcome

    def setPlayerTalking(self, dbid, talking):
        self.onPlayerSpeaking(dbid, talking)
        VoiceChatInterface.g_instance.setPlayerSpeaking(dbid, talking)
        from gui.WindowsManager import g_windowsManager
        if g_windowsManager.battleWindow is not None:
            g_windowsManager.battleWindow.setPlayerSpeaking(dbid, talking)
        return

    def muffleMasterVolume(self):
        if not self.muffled:
            self.oldMasterVolume = FMOD.getMasterVolume()
            FMOD.setMasterVolume(self.oldMasterVolume * SoundGroups.g_instance.getVolume('masterFadeVivox'))
            self.muffled = True

    def restoreMasterVolume(self):
        self.muffled = False
        FMOD.setMasterVolume(self.oldMasterVolume)

    def isAnyoneTalking(self):
        for info in self.channelUsers.values():
            if info['talking']:
                return True

        return False

    def _onParticipantAdded(self, data):
        uri = data[constants.KEY_PARTICIPANT_URI]
        dbid, _ = self.extractDBIDFromURI(uri)
        if dbid == -1:
            return
        self.channelUsers[dbid] = {'talking': False,
         'uri': uri,
         'muted': False,
         'lastVolumeUpdateTime': BigWorld.time(),
         'energy': 0,
         'volume': 0}
        if self.usersRoster.get(dbid, False):
            self._muteParticipantForMe(dbid, True)

    def _onParticipantUpdated(self, data):
        uri = data[constants.KEY_PARTICIPANT_URI]
        dbid, participantLogin = self.extractDBIDFromURI(uri)
        if dbid == -1:
            return
        talking = int(data[constants.KEY_IS_SPEAKING])
        channelUser = self.channelUsers[dbid]
        if dbid in self.channelUsers:
            if channelUser['talking'] != talking:
                channelUser['talking'] = talking
                self.muffleMasterVolume() if self.isAnyoneTalking() else self.restoreMasterVolume()
        self.setPlayerTalking(dbid, talking)
        channelUser['energy'] = data[constants.KEY_ENERGY]
        channelUser['volume'] = data[constants.KEY_VOLUME]

    def _onParticipantRemoved(self, data):
        uri = data[constants.KEY_PARTICIPANT_URI]
        dbid, _ = self.extractDBIDFromURI(uri)
        if dbid in self.channelUsers:
            del self.channelUsers[dbid]
        self.setPlayerTalking(dbid, False)

    def _onJoinedChannel(self, data):
        self.setVolume()
        verify(not self.channelUsers)

    def onLeftChannel(self, data):
        for dbid in self.channelUsers.keys():
            self.setPlayerTalking(dbid, False)

        self.channelUsers.clear()
        self.restoreMasterVolume()

    def onLogined(self):
        BigWorld.player().logVivoxLogin()

    def onStateChanged(self, old, new):
        if new == self.channelsMgr.STATE_JOINING_CHANNEL:
            muteMic = self.channelsMgr.channel[0] != self.testChannel and not self.__activateMicByVoice
            self.setMicMute(muteMic)

    def extractDBIDFromURI(self, uri):
        try:
            domain = self.vivoxDomain.partition('www.')[2]
            login = uri.partition('sip:')[2].rpartition('@' + domain)[0]
            s = login[login.find('.') + 1:]
            return (int(s), login)
        except:
            return -1
