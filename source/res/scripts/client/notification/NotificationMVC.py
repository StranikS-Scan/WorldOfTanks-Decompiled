# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/NotificationMVC.py
from notification.AlertController import AlertController
from notification.NotificationsCounter import NotificationsCounter
from notification.NotificationsModel import NotificationsModel
from notification.actions_handlers import NotificationsActionsHandlers

class _NotificationMVC(object):

    def __init__(self):
        self.__model = None
        self.__alertsController = None
        self.__actionsHandlers = None
        self.__unreadMessagesCounter = NotificationsCounter()
        self.__firstEntry = True
        return

    def initialize(self):
        self.__model = NotificationsModel(self.__unreadMessagesCounter, self.__firstEntry)
        self.__actionsHandlers = NotificationsActionsHandlers()
        self.__alertsController = AlertController(self.__model)

    def getModel(self):
        return self.__model

    def getAlertController(self):
        return self.__alertsController

    def handleAction(self, typeID, entityID, action):
        self.__actionsHandlers.handleAction(self.__model, int(typeID), long(entityID), action)

    def cleanUp(self, resetCounter=False):
        self.__alertsController.cleanUp()
        self.__actionsHandlers.cleanUp()
        self.__model.cleanUp()
        self.__alertsController = None
        self.__actionsHandlers = None
        self.__firstEntry = False
        if resetCounter:
            self.__unreadMessagesCounter.clear()
            self.__unreadMessagesCounter = NotificationsCounter()
            self.__firstEntry = True
        self.__model = None
        return


g_instance = _NotificationMVC()
