# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/battle_control/controllers/notification_manager.py
import logging
from collections import namedtuple
import BigWorld
from enum import IntEnum
logger = logging.getLogger(__name__)

class INotificationManagerListener(object):

    def addNotificationManager(self, notificationManager):
        pass


NotificationObj = namedtuple('NotificationObj', ['typeIdx', 'messageVO'])

class NotificationType(IntEnum):
    respActivatedMsg = 0
    respFinishedMsg = 1
    respNotAvailableMsg = 2
    allyInBattleMsg = 3
    stayInCoverMsg = 4
    pickUpSphereMsg = 5
    allyRespawnedMessage = 6
    respNotAvailableSoonMsg = 7


allNotificationTypes = (NotificationType.respActivatedMsg,
 NotificationType.respFinishedMsg,
 NotificationType.respNotAvailableMsg,
 NotificationType.allyInBattleMsg,
 NotificationType.stayInCoverMsg,
 NotificationType.pickUpSphereMsg,
 NotificationType.allyRespawnedMessage,
 NotificationType.respNotAvailableSoonMsg)
DeleteMsgTypeMapping = {NotificationType.respActivatedMsg: allNotificationTypes,
 NotificationType.stayInCoverMsg: allNotificationTypes,
 NotificationType.allyInBattleMsg: (NotificationType.allyInBattleMsg, NotificationType.respActivatedMsg, NotificationType.stayInCoverMsg),
 NotificationType.respFinishedMsg: (NotificationType.respActivatedMsg, NotificationType.allyInBattleMsg),
 NotificationType.allyRespawnedMessage: (NotificationType.stayInCoverMsg, NotificationType.allyInBattleMsg),
 NotificationType.respNotAvailableMsg: (NotificationType.respActivatedMsg,
                                        NotificationType.stayInCoverMsg,
                                        NotificationType.allyInBattleMsg,
                                        NotificationType.respNotAvailableSoonMsg)}

class MessageType(object):
    NONE = 0
    UPGRADE = 1
    RESPAWN = 2


class NotificationManager(object):
    RESPAWN_FAST_SHOW_TIME = 2
    RESPAWN_ADDITIONAL_DELAY = 2

    def __init__(self):
        self.__upgradeHandler = None
        self.__isUpgradeVisible = False
        self.__isUpgradeVisibilityUpdated = True
        self.__respawnHandler = None
        self.__respawnQueue = []
        self._messageQueue = []
        self.currCallback = None
        self.currMessageType = MessageType.NONE
        self.__curMsg = None
        self.__curStateMsg = None
        self.__upgradeHidingTime = 0
        return

    def fini(self):
        if self.currCallback:
            BigWorld.cancelCallback(self.currCallback)
            self.currCallback = None
        self.__upgradeHandler = None
        self.__isUpgradeVisible = False
        self.__isUpgradeVisibilityUpdated = True
        self.__respawnHandler = None
        self.__respawnQueue = []
        self._messageQueue = []
        self.__curMsg = None
        self.__upgradeHidingTime = 0
        return

    def addRespawnPanelHandler(self, handler):
        self.__respawnHandler = handler

    def addRespawnMessage(self, idx, message):
        self.addMessageToQueues(idx, message)
        if self.currMessageType == MessageType.NONE:
            self.update()

    def addMessageToQueues(self, idx, message):
        newMsg = NotificationObj(idx, message)
        if idx in (NotificationType.allyInBattleMsg, NotificationType.stayInCoverMsg, NotificationType.allyRespawnedMessage):
            self.__curStateMsg = NotificationObj(idx, message.copy()) if idx is not NotificationType.allyRespawnedMessage else None
        deleteMsgTypes = DeleteMsgTypeMapping.get(idx)
        if deleteMsgTypes:
            for msg in self._messageQueue:
                if msg.typeIdx in deleteMsgTypes:
                    self._messageQueue.remove(msg)

            for msg in self.__respawnQueue:
                if msg.typeIdx in deleteMsgTypes:
                    self.__respawnQueue.remove(msg)

            if self.__curMsg and self.__curMsg.typeIdx in deleteMsgTypes:
                if self.__curMsg.typeIdx == NotificationType.allyInBattleMsg and newMsg.typeIdx == NotificationType.allyInBattleMsg:
                    if not self.__respawnQueue:
                        self.currMessageType = MessageType.NONE
                else:
                    self.stopRespawnMessage()
        self._messageQueue.append(newMsg)
        return

    def clearQueue(self):
        self._messageQueue = []
        self.__respawnQueue = []
        if self.__curMsg:
            self.stopRespawnMessage()

    def stopRespawnMessage(self):
        if self.currCallback:
            BigWorld.cancelCallback(self.currCallback)
            self.currCallback = None
        if self.__respawnHandler:
            self.__respawnHandler(None)
        if not self.__respawnQueue:
            self.currMessageType = MessageType.NONE
        self.__curMsg = None
        return

    def addUpgradePanelHandler(self, handler):
        self.__upgradeHandler = handler

    def setUpgradeVisibility(self, isVisible):
        if isVisible != self.__isUpgradeVisible:
            self.__isUpgradeVisibilityUpdated = False
            if not isVisible:
                self.__upgradeHidingTime = BigWorld.serverTime()
        self.__isUpgradeVisible = isVisible
        if not self.__isUpgradeVisibilityUpdated:
            self.update(byUpgrade=True)

    def __checkUpgrade(self):
        if not self.__isUpgradeVisibilityUpdated:
            self.__upgradeHandler(addToManager=False)
            self.__isUpgradeVisibilityUpdated = True
            if self.__isUpgradeVisible:
                self.currMessageType = MessageType.UPGRADE
                return
            self.currMessageType = MessageType.NONE

    def __checkRespawn(self):
        if self.currCallback:
            BigWorld.cancelCallback(self.currCallback)
            self.currCallback = None
        if self.__curStateMsg and self.__curStateMsg.typeIdx not in [ msg.typeIdx for msg in self.__respawnQueue ]:
            self.__respawnQueue.insert(0, NotificationObj(self.__curStateMsg.typeIdx, self.__curStateMsg.messageVO.copy()))
        if self.__respawnQueue:
            msg = self.__getValidRespawnMessage()
            if not msg:
                self.currMessageType = MessageType.NONE
                return
            msg.messageVO['delay'] = max(msg.messageVO['delay'], self.__upgradeHideTimeout)
            if msg.typeIdx in (NotificationType.respActivatedMsg, NotificationType.stayInCoverMsg, NotificationType.allyInBattleMsg):
                msg.messageVO['time'] = max(0, msg.messageVO['showBefore'] - msg.messageVO.get('delay') - BigWorld.serverTime())
            elif self.__isUpgradeVisible:
                msg.messageVO['time'] = self.RESPAWN_FAST_SHOW_TIME
            showTime = msg.messageVO.get('time') + msg.messageVO.get('delay')
            msg.messageVO.pop('showBefore')
            sendAgain = not self.__curMsg or not (self.__curMsg.typeIdx == NotificationType.allyInBattleMsg and msg.typeIdx == NotificationType.allyInBattleMsg)
            self.__respawnHandler(msg.messageVO, sendAgain)
            self.currCallback = BigWorld.callback(showTime, self.update)
            self.currMessageType = MessageType.RESPAWN
            self.__curMsg = msg
            return
        else:
            self.stopRespawnMessage()
            return

    def __updateCurMessageTimer(self):
        self.stopRespawnMessage()
        self.update()

    def update(self, byUpgrade=False):
        if not self.__isUpgradeVisible:
            self.__respawnQueue.extend(self._messageQueue)
            self._messageQueue = []
        if self.currMessageType != MessageType.RESPAWN:
            self.__checkUpgrade()
            if self.currMessageType == MessageType.NONE:
                self.__checkRespawn()
                return
        elif not byUpgrade:
            self.__checkRespawn()
            if self.currMessageType == MessageType.NONE:
                self.__checkUpgrade()
                return
        elif self.__isUpgradeVisible and not self.__isUpgradeVisibilityUpdated:
            self.__updateCurMessageTimer()

    def __getValidRespawnMessage(self):
        msg = self.__respawnQueue.pop(0)
        while BigWorld.serverTime() > msg.messageVO['showBefore']:
            if self.__respawnQueue:
                msg = self.__respawnQueue.pop(0)
            msg = None
            break

        return msg

    @property
    def __upgradeHideTimeout(self):
        return max(0, self.RESPAWN_ADDITIONAL_DELAY - (BigWorld.serverTime() - self.__upgradeHidingTime))
