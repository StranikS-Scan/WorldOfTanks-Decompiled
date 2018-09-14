# Embedded file name: scripts/client/gui/wgnc/provider.py
import time
import BigWorld
from debug_utils import LOG_ERROR, LOG_DEBUG, LOG_WARNING
from gui.shared.utils.decorators import ReprInjector
from gui.wgnc.errors import ParseError, ValidationError
from gui.wgnc.xml import fromString

@ReprInjector.simple('notID', 'ttl', 'actions', 'items', 'order', 'marked', 'client')

class _NotificationVO(object):
    __slots__ = ('notID', 'ttl', 'actions', 'items', 'proxyDataItems', 'order', 'marked', 'client')

    def __init__(self, notID, ttl, actions, items, proxyDataItems):
        super(_NotificationVO, self).__init__()
        self.notID = notID
        self.ttl = ttl
        self.actions = actions
        self.items = items
        self.proxyDataItems = proxyDataItems
        self.order = BigWorld.time()
        self.marked = False
        self.client = None
        return

    def clear(self):
        self.notID = 0L
        self.ttl = 0.0
        self.actions = None
        self.items = None
        self.order = 0
        self.marked = False
        return

    def validate(self):
        result = True
        try:
            if self.items:
                self.items.validate(self.actions)
            if self.actions:
                self.actions.validate(self.items)
        except ValidationError as e:
            LOG_ERROR('Notification is invalid', e.message, self)
            result = False

        if self.items:
            self.client = self.items.getClientLogic()
        return result

    def isActive(self):
        result = True
        stamp = time.time()
        if self.ttl and self.ttl < stamp:
            result = False
            LOG_DEBUG('Notification is ignored, ttl is expired', self.notID, self.ttl, stamp)
        return result

    def getItemByName(self, name):
        if self.items:
            return self.items.getItemByName(name)
        else:
            return None

    def getItemByType(self, itemType):
        if self.items:
            return self.items.getItemByType(itemType)
        else:
            return None

    def getProxyItemByType(self, itemType):
        if self.proxyDataItems:
            return self.proxyDataItems.getItemByType(itemType)
        else:
            return None

    def showItem(self, notID, target):
        if self.items:
            self.items.showItem(notID, target)

    def showAll(self):
        if self.items:
            for item in self.items.all():
                if not item.isHidden():
                    item.show(self.notID)

        if self.proxyDataItems:
            for proxyItem in self.proxyDataItems.all():
                proxyItem.show(self.notID)

    def invoke(self, actionsNames, actorName = ''):
        result = False
        if self.actions:
            if actorName:
                actor = self.getItemByName(actorName)
                if self.client:
                    self.client.process(actor, self.notID, actionsNames, self.items)
            else:
                actor = None
            result = self.actions.invoke(self.notID, actionsNames, actor)
        return result


class _WGNCProvider(object):
    __slots__ = ('__nots', '__isEnabled', '__pending')

    def __init__(self):
        super(_WGNCProvider, self).__init__()
        self.__nots = {}
        self.__isEnabled = False
        self.__pending = []

    def clear(self):
        while self.__nots:
            _, item = self.__nots.popitem()
            item.clear()

        self.__isEnabled = False
        self.__pending = []

    def setEnabled(self, value):
        if self.__isEnabled == value:
            return
        self.__isEnabled = value
        if self.__isEnabled:
            while self.__pending:
                self.fromXmlString(self.__pending.pop(0))

    def fromXmlString(self, xmlString):
        if not self.__isEnabled:
            self.__pending.append(xmlString)
            return
        try:
            notID, ttl, actionsHolder, guiItemsHolder, proxyDataHolder = fromString(xmlString)
        except ParseError as e:
            LOG_ERROR('Can not parse notification', e.message, xmlString)
            return

        if notID in self.__nots:
            LOG_WARNING('Notification already is added', notID, self.__nots[notID])
            return 0L
        vo = _NotificationVO(notID, ttl, actionsHolder, guiItemsHolder, proxyDataHolder)
        if not vo.isActive():
            return 0L
        if not vo.validate():
            return 0L
        self.__nots[notID] = vo
        vo.showAll()
        return notID

    def getNotItemByName(self, notID, name):
        if notID not in self.__nots:
            LOG_ERROR('Notification is not found', notID)
            return
        return self.__nots[notID].getItemByName(name)

    def getNotItemByType(self, notID, name):
        if notID not in self.__nots:
            LOG_ERROR('Notification is not found', notID)
            return
        return self.__nots[notID].getItemByType(name)

    def showNotItemByName(self, notID, target):
        if notID not in self.__nots:
            LOG_ERROR('Notification is not found', notID)
            return True
        self.__nots[notID].showItem(notID, target)

    def setNotsAsMarked(self):
        for notification in self.__nots.itervalues():
            notification.marked = True

    def getMarkedNots(self):
        nots = sorted(self.__nots.itervalues(), key=lambda item: item.order)
        for notification in nots:
            if not notification.marked:
                continue
            yield notification

    def getNotMarkedNots(self):
        nots = sorted(self.__nots.itervalues(), key=lambda item: item.order)
        for notification in nots:
            if notification.marked:
                continue
            yield notification

    def showNoMarkedNots(self):
        nots = sorted(self.__nots.itervalues(), key=lambda item: item.order)
        for notification in nots:
            if notification.marked or not notification.isActive():
                continue
            notification.showAll()

    def doAction(self, notID, actionsNames, actorName = ''):
        if notID not in self.__nots:
            LOG_ERROR('Notification is not found', notID)
            return False
        return self.__nots[notID].invoke(actionsNames, actorName)


g_instance = _WGNCProvider()
