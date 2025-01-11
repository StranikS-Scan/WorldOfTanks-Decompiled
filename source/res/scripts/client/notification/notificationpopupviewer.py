# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/NotificationPopUpViewer.py
from typing import TYPE_CHECKING
import logging
from PlayerEvents import g_playerEvents
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.meta.NotificationPopUpViewerMeta import NotificationPopUpViewerMeta
from gui.game_loading.resources.consts import Milestones
from gui.shared.notifications import NotificationGroup, NotificationPriorityLevel
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.impl.lobby.gf_notifications import GFNotificationInject
from helpers import dependency
from messenger import g_settings
from messenger.formatters import TimeFormatter
from messenger.proto.events import g_messengerEvents
from notification import NotificationMVC
from notification.BaseNotificationView import BaseNotificationView
from notification.settings import NOTIFICATION_STATE
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.shared.utils import IHangarSpace
if TYPE_CHECKING:
    from typing import Dict, Optional, Set
_logger = logging.getLogger(__name__)

class NotificationPopUpViewer(NotificationPopUpViewerMeta, BaseNotificationView):
    __connectionMgr = dependency.descriptor(IConnectionManager)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        mvc = NotificationMVC.g_instance
        mvc.initialize()
        settings = self._getSettings()
        self.__maxAvailableItemsCount = settings.stackLength
        self.__messagesPadding = settings.padding
        self.__noDisplayingPopups = True
        self.__lockedNotificationUseQueue = True
        self.__lockedNotificationPriority = {}
        self.__locks = set()
        self.__pendingMessagesQueue = []
        super(NotificationPopUpViewer, self).__init__()
        self.setModel(mvc.getModel())

    def registerGFNotification(self, component, alias, gfViewName, isPopUp, linkageData):
        from gui.Scaleform.framework import g_entitiesFactories
        idx = WindowLayer.UNDEFINED
        componentPy = g_entitiesFactories.initialize(GFNotificationInject(gfViewName, isPopUp, linkageData), component, idx)
        self.components[alias] = componentPy
        componentPy.setEnvironment(self.app)
        componentPy.create()
        g_eventBus.handleEvent(events.ComponentEvent(events.ComponentEvent.COMPONENT_REGISTERED, self, componentPy, alias), EVENT_BUS_SCOPE.GLOBAL)
        self._onRegisterFlashComponent(componentPy, alias)

    def onClickAction(self, typeID, entityID, action):
        NotificationMVC.g_instance.handleAction(typeID, self._getNotificationID(entityID), action)

    def onMessageHidden(self, byTimeout, wasNotified, typeID, entityID):
        if self._model.getDisplayState() == NOTIFICATION_STATE.POPUPS:
            if not byTimeout and wasNotified:
                notification = self._model.getNotification(typeID, self._getNotificationID(entityID))
                if notification and notification.decrementCounterOnHidden():
                    self._model.decrementNotifiedMessagesCount(*notification.getCounterInfo())

    def setListClear(self):
        self.__noDisplayingPopups = True
        if self._model is not None and self._model.getDisplayState() == NOTIFICATION_STATE.POPUPS:
            if self.__pendingMessagesQueue and self.__pendingMessagesQueue[0].isAlert():
                self.__showAlertMessage(self.__pendingMessagesQueue.pop(0))
        return

    def getMessageActualTime(self, msTime):
        return TimeFormatter.getActualMsgTimeStr(msTime)

    def _populate(self):
        super(NotificationPopUpViewer, self)._populate()
        self.as_initInfoS(self.__maxAvailableItemsCount, self.__messagesPadding)
        self.__startNotifications()

    def _dispose(self):
        self.__pendingMessagesQueue = []
        self._model.onNotificationReceived -= self.__onNotificationReceived
        self._model.onNotificationUpdated -= self.__onNotificationUpdated
        self._model.onNotificationRemoved -= self.__onNotificationRemoved
        self._model.onDisplayStateChanged -= self.__displayStateChangeHandler
        self._model.onPopUpPaddingChanged -= self.__onPopUpPaddingChanged
        mvcInstance = NotificationMVC.g_instance
        mvcInstance.getAlertController().onAllAlertsClosed -= self.__allAlertsMessageCloseHandler
        g_messengerEvents.onLockPopUpMessages -= self.__onLockPopUpMessages
        g_messengerEvents.onUnlockPopUpMessages -= self.__onUnlockPopUpMessages
        g_playerEvents.onLoadingMilestoneReached -= self._onLoadingMilestoneReached
        self.cleanUp()
        mvcInstance.cleanUp(resetCounter=self.__connectionMgr.isDisconnected())
        super(NotificationPopUpViewer, self)._dispose()

    def _getSettings(self):
        return g_settings.lobby.serviceChannel

    def __onNotificationReceived(self, notification):
        if self._model.getDisplayState() == NOTIFICATION_STATE.POPUPS:
            if notification.isNotify() and self._model.hasNotification(notification.getType(), notification.getID()) and (notification.getGroup() != NotificationGroup.INFO or notification.getPriorityLevel() == NotificationPriorityLevel.LOW):
                self._model.incrementNotifiedMessagesCount(*notification.getCounterInfo())
            if notification.onlyNCList():
                return
            if NotificationMVC.g_instance.getAlertController().isAlertShowing():
                self.__pendingMessagesQueue.append(notification)
            elif self.__pendingMessagesQueue or self.__isLocked(notification):
                if self.__lockedNotificationUseQueue:
                    self.__pendingMessagesQueue.append(notification)
            elif notification.isAlert():
                if self.__noDisplayingPopups:
                    self.__showAlertMessage(notification)
                else:
                    self.__pendingMessagesQueue.append(notification)
            else:
                self.__sendMessageForDisplay(notification)

    def __onNotificationUpdated(self, notification, isStateChanged):
        flashID = self._getFlashID(notification.getCounterInfo())
        if self.as_hasPopUpIndexS(notification.getType(), flashID):
            self.as_updateMessageS(self.__getPopUpVO(notification))
        elif isStateChanged:
            self.__onNotificationReceived(notification)

    def __onNotificationRemoved(self, typeID, entityID, groupID, countOnce):
        self._model.decrementNotifiedMessagesCount(groupID, typeID, entityID, countOnce)
        notificationInfo = (groupID,
         typeID,
         entityID,
         countOnce)
        self.as_removeMessageS(typeID, self._getFlashID(notificationInfo))

    def __sendMessageForDisplay(self, notification):
        if notification.getPriorityLevel() != NotificationPriorityLevel.LOW:
            self.as_appendMessageS(self.__getPopUpVO(notification))
            self.__noDisplayingPopups = False

    def __showAlertMessage(self, notification):
        NotificationMVC.g_instance.getAlertController().showAlertMessage(notification)

    def __allAlertsMessageCloseHandler(self):
        self.__showMessagesFromQueue()

    def __showMessagesFromQueue(self):
        if self.__pendingMessagesQueue:
            needToShowFromQueueMessages = []
            while self.__pendingMessagesQueue:
                notification = self.__pendingMessagesQueue.pop(0)
                isAlert = notification.isAlert()
                if isAlert:
                    self.__showAlertMessage(notification)
                    return
                needToShowFromQueueMessages.append(notification)

            while needToShowFromQueueMessages:
                notification = needToShowFromQueueMessages.pop(0)
                if len(needToShowFromQueueMessages) < self.__maxAvailableItemsCount:
                    self.__sendMessageForDisplay(notification)

    def __onPopUpPaddingChanged(self, enabled=True, paddinX=0, paddinY=0):
        self.as_setViewPaddingS(enabled, paddinX, paddinY)

    def __displayStateChangeHandler(self, oldState, newState, data):
        if newState == NOTIFICATION_STATE.LIST:
            self.as_removeAllMessagesS()
            self.__pendingMessagesQueue = []

    def __getPopUpVO(self, notificaton):
        flashId = self._getFlashID(notificaton.getCounterInfo())
        return notificaton.getPopUpVO(flashId)

    def __isLocked(self, notification):
        priorities = {priority for val in self.__lockedNotificationPriority.values() for priority in val}
        return notification.getPriorityLevel() in priorities or notification.getPriorityLevel() in self.__locks

    def __onLockPopUpMessages(self, key, lockHigh=False, useQueue=True, clear=False):
        priorities = self.__lockedNotificationPriority.setdefault(key, {NotificationPriorityLevel.MEDIUM})
        if lockHigh:
            priorities.add(NotificationPriorityLevel.HIGH)
            locks = {NotificationPriorityLevel.MEDIUM, NotificationPriorityLevel.HIGH}
        else:
            locks = {NotificationPriorityLevel.MEDIUM}
        self.__lockedNotificationUseQueue = useQueue
        self.__lockedNotificationPriority[key] = locks
        self.__updateLocks()
        if clear:
            self.as_removeAllMessagesS()

    def __onUnlockPopUpMessages(self, key):
        _logger.debug('NotificationPopUpViewer has been unlocked. key=%s', key)
        if key not in self.__lockedNotificationPriority:
            _logger.error('Failed to lock NotificationPopUpViewer. Missing key=%s.', key)
        if self.__lockedNotificationPriority.get(key):
            del self.__lockedNotificationPriority[key]
        self.__updateLocks()
        if not self.__locks:
            self.__showMessagesFromQueue()
        self.__lockedNotificationUseQueue = True
        if key in self.__lockedNotificationPriority:
            del self.__lockedNotificationPriority[key]
        if self.__pendingMessagesQueue and any((self.__isLocked(n) for n in self.__pendingMessagesQueue)):
            return
        self.__showMessagesFromQueue()

    def __updateLocks(self):
        locks = self.__lockedNotificationPriority.values()
        self.__locks = set.union(*locks) if locks else set()

    def __startNotifications(self):
        if self.__hangarSpace.spaceInited:
            self._model.onNotificationReceived += self.__onNotificationReceived
            self._model.onNotificationUpdated += self.__onNotificationUpdated
            self._model.onNotificationRemoved += self.__onNotificationRemoved
            self._model.onDisplayStateChanged += self.__displayStateChangeHandler
            self._model.onPopUpPaddingChanged += self.__onPopUpPaddingChanged
            mvcInstance = NotificationMVC.g_instance
            mvcInstance.getAlertController().onAllAlertsClosed += self.__allAlertsMessageCloseHandler
            g_messengerEvents.onLockPopUpMessages += self.__onLockPopUpMessages
            g_messengerEvents.onUnlockPopUpMessages += self.__onUnlockPopUpMessages
            self._model.setup()
        else:
            g_playerEvents.onLoadingMilestoneReached += self._onLoadingMilestoneReached

    def _onLoadingMilestoneReached(self, milestoneName):
        if milestoneName == Milestones.HANGAR_READY:
            g_playerEvents.onLoadingMilestoneReached -= self._onLoadingMilestoneReached
            self.__startNotifications()
