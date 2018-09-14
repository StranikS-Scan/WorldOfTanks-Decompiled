# Embedded file name: scripts/client/gui/Scaleform/VoiceChatInterface.py
import BigWorld, Event
import BattleReplay
from VOIP import getVOIPManager
from VOIP.voip_constants import VOIP_SUPPORTED_API
from adisp import async, process
from enumerations import Enumeration
from windows import UIInterface
from debug_utils import *
from gui import GUI_SETTINGS
from account_helpers.settings_core.SettingsCore import g_settingsCore
VC_STATES = Enumeration('Voice chat states enumeration', ['NotInitialized', 'Initialized', 'Failed'])

class _VoiceChatInterface(UIInterface):
    onVoiceChatInitFailed = Event.Event()
    onVoiceChatInitSucceded = Event.Event()
    onPlayerSpeaking = Event.Event()
    onStateToggled = Event.Event()

    def __init__(self):
        UIInterface.__init__(self)
        self.__state = VC_STATES.NotInitialized
        self.__failedEventRaised = False
        self.__callback = None
        return

    def reset(self):
        self.__failedEventRaised = False

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        voipMgr = getVOIPManager()
        voipMgr.onFailedToConnect += self.processFailedMessage
        voipMgr.onInitialized += self.__initResponse
        voipMgr.OnCaptureDevicesUpdated += self.__captureDevicesResponse
        voipMgr.onPlayerSpeaking += self.__onPlayerSpeaking
        voipMgr.onStateToggled += self.__onStateToggled
        if not voipMgr.isInitialized():
            self.__doInitialize()

    def dispossessUI(self, proxy):
        if self.uiHolder != proxy:
            return
        voipMgr = getVOIPManager()
        voipMgr.onInitialized -= self.__initResponse
        voipMgr.OnCaptureDevicesUpdated -= self.__captureDevicesResponse
        voipMgr.onFailedToConnect -= self.processFailedMessage
        voipMgr.onPlayerSpeaking -= self.__onPlayerSpeaking
        voipMgr.onStateToggled -= self.__onStateToggled
        UIInterface.dispossessUI(self)

    def processFailedMessage(self, *args):
        if not self.__failedEventRaised and not self.ready and GUI_SETTINGS.voiceChat and not BattleReplay.isPlaying():
            self.__failedEventRaised = True
            self.onVoiceChatInitFailed()

    def getPlayerDBID(self):
        import Avatar, Account
        if type(BigWorld.player()) is Account.PlayerAccount:
            return BigWorld.player().databaseID
        elif type(BigWorld.player()) is Avatar.PlayerAvatar and hasattr(BigWorld.player(), 'playerVehicleID'):
            return BigWorld.player().arena.vehicles[BigWorld.player().playerVehicleID].get('accountDBID', None)
        else:
            return

    def setPlayerSpeaking(self, accountDBID, isSpeak):
        if not GUI_SETTINGS.voiceChat:
            return
        self.onPlayerSpeaking(accountDBID, isSpeak)

    def isPlayerSpeaking(self, accountDBID):
        if GUI_SETTINGS.voiceChat:
            return getVOIPManager().isParticipantTalking(accountDBID)
        return False

    @property
    def state(self):
        return self.__state

    @property
    def ready(self):
        return getVOIPManager().isInitialized()

    def __initResponse(self, data):
        if self.__callback is not None:
            self.__state = VC_STATES.Initialized if data is not None else VC_STATES.Failed
            if self.__state == VC_STATES.Initialized and self.__failedEventRaised:
                self.__failedEventRaised = False
                self.onVoiceChatInitSucceded()
            self.__callback(data is not None)
            self.__callback = None
        return

    @async
    def initialize(self, domain, callback):
        rh = getVOIPManager()
        if domain == '':
            LOG_ERROR('Initialize. Vivox is not supported')
            self.__state = VC_STATES.Failed
            callback(False)
            return
        if self.__state == VC_STATES.Initialized:
            g_settingsCore.options.getSetting('enableVoIP').initFromPref()
            callback(True)
            return
        self.__callback = callback
        g_settingsCore.options.getSetting('enableVoIP').initFromPref()
        rh.initialize(domain)

    def __captureDevicesResponse(self):
        if self.__callback is not None:
            self.__callback(getVOIPManager().getCaptureDevices())
        return

    @async
    def requestCaptureDevices(self, callback):
        if getVOIPManager().getVOIPDomain() == '':
            LOG_ERROR('RequestCaptureDevices. Vivox is not supported')
            callback([])
            return
        if not self.ready:
            LOG_ERROR('RequestCaptureDevices. Vivox has not been initialized')
            callback([])
            return
        self.__callback = callback
        getVOIPManager().requestCaptureDevices()

    def isVivox(self):
        return getVOIPManager().getAPI() == VOIP_SUPPORTED_API.VIVOX

    def isYY(self):
        return getVOIPManager().getAPI() == VOIP_SUPPORTED_API.YY

    @property
    def voiceChatProvider(self):
        if self.isVivox():
            return 'vivox'
        if self.isYY():
            return 'YY'
        return 'unknown'

    @process
    def __doInitialize(self):
        serverSettings = getattr(BigWorld.player(), 'serverSettings', None)
        if serverSettings and 'voipDomain' in serverSettings:
            domain = serverSettings['voipDomain']
        else:
            domain = ''
        yield self.initialize(domain)
        yield self.requestCaptureDevices()
        return

    def __onPlayerSpeaking(self, accountDBID, isSpeak):
        if not GUI_SETTINGS.voiceChat:
            return
        self.onPlayerSpeaking(accountDBID, isSpeak)

    def __onStateToggled(self, isEnabled, toReset):
        if not GUI_SETTINGS.voiceChat:
            return
        for dbID in toReset:
            self.__onPlayerSpeaking(dbID, False)

        self.onStateToggled(isEnabled)


g_instance = _VoiceChatInterface()
