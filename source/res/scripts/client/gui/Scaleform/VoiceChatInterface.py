# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/VoiceChatInterface.py
# Compiled at: 2011-09-09 14:42:19
import BigWorld, Settings, constants, Event
from adisp import process, async
from enumerations import Enumeration
from windows import UIInterface
from debug_utils import LOG_ERROR, LOG_DEBUG, LOG_NOTE
from chat_shared import CHAT_ACTIONS
from ChatManager import chatManager
from gui.Scaleform import FEATURES
VC_STATES = Enumeration('Voice chat states enumeration', ['NotInitialized', 'Initialized', 'Failed'])

class _VoiceChatInterface(UIInterface):
    onVoiceChatInitFailed = Event.Event()
    onVoiceChatInitSucceded = Event.Event()
    onPlayerSpeaking = Event.Event()

    def __init__(self):
        UIInterface.__init__(self)
        self.__initializationTimoutCallback = None
        self.__state = VC_STATES.NotInitialized
        self.__failedEventRaised = False
        self._playersSpeak = {}
        return

    def reset(self):
        self.__failedEventRaised = False

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        chatManager.subscribeChatAction(self.processFailedMessage, CHAT_ACTIONS.VOIPSettings)

    def processFailedMessage(self, *args):
        if not self.__failedEventRaised and self.__state != VC_STATES.Initialized and FEATURES.VOICE_CHAT:
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

    def dispossessUI(self):
        chatManager.unsubscribeChatAction(self.processFailedMessage, CHAT_ACTIONS.VOIPSettings)
        UIInterface.dispossessUI(self)

    def setPlayerSpeaking(self, accountDBID, isSpeak):
        if not FEATURES.VOICE_CHAT:
            return
        else:
            self._playersSpeak[accountDBID] = isSpeak
            self.onPlayerSpeaking(accountDBID, isSpeak)
            from gui.WindowsManager import g_windowsManager
            if g_windowsManager.battleWindow is None:
                self.call('common.speakingPlayersResponse', [accountDBID, isSpeak, accountDBID == self.getPlayerDBID()])
            return

    def isPlayerSpeaking(self, accountDBID):
        if FEATURES.VOICE_CHAT:
            return self._playersSpeak.get(accountDBID, False)
        else:
            return False

    @property
    def state(self):
        return self.__state

    @property
    def ready(self):
        return self.__state == VC_STATES.Initialized

    @async
    def initialize(self, domain, callback):
        import Vivox
        rh = Vivox.getResponseHandler()
        if domain == '':
            LOG_ERROR('Initialize. Vivox is not supported')
            self.__state = VC_STATES.Failed
            callback(False)
            return
        if self.__state == VC_STATES.Initialized:
            callback(True)
            return

        def __response(data):
            rh.channelsMgr.onInitialized -= __response
            self.__state = VC_STATES.Initialized if data is not None else VC_STATES.Failed
            if self.__state == VC_STATES.Initialized and self.__failedEventRaised:
                self.__failedEventRaised = False
                self.onVoiceChatInitSucceded()
            if self.__initializationTimoutCallback is not None:
                BigWorld.cancelCallback(self.__initializationTimoutCallback)
                self.__initializationTimoutCallback = None
            callback(data is not None)
            return

        def __initTimoutCallback():
            if self.__initializationTimoutCallback is not None:
                BigWorld.cancelCallback(self.__initializationTimoutCallback)
                self.__initializationTimoutCallback = None
            return

        rh.enable(Settings.g_instance.userPrefs.readBool(Settings.KEY_ENABLE_VOIP))
        rh.channelsMgr.onInitialized += __response
        self.__initializationTimoutCallback = BigWorld.callback(constants.VOICE_CHAT_INIT_TIMEOUT, __initTimoutCallback)
        rh.initialize(domain)

    @async
    def requestCaptureDevices(self, callback):
        import Vivox
        from Vivox.ChannelsMgr import ChannelsMgr
        if Vivox.getResponseHandler().vivoxDomain == '':
            LOG_ERROR('RequestCaptureDevices. Vivox is not supported')
            callback([])
            return
        if self.__state != VC_STATES.Initialized:
            LOG_ERROR('RequestCaptureDevices. Vivox has not been initialized')
            callback([])
            return

        def __response():
            Vivox.getResponseHandler().OnCaptureDevicesUpdated -= __response
            callback(Vivox.getResponseHandler().captureDevices)

        Vivox.getResponseHandler().OnCaptureDevicesUpdated += __response
        Vivox.getResponseHandler().requestCaptureDevices()


g_instance = _VoiceChatInterface()
