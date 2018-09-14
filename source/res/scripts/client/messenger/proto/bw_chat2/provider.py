# Embedded file name: scripts/client/messenger/proto/bw_chat2/provider.py
from collections import defaultdict, deque
from gui.shared.rq_cooldown import RequestCooldownManager, REQUEST_SCOPE
import weakref
import BigWorld
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_CURRENT_EXCEPTION
from ids_generators import SequenceIDGenerator
from messenger.proto.bw_chat2.errors import createCoolDownError
from messenger.proto.events import g_messengerEvents
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS, messageArgs

class _ChatCooldownManager(RequestCooldownManager):

    def __init__(self):
        super(_ChatCooldownManager, self).__init__(REQUEST_SCOPE.BW_CHAT2)

    def lookupName(self, rqTypeID):
        return _ACTIONS.getActionName(rqTypeID)

    def getDefaultCoolDown(self):
        return 5.0


class BWChatProvider(object):

    def __init__(self):
        super(BWChatProvider, self).__init__()
        self.__handlers = defaultdict(set)
        self.__msgFilters = None
        self.__coolDown = _ChatCooldownManager()
        self.__idGen = SequenceIDGenerator()
        return

    def clear(self):
        self.__handlers.clear()

    def doAction(self, actionID, args = None, response = False, skipCoolDown = False):
        player = BigWorld.player()
        success, reqID = False, 0
        if player:
            if self.__coolDown.isInProcess(actionID):
                if not skipCoolDown:
                    g_messengerEvents.onServerErrorReceived(createCoolDownError(actionID))
            else:
                if response:
                    reqID = self.__idGen.next()
                player.base.messenger_onActionByClient_chat2(actionID, reqID, args or messageArgs())
                success = True
        else:
            LOG_ERROR('Player is not defined')
        return (success, reqID)

    def onActionReceived(self, actionID, reqID, args):
        handlers = self.__handlers[actionID]
        for handler in handlers:
            try:
                handler((actionID, reqID), args)
            except TypeError:
                LOG_ERROR('Handler has been invoked with error', handler)
                LOG_CURRENT_EXCEPTION()

    def setFilters(self, msgFilterChain):
        self.__msgFilters = msgFilterChain

    def filterInMessage(self, message):
        text = self.__msgFilters.chainIn(message.accountDBID, message.text)
        if not text:
            result = None
        else:
            message.text = text
            result = message
        return result

    def filterOutMessage(self, text, limits):
        return self.__msgFilters.chainOut(text, limits)

    def setActionCoolDown(self, actionID, coolDown):
        self.__coolDown.process(actionID, coolDown)

    def isActionInCoolDown(self, actionID):
        return self.__coolDown.isInProcess(actionID)

    def getActionCoolDown(self, actionID):
        return self.__coolDown.getTime(actionID)

    def clearActionCoolDown(self, actionID):
        self.__coolDown.reset(actionID)

    def registerHandler(self, actionID, handler):
        handlers = self.__handlers[actionID]
        if handler in handlers:
            LOG_WARNING('Handler already is exist', actionID, handler)
        else:
            if not hasattr(handler, '__self__') or not isinstance(handler.__self__, ActionsHandler):
                LOG_ERROR('Class of handler is not subclass of ActionsHandler', handler)
                return
            if callable(handler):
                handlers.add(handler)
            else:
                LOG_ERROR('Handler is invalid', handler)

    def unregisterHandler(self, actionID, handler):
        handlers = self.__handlers[actionID]
        if handler in handlers:
            handlers.remove(handler)


class ActionsHandler(object):

    def __init__(self, provider):
        super(ActionsHandler, self).__init__()
        self.__provider = weakref.ref(provider)

    def clear(self):
        self._provider = lambda : None

    def provider(self):
        return self.__provider()

    def registerHandlers(self):
        raise NotImplementedError

    def unregisterHandlers(self):
        raise NotImplementedError


class ResponseHandler(ActionsHandler):

    def pushRq(self, reqID, value = None):
        raise NotImplementedError

    def popRq(self, reqID):
        raise NotImplementedError

    def registerHandlers(self):
        register = self.provider().registerHandler
        register(_ACTIONS.RESPONSE_FAILURE, self._onResponseFailure)
        register(_ACTIONS.RESPONSE_SUCCESS, self._onResponseSuccess)

    def unregisterHandlers(self):
        unregister = self.provider().unregisterHandler
        unregister(_ACTIONS.RESPONSE_FAILURE, self._onResponseFailure)
        unregister(_ACTIONS.RESPONSE_SUCCESS, self._onResponseSuccess)

    def _onResponseFailure(self, ids, _):
        return self.popRq(ids[1])

    def _onResponseSuccess(self, ids, _):
        return self.popRq(ids[1])


class ResponseSeqHandler(ResponseHandler):

    def __init__(self, provider, maxRqs):
        super(ResponseHandler, self).__init__(provider)
        self._reqIDs = deque([], maxRqs)

    def clear(self):
        self._reqIDs.clear()
        super(ResponseHandler, self).clear()

    def pushRq(self, reqID, value = None):
        self._reqIDs.append(reqID)

    def popRq(self, reqID):
        result = False
        if reqID in self._reqIDs:
            self._reqIDs.remove(reqID)
            result = True
        return result


class ResponseDictHandler(ResponseHandler):

    def __init__(self, provider):
        super(ResponseHandler, self).__init__(provider)
        self._reqIDs = {}

    def clear(self):
        self._reqIDs.clear()
        super(ResponseHandler, self).clear()

    def pushRq(self, reqID, value = None):
        self._reqIDs[reqID] = value

    def popRq(self, reqID):
        result = None
        if reqID in self._reqIDs:
            result = self._reqIDs.pop(reqID)
        return result

    def excludeRqsByValue(self, value):
        result = False
        if value in self._reqIDs.values():
            result = True
            self._reqIDs = dict(filter(lambda item: item[1] != value, self._reqIDs.iteritems()))
        return result
