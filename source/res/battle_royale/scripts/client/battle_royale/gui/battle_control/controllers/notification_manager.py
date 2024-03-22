# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/battle_control/controllers/notification_manager.py
import logging
import BigWorld
import typing
from enum import IntEnum
from Event import Event
from helpers.CallbackDelayer import CallbackDelayer
if typing.TYPE_CHECKING:
    from battle_royale.gui.Scaleform.daapi.view.battle.respawn_message_panel import RespawnMessagePanel
logger = logging.getLogger(__name__)

class INotificationManagerListener(object):

    def addNotificationManager(self, notificationManager):
        pass


class RespawnMessage(CallbackDelayer):

    def __init__(self):
        super(RespawnMessage, self).__init__()
        self.msgType = None
        self.messageVO = {}
        self.delay = 0
        self.postDelay = 0
        self.time = 0
        self.showBefore = 0
        self.__endTime = 0
        self.__msgCallbackID = None
        self.__delayCallbackID = None
        self.__postDelayCallbackID = None
        self.__stopCallbackID = None
        self.hideCallback = None
        self.__panel = None
        return

    def setHideCallback(self, hideCallback):
        self.hideCallback = hideCallback

    def sendMessage(self, panel):
        self.__panel = panel
        if self.delay:
            self.__startDelayTimer()
        else:
            self.__onDelayFinished()

    def updateTime(self, newTime):
        if self.time > newTime:
            if self.__stopCallbackID is not None:
                BigWorld.cancelCallback(self.__stopCallbackID)
            self.__stopCallbackID = BigWorld.callback(newTime + self.delay, self.__stopByCallback)
        else:
            self.time = newTime
            self.__endTime = self.time + BigWorld.serverTime()
        return

    def stop(self, skipPostDelay=False):
        if self.__stopCallbackID is not None:
            BigWorld.cancelCallback(self.__stopCallbackID)
            self.__stopCallbackID = None
        if self.__msgCallbackID is not None:
            BigWorld.cancelCallback(self.__msgCallbackID)
            self.__msgCallbackID = None
        if not self.__delayCallbackID and not self.__postDelayCallbackID:
            self.__panel.hideMessage()
        if self.__delayCallbackID or skipPostDelay or not self.postDelay:
            if self.__delayCallbackID is not None:
                BigWorld.cancelCallback(self.__delayCallbackID)
                self.__delayCallbackID = None
            self.__hide()
        else:
            self.__startPostDelayTimer()
        return

    def __hide(self):
        self.__postDelayCallbackID = None
        self.hideCallback()
        return

    @property
    def timeLeft(self):
        return int(self._calculate())

    def __startDelayTimer(self):
        self.__delayCallbackID = BigWorld.callback(self.delay, self.__onDelayFinished)

    def __onDelayFinished(self):
        self.__delayCallbackID = None
        self.__endTime = self.time + BigWorld.serverTime()
        self.time = int(self._calculate())
        self.__panel.sendMessage(self.messageVO)
        self.__setMsgCallback()
        return

    def __setMsgCallback(self):
        self.__msgCallbackID = None
        length = self.__tick()
        if length > 0:
            self.__msgCallbackID = BigWorld.callback(length if length < 1 else 1, self.__setMsgCallback)
        else:
            self.stop()
        return

    def __stopByCallback(self):
        self.__stopCallbackID = None
        self.stop()
        return

    def __startPostDelayTimer(self):
        if not self.__postDelayCallbackID:
            self.__postDelayCallbackID = BigWorld.callback(self.postDelay, self.__hide)

    def _calculate(self):
        return max(0, self.__endTime - BigWorld.serverTime())

    def __tick(self):
        floatLength = self._calculate()
        if not floatLength:
            return 0
        intLength = max(int(floatLength), 0)
        self.__panel.sendMessageTime(intLength)
        return floatLength

    def __repr__(self):
        return 'RespawnMessage(msgType: %s, messageVO: %s, delay: %s, time: %s, showBefore: %s)' % (self.msgType,
         self.messageVO,
         self.delay,
         self.time,
         self.showBefore)

    def __cmp__(self, other):
        return cmp((self.msgType,
         self.messageVO,
         self.delay,
         self.time,
         self.showBefore), (other.msgType,
         other.messageVO,
         other.delay,
         other.time,
         other.showBefore))


class MessageType(IntEnum):
    respActivatedMsg = 0
    respFinishedMsg = 1
    respNotAvailableMsg = 2
    allyInBattleMsg = 3
    stayInCoverMsg = 4
    pickUpSphereMsg = 5
    allyRespawnedMessage = 6
    respNotAvailableSoonMsg = 7
    vehicleDeadMsg = 8


InvalidMessageTypeRange = (MessageType.vehicleDeadMsg,)
allMessageTypes = (MessageType.respActivatedMsg,
 MessageType.respFinishedMsg,
 MessageType.respNotAvailableMsg,
 MessageType.allyInBattleMsg,
 MessageType.stayInCoverMsg,
 MessageType.pickUpSphereMsg,
 MessageType.allyRespawnedMessage,
 MessageType.respNotAvailableSoonMsg)
DeleteMsgTypeMapping = {MessageType.respActivatedMsg: allMessageTypes,
 MessageType.stayInCoverMsg: allMessageTypes,
 MessageType.allyInBattleMsg: (MessageType.allyInBattleMsg, MessageType.respActivatedMsg, MessageType.stayInCoverMsg),
 MessageType.respFinishedMsg: (MessageType.respActivatedMsg, MessageType.allyInBattleMsg),
 MessageType.vehicleDeadMsg: (MessageType.respFinishedMsg,),
 MessageType.allyRespawnedMessage: (MessageType.stayInCoverMsg, MessageType.allyInBattleMsg),
 MessageType.respNotAvailableMsg: (MessageType.stayInCoverMsg, MessageType.allyInBattleMsg, MessageType.respNotAvailableSoonMsg)}

class INotificationHandler(object):

    def __init__(self):
        self.isActive = False

    def tryToProceed(self):
        raise NotImplementedError

    def checkOtherHandlers(self, handlerList):
        pass


class NotificationManager(object):
    RESPAWN_FAST_SHOW_TIME = 2
    RESPAWN_ADDITIONAL_DELAY = 2

    def __init__(self):
        self.upgradeHandler = None
        self.respawnHandler = None
        self._curHandler = None
        self.__needToUpdate = False
        return

    @property
    def handlersList(self):
        return (self.upgradeHandler, self.respawnHandler)

    def fini(self):
        if self.respawnHandler:
            self.respawnHandler.clearAll()
        self.respawnHandler = None
        self.upgradeHandler = None
        self._curHandler = None
        return

    def addRespawnPanel(self, panel):
        self.respawnHandler = RespawnHandler(panel)
        self.respawnHandler.onUpdateNeeded += self.onHandlerRealised

    def addRespawnMessage(self, message):
        self.respawnHandler.addMessage(message)
        self.update()

    def updateHandlersDependencies(self):
        self.respawnHandler.checkOtherHandlers((self.upgradeHandler,))

    def clearQueue(self):
        self.respawnHandler.clearAll()

    def addUpgradePanelHandler(self, handlerMethod):
        self.upgradeHandler = UpgradeHandler(handlerMethod)
        self.upgradeHandler.onUpdateNeeded += self.onHandlerRealised

    def setUpgradeVisibility(self, isVisible):
        self.upgradeHandler.setState(isVisible)
        self.updateHandlersDependencies()
        self.update()

    def update(self):
        if self._curHandler:
            return
        prevUpdateNeeded = self.__needToUpdate
        self.__needToUpdate = False
        for handler in self.handlersList:
            isBusy, alreadyDeactivated = handler.tryToProceed()
            self.__needToUpdate = self.__needToUpdate or alreadyDeactivated
            if isBusy:
                self.setCurrentHandler(handler)
                return

        if prevUpdateNeeded and self.__needToUpdate:
            logger.warning('Something wrong with NotificationManager.update, dont need to do more than 2 calls')
        if self.__needToUpdate:
            self.update()

    def setCurrentHandler(self, handler):
        if self._curHandler == handler:
            logger.warning('curHandler == handler %s', handler)
            return
        self.updateHandlersDependencies()
        self._curHandler = handler

    def onHandlerRealised(self):
        if not self._curHandler:
            logger.warning('Wrong call from handler. There is no active handlers')
            return
        else:
            self._curHandler = None
            self.updateHandlersDependencies()
            self.update()
            return


class UpgradeHandler(INotificationHandler):

    def __init__(self, handleMethod):
        super(UpgradeHandler, self).__init__()
        self.handleMethod = handleMethod
        self.__lastUpdateState = False
        self.__isUpgradeVisible = False
        self.__isUpgradeVisibilityUpdated = True
        self.hideTime = 0
        self.onUpdateNeeded = Event()

    @property
    def isUpgradeVisible(self):
        return self.__isUpgradeVisible

    def setState(self, isVisible):
        self.__isUpgradeVisibilityUpdated = isVisible == self.__lastUpdateState
        self.__isUpgradeVisible = isVisible
        if self.isActive and not self.__isUpgradeVisibilityUpdated:
            self.update()
            if not self.isUpgradeVisible:
                self.isActive = False
                self.onUpdateNeeded()

    def update(self):
        if not self.__isUpgradeVisibilityUpdated:
            self.handleMethod(addToManager=False)
            self.__lastUpdateState = self.isUpgradeVisible
            self.__isUpgradeVisibilityUpdated = True
            if not self.isUpgradeVisible:
                self.hideTime = BigWorld.serverTime()

    def tryToProceed(self):
        if not self.__isUpgradeVisible and self.__isUpgradeVisibilityUpdated:
            return (False, False)
        self.update()
        if self.__isUpgradeVisible:
            self.isActive = True
            return (True, False)
        logger.warning('UpgradeHandler.tryToProceed return False after updateseems like manager change internal state of handler')
        return (False, True)


class RespawnHandler(INotificationHandler):
    RESPAWN_FAST_SHOW_TIME = 2
    RESPAWN_ADDITIONAL_DELAY = 3

    def __init__(self, panel):
        super(RespawnHandler, self).__init__()
        self.panel = panel
        self.isHighPriority = True
        self._highPriorQueue = []
        self._messageQueue = []
        self._curMsg = None
        self.__curStateMsg = None
        self.__upgradeHidingTime = 0
        self.prevActiveState = False
        self.onUpdateNeeded = Event()
        return

    @property
    def hasMessage(self):
        return bool(self._curMsg)

    def checkOtherHandlers(self, handlers):
        for handler in handlers:
            if isinstance(handler, UpgradeHandler):
                if handler.isUpgradeVisible:
                    self.isHighPriority = False
                    self.__upgradeHidingTime = handler.hideTime
                    if self._curMsg and (self._curMsg.timeLeft > self.RESPAWN_FAST_SHOW_TIME or not self._curMsg.timeLeft):
                        self._curMsg.updateTime(self.RESPAWN_FAST_SHOW_TIME)
                    break
        else:
            self.isHighPriority = True
            self.updateQueues()

    def addMessage(self, message):
        self.addMessageToQueues(message)
        if self.isHighPriority:
            self.updateQueues()
        if not self.isHighPriority and len(self._messageQueue) == 1:
            message.delay = self.RESPAWN_ADDITIONAL_DELAY

    def addMessageToQueues(self, newMsg):
        if newMsg.msgType in (MessageType.allyInBattleMsg, MessageType.stayInCoverMsg):
            self.__curStateMsg = newMsg
        elif newMsg.msgType in (MessageType.allyRespawnedMessage, MessageType.respNotAvailableMsg):
            self.__curStateMsg = None
        deleteMsgTypes = DeleteMsgTypeMapping.get(newMsg.msgType)
        addToQueue = True
        if deleteMsgTypes:
            self.__deleteMessageFromQueue(self._highPriorQueue, deleteMsgTypes)
            self.__deleteMessageFromQueue(self._messageQueue, deleteMsgTypes)
            if self._curMsg and self._curMsg.msgType in deleteMsgTypes:
                if self._curMsg.msgType == MessageType.allyInBattleMsg and newMsg.msgType == MessageType.allyInBattleMsg:
                    self._curMsg.updateTime(newMsg.time)
                    addToQueue = False
                else:
                    self._messageQueue.append(newMsg)
                    self._curMsg.stop()
                    return
        if addToQueue:
            self._messageQueue.append(newMsg)
        return

    def updateQueues(self):
        self._highPriorQueue.extend(self._messageQueue)
        self._messageQueue = []

    def tryToProceed(self):
        if not self.hasMessage and not self._highPriorQueue and not self.__curStateMsg:
            return (False, False)
        self.update()
        if self.hasMessage:
            self.isActive = True
            return (True, False)
        return (False, True)

    def update(self):
        if self.__curStateMsg and self.__curStateMsg.msgType not in [ msg.msgType for msg in self._highPriorQueue ] and self.isHighPriority:
            self._highPriorQueue.insert(0, self.__curStateMsg)
        msg = self.__getValidMessage()
        if not msg:
            if self._curMsg:
                logger.warning('_curMsg not empty %s', self._curMsg.msgType)
            self._curMsg = None
            self.__curStateMsg = None
            return
        else:
            msg.delay = max(msg.delay, self.__upgradeHideTimeout)
            if not self.isHighPriority:
                msg.updateTime(self.RESPAWN_FAST_SHOW_TIME)
            elif msg.msgType in (MessageType.respActivatedMsg, MessageType.stayInCoverMsg, MessageType.allyInBattleMsg):
                msg.time = max(0, msg.showBefore - msg.delay - BigWorld.serverTime())
            self.send(msg)
            return

    def send(self, message):
        if message.msgType in InvalidMessageTypeRange:
            logger.warning('try send technical msg %s', message.msgType)
            return
        message.setHideCallback(self.onMessageHide)
        message.sendMessage(self.panel)
        if self._curMsg:
            logger.warning('_curMsg not empty %s', self._curMsg.msgType)
        self._curMsg = message

    def onMessageHide(self):
        self._curMsg = None
        self.update()
        if self.isActive and not self._curMsg:
            self.isActive = False
            self.onUpdateNeeded()
        return

    def clearAll(self):
        self._messageQueue = []
        self._highPriorQueue = []
        self.__curStateMsg = None
        if self._curMsg:
            self._curMsg.stop(skipPostDelay=True)
        return

    def __getValidMessage(self):
        if not self._highPriorQueue:
            return
        else:
            msg = self._highPriorQueue.pop(0)
            while BigWorld.serverTime() > msg.showBefore:
                if self._highPriorQueue:
                    msg = self._highPriorQueue.pop(0)
                msg = None
                break

            return msg

    @staticmethod
    def __deleteMessageFromQueue(queue, deleteMsgTypes):
        for msg in queue:
            if msg.msgType in deleteMsgTypes:
                queue.remove(msg)

    @property
    def __upgradeHideTimeout(self):
        return max(0, self.RESPAWN_ADDITIONAL_DELAY - (BigWorld.serverTime() - self.__upgradeHidingTime))
