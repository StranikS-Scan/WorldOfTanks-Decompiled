# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/managers/voice_chat.py
from messenger.proto.events import g_messengerEvents
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewTypes
from gui.shared.utils import getPlayerDatabaseID
from gui import DialogsInterface
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
from gui.Scaleform.framework.entities.abstract.VoiceChatManagerMeta import VoiceChatManagerMeta
_MESSAGE_INIT_SUCCESS = 'voiceChatInitSucceded'
_MESSAGE_INIT_FAILED = 'voiceChatInitFailed'

class BaseVoiceChatManager(VoiceChatManagerMeta):

    def __init__(self, app):
        super(BaseVoiceChatManager, self).__init__()
        self.setEnvironment(app)

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def isPlayerSpeaking(self, accountDBID):
        return self.bwProto.voipController.isPlayerSpeaking(accountDBID)

    def isVivox(self):
        return self.bwProto.voipController.isVivox()

    def isYY(self):
        return self.bwProto.voipController.isYY()

    def isVOIPEnabled(self):
        return self.bwProto.voipController.isVOIPEnabled()

    def _populate(self):
        super(BaseVoiceChatManager, self)._populate()
        voipEvents = g_messengerEvents.voip
        voipEvents.onVoiceChatInitSucceeded += self._showChatInitSuccessMessage
        voipEvents.onVoiceChatInitFailed += self._showChatInitErrorMessage
        voipEvents.onPlayerSpeaking += self.__onPlayerSpeaking
        self.app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer

    def _dispose(self):
        voipEvents = g_messengerEvents.voip
        voipEvents.onVoiceChatInitSucceeded -= self._showChatInitSuccessMessage
        voipEvents.onVoiceChatInitFailed -= self._showChatInitErrorMessage
        voipEvents.onPlayerSpeaking -= self.__onPlayerSpeaking
        containerMgr = self.app.containerManager
        if containerMgr:
            containerMgr.onViewAddedToContainer -= self.__onViewAddedToContainer
        super(BaseVoiceChatManager, self)._dispose()

    def _onViewAdded(self, viewAlias):
        raise NotImplementedError

    def _showChatInitSuccessMessage(self):
        raise NotImplementedError

    def _showChatInitErrorMessage(self):
        raise NotImplementedError

    def _showDialog(self, key):
        DialogsInterface.showI18nInfoDialog(key, lambda result: None)

    def __onPlayerSpeaking(self, accountDBID, isSpeak):
        self.as_onPlayerSpeakS(accountDBID, isSpeak, accountDBID == getPlayerDatabaseID())

    def __onViewAddedToContainer(self, _, pyView):
        settings = pyView.settings
        viewType = settings.type
        if viewType == ViewTypes.DEFAULT:
            viewAlias = settings.alias
            self._onViewAdded(viewAlias)


class LobbyVoiceChatManager(BaseVoiceChatManager):

    def __init__(self, app):
        super(LobbyVoiceChatManager, self).__init__(app)
        self.__failedEventRaised = False
        self.__pendingMessage = None
        self.__enterToLobby = False
        return

    def _onViewAdded(self, viewAlias):
        if viewAlias == VIEW_ALIAS.LOBBY:
            self.__enterToLobby = True
            if self.__pendingMessage is not None:
                self._showDialog(self.__pendingMessage)
                self.__pendingMessage = None
        else:
            self.__enterToLobby = False
        return

    def _showChatInitSuccessMessage(self):
        if self.__failedEventRaised:
            self.__failedEventRaised = False
            self.__pendingMessage = None
            if self.__enterToLobby:
                self._showDialog(_MESSAGE_INIT_SUCCESS)
        return

    def _showChatInitErrorMessage(self):
        if not self.__failedEventRaised:
            self.__failedEventRaised = True
            if self.__enterToLobby:
                self._showDialog(_MESSAGE_INIT_FAILED)
            else:
                self.__pendingMessage = _MESSAGE_INIT_FAILED


class BattleVoiceChatManager(BaseVoiceChatManager):

    def __init__(self, app):
        super(BattleVoiceChatManager, self).__init__(app)
        self.__enteredToBattle = False
        self.__failedEventRaised = False

    def _onViewAdded(self, viewAlias):
        self.__enteredToBattle = viewAlias in VIEW_ALIAS.BATTLE_PAGES

    def _showChatInitSuccessMessage(self):
        pass

    def _showChatInitErrorMessage(self):
        if self.__enteredToBattle and not self.__failedEventRaised:
            self._showDialog(_MESSAGE_INIT_FAILED)
            self.__failedEventRaised = True
