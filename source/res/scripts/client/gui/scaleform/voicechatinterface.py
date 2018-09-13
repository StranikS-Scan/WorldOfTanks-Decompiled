# Embedded file name: scripts/client/gui/Scaleform/VoiceChatInterface.py
import BigWorld, Settings, Event
import BattleReplay
from adisp import async
from enumerations import Enumeration
from windows import UIInterface
from debug_utils import *
from gui import GUI_SETTINGS
VC_STATES = Enumeration('Voice chat states enumeration', ['NotInitialized', 'Initialized', 'Failed'])

class _VoiceChatInterface(UIInterface):
    onVoiceChatInitFailed = Event.Event()
    onVoiceChatInitSucceded = Event.Event()
    onPlayerSpeaking = Event.Event()

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
        import VOIP
        VOIP.getVOIPManager().channelsMgr.onFailedToConnect += self.processFailedMessage
        VOIP.getVOIPManager().channelsMgr.onInitialized += self.__initResponse
        VOIP.getVOIPManager().OnCaptureDevicesUpdated += self.__captureDevicesResponse

    def dispossessUI(self, proxy):
        if self.uiHolder != proxy:
            return
        import VOIP
        VOIP.getVOIPManager().channelsMgr.onInitialized -= self.__initResponse
        VOIP.getVOIPManager().OnCaptureDevicesUpdated -= self.__captureDevicesResponse
        VOIP.getVOIPManager().channelsMgr.onFailedToConnect -= self.processFailedMessage
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
            import VOIP
            return VOIP.getVOIPManager().isParticipantTalking(accountDBID)
        return False

    @property
    def state(self):
        return self.__state

    @property
    def ready(self):
        import VOIP
        return VOIP.getVOIPManager().channelsMgr.initialized

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
        import VOIP
        rh = VOIP.getVOIPManager()
        if domain == '':
            LOG_ERROR('Initialize. Vivox is not supported')
            self.__state = VC_STATES.Failed
            callback(False)
            return
        if self.__state == VC_STATES.Initialized:
            callback(True)
            return
        self.__callback = callback
        rh.enable(Settings.g_instance.userPrefs.readBool(Settings.KEY_ENABLE_VOIP))
        rh.initialize(domain)

    def __captureDevicesResponse(self):
        if self.__callback is not None:
            import VOIP
            self.__callback(VOIP.getVOIPManager().captureDevices)
        return

    @async
    def requestCaptureDevices(self, callback):
        import VOIP
        if VOIP.getVOIPManager().vivoxDomain == '':
            LOG_ERROR('RequestCaptureDevices. Vivox is not supported')
            callback([])
            return
        if not self.ready:
            LOG_ERROR('RequestCaptureDevices. Vivox has not been initialized')
            callback([])
            return
        self.__callback = callback
        VOIP.getVOIPManager().requestCaptureDevices()

    def isVivox(self):
        try:
            from VOIP import getVOIPManager
            from VOIP.Vivox.VivoxManager import VivoxManager
            return isinstance(getVOIPManager(), VivoxManager)
        except Exception:
            LOG_CURRENT_EXCEPTION()
            return False

    def isYY(self):
        try:
            from VOIP import getVOIPManager
            from VOIP.YY.YYManager import YYManager
            return isinstance(getVOIPManager(), YYManager)
        except Exception:
            LOG_CURRENT_EXCEPTION()
            return False

    @property
    def voiceChatProvider(self):
        if self.isVivox():
            return 'vivox'
        if self.isYY():
            return 'YY'
        return 'unknown'


g_instance = _VoiceChatInterface()
