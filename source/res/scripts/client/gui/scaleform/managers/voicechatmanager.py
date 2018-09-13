# Embedded file name: scripts/client/gui/Scaleform/managers/VoiceChatManager.py
import BigWorld
import Event
import BattleReplay
from adisp import async, process
from debug_utils import LOG_WARNING, LOG_DEBUG
from gui.Scaleform.daapi.settings import VIEW_ALIAS
from gui.Scaleform.framework import AppRef, ViewTypes
from helpers import isPlayerAccount, isPlayerAvatar
from VOIP import getVOIPManager
from VOIP.ChannelsMgr import ChannelsMgr
from PlayerEvents import g_playerEvents
from gui import GUI_SETTINGS, DialogsInterface
from gui.shared.utils import CONST_CONTAINER
from gui.Scaleform.framework.entities.abstract.VoiceChatManagerMeta import VoiceChatManagerMeta
from account_helpers.settings_core.SettingsCore import g_settingsCore
from account_helpers.settings_core.settings_constants import SOUND

class VoiceChatManager(VoiceChatManagerMeta, AppRef):

    class PROVIDERS(CONST_CONTAINER):
        UNKNOWN = 'unknown'
        VIVOX = 'vivox'
        YY = 'YY'

    onPlayerSpeaking = Event.Event()

    def __init__(self):
        super(VoiceChatManager, self).__init__()
        self.__failedEventRaised = False
        self.__callbacks = []
        self.__captureDevicesCallbacks = []
        self.__pendingMessage = None
        self.__enterToLobby = False
        return

    def __initResponse(self, _):
        self.__showChatInitSuccessMessage()
        while len(self.__callbacks):
            self.__callbacks.pop(0)(self.ready)

    def __captureDevicesResponse(self):
        devices = getVOIPManager().captureDevices
        while len(self.__captureDevicesCallbacks):
            self.__captureDevicesCallbacks.pop(0)(devices)

        option = g_settingsCore.options.getSetting(SOUND.CAPTURE_DEVICES)
        option.apply(option.get())

    def __showChatInitSuccessMessage(self):
        if GUI_SETTINGS.voiceChat and not BattleReplay.isPlaying():
            if self.__failedEventRaised and self.ready:
                self.__failedEventRaised = False
                self.__pendingMessage = None
                if self.__enterToLobby:
                    self.__showDialog('voiceChatInitSucceded')
        return

    def __showChatInitErrorMessage(self):
        if GUI_SETTINGS.voiceChat and not BattleReplay.isPlaying():
            if not self.__failedEventRaised and not self.ready:
                self.__failedEventRaised = True
                if self.__enterToLobby:
                    self.__showDialog('voiceChatInitFailed')
                else:
                    self.__pendingMessage = 'voiceChatInitFailed'

    def _populate(self):
        super(VoiceChatManager, self)._populate()
        g_playerEvents.onAccountBecomePlayer += self.onAccountBecomePlayer
        self.app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
        voipMgr = getVOIPManager()
        voipMgr.channelsMgr.onInitialized += self.__initResponse
        voipMgr.channelsMgr.onFailedToConnect += self.checkForInitialization
        voipMgr.OnCaptureDevicesUpdated += self.__captureDevicesResponse
        voipMgr.onPlayerSpeaking += self.__onPlayerSpeaking

    def _dispose(self):
        self.__callbacks = None
        self.__captureDevicesCallbacks = None
        containerMgr = self.app.containerManager
        if containerMgr:
            containerMgr.onViewAddedToContainer -= self.__onViewAddedToContainer
        voipMgr = getVOIPManager()
        voipMgr.channelsMgr.onFailedToConnect -= self.checkForInitialization
        voipMgr.onPlayerSpeaking -= self.__onPlayerSpeaking
        voipMgr.channelsMgr.onInitialized -= self.__initResponse
        voipMgr.OnCaptureDevicesUpdated -= self.__captureDevicesResponse
        g_playerEvents.onAccountBecomePlayer -= self.onAccountBecomePlayer
        super(VoiceChatManager, self)._dispose()
        return

    def checkForInitialization(self, *args):
        self.__showChatInitErrorMessage()

    @property
    def state(self):
        return getVOIPManager().channelsMgr.state

    @property
    def ready(self):
        return getVOIPManager().channelsMgr.initialized

    @process
    def onAccountBecomePlayer(self):
        yield self.initialize(BigWorld.player().serverSettings['voipDomain'])
        yield self.requestCaptureDevices()

    @async
    def initialize(self, domain, callback):
        if self.ready:
            callback(True)
            return
        if domain == '':
            LOG_WARNING('Initialize. Vivox is not supported')
            return
        self.__callbacks.append(callback)
        if self.state == ChannelsMgr.STATE_INITIALIZING:
            return
        voipMgr = getVOIPManager()
        voipMgr.initialize(domain)
        voipMgr.enable(g_settingsCore.getSetting(SOUND.VOIP_ENABLE))

    @async
    def requestCaptureDevices(self, callback):
        if getVOIPManager().vivoxDomain == '':
            LOG_WARNING('RequestCaptureDevices. Vivox is not supported')
            callback([])
            return
        if not self.ready:
            LOG_WARNING('RequestCaptureDevices. Vivox has not been initialized')
            callback([])
            return
        self.__captureDevicesCallbacks.append(callback)
        getVOIPManager().requestCaptureDevices()

    def getPlayerDBID(self):
        p = BigWorld.player()
        if isPlayerAccount():
            return p.databaseID
        elif isPlayerAvatar() and hasattr(p, 'playerVehicleID'):
            return p.arena.vehicles[p.playerVehicleID].get('accountDBID', None)
        else:
            return None

    def __onPlayerSpeaking(self, accountDBID, isSpeak):
        if not GUI_SETTINGS.voiceChat:
            return
        self.onPlayerSpeaking(accountDBID, bool(isSpeak))
        self.as_onPlayerSpeakS(accountDBID, isSpeak, accountDBID == self.getPlayerDBID())

    def isPlayerSpeaking(self, accountDBID):
        if GUI_SETTINGS.voiceChat:
            return bool(getVOIPManager().isParticipantTalking(accountDBID))
        return False

    def isVivox(self):
        try:
            from VOIP.Vivox.VivoxManager import VivoxManager
            return isinstance(getVOIPManager(), VivoxManager)
        except Exception:
            return False

    def isYY(self):
        try:
            from VOIP.YY.YYManager import YYManager
            return isinstance(getVOIPManager(), YYManager)
        except Exception:
            return False

    @property
    def provider(self):
        if self.isVivox():
            return self.PROVIDERS.VIVOX
        if self.isYY():
            return self.PROVIDERS.YY
        return self.PROVIDERS.UNKNOWN

    def isVOIPEnabled(self):
        return GUI_SETTINGS.voiceChat

    def __onViewAddedToContainer(self, _, pyView):
        settings = pyView.settings
        viewType = settings.type
        if viewType == ViewTypes.DEFAULT:
            viewAlias = settings.alias
            if viewAlias == VIEW_ALIAS.LOBBY:
                self.__enterToLobby = True
                if self.__pendingMessage is not None:
                    self.__showDialog(self.__pendingMessage)
                    self.__pendingMessage = None
            else:
                self.__enterToLobby = False
        return

    def __showDialog(self, key):
        DialogsInterface.showI18nInfoDialog(key, lambda result: None)
