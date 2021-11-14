# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/proto/bw_chat2/chat_handlers.py
import logging
import operator
import weakref
from collections import namedtuple
import BigWorld
import BattleReplay
from account_helpers.settings_core.settings_constants import BattleCommStorageKeys
from chat_commands_consts import INVALID_VEHICLE_POSITION
from constants import PREBATTLE_TYPE, ARENA_BONUS_TYPE
from gui import GUI_SETTINGS
from helpers import dependency
from messenger.m_constants import BATTLE_CHANNEL, MESSENGER_SCOPE, USER_TAG, UserEntityScope
from messenger.proto.bw_chat2 import admin_chat_cmd, entities, limits, wrappers, errors
from messenger.proto.bw_chat2 import provider as bw2_provider
from messenger.proto.bw_chat2.battle_chat_cmd import BattleCommandFactory
from messenger.proto.bw_chat2.unit_chat_cmd import UnitCommandFactory
from messenger.proto.events import g_messengerEvents
from messenger.proto.interfaces import IBattleCommandFactory
from messenger.storage import storage_getter
from messenger_common_chat2 import BATTLE_CHAT_COMMANDS, UNIT_CHAT_COMMANDS, getCooldownGameModeDataForGameMode
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from messenger_common_chat2 import MESSENGER_LIMITS as _LIMITS
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from uilogging.deprecated.decorators import loggerTarget, loggerEntry, simpleLog
from uilogging.deprecated.ibc.constants import IBC_LOG_KEYS
from uilogging.deprecated.ibc.loggers import IBCLogger
_ActionsCollection = namedtuple('_ActionsCollection', 'initID deInitID onBroadcastID broadcastID')
_logger = logging.getLogger(__name__)

class _EntityChatHandler(bw2_provider.ResponseSeqHandler):

    def __init__(self, provider, adminChat, actions, factory, limits_):
        super(_EntityChatHandler, self).__init__(provider, 10)
        self.__isInited = False
        self.__isEnabled = False
        self.__messagesQueue = []
        self.__adminChat = weakref.proxy(adminChat)
        self.__actions = actions
        self.__factory = factory
        self.__limits = limits_
        self.__msgFilters = None
        return

    @storage_getter('channels')
    def channelsStorage(self):
        return None

    @storage_getter('users')
    def usersStorage(self):
        return None

    def isInited(self):
        return self.__isInited

    def clear(self):
        self.__isInited = False
        self.__isEnabled = False
        self.__messagesQueue = []
        self.__adminChat = None
        super(_EntityChatHandler, self).clear()
        return

    def leave(self):
        self._reqIDs.clear()
        self.__isInited = False

    def disconnect(self):
        self.__isEnabled = False
        self.__messagesQueue = []
        self.leave()

    def addHistory(self):
        pass

    def registerHandlers(self):
        register = self.provider().registerHandler
        register(self.__actions.initID, self._onEntityChatInit)
        register(self.__actions.deInitID, self._onEntityChatDeInit)
        register(self.__actions.onBroadcastID, self._onMessageBroadcast)
        g_messengerEvents.users.onUsersListReceived += self.__me_onUsersListReceived
        super(_EntityChatHandler, self).registerHandlers()

    def unregisterHandlers(self):
        unregister = self.provider().unregisterHandler
        unregister(self.__actions.initID, self._onEntityChatInit)
        unregister(self.__actions.deInitID, self._onEntityChatDeInit)
        unregister(self.__actions.onBroadcastID, self._onMessageBroadcast)
        g_messengerEvents.users.onUsersListReceived -= self.__me_onUsersListReceived
        super(_EntityChatHandler, self).unregisterHandlers()

    def broadcast(self, text, *args):
        if self.__isInited:
            provider = self.provider()
            text = provider.filterOutMessage(text, self.__limits)
            if not text:
                return
            result, cmd = self.__adminChat.parseLine(text)
            if result:
                if cmd:
                    cmd.setClientID(self._getClientIDForCommand())
                return
            actionID = self.__actions.broadcastID
            success, reqID = provider.doAction(actionID, self.__factory.broadcastArgs(text, *args), True)
            if reqID:
                self.pushRq(reqID)
            if success:
                cooldown = self.__limits.getBroadcastCoolDown()
                provider.setActionCoolDown(actionID, cooldown)
        else:
            _logger.warning('TODO: Adds error message')

    def isBroadcastInCooldown(self):
        return self.provider().isActionInCoolDown(self.__actions.broadcastID)

    def _doInit(self, args):
        raise NotImplementedError

    def _addHistory(self, iterator):
        for message in iterator:
            self._addMessage(message)

    def _getChannel(self, message):
        raise NotImplementedError

    def _getClientIDForCommand(self):
        raise NotImplementedError

    def _addChannel(self, channel):
        if not self.channelsStorage.addChannel(channel):
            return self.channelsStorage.getChannel(channel)
        g_messengerEvents.channels.onChannelInited(channel)
        return channel

    def _removeChannel(self, channel):
        if channel and self.channelsStorage.removeChannel(channel, clear=False):
            g_messengerEvents.channels.onChannelDestroyed(channel)
            channel.clear()
        return None

    def _addMessage(self, message):
        message = self._preprocessMessage(message)
        if message is not None:
            g_messengerEvents.channels.onMessageReceived(message, self._getChannel(message))
        return

    def _preprocessMessage(self, message):
        self._preprocessMessageVO(message)
        message = self.provider().filterInMessage(message)
        if message:
            user = self._getUser(message)
            if not (user and user.isIgnored()):
                return message
        return None

    def _getUser(self, message):
        raise NotImplementedError

    def _onEntityChatInit(self, _, args):
        if self.__isInited:
            if not BattleReplay.g_replayCtrl.isPlaying:
                _logger.warning('EntityChat already is inited %r', self.__class__.__name__)
            return
        self.__isInited = True
        self._doInit(dict(args))
        history = self.__factory.historyIter(args)
        if self.__isEnabled:
            self._addHistory(history)
        else:
            self.__messagesQueue.extend(list(history))

    def _onEntityChatDeInit(self, _, args):
        self.leave()

    def _onMessageBroadcast(self, _, args):
        message = self.__factory.messageVO(args)
        if self.__isEnabled:
            self._addMessage(message)
        else:
            self.__messagesQueue.append(message)

    def _onResponseFailure(self, ids, args):
        if super(_EntityChatHandler, self)._onResponseFailure(ids, args):
            error = errors.createBroadcastError(args, self.__actions.broadcastID)
            if error:
                g_messengerEvents.onErrorReceived(error)

    def _preprocessMessageVO(self, message):
        pass

    def __me_onUsersListReceived(self, tags):
        if USER_TAG.IGNORED not in tags:
            return
        self.__isEnabled = True
        while self.__messagesQueue:
            self._addMessage(self.__messagesQueue.pop(0))


class ArenaChatHandler(_EntityChatHandler):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, provider, adminChat):
        super(ArenaChatHandler, self).__init__(provider, adminChat, _ActionsCollection(_ACTIONS.INIT_BATTLE_CHAT, _ACTIONS.DEINIT_BATTLE_CHAT, _ACTIONS.ON_BATTLE_MESSAGE_BROADCAST, _ACTIONS.BROADCAST_BATTLE_MESSAGE), wrappers.ArenaDataFactory(), limits.ArenaLimits())
        self.__teamChannel = None
        self.__commonChannel = None
        return

    def getTeamChannel(self):
        return self.__teamChannel

    def getCommonChannel(self):
        return self.__commonChannel

    def leave(self):
        self.__doRemoveChannels()
        super(ArenaChatHandler, self).leave()

    def clear(self):
        self.__doRemoveChannels()
        super(ArenaChatHandler, self).clear()

    def _doInit(self, args):
        self.__teamChannel = self._addChannel(entities.BWBattleChannelEntity(BATTLE_CHANNEL.TEAM))
        self.__commonChannel = self._addChannel(entities.BWBattleChannelEntity(BATTLE_CHANNEL.COMMON))

    def _getChannel(self, message):
        if message.isCommonChannel:
            channel = self.__commonChannel
        else:
            channel = self.__teamChannel
        return channel

    def _getClientIDForCommand(self):
        return self.__teamChannel.getClientID() if self.__teamChannel else 0

    def _getUser(self, message):
        return self.usersStorage.getUser(message.avatarSessionID, scope=UserEntityScope.BATTLE)

    def _preprocessMessageVO(self, message):
        message.avatarSessionID = self.__sessionProvider.getArenaDP().getSessionIDByVehID(message.vehicleID)

    def __doRemoveChannels(self):
        self.__teamChannel = self._removeChannel(self.__teamChannel)
        self.__commonChannel = self._removeChannel(self.__commonChannel)


class UnitChatHandler(_EntityChatHandler):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, provider, adminChat):
        super(UnitChatHandler, self).__init__(provider, adminChat, _ActionsCollection(_ACTIONS.INIT_UNIT_CHAT, _ACTIONS.DEINIT_UNIT_CHAT, _ACTIONS.ON_UNIT_MESSAGE_BROADCAST, _ACTIONS.BROADCAST_UNIT_MESSAGE), wrappers.UnitDataFactory(), limits.UnitLimits())
        self.__channel = None
        self.__history = None
        self.__factory = UnitCommandFactory()
        return

    def registerHandlers(self):
        register = self.provider().registerHandler
        for command in UNIT_CHAT_COMMANDS:
            register(command.id, self.__onCommandReceived)

        super(UnitChatHandler, self).registerHandlers()

    def unregisterHandlers(self):
        unregister = self.provider().unregisterHandler
        for command in UNIT_CHAT_COMMANDS:
            unregister(command.id, self.__onCommandReceived)

        super(UnitChatHandler, self).unregisterHandlers()

    def getUnitChannel(self):
        return self.__channel

    def addHistory(self):
        if self.__history:
            self._addHistory(self.__history)

    def leave(self):
        self.__doRemoveChannel()
        self.__history = None
        super(UnitChatHandler, self).leave()
        return

    def clear(self):
        self.__doRemoveChannel()
        super(UnitChatHandler, self).clear()

    def send(self, decorator):
        command = decorator.getCommand()
        if command:
            provider = self.provider()
            success, reqID = provider.doAction(command.id, decorator.getProtoData(), True, True)
            if success:
                if reqID:
                    self.pushRq(reqID, command)
                provider.setActionCoolDown(command.id, command.cooldownPeriod)
        else:
            _logger.error('Unit command not found %s', decorator.getCommandText())

    def createByMapPos(self, x, y):
        return self.__factory.createByMapPos(x, y)

    def _doInit(self, args):
        if 'int32Arg1' in args:
            self.__doCreateChannel(args['int32Arg1'])
        else:
            _logger.error('Type of prebattle is not defined %r', args)

    def _addHistory(self, iterator):
        if self.__history is None:
            self.__history = iterator
            if self.__channel is not None:
                messages = []
                for message in iterator:
                    message = self._preprocessMessage(message)
                    if message is not None:
                        messages.append(message)

                g_messengerEvents.channels.onHistoryReceived(sorted(messages, key=operator.attrgetter('sentAt')), self.__channel)
        else:
            super(UnitChatHandler, self)._addHistory(iterator)
        return

    def _getChannel(self, message):
        return self.__channel

    def _getClientIDForCommand(self):
        return self.__channel.getClientID() if self.__channel else 0

    def _getUser(self, message):
        battleUser = self.usersStorage.getUser(message.avatarSessionID, scope=UserEntityScope.BATTLE)
        return battleUser if battleUser is not None else self.usersStorage.getUser(message.accountDBID)

    def _onMessageBroadcast(self, _, args):
        self.addHistory()
        super(UnitChatHandler, self)._onMessageBroadcast(_, args)

    def _preprocessMessageVO(self, message):
        arenaDP = self.__sessionProvider.getArenaDP()
        if arenaDP is not None:
            vInfo = arenaDP.getVehicleInfo(arenaDP.getVehIDByAccDBID(message.accountDBID))
            message.avatarSessionID = vInfo.player.avatarSessionID
        return

    def __doCreateChannel(self, prbType):
        if self.__channel:
            return
        else:
            settings = None
            if prbType in PREBATTLE_TYPE.SQUAD_PREBATTLES:
                settings = BATTLE_CHANNEL.SQUAD
            self.__channel = self._addChannel(entities.BWUnitChannelEntity(settings, prbType))
            return

    def __doRemoveChannel(self):
        self.__channel = self._removeChannel(self.__channel)

    def __onCommandReceived(self, ids, args):
        if not self.__channel:
            return
        actionID, _ = ids
        cmd = self.__factory.createByAction(actionID, args)
        cmd.setClientID(self.__channel.getClientID())
        g_messengerEvents.channels.onCommandReceived(cmd)


_MUTE_CHAT_COMMAND_AND_SENDER_DURATION = 15
_EPIC_MINIMAP_ZOOM_MODE_SCALE = 500

@loggerTarget(logKey=IBC_LOG_KEYS.IBC_CALLOUT_PANEL, loggerCls=IBCLogger)
class BattleChatCommandHandler(bw2_provider.ResponseDictHandler, IBattleCommandFactory):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, provider):
        super(BattleChatCommandHandler, self).__init__(provider)
        self.__factory = BattleCommandFactory()
        self.__targetIDs = []
        self.__receivedChatCommands = {}
        self.__isEnabled = True

    @property
    def factory(self):
        return self.__factory

    def clear(self):
        self.__factory = None
        self.__targetIDs = []
        self.__receivedChatCommands = None
        super(BattleChatCommandHandler, self).clear()
        return

    @loggerEntry
    def switch(self, scope):
        self.__targetIDs = []
        if scope != MESSENGER_SCOPE.BATTLE:
            return
        else:
            arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
            if arena is not None:
                arena.onVehicleKilled += self.__onVehicleKilled
                self.__isEnabled = self.__settingsCore.getSetting(BattleCommStorageKeys.ENABLE_BATTLE_COMMUNICATION)
            return

    @simpleLog(argsIndex=0, preProcessAction=lambda x: x.getCommand().name, resetTime=False)
    def send(self, decorator):
        command = decorator.getCommand()
        if command:
            provider = self.provider()
            success, reqID = provider.doAction(command.id, decorator.getProtoData(), True, not GUI_SETTINGS.isBattleCmdCoolDownVisible)
            if reqID:
                self.pushRq(reqID, command)
            if success:
                if decorator.isEnemyTarget():
                    self.__targetIDs.append(decorator.getTargetID())
                if _ACTIONS.isBattleChatAction(command.id):
                    cooldownConfig = getCooldownGameModeDataForGameMode(self.__sessionProvider.arenaVisitor.getArenaBonusType())
                    provider.setBattleActionCoolDown(reqID, command.id, decorator.getTargetID(), cooldownConfig)
                else:
                    provider.setActionCoolDown(command.id, command.cooldownPeriod)
        else:
            _logger.error('Battle command is not found %r', decorator)

    def registerHandlers(self):
        register = self.provider().registerHandler
        for command in BATTLE_CHAT_COMMANDS:
            register(command.id, self.__onCommandReceived)

        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged
        super(BattleChatCommandHandler, self).registerHandlers()

    def unregisterHandlers(self):
        unregister = self.provider().unregisterHandler
        for command in BATTLE_CHAT_COMMANDS:
            unregister(command.id, self.__onCommandReceived)

        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged
        super(BattleChatCommandHandler, self).unregisterHandlers()

    def createByName(self, name):
        return self.__factory.createByName(name)

    def createSPGAimTargetCommand(self, targetID, reloadTime):
        return self.__factory.createSPGAimTargetCommand(targetID, reloadTime)

    def createByNameTarget(self, name, targetID):
        return self.__factory.createByNameTarget(name, targetID)

    def createByPosition(self, position, name, reloadTime=0.0):
        return self.__factory.createByPosition(position, name, reloadTime)

    def createByObjectiveIndex(self, idx, isAtk, actionName):
        return self.__factory.createByObjectiveIndex(idx, isAtk, actionName)

    def createByBaseIndexAndName(self, pointId, commandName, baseName):
        return self.__factory.createByBaseIndexAndName(pointId, commandName, baseName)

    def createByGlobalMsgName(self, actionID, baseName=''):
        return self.__factory.createByGlobalMsgName(actionID, baseName)

    def create4Reload(self, isCassetteClip, timeLeft, quantity):
        return self.__factory.create4Reload(isCassetteClip, timeLeft, quantity)

    def createReplyByName(self, replyID, replyType, replierID):
        return self.__factory.createReplyByName(replyID, replyType, replierID)

    def createCancelReplyByName(self, replyID, replyType, replierID):
        return self.__factory.createCancelReplyByName(replyID, replyType, replierID)

    def createClearChatCommandsFromTarget(self, targetID, targetMarkerType):
        return self.__factory.createClearChatCommandsFromTarget(targetID, targetMarkerType)

    def _onResponseFailure(self, ids, args):
        command = super(BattleChatCommandHandler, self)._onResponseFailure(ids, args)
        if command:
            if _ACTIONS.isBattleChatAction(command.id):
                self.provider().clearBattleActionCoolDown(ids, command.id)
            else:
                self.provider().clearActionCoolDown(command.id)
            error = errors.createBattleCommandError(args, command)
            if error:
                g_messengerEvents.onErrorReceived(error)
            else:
                _logger.warning('Error is not resolved on the client %d, %r', command.getID(), args)

    def __isSilentModeForEpicBattleMode(self, cmd):
        mapsCtrl = self.__sessionProvider.dynamic.maps
        if mapsCtrl.overviewMapScreenVisible:
            return False
        respawnCtrl = self.__sessionProvider.dynamic.respawn
        if respawnCtrl and respawnCtrl.isRespawnVisible():
            return False
        senderSessionID = cmd.getSenderID()
        senderVID = self.__sessionProvider.getArenaDP().getVehIDBySessionID(senderSessionID)

        def isPositionOnMinimap(position):
            if position == INVALID_VEHICLE_POSITION:
                return False
            minimapCenter = mapsCtrl.getMinimapCenterPosition()
            halfMinimapWidth = mapsCtrl.getMinimapZoomMode() * _EPIC_MINIMAP_ZOOM_MODE_SCALE
            return False if not minimapCenter.x - halfMinimapWidth <= position.x <= minimapCenter.x + halfMinimapWidth or not minimapCenter.z - halfMinimapWidth <= position.z <= minimapCenter.z + halfMinimapWidth else True

        shouldBeSilent = False
        if senderVID != BigWorld.player().playerVehicleID:
            senderPos = mapsCtrl.getVehiclePosition(senderVID)
            senderInRange = isPositionOnMinimap(senderPos)
        else:
            senderInRange = True
        if cmd.isVehicleRelatedCommand():
            targetInRange = senderInRange
            if cmd.hasTarget():
                targetPos = mapsCtrl.getVehiclePosition(cmd.getFirstTargetID())
                targetInRange = isPositionOnMinimap(targetPos)
            shouldBeSilent = not (senderInRange or targetInRange)
        elif cmd.isLocationRelatedCommand():
            markingPos = cmd.getMarkedPosition()
            shouldBeSilent = not (senderInRange or isPositionOnMinimap(markingPos))
        elif cmd.isBaseRelatedCommand() or cmd.isMarkedObjective():
            shouldBeSilent = False
        if cmd.isEpicGlobalMessage():
            shouldBeSilent = False
        return shouldBeSilent

    def __isSilentMode(self, cmd):
        arenaDP = self.__sessionProvider.getArenaDP()
        if not cmd.isMuteTypeMessage() or cmd.getSenderID() == '' or arenaDP is None:
            return False
        elif arenaDP.getVehIDBySessionID(cmd.getSenderID()) == arenaDP.getPlayerVehicleID():
            return False
        else:
            silentMode = False
            currTime = BigWorld.time()
            cmdID = cmd.getID()
            key = (cmd.getSenderID(), cmdID)
            if key not in self.__receivedChatCommands:
                self.__receivedChatCommands[key] = currTime + _MUTE_CHAT_COMMAND_AND_SENDER_DURATION
            elif currTime < self.__receivedChatCommands[key]:
                silentMode = True
            else:
                self.__receivedChatCommands[key] = currTime + _MUTE_CHAT_COMMAND_AND_SENDER_DURATION
            return silentMode

    def __onSettingsChanged(self, diff):
        battleCommunicationEnabled = diff.get(BattleCommStorageKeys.ENABLE_BATTLE_COMMUNICATION)
        if not battleCommunicationEnabled:
            return
        self.__isEnabled = bool(battleCommunicationEnabled)

    def __onCommandReceived(self, ids, args):
        actionID, _ = ids
        cmd = self.__factory.createByAction(actionID, args)
        if self.__isEnabled is False:
            return
        else:
            silentMode = self.__isSilentMode(cmd)
            if not silentMode and self.__sessionProvider.arenaVisitor.getArenaBonusType() == ARENA_BONUS_TYPE.EPIC_BATTLE:
                silentMode = self.__isSilentModeForEpicBattleMode(cmd)
            if silentMode:
                cmd.setSilentMode(silentMode)
            if cmd.isIgnored():
                g_mutedMessages[cmd.getFirstTargetID()] = cmd
                _logger.debug("Chat command '%s' is ignored", cmd.getCommandText())
                return
            if cmd.isPrivate() and not (cmd.isReceiver() or cmd.isSender()):
                return
            arenaDP = self.__sessionProvider.getArenaDP()
            if arenaDP is not None:
                if arenaDP.isObserver(arenaDP.getPlayerVehicleID()) and (cmd.isReply() or cmd.isCancelReply() or cmd.isAutoCommit()):
                    return
            g_messengerEvents.channels.onCommandReceived(cmd)
            return

    def __onVehicleKilled(self, victimID, *args):
        provider = self.provider()
        if victimID in self.__targetIDs:
            self.__targetIDs.remove(victimID)
            for actionID in self.__factory.getEnemyTargetCommandsIDs():
                provider.clearActionCoolDown(actionID)


class AdminChatCommandHandler(bw2_provider.ResponseDictHandler):

    def parseLine(self, text, clientID=0):
        cmd, result = None, admin_chat_cmd.parseCommandLine(text)
        if not result:
            return (False, None)
        else:
            if result.hasError():
                g_messengerEvents.onErrorReceived(result.getError())
            else:
                decorator = admin_chat_cmd.makeDecorator(result, clientID)
                if self.send(decorator):
                    cmd = decorator
            return (True, cmd)

    def send(self, decorator):
        provider = self.provider()
        commandID = decorator.getID()
        success, reqID = provider.doAction(commandID, decorator.getProtoData(), True)
        if reqID:
            self.pushRq(reqID, decorator)
        if success:
            provider.setActionCoolDown(commandID, _LIMITS.ADMIN_COMMANDS_FROM_CLIENT_COOLDOWN_SEC)
        return success

    def _onResponseFailure(self, ids, args):
        if super(AdminChatCommandHandler, self)._onResponseFailure(ids, args):
            error = errors.createAdminCommandError(args)
            if error:
                g_messengerEvents.onErrorReceived(error)
            else:
                _logger.warning('Error is not resolved on the client %d, args: %r', ids, args)

    def _onResponseSuccess(self, ids, args):
        cmd = super(AdminChatCommandHandler, self)._onResponseSuccess(ids, args)
        if cmd:
            g_messengerEvents.channels.onCommandReceived(cmd)


g_mutedMessages = {}
