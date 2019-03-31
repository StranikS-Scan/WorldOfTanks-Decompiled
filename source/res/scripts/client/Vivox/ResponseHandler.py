# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Vivox/ResponseHandler.py
# Compiled at: 2011-08-03 20:48:17
import BigWorld
import Event
import constants
import Vivox
import Helpers
from debug_utils import LOG_DEBUG, verify, LOG_ERROR
import SoundGroups
from wotdecorators import noexcept
from chat_shared import CHAT_ACTIONS, CHAT_COMMANDS, CHAT_RESPONSES, USERS_ROSTER_VOICE_MUTED
from ChatManager import chatManager
from gui.WindowsManager import g_windowsManager
import ChannelsMgr
from gui.Scaleform import VoiceChatInterface
import FMOD

class ResponseHandler:

    def __init__(self):
        self.channelsMgr = ChannelsMgr.ChannelsMgr()
        self.vivoxDomain = ''
        self.testChannel = ''
        self.mainChannel = ['', '']
        self.inTesting = False
        self.usersRoster = {}
        self.channelUsers = {}
        self.channelID = -1
        self.captureDevices = []
        self.currentCaptureDevice = ''
        self.OnCaptureDevicesUpdated = Event.Event()
        self.onParticipantMute = Event.Event()
        self.channelsMgr.onCaptureDevicesUpdated += self.onCaptureDevicesUpdated
        self.channelsMgr.onParticipantAdded += self.onParticipantAdded
        self.channelsMgr.onParticipantRemoved += self.onParticipantRemoved
        self.channelsMgr.onParticipantUpdated += self.onParticipantUpdated
        self.channelsMgr.onJoinedChannel += self.onJoinedChannel
        self.channelsMgr.onLeftChannel += self.onLeftChannel
        self.channelsMgr.onLogined += self.onLogined
        self.channelsMgr.onStateChanged += self.onStateChanged

    def destroy(self):
        self.channelsMgr.onCaptureDevicesUpdated -= self.onCaptureDevicesUpdated
        self.channelsMgr.onParticipantAdded -= self.onParticipantAdded
        self.channelsMgr.onParticipantRemoved -= self.onParticipantRemoved
        self.channelsMgr.onParticipantUpdated -= self.onParticipantUpdated
        self.channelsMgr.onJoinedChannel -= self.onJoinedChannel
        self.channelsMgr.onLeftChannel -= self.onLeftChannel
        self.channelsMgr.onLogined -= self.onLogined
        self.channelsMgr.onStateChanged -= self.onStateChanged
        self.channelsMgr.destroy()

    def subscribeChatActions(self):
        chatManager.subscribeChatAction(self.__onEnterChatChannel, CHAT_ACTIONS.VOIPSettings)
        chatManager.subscribeChatAction(self.__onLeftChatChannel, CHAT_ACTIONS.channelDestroyed)
        chatManager.subscribeChatAction(self.__onLeftChatChannel, CHAT_ACTIONS.selfLeave)
        chatManager.subscribeChatAction(self.__onUserCredentials, CHAT_ACTIONS.VOIPCredentials)
        chatManager.subscribeChatAction(self.__onRequestUsersRoster, CHAT_ACTIONS.requestUsersRoster)
        chatManager.subscribeChatAction(self.__onChatActionSetMuted, CHAT_ACTIONS.setMuted)
        chatManager.subscribeChatAction(self.__onChatActionUnsetMuted, CHAT_ACTIONS.unsetMuted)
        chatManager.subscribeChatAction(self.__onChatResponseMutedError, CHAT_RESPONSES.setMutedError)
        chatManager.subscribeChatAction(self.__onChatResponseMutedError, CHAT_RESPONSES.unsetMutedError)

    def unsubscribeChatActions(self):
        chatManager.unsubscribeChatAction(self.__onEnterChatChannel, CHAT_ACTIONS.VOIPSettings)
        chatManager.unsubscribeChatAction(self.__onLeftChatChannel, CHAT_ACTIONS.channelDestroyed)
        chatManager.unsubscribeChatAction(self.__onLeftChatChannel, CHAT_ACTIONS.selfLeave)
        chatManager.unsubscribeChatAction(self.__onUserCredentials, CHAT_ACTIONS.VOIPCredentials)
        chatManager.unsubscribeChatAction(self.__onRequestUsersRoster, CHAT_ACTIONS.requestUsersRoster)
        chatManager.unsubscribeChatAction(self.__onChatActionSetMuted, CHAT_ACTIONS.setMuted)
        chatManager.unsubscribeChatAction(self.__onChatActionUnsetMuted, CHAT_ACTIONS.unsetMuted)
        chatManager.unsubscribeChatAction(self.__onChatResponseMutedError, CHAT_RESPONSES.setMutedError)
        chatManager.unsubscribeChatAction(self.__onChatResponseMutedError, CHAT_RESPONSES.unsetMutedError)

    def initialize(self, domain):
        if not domain:
            return
        if self.vivoxDomain:
            verify(domain == self.vivoxDomain)
            return
        self.vivoxDomain = domain
        self.testChannel = 'sip:confctl-2@' + domain.partition('www.')[2]
        self.channelsMgr.initialize(domain)

    def initialized(self):
        return self.channelsMgr.initialized

    def __onUserCredentials(self, data):
        LOG_DEBUG('__onUserCredentials', data['data'][0], data['data'][1])
        self.channelsMgr.login(data['data'][0], data['data'][1])
        BigWorld.player().requestUsersRoster(USERS_ROSTER_VOICE_MUTED)

    def __onEnterChatChannel(self, data):
        LOG_DEBUG('__onEnterChannel', data.items())
        if data['data']['URL'] == '' or data['data']['password'] == '':
            return
        self.channelID = data['channel']
        credentials = [data['data']['URL'], data['data']['password']]
        if self.inTesting:
            self.mainChannel = credentials
        else:
            self.__enterChannel(credentials[0], credentials[1])

    def __onLeftChatChannel(self, data):
        if self.channelID == data['channel']:
            if self.inTesting:
                verify(self.mainChannel[0])
                self.mainChannel = ['', '']
            else:
                self.channelID = -1
                verify(not self.mainChannel[0])
                self.__leaveChannel()

    def __enterChannel(self, name, password):
        if not self.channelsMgr.user[0]:
            BigWorld.player().requestVOIPCredentials()
        self.channelsMgr.enterChannel(name, password)

    def __leaveChannel(self):
        self.channelsMgr.leaveChannel()

    def logout(self):
        self.usersRoster.clear()
        self.channelsMgr.logout()

    def enable(self, enabled):
        self.channelsMgr.enable(enabled)

    def setMicMute(self, muted=True):
        cmd = {}
        cmd[constants.KEY_COMMAND] = 'mute_mic'
        cmd[constants.KEY_STATE] = str(muted)
        BigWorld.VOIP.command(cmd)
        LOG_DEBUG('mute_mic: %s' % str(muted))

    def setMasterVolume(self, attenuation):
        BigWorld.VOIP.setMasterVolume(attenuation, {})

    def setMicrophoneVolume(self, attenuation):
        BigWorld.VOIP.setMicrophoneVolume(attenuation, {})

    def setVolume(self):
        self.setMasterVolume(int(round(SoundGroups.g_instance.getVolume('masterVivox') * 100)))
        self.setMicrophoneVolume(int(round(SoundGroups.g_instance.getVolume('micVivox') * 100)))

    def enterTestChannel(self):
        verify(not self.inTesting)
        if self.inTesting:
            return
        self.inTesting = True
        self.mainChannel = self.channelsMgr.channel
        self.__enterChannel(self.testChannel, '')

    def leaveTestChannel(self):
        verify(self.inTesting)
        if not self.inTesting:
            return
        self.inTesting = False
        if self.mainChannel[0]:
            self.__enterChannel(self.mainChannel[0], self.mainChannel[1])
        else:
            self.__leaveChannel()
        self.mainChannel = ['', '']

    def muteParticipantForMe(self, dbid, mute, name=''):
        if dbid not in self.channelUsers:
            LOG_DEBUG("mute_for_me: User not found in participant's list")
            return False
        p = BigWorld.player()
        p.setMuted(dbid, name) if mute else p.unsetMuted(dbid)
        self.__muteParticipantForMe(dbid, mute)

    def __muteParticipantForMe(self, dbid, mute):
        verify(dbid in self.channelUsers)
        self.channelUsers[dbid]['muted'] = mute
        uri = self.channelUsers[dbid]['uri']
        cmd = {}
        cmd[constants.KEY_COMMAND] = constants.CMD_SET_PARTICIPANT_MUTE
        cmd[constants.KEY_PARTICIPANT_URI] = uri
        cmd[constants.KEY_STATE] = str(mute)
        BigWorld.VOIP.command(cmd)
        LOG_DEBUG('mute_for_me: %d, %s' % (dbid, str(mute)))
        self.onParticipantMute(dbid, mute)
        return True

    def __onChatActionSetMuted(self, data):
        self.__onChatActionMute(data['data'][0], True)

    def __onChatActionUnsetMuted(self, data):
        self.__onChatActionMute(data['data'], False)

    def __onChatActionMute(self, dbid, muted):
        LOG_DEBUG('__onChatActionMute', dbid, muted)
        self.usersRoster[dbid] = muted
        if dbid in self.channelUsers and self.channelUsers[dbid]['muted'] != muted:
            self.__muteParticipantForMe(dbid, muted)

    def __onChatResponseMutedError(self, data):
        LOG_ERROR('__onChatResponseMutedError', data.items())
        verify(False and data)

    def __onRequestUsersRoster(self, data):
        for dbid, name, flags in data['data']:
            muted = bool(flags & USERS_ROSTER_VOICE_MUTED)
            self.usersRoster[dbid] = muted
            if muted and dbid in self.channelUsers:
                self.__muteParticipantForMe(dbid, True)

    def requestCaptureDevices(self):
        BigWorld.VOIP.wg_getCaptureDevices()

    def setCaptureDevice(self, deviceName):
        BigWorld.VOIP.wg_setCaptureDevice(deviceName)
        self.requestCaptureDevices()

    def onParticipantUpdated(self, data):
        uri = data[constants.KEY_PARTICIPANT_URI]
        dbid = self.extractDBIDFromURI(uri)
        if dbid == -1:
            return
        talking = int(data[constants.KEY_IS_SPEAKING])
        if dbid in self.channelUsers:
            if self.channelUsers[dbid]['talking'] != talking:
                self.channelUsers[dbid]['talking'] = talking
                self.muffleMasterVolume() if self.isAnyoneTalking() else self.restoreMasterVolume()
        self.setPlayerTalking(dbid, talking)

    def setPlayerTalking(self, dbid, talking):
        VoiceChatInterface.g_instance.setPlayerSpeaking(dbid, talking)
        if g_windowsManager.battleWindow is not None:
            g_windowsManager.battleWindow.setPlayerSpeaking(dbid, talking)
        return

    def muffleMasterVolume(self):
        masterVolume = SoundGroups.g_instance.getMasterVolume() * SoundGroups.g_instance.getVolume('masterFadeVivox')
        FMOD.setMasterVolume(masterVolume)

    def restoreMasterVolume(self):
        FMOD.setMasterVolume(SoundGroups.g_instance.getMasterVolume())

    def isAnyoneTalking(self):
        for info in self.channelUsers.values():
            if info['talking']:
                return True

        return False

    def onCaptureDevicesUpdated(self, data):
        captureDevicesCount = int(data[constants.KEY_COUNT])
        self.captureDevices = []
        for i in xrange(captureDevicesCount):
            self.captureDevices.append(str(data[constants.KEY_CAPTURE_DEVICES + '_' + str(i)]))

        self.currentCaptureDevice = str(data[constants.KEY_CURRENT_CAPTURE_DEVICE])
        self.OnCaptureDevicesUpdated()

    def onParticipantAdded(self, data):
        uri = data[constants.KEY_PARTICIPANT_URI]
        dbid = self.extractDBIDFromURI(uri)
        if dbid == -1:
            return
        self.channelUsers[dbid] = {'talking': False,
         'uri': uri,
         'muted': False}
        if self.usersRoster.get(dbid, False):
            self.__muteParticipantForMe(dbid, True)

    def onParticipantRemoved(self, data):
        uri = data[constants.KEY_PARTICIPANT_URI]
        dbid = self.extractDBIDFromURI(uri)
        if dbid in self.channelUsers:
            del self.channelUsers[dbid]
        self.setPlayerTalking(dbid, False)

    def onJoinedChannel(self, data):
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
            self.setMicMute(self.channelsMgr.channel[0] != self.testChannel)

    def extractDBIDFromURI(self, uri):
        try:
            domain = self.vivoxDomain.partition('www.')[2]
            login = uri.partition('sip:')[2].rpartition('@' + domain)[0]
            s = login[login.find('.') + 1:]
            return int(s)
        except:
            return -1
