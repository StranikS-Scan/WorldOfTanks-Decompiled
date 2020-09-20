# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/bw_chat2/provider.py
import weakref
from collections import defaultdict, deque
import BigWorld
import BattleReplay
from BattleReplay import CallbackDataNames
from chat_commands_consts import CHAT_COMMANDS_THAT_IGNORE_COOLDOWNS
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_CURRENT_EXCEPTION
from gui.shared.rq_cooldown import RequestCooldownManager, REQUEST_SCOPE
from ids_generators import SequenceIDGenerator
from messenger.proto.bw_chat2.errors import createCoolDownError
from messenger.proto.events import g_messengerEvents
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from messenger_common_chat2 import messageArgs, addCoolDowns, areSenderCooldownsActive

class _ChatCooldownManager(RequestCooldownManager):

    def __init__(self):
        super(_ChatCooldownManager, self).__init__(REQUEST_SCOPE.BW_CHAT2)

    def lookupName(self, rqTypeID):
        return _ACTIONS.getActionName(rqTypeID)

    def getDefaultCoolDown(self):
        pass


class BWChatProvider(object):
    __slots__ = ('__weakref__', '__handlers', '__msgFilters', '__coolDown', '__idGen', '__isEnabled', '__queue', '__battleCmdCooldowns')

    def __init__(self):
        super(BWChatProvider, self).__init__()
        self.__handlers = defaultdict(set)
        self.__msgFilters = None
        self.__coolDown = _ChatCooldownManager()
        self.__battleCmdCooldowns = []
        self.__idGen = SequenceIDGenerator()
        self.__isEnabled = False
        self.__queue = []
        return

    def clear(self):
        self.__handlers.clear()
        self.__battleCmdCooldowns = []
        BattleReplay.g_replayCtrl.delDataCallback(CallbackDataNames.BW_CHAT2_REPLAY_ACTION_RECEIVED_CALLBACK, self.__onActionReceivedFromReplay)

    def goToReplay(self):
        BattleReplay.g_replayCtrl.setDataCallback(CallbackDataNames.BW_CHAT2_REPLAY_ACTION_RECEIVED_CALLBACK, self.__onActionReceivedFromReplay)

    def setEnable(self, value):
        if self.__isEnabled == value:
            return
        self.__isEnabled = value
        if self.__isEnabled:
            self.__sendActionsFromQueue()
        else:
            self.__queue = []

    def doAction(self, actionID, args=None, response=False, skipCoolDown=False):
        success, reqID = False, 0
        if self.__isCooldownInProcess(actionID, args):
            if not skipCoolDown:
                g_messengerEvents.onErrorReceived(createCoolDownError(actionID, self.__getCooldownTime(actionID, args)))
        else:
            if response:
                reqID = self.__idGen.next()
            if self.__isEnabled:
                success = self.__sendAction(actionID, reqID, args)
            else:
                success = self.__addActionToQueue(actionID, reqID, args)
        return (success, reqID)

    def onActionReceived(self, actionID, reqID, args):
        if BattleReplay.g_replayCtrl.isRecording and self.__isActionWrittenToReplay(actionID):
            BattleReplay.g_replayCtrl.serializeCallbackData(CallbackDataNames.BW_CHAT2_REPLAY_ACTION_RECEIVED_CALLBACK, (actionID, reqID, args))
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
        text = message.text
        senderDBID = message.accountDBID
        if senderDBID > 0:
            text = self.__msgFilters.chainIn(senderDBID, text)
        else:
            senderAvatarID = message.avatarSessionID
            if senderAvatarID:
                text = self.__msgFilters.chainIn(senderAvatarID, text)
        if not text:
            result = None
        else:
            message.text = text
            result = message
        return result

    def filterOutMessage(self, text, limits):
        return self.__msgFilters.chainOut(text, limits)

    def setActionCoolDown(self, actionID, coolDown, targetID=0, cooldownConfig=None):
        command = _ACTIONS.battleChatCommandFromActionID(actionID)
        if command and cooldownConfig is not None and command.name not in CHAT_COMMANDS_THAT_IGNORE_COOLDOWNS:
            currTime = BigWorld.time()
            addCoolDowns(currTime, self.__battleCmdCooldowns, command.id, command.name, command.cooldownPeriod, targetID, cooldownConfig)
        else:
            self.__coolDown.process(actionID, coolDown)
        return

    def isActionInCoolDown(self, actionID):
        command = _ACTIONS.battleChatCommandFromActionID(actionID)
        if command:
            return [ cdData for cdData in self.__battleCmdCooldowns if cdData.cmdID == actionID ]
        return self.__coolDown.isInProcess(actionID)

    def getActionCooldownData(self, actionID):
        command = _ACTIONS.battleChatCommandFromActionID(actionID)
        if command:
            return [ cdData for cdData in self.__battleCmdCooldowns if cdData.cmdID == actionID ]
        return []

    def clearActionCoolDown(self, actionID):
        command = _ACTIONS.battleChatCommandFromActionID(actionID)
        if command:
            removeList = [ cdData for cdData in self.__battleCmdCooldowns if cdData.cmdID == command.id ]
            if removeList:
                for dataForRemoval in removeList:
                    self.__battleCmdCooldowns.remove(dataForRemoval)

        else:
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

    def __sendAction(self, actionID, reqID, args=None):
        player = BigWorld.player()
        if not player:
            LOG_ERROR('Player is not defined')
            return False
        player.base.messenger_onActionByClient_chat2(actionID, reqID, args or messageArgs())
        return True

    def __addActionToQueue(self, actionID, reqID, args=None):
        self.__queue.append((actionID, reqID, args))
        return True

    def __sendActionsFromQueue(self):
        invokedIDs = set()
        while self.__queue:
            actionID, reqID, args = self.__queue.pop()
            if actionID in invokedIDs:
                LOG_WARNING('Action is ignored, your must send action after event "showGUI" is invoked', actionID, reqID, args)
                continue
            self.__sendAction(actionID, reqID, args)
            invokedIDs.add(actionID)

    @staticmethod
    def __isActionWrittenToReplay(actionID):
        return actionID == _ACTIONS.INIT_BATTLE_CHAT or _ACTIONS.battleChatCommandFromActionID(actionID) is not None

    def __onActionReceivedFromReplay(self, actionID, reqID, args):
        self.onActionReceived(actionID, reqID, args)

    def __isCooldownInProcess(self, actionID, args=None):
        command = _ACTIONS.battleChatCommandFromActionID(actionID)
        if command:
            currTime = BigWorld.time()
            targetID = args['int32Arg1']
            sndrBlockReason = areSenderCooldownsActive(currTime, self.__battleCmdCooldowns, actionID, targetID)
            cdTime = sndrBlockReason.cooldownEnd - currTime if sndrBlockReason is not None else 0
            return command.name not in CHAT_COMMANDS_THAT_IGNORE_COOLDOWNS and sndrBlockReason is not None and cdTime > 0
        else:
            return self.__coolDown.isInProcess(actionID)

    def __getCooldownTime(self, actionID, args=None):
        command = _ACTIONS.battleChatCommandFromActionID(actionID)
        if command:
            currTime = BigWorld.time()
            targetID = args['int32Arg1']
            sndrBlockReason = areSenderCooldownsActive(currTime, self.__battleCmdCooldowns, actionID, targetID)
            cdTime = round(sndrBlockReason.cooldownEnd - currTime, 1) if sndrBlockReason is not None else 0
            return cdTime
        else:
            self.__coolDown.getTime(actionID)
            return


class ActionsHandler(object):

    def __init__(self, provider):
        super(ActionsHandler, self).__init__()
        self.__provider = weakref.ref(provider)

    def clear(self):
        self.__provider = lambda : None

    def provider(self):
        return self.__provider()

    def registerHandlers(self):
        raise NotImplementedError

    def unregisterHandlers(self):
        raise NotImplementedError


class ResponseHandler(ActionsHandler):

    def pushRq(self, reqID, value=None):
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

    def pushRq(self, reqID, value=None):
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

    def pushRq(self, reqID, value=None):
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
            self._reqIDs = dict((item for item in self._reqIDs.iteritems() if item[1] != value))
        return result
