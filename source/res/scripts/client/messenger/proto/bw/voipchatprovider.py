# Embedded file name: scripts/client/messenger/proto/bw/VOIPChatProvider.py
import BigWorld
from chat_shared import CHAT_ACTIONS
from debug_utils import LOG_WARNING
from messenger import g_settings
from messenger.proto.bw import ChatActionsListener
from messenger.proto.events import g_messengerEvents
from messenger.proto.interfaces import IVOIPChatProvider

class VOIPChatProvider(ChatActionsListener, IVOIPChatProvider):

    def __init__(self):
        super(VOIPChatProvider, self).__init__()
        self.__channelID = 0
        self.__channelParams = ('', '')

    def getChannelParams(self):
        return self.__channelParams

    def requestCredentials(self, reset = 0):
        if g_settings.server.BW_CHAT2.isEnabled():
            LOG_WARNING('That routine is ignored, uses chat2 to receive credentials.')
        else:
            BigWorld.player().requestVOIPCredentials(reset)

    def logVivoxLogin(self):
        if g_settings.server.BW_CHAT2.isEnabled():
            LOG_WARNING('That routine is ignored, uses chat2 to log Vivox login.')
        else:
            BigWorld.player().logVivoxLogin()

    def addListeners(self):
        if g_settings.server.BW_CHAT2.isEnabled():
            return
        self.addListener(self.__onEnterChatChannel, CHAT_ACTIONS.VOIPSettings)
        self.addListener(self.__onLeftChatChannel, CHAT_ACTIONS.channelDestroyed)
        self.addListener(self.__onLeftChatChannel, CHAT_ACTIONS.selfLeave)
        self.addListener(self.__onUserCredentials, CHAT_ACTIONS.VOIPCredentials)

    def removeAllListeners(self):
        super(VOIPChatProvider, self).removeAllListeners()
        self.__channelID = 0
        self.__channelParams = ('', '')

    def __onEnterChatChannel(self, data):
        chatData = data['data']
        url = chatData['URL']
        pwd = chatData['password']
        channelID = data['channel']
        if not channelID or url == '' or pwd == '':
            return
        if self.__channelParams[0] == url:
            return
        self.__channelID = channelID
        self.__channelParams = (url, pwd)
        g_messengerEvents.voip.onChannelEntered(url, pwd)

    def __onLeftChatChannel(self, data):
        if self.__channelID != data['channel']:
            return
        g_messengerEvents.voip.onChannelLeft()
        self.__channelID = 0
        self.__channelParams = ('', '')

    def __onUserCredentials(self, data):
        chatData = data['data']
        g_messengerEvents.voip.onCredentialReceived(chatData[0], chatData[1])
