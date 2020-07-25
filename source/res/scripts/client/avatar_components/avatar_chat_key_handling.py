# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/avatar_chat_key_handling.py
import logging
from collections import namedtuple
import BigWorld
from Math import Matrix
import BattleReplay
import CommandMapping
import Flock
from account_helpers.settings_core.settings_constants import BattleCommStorageKeys
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from battleground.location_point_manager import g_locationPointManager
from bootcamp.Bootcamp import g_bootcamp
from chat_commands_consts import getBaseTeamAndIDFromUniqueID, BATTLE_CHAT_COMMAND_NAMES, _COMMAND_NAME_TRANSFORM_MARKER_TYPE, _PERSONAL_MESSAGE_MUTE_DURATION, MarkerType, ONE_SHOT_COMMANDS_TO_REPLIES
from gui import GUI_CTRL_MODE_FLAG
from gui.sounds.epic_sound_constants import EPIC_SOUND
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from messenger.proto.events import g_messengerEvents
from messenger_common_chat2 import BATTLE_CHAT_COMMANDS_BY_NAMES
from messenger_common_chat2 import MESSENGER_ACTION_IDS as _ACTIONS
from skeletons.account_helpers.settings_core import ISettingsCore, ISettingsCache
_DELAY_FOR_OPENING_RADIAL_MENU = 0.2
_PLAY_PING_SOUNDS_FOR_PLAYER_USING_DIRECTION_ONLY = True
_SOUND_OBJECT_NAMES_BY_MARKER_TYPE = {MarkerType.VEHICLE_MARKER_TYPE: 'VehicleMarkerSoundObject_',
 MarkerType.BASE_MARKER_TYPE: 'BaseMakerSoundObject_',
 MarkerType.LOCATION_MARKER_TYPE: 'LocationMakerSoundObject_',
 MarkerType.HEADQUARTER_MARKER_TYPE: 'HeadquarterMarkerSoundObject_'}
_DEFAULT_SOUND_OBJECT_NAME = 'DefaultSoundObject_'
_TARGET_ID_IS_ENEMY_VEHICLE = {BATTLE_CHAT_COMMAND_NAMES.ATTACK_ENEMY, BATTLE_CHAT_COMMAND_NAMES.ATTACKING_ENEMY}
_CHAT_COMMAND_DEFINING_SOS_REPLY = {BATTLE_CHAT_COMMAND_NAMES.HELPME}
_IS_NON_PLAYER_NOTIFICATION = '_npc'
_SKIP_ON_COMMAND_RECEIVED = {BATTLE_CHAT_COMMAND_NAMES.GOING_THERE,
 BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION,
 BATTLE_CHAT_COMMAND_NAMES.SPG_AIM_AREA,
 BATTLE_CHAT_COMMAND_NAMES.CLEAR_CHAT_COMMANDS}
CommandNotificationData = namedtuple('CommandNotificationData', 'matrixProvider, soundObjectName, targetID')
_logger = logging.getLogger(__name__)

class AvatarChatKeyHandling(object):
    settingsCore = dependency.descriptor(ISettingsCore)
    settingsCache = dependency.descriptor(ISettingsCache)

    def __init__(self):
        self.__isEnabled = None
        self.__callbackDelayer = CallbackDelayer()
        self.__arePrivateVoiceOverBlocked = False
        self.__customSoundHandler = {BATTLE_CHAT_COMMAND_NAMES.CANCEL_REPLY: self.__onCommandReceivedCancelReply,
         BATTLE_CHAT_COMMAND_NAMES.REPLY: self.__onCommandReceivedReply,
         BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY: self.__onCommandReceivedSupportingAlly}
        self.__customSoundHandlerReply = {BATTLE_CHAT_COMMAND_NAMES.ATTENTION_TO_POSITION: self.__onCommandReceivedAttentionToPositionReply}
        self.__customMatrixProviderGetter = {MarkerType.VEHICLE_MARKER_TYPE: self.__getVehicleMatrixProvider,
         MarkerType.BASE_MARKER_TYPE: self.__getBaseMatrixProvider,
         MarkerType.HEADQUARTER_MARKER_TYPE: self.__getHQMatrixProvider,
         MarkerType.LOCATION_MARKER_TYPE: self.__getLocationMarkerMatrixProvider}
        return

    def onBecomePlayer(self):
        if g_bootcamp.isRunning() or self.__isBattleRoyale():
            return
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        if not self.settingsCache.settings.isSynced():
            self.settingsCache.onSyncCompleted += self.__onSettingsReady
        else:
            self.__isEnabled = bool(self.settingsCore.getSetting(BattleCommStorageKeys.ENABLE_BATTLE_COMMUNICATION))
        if not self.__isEnabled:
            return
        self.__activateHandling()

    def onBecomeNonPlayer(self):
        if g_bootcamp.isRunning() or self.__isBattleRoyale():
            return
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.settingsCache.onSyncCompleted -= self.__onSettingsReady
        if not self.__isEnabled:
            return
        self.__deactivateHandling()

    def handleKey(self, isDown, key, mods):
        if not self.__isEnabled or self.guiSessionProvider.shared.calloutCtrl is None or BattleReplay.g_replayCtrl.isPlaying:
            return False
        cmdMap = CommandMapping.g_instance
        if cmdMap.isFiredList((CommandMapping.CMD_CHAT_SHORTCUT_THANKYOU,
         CommandMapping.CMD_CHAT_SHORTCUT_BACKTOBASE,
         CommandMapping.CMD_CHAT_SHORTCUT_HELPME,
         CommandMapping.CMD_CHAT_SHORTCUT_RELOAD), key) and self.isVehicleAlive and isDown:
            self.guiSessionProvider.handleContexChatCommand(key)
            return True
        isGuiControlOn = not self.getForcedGuiControlModeFlags() & GUI_CTRL_MODE_FLAG.CURSOR_VISIBLE
        if cmdMap.isFired(CommandMapping.CMD_CHAT_SHORTCUT_CONTEXT_COMMIT, key) and self.isVehicleAlive and isDown and isGuiControlOn:
            self.guiSessionProvider.handleContexChatCommand(key)
            return True
        else:
            return self.guiSessionProvider.shared.calloutCtrl.handleCalloutAndRadialMenuKeyPress(key, isDown)

    def __isBattleRoyale(self):
        return ARENA_BONUS_TYPE_CAPS.checkAny(self.arena.bonusType, ARENA_BONUS_TYPE_CAPS.BATTLEROYALE)

    def __activateHandling(self):
        ctrl = self.guiSessionProvider.shared.feedback
        if ctrl:
            ctrl.onReplyFeedbackReceived += self.__onReplyFeedbackReceived
            ctrl.onStaticMarkerAdded += self.__onStaticMarkerAdded
        g_messengerEvents.channels.onCommandReceived += self.__onCommandReceived

    def __deactivateHandling(self):
        ctrl = self.guiSessionProvider.shared.feedback
        if ctrl:
            ctrl.onReplyFeedbackReceived -= self.__onReplyFeedbackReceived
            ctrl.onStaticMarkerAdded -= self.__onStaticMarkerAdded
        g_messengerEvents.channels.onCommandReceived -= self.__onCommandReceived
        self.__callbackDelayer.destroy()

    def __onSettingsChanged(self, diff):
        _logger.debug('Settings has changed, checking the battle communication.')
        isEnabled = diff.get(BattleCommStorageKeys.ENABLE_BATTLE_COMMUNICATION)
        if isEnabled is None or isEnabled == self.__isEnabled:
            return
        else:
            if isEnabled is True:
                self.__activateHandling()
            else:
                self.__deactivateHandling()
            self.__isEnabled = isEnabled
            return

    def __onPrivateVoiceOverBlockedReset(self):
        self.__arePrivateVoiceOverBlocked = False

    def __getAdvancedChatCommandData(self, targetID, markerType):
        advChatCmp = getattr(self.guiSessionProvider.arenaVisitor.getComponentSystem(), 'advancedChatComponent', None)
        if advChatCmp is None:
            return
        else:
            advChatCmdData = advChatCmp.getCommandDataForTargetIDAndMarkerType(targetID, markerType)
            return advChatCmdData

    def __getMatrixProvider(self, position):
        matrixProvider = Matrix()
        matrixProvider.translation = position
        return matrixProvider

    def __getVehicleIDForCmdSender(self, cmd):
        arenaDP = self.guiSessionProvider.getCtx().getArenaDP()
        if arenaDP is None:
            return
        else:
            cmdSenderVehicleID = self.guiSessionProvider.getArenaDP().getVehIDBySessionID(cmd.getSenderID())
            return cmdSenderVehicleID

    def __getVehicleMatrixProvider(self, cmd, vehicleID=None):
        if vehicleID is None:
            vehicleID = self.__getVehicleIDByCmd(cmd)
        vehicle = BigWorld.entities.get(vehicleID)
        return None if vehicle is None else vehicle.matrix

    def __getObjectivePosition(self, objectID):
        teamId, baseId = getBaseTeamAndIDFromUniqueID(objectID)
        position = self.__getBasePosition(teamId, baseId)
        if position is None:
            position = self.__getControlPointPosition(objectID)
        return position

    def __getBasePosition(self, teamId, baseId):
        for team, position, number in self.guiSessionProvider.arenaVisitor.type.getTeamBasePositionsIterator():
            if team == teamId and number == baseId:
                return position

        return None

    def __getControlPointPosition(self, objectID):
        for position, number in self.guiSessionProvider.arenaVisitor.type.getControlPointsIterator():
            if number == objectID:
                return position

        return None

    def __getBaseMatrixProvider(self, cmd, targetID=None):
        if targetID is None:
            targetID = cmd.getFirstTargetID()
        position = self.__getObjectivePosition(targetID)
        if position is None:
            return
        else:
            matrixProvider = self.__getMatrixProvider(position)
            return matrixProvider

    def __getHQMatrixProvider(self, cmd, destructibleEntityID=None):
        destructibleEntityComp = getattr(self.guiSessionProvider.arenaVisitor.getComponentSystem(), 'destructibleEntityComponent', None)
        if not destructibleEntityComp:
            return
        else:
            if destructibleEntityID is None:
                destructibleEntityID = cmd.getFirstTargetID()
            destructibleObj = destructibleEntityComp.getDestructibleEntity(destructibleEntityID)
            if destructibleObj is None:
                return
            matrixProvider = self.__getMatrixProvider(destructibleObj.position)
            return matrixProvider

    def __getLocationMarkerMatrixProvider(self, cmd, targetID=None):
        if cmd is not None:
            matrixProvider = self.__getMatrixProvider(cmd.getMarkedPosition())
            return matrixProvider
        if targetID is None and cmd is not None:
            targetID = cmd.getFirstTargetID()
        locationPointData = g_locationPointManager.getLocationPointData(targetID)
        if locationPointData is not None:
            matrixProvider = self.__getMatrixProvider(locationPointData.position)
            return matrixProvider
        else:
            return

    def __onCommandReceivedCancelReply(self, commandName, cmd):
        if not cmd.isCancelReply():
            return
        else:
            cmdSenderVehicleID = self.__getVehicleIDForCmdSender(cmd)
            if cmdSenderVehicleID != self.playerVehicleID:
                return
            notification = cmd.getSoundEventName(True)
            self.__playSoundNotification(notification, None, None, None, True, True)
            return

    def __onCommandReceivedReply(self, commandName, cmd):
        replyToActionName = cmd.getCommandData()['strArg1']
        if replyToActionName not in ONE_SHOT_COMMANDS_TO_REPLIES.keys():
            return
        elif replyToActionName in self.__customSoundHandlerReply:
            self.__customSoundHandlerReply[replyToActionName](replyToActionName, cmd)
            return
        else:
            if cmd.hasTarget():
                if not cmd.isSender() and not cmd.isReceiver():
                    return
            repliedToActionID = BATTLE_CHAT_COMMANDS_BY_NAMES[replyToActionName].id
            notificationReply = _ACTIONS.battleChatCommandFromActionID(repliedToActionID).soundNotificationReply
            if notificationReply is None:
                _logger.warning('notificationReply is None for replyToActionName = %s !- Take a look at messenger_common_chat2.py', replyToActionName)
                return
            self.__playSoundNotificationOnCommandReceived(cmd, MarkerType.VEHICLE_MARKER_TYPE, True, notificationReply)
            return

    def __onCommandReceivedSupportingAlly(self, commandName, cmd):
        enableVoice = True
        if cmd.hasTarget() and not cmd.isSender() and not cmd.isReceiver():
            enableVoice = False
        markerType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE.get(commandName, MarkerType.VEHICLE_MARKER_TYPE)
        self.__playSoundNotificationOnCommandReceived(cmd, markerType, True, None, enableVoice)
        return

    def __onCommandReceivedAttentionToPositionReply(self, replyToActionName, cmd):
        repliedToActionID = BATTLE_CHAT_COMMANDS_BY_NAMES[replyToActionName].id
        notificationReply = _ACTIONS.battleChatCommandFromActionID(repliedToActionID).soundNotificationReply
        if notificationReply is None:
            _logger.warning('soundNotificationReply is None for replyToActionName %s! - Take a look at messenger_common_chat2.py', replyToActionName)
            return
        else:
            self.__playSoundNotificationOnCommandReceived(cmd, MarkerType.VEHICLE_MARKER_TYPE, True, notificationReply)
            return

    def __onStaticMarkerAdded(self, areaID, creatorID, position, markerSymbolName, show3DMarker=False, markerText='', numberOfReplies=0, isTargetForPlayer=False):
        originalCmdId = self.__getOriginalCommandID(areaID, MarkerType.LOCATION_MARKER_TYPE)
        if originalCmdId <= 0:
            return
        else:
            command = _ACTIONS.battleChatCommandFromActionID(originalCmdId)
            if not command:
                return
            notification = command.soundNotification
            if notification is None:
                return
            matrixProvider = self.__getMatrixProvider(position)
            sentByPlayer = True if creatorID == self.playerVehicleID else False
            self.__playSoundNotification(notification, None, None, matrixProvider, True, sentByPlayer)
            return

    def __getOriginalCommandID(self, targetID, markerType):
        advancedChatCommandData = self.__getAdvancedChatCommandData(targetID, markerType)
        return None if advancedChatCommandData is None else advancedChatCommandData.command.getID()

    def __onReplyFeedbackReceived(self, targetID, replierID, markerType, oldReplyCount, newReplyCount):
        if oldReplyCount > newReplyCount:
            return
        else:
            advancedChatCommandData = self.__getAdvancedChatCommandData(targetID, markerType)
            if advancedChatCommandData is None or advancedChatCommandData.command is None:
                return
            senderID = self.__getVehicleIDForCmdSender(advancedChatCommandData.command)
            if senderID != self.playerVehicleID:
                if self.playerVehicleID not in advancedChatCommandData.owners:
                    return
            commandID = advancedChatCommandData.command.getID()
            soundNotificationReply = _ACTIONS.battleChatCommandFromActionID(commandID).soundNotificationReply
            if soundNotificationReply is None or markerType not in self.__customMatrixProviderGetter:
                return
            soundObjectName = _SOUND_OBJECT_NAMES_BY_MARKER_TYPE.get(markerType, _DEFAULT_SOUND_OBJECT_NAME)
            soundObjectName += str(targetID)
            matrixProvider = None
            if targetID == self.playerVehicleID:
                matrixProvider = self.__customMatrixProviderGetter[markerType](None, replierID)
            else:
                matrixProvider = self.__customMatrixProviderGetter[markerType](None, targetID)
            enableVoice = True
            if replierID != self.playerVehicleID and targetID != self.playerVehicleID:
                enableVoice = False
            sentByPlayer = True if replierID == self.playerVehicleID else False
            self.__playSoundNotification(soundNotificationReply, None, soundObjectName, matrixProvider, enableVoice, sentByPlayer)
            return

    def __onCommandReceived(self, cmd):
        commandName = _ACTIONS.battleChatCommandFromActionID(cmd.getID()).name
        if commandName in _SKIP_ON_COMMAND_RECEIVED:
            return
        if commandName in self.__customSoundHandler:
            self.__customSoundHandler[commandName](commandName, cmd)
        else:
            markerType = _COMMAND_NAME_TRANSFORM_MARKER_TYPE.get(commandName, MarkerType.VEHICLE_MARKER_TYPE)
            self.__playSoundNotificationOnCommandReceived(cmd, markerType, True)

    def __enableVoices(self, enabled, clearQueue=False):
        if self.soundNotifications:
            self.soundNotifications.enableVoices(enabled, clearQueue)

    def __getVehicleIDByCmd(self, cmd):
        vehicleID = None
        commandName = _ACTIONS.battleChatCommandFromActionID(cmd.getID()).name
        if commandName in _TARGET_ID_IS_ENEMY_VEHICLE:
            vehicleID = cmd.getFirstTargetID()
            return vehicleID
        else:
            if cmd.isReceiver():
                vehicleID = self.__getVehicleIDForCmdSender(cmd)
            elif cmd.isSender():
                vehicleID = self.playerVehicleID
            elif commandName is BATTLE_CHAT_COMMAND_NAMES.SUPPORTING_ALLY:
                vehicleID = cmd.getFirstTargetID()
            else:
                vehicleID = self.__getVehicleIDForCmdSender(cmd)
            return vehicleID

    def __getSoundObjectNameAndMatrixProvider(self, cmd, markerType):
        if markerType not in self.__customMatrixProviderGetter:
            return CommandNotificationData(matrixProvider=None, soundObjectName=None, targetID=None)
        else:
            matrixProvider = self.__customMatrixProviderGetter[markerType](cmd)
            vehicleID = self.__getVehicleIDByCmd(cmd)
            soundObjectName = _SOUND_OBJECT_NAMES_BY_MARKER_TYPE.get(MarkerType.VEHICLE_MARKER_TYPE, _DEFAULT_SOUND_OBJECT_NAME)
            soundObjectName += str(vehicleID)
            return CommandNotificationData(matrixProvider=matrixProvider, soundObjectName=soundObjectName, targetID=vehicleID)

    def __playSoundNotificationOnCommandReceived(self, cmd, markerType, useSoundNotification=False, notificationName=None, enableVoice=True):
        if cmd.isEpicGlobalMessage():
            if self.soundNotifications:
                self.soundNotifications.play(EPIC_SOUND.BF_EB_GLOBAL_MESSAGE)
        else:
            commandNotificationData = self.__getSoundObjectNameAndMatrixProvider(cmd, markerType)
            if notificationName is None:
                notificationName = cmd.getSoundEventName(useSoundNotification)
            if enableVoice is True:
                if cmd.isReceiver():
                    if self.__arePrivateVoiceOverBlocked is False:
                        self.__arePrivateVoiceOverBlocked = True
                        self.__callbackDelayer.delayCallback(_PERSONAL_MESSAGE_MUTE_DURATION, self.__onPrivateVoiceOverBlockedReset)
                    else:
                        enableVoice = False
                        _logger.info('Voice was blocked for the receiver of a private message due to flood prevention system!')
            cmdSenderVehicleID = self.__getVehicleIDForCmdSender(cmd)
            sentByPlayer = True if cmdSenderVehicleID == self.playerVehicleID else False
            self.__playSoundNotification(notificationName, None, commandNotificationData.soundObjectName, commandNotificationData.matrixProvider, enableVoice, sentByPlayer)
        return

    def __resetDebugOutput(self):
        if self.__debugLine is not None:
            if BigWorld.player() is not None:
                BigWorld.player().delModel(self.__debugLine.model)
            del self.__debugLine
            self.__debugLine = None
        return

    def __drawDebugOutput(self, matrixProvider):
        self.__resetDebugOutput()
        if matrixProvider is None:
            return
        else:
            matrixProvider = Matrix(matrixProvider)
            pos = matrixProvider.translation
            endPos = matrixProvider.translation
            endPos.y += 70.0
            self.__debugLine = Flock.DebugLine(pos, endPos)
            self.__debugLine.thickness = 1.0
            matrixProvider.translation = pos
            self.__debugGizmo.setMatrix(matrixProvider)
            self.__callbackDelayer.delayCallback(4.0, self.__resetDebugOutput)
            return

    def __playSoundNotification(self, notification, sndPos=None, soundObjectName=None, matrixProvider=None, enableVoice=True, isSentByPlayer=True):
        if not self.soundNotifications or notification is None:
            return
        else:
            categoryVoiceIsEnabled = self.soundNotifications.isCategoryEnabled('voice')
            if categoryVoiceIsEnabled and enableVoice is False:
                self.__enableVoices(enableVoice)
            if not isSentByPlayer:
                notification += _IS_NON_PLAYER_NOTIFICATION
            elif _PLAY_PING_SOUNDS_FOR_PLAYER_USING_DIRECTION_ONLY:
                matrixProvider = None
            self.soundNotifications.play(notification, None, None, sndPos, soundObjectName, matrixProvider)
            if categoryVoiceIsEnabled and enableVoice is False:
                self.__enableVoices(True)
            return

    def __onSettingsReady(self):
        _logger.debug('Settings are synced, checking the IBC.')
        self.settingsCache.onSyncCompleted -= self.__onSettingsReady
        if self.__isEnabled is None:
            self.__isEnabled = bool(self.settingsCore.getSetting(BattleCommStorageKeys.ENABLE_BATTLE_COMMUNICATION))
            if not self.__isEnabled:
                return
            self.__activateHandling()
        return
