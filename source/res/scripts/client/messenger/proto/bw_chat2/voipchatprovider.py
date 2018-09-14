# Embedded file name: scripts/client/messenger/proto/bw_chat2/VOIPChatProvider.py
from debug_utils import LOG_WARNING, LOG_NOTE
from messenger.proto.bw_chat2 import errors, provider
from messenger.proto.events import g_messengerEvents
from messenger.proto.interfaces import IVOIPChatProvider
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS, messageArgs
from messenger_common_chat2 import MESSENGER_LIMITS as _LIMITS
_EMPTY_CHANNELS_PARAMS = ('', '')

class VOIPChatProvider(provider.ResponseDictHandler, IVOIPChatProvider):

    def __init__(self, provider):
        super(VOIPChatProvider, self).__init__(provider)
        self.__channelParams = _EMPTY_CHANNELS_PARAMS

    def clear(self):
        self.__channelParams = _EMPTY_CHANNELS_PARAMS
        super(VOIPChatProvider, self).clear()

    def leave(self):
        self.__channelParams = _EMPTY_CHANNELS_PARAMS

    def getChannelParams(self):
        return self.__channelParams

    def requestCredentials(self, reset = 0):
        provider = self.provider()
        actionID = _ACTIONS.GET_VOIP_CREDENTIALS
        if reset:
            provider.clearActionCoolDown(actionID)
        success, reqID = provider.doAction(actionID, messageArgs(int32Arg1=reset), True)
        if reqID:
            self.pushRq(reqID, actionID)
        if success:
            provider.setActionCoolDown(actionID, _LIMITS.VOIP_CREDENTIALS_REQUEST_COOLDOWN_SEC)

    def logVivoxLogin(self):
        self.provider().doAction(_ACTIONS.LOG_VIVOX_LOGIN)

    def registerHandlers(self):
        register = self.provider().registerHandler
        register(_ACTIONS.ENTER_VOIP_CHANNEL, self.__onChannelEntered)
        register(_ACTIONS.LEAVE_VOIP_CHANNEL, self.__onChannelLeft)
        super(VOIPChatProvider, self).registerHandlers()

    def unregisterHandlers(self):
        unregister = self.provider().unregisterHandler
        unregister(_ACTIONS.ENTER_VOIP_CHANNEL, self.__onChannelEntered)
        unregister(_ACTIONS.LEAVE_VOIP_CHANNEL, self.__onChannelLeft)
        super(VOIPChatProvider, self).unregisterHandlers()

    def _onResponseSuccess(self, ids, args):
        actionID = super(VOIPChatProvider, self)._onResponseSuccess(ids, args)
        if actionID == _ACTIONS.GET_VOIP_CREDENTIALS:
            g_messengerEvents.voip.onCredentialReceived(args['strArg1'], args['strArg2'])

    def _onResponseFailure(self, ids, args):
        actionID = super(VOIPChatProvider, self)._onResponseFailure(ids, args)
        if actionID is None:
            return
        else:
            error, logOnly = errors.createVOIPError(args, actionID)
            if error:
                if logOnly:
                    LOG_NOTE(error)
                else:
                    g_messengerEvents.onErrorReceived(error)
            else:
                LOG_WARNING('Error is not resolved on the client to display in GUI', actionID, ids, args)
            return

    def __onChannelEntered(self, _, args):
        url = args['strArg1']
        pwd = args['strArg2']
        if not url or not pwd or self.__channelParams[0] == url:
            return
        self.__channelParams = (url, pwd)
        g_messengerEvents.voip.onChannelEntered(url, pwd)

    def __onChannelLeft(self, ids, args):
        g_messengerEvents.voip.onChannelLeft()
        self.__channelParams = _EMPTY_CHANNELS_PARAMS
