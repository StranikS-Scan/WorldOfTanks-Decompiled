# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/bw_chat2/VOIPChatController.py
import BigWorld
import BattleReplay
import VOIP
import CommandMapping
from VOIP.voip_constants import VOIP_SUPPORTED_API
from debug_utils import LOG_WARNING
from adisp import async, process
from gui import GUI_SETTINGS
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
from helpers import dependency
from messenger.proto.events import g_messengerEvents
from messenger.proto.interfaces import IVOIPChatController
from account_helpers.settings_core.settings_constants import SOUND
from skeletons.account_helpers.settings_core import ISettingsCore

class VOIPChatController(IVOIPChatController):
    __slots__ = ('__callbacks', '__captureDevicesCallbacks')
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__callbacks = []
        self.__captureDevicesCallbacks = []

    def start(self):
        voipMgr = VOIP.getVOIPManager()
        voipMgr.onInitialized += self.__initResponse
        voipMgr.onFailedToConnect += self.__failedResponse
        voipMgr.onCaptureDevicesUpdated += self.__captureDevicesResponse
        voipMgr.onPlayerSpeaking += self.__onPlayerSpeaking
        voipMgr.onJoinedChannel += self.__onJoinedChannel
        voipMgr.onLeftChannel += self.__onLeftChannel
        g_eventBus.addListener(GameEvent.TOGGLE_VOIP_CHANNEL_ENABLED, self.__onToggleChannelEnabled, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__initialize()

    def stop(self):
        voipMgr = VOIP.getVOIPManager()
        voipMgr.onInitialized -= self.__initResponse
        voipMgr.onFailedToConnect -= self.__failedResponse
        voipMgr.onCaptureDevicesUpdated -= self.__captureDevicesResponse
        voipMgr.onPlayerSpeaking -= self.__onPlayerSpeaking
        voipMgr.onJoinedChannel -= self.__onJoinedChannel
        voipMgr.onLeftChannel -= self.__onLeftChannel
        g_eventBus.removeListener(GameEvent.TOGGLE_VOIP_CHANNEL_ENABLED, self.__onToggleChannelEnabled, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__callbacks = []
        self.__captureDevicesCallbacks = []

    def isReady(self):
        return VOIP.getVOIPManager().isInitialized()

    def isPlayerSpeaking(self, accountDBID):
        return bool(VOIP.getVOIPManager().isParticipantTalking(accountDBID)) if self.isVOIPEnabled() else False

    def isVOIPEnabled(self):
        return GUI_SETTINGS.voiceChat

    def isVivox(self):
        return VOIP.getVOIPManager().getAPI() == VOIP_SUPPORTED_API.VIVOX

    def isYY(self):
        return VOIP.getVOIPManager().getAPI() == VOIP_SUPPORTED_API.YY

    def invalidateInitialization(self):
        if self.isVOIPEnabled() and not BattleReplay.isPlaying() and not self.isReady():
            g_messengerEvents.voip.onVoiceChatInitFailed()

    def setMicrophoneMute(self, isMuted, force=False):
        voipMgr = VOIP.getVOIPManager()
        if voipMgr is not None:
            if force or voipMgr.getCurrentChannel() and not voipMgr.isInTesting():
                voipMgr.setMicMute(muted=isMuted)
        return

    def invalidateMicrophoneMute(self):
        keyCode = CommandMapping.g_instance.get('CMD_VOICECHAT_MUTE')
        if not BigWorld.isKeyDown(keyCode):
            self.setMicrophoneMute(isMuted=True, force=True)

    @async
    def requestCaptureDevices(self, firstTime=False, callback=None):
        voipMgr = VOIP.getVOIPManager()
        if voipMgr.getVOIPDomain() == '':
            LOG_WARNING('RequestCaptureDevices. Vivox is not supported')
            callback([])
            return
        if not self.isReady():
            LOG_WARNING('RequestCaptureDevices. Vivox has not been initialized')
            callback([])
            return
        options = self.settingsCore.options

        def resetCapturedDevice(devices, firstTime=firstTime):
            if firstTime:
                option = options.getSetting(SOUND.CAPTURE_DEVICES)
                option.apply(option.get(), firstTime)
            callback(devices)

        self.__captureDevicesCallbacks.append(resetCapturedDevice)
        voipMgr.requestCaptureDevices()

    def isCurrentChannelEnabled(self):
        return VOIP.getVOIPManager().isCurrentChannelEnabled()

    def enableCurrentChannel(self, isEnableChannel):
        VOIP.getVOIPManager().enableCurrentChannel(isEnableChannel)

    @process
    def __initialize(self):
        serverSettings = getattr(BigWorld.player(), 'serverSettings', {})
        if serverSettings and 'voipDomain' in serverSettings:
            domain = serverSettings['voipUserDomain']
            server = serverSettings['voipDomain']
        else:
            domain = ''
            server = ''
        yield self.__initializeSettings(domain, server)
        yield self.requestCaptureDevices(True)

    @async
    def __initializeSettings(self, domain, server, callback):
        if self.isReady():
            self.__applyUserSettings()
            callback(True)
            return
        if domain == '':
            LOG_WARNING('Initialize. Vivox is not supported')
            return
        self.__callbacks.append(callback)
        voipMgr = VOIP.getVOIPManager()
        if voipMgr.isNotInitialized():
            voipMgr.initialize(domain, server)
        self.__applyUserSettings()

    def __applyUserSettings(self):
        options = self.settingsCore.options
        vOIPSetting = options.getSetting('enableVoIP')
        vOIPSetting.initFromPref()
        channelSettings = options.getSetting(SOUND.VOIP_ENABLE_CHANNEL)
        channelSettings.initFromPref()

    def __initResponse(self, _):
        if self.isVOIPEnabled() and self.isReady():
            g_messengerEvents.voip.onVoiceChatInitSucceeded()
        while self.__callbacks:
            self.__callbacks.pop(0)(self.isReady())

    def __failedResponse(self):
        self.invalidateInitialization()

    def __captureDevicesResponse(self):
        devices = VOIP.getVOIPManager().getCaptureDevices()
        while self.__captureDevicesCallbacks:
            self.__captureDevicesCallbacks.pop(0)(devices)

    def __onPlayerSpeaking(self, accountDBID, isSpeak):
        if self.isVOIPEnabled():
            g_messengerEvents.voip.onPlayerSpeaking(accountDBID, bool(isSpeak))

    def __onJoinedChannel(self, channel, isTestChannel, isRejoin):
        if self.isVOIPEnabled():
            keyCode = CommandMapping.g_instance.get('CMD_VOICECHAT_MUTE')
            if BigWorld.isKeyDown(keyCode):
                VOIP.getVOIPManager().setMicMute(False)
            g_messengerEvents.voip.onChannelEntered(channel, isTestChannel, isRejoin)

    def __onLeftChannel(self, channel, wasTestChannel):
        if self.isVOIPEnabled():
            g_messengerEvents.voip.onChannelLeft(channel, wasTestChannel)

    def __onToggleChannelEnabled(self, event):
        voipMgr = VOIP.getVOIPManager()
        voipMgr.enableCurrentChannel(not voipMgr.isCurrentChannelEnabled())
