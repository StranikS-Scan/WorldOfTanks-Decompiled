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
    """
    This base class is a bridge between python and Action script for voice Chat logic.
    Specific behaviour for Lobby and Battle should be implemented in child classes.
    """

    def __init__(self, app):
        """
        Constructor, we will memorize reference on application
        :param app: SFApplication instance
        """
        super(BaseVoiceChatManager, self).__init__()
        self.setEnvironment(app)

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        """
        Returns instance of chat plugin to have access to VOIP Controller
        :return: instance of chat plugin
        """
        return None

    def isPlayerSpeaking(self, accountDBID):
        """
        This method is called by Action script.
        :param accountDBID: player dbID
        :return: bool value from Voip Controller
        """
        return self.bwProto.voipController.isPlayerSpeaking(accountDBID)

    def isVivox(self):
        """
        This method is called by Action script.
        :return: bool value from Voip Controller
        """
        return self.bwProto.voipController.isVivox()

    def isYY(self):
        """
        This method is called by Action script.
        :return: bool value from Voip Controller
        """
        return self.bwProto.voipController.isYY()

    def isVOIPEnabled(self):
        """
        This method is called by Action script and other python classes.
        :return: bool value from Voip Controller, the result is depending on gui settings.
        """
        return self.bwProto.voipController.isVOIPEnabled()

    def _populate(self):
        """
        Population procedure for flash component, we are subscribing on the required events.
        """
        super(BaseVoiceChatManager, self)._populate()
        voipEvents = g_messengerEvents.voip
        voipEvents.onVoiceChatInitSucceeded += self._showChatInitSuccessMessage
        voipEvents.onVoiceChatInitFailed += self._showChatInitErrorMessage
        voipEvents.onPlayerSpeaking += self.__onPlayerSpeaking
        self.app.containerManager.onViewAddedToContainer += self.__onViewAddedToContainer

    def _dispose(self):
        """
        Disposing procedure for flash component, we are un-subscribing from the events.
        """
        voipEvents = g_messengerEvents.voip
        voipEvents.onVoiceChatInitSucceeded -= self._showChatInitSuccessMessage
        voipEvents.onVoiceChatInitFailed -= self._showChatInitErrorMessage
        voipEvents.onPlayerSpeaking -= self.__onPlayerSpeaking
        containerMgr = self.app.containerManager
        if containerMgr:
            containerMgr.onViewAddedToContainer -= self.__onViewAddedToContainer
        super(BaseVoiceChatManager, self)._dispose()

    def _onViewAdded(self, viewAlias):
        """
        Implement this method in a child class to catch the event about view changing.
        :param viewAlias: string containing view alias type, see VIEW_ALIAS class.
        """
        raise NotImplementedError

    def _showChatInitSuccessMessage(self):
        """
        Implement this method in a child class to catch the event,
        when Init Success dialog should be shown.
        """
        raise NotImplementedError

    def _showChatInitErrorMessage(self):
        """
        Implement this method in a child class to catch the event,
        when Init Failed dialog should be shown.
        """
        raise NotImplementedError

    def _showDialog(self, key):
        """
        Show a modal dialog with the message in the key provided.
        :param key: key for the message
        """
        DialogsInterface.showI18nInfoDialog(key, lambda result: None)

    def __onPlayerSpeaking(self, accountDBID, isSpeak):
        """
        Raise flash event after receiving notification about player speaking.
        :param accountDBID: player db id
        :param isSpeak: is player speaking
        """
        self.as_onPlayerSpeakS(accountDBID, isSpeak, accountDBID == getPlayerDatabaseID())

    def __onViewAddedToContainer(self, _, pyView):
        """
        Listen to onViewAddedToContainer event and call internal _onViewAdded method if necessary.
        :param _: container in which view was added.
        :param pyView: view that was added to container.
        """
        settings = pyView.settings
        viewType = settings.type
        if viewType == ViewTypes.DEFAULT:
            viewAlias = settings.alias
            self._onViewAdded(viewAlias)


class LobbyVoiceChatManager(BaseVoiceChatManager):
    """
    This manager extends BaseVoiceChatManager class and it is used only for Lobby/Login screen.
    The main purpose for this class is to show Failed/Success Voice chat initialization dialog.
    """

    def __init__(self, app):
        """
        Constructor, initialize the required flags and variables.
        :param app: SFApplication instance
        """
        super(LobbyVoiceChatManager, self).__init__(app)
        self.__failedEventRaised = False
        self.__pendingMessage = None
        self.__enterToLobby = False
        return

    def _onViewAdded(self, viewAlias):
        """
        Update flag indicating that we are in/out of lobby.
        In case when there is a pending message, we will show it after user login.
        :param viewAlias: string describing view type
        """
        if viewAlias == VIEW_ALIAS.LOBBY:
            self.__enterToLobby = True
            if self.__pendingMessage is not None:
                self._showDialog(self.__pendingMessage)
                self.__pendingMessage = None
        else:
            self.__enterToLobby = False
        return

    def _showChatInitSuccessMessage(self):
        """
        If error message has been shown -> show success message
        """
        if self.__failedEventRaised:
            self.__failedEventRaised = False
            self.__pendingMessage = None
            if self.__enterToLobby:
                self._showDialog(_MESSAGE_INIT_SUCCESS)
        return

    def _showChatInitErrorMessage(self):
        """
        If error message has not been shown -> show error message
        """
        if not self.__failedEventRaised:
            self.__failedEventRaised = True
            if self.__enterToLobby:
                self._showDialog(_MESSAGE_INIT_FAILED)
            else:
                self.__pendingMessage = _MESSAGE_INIT_FAILED


class BattleVoiceChatManager(BaseVoiceChatManager):
    """
    This manager is used only for Battle pages.
    It extends BaseVoiceChatManager class to show INIT_FAILED dialog when necessary.
    """

    def __init__(self, app):
        """
        Constructor, initialize flag about battle entrance.
        :param app: SFApplication instance
        """
        super(BattleVoiceChatManager, self).__init__(app)
        self.__enteredToBattle = False

    def _onViewAdded(self, viewAlias):
        """
        Raise the flag that we are in a battle only if the view is one from battle pages.
        :param viewAlias: string describing view type
        """
        self.__enteredToBattle = viewAlias in VIEW_ALIAS.BATTLE_PAGES

    def _showChatInitSuccessMessage(self):
        """
        In battle we shouldn't show Success message, just skip it.
        """
        pass

    def _showChatInitErrorMessage(self):
        """
        Show the dialog about error only we have entered to the battle.
        """
        if self.__enteredToBattle:
            self._showDialog(_MESSAGE_INIT_FAILED)
