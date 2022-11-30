# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_notifications_helpers.py
from operator import itemgetter
import typing
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items.loot_box import NewYearLootBoxes
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.requesters import TokensRequester
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import dependency
from items.components.ny_constants import NYFriendServiceDataTokens
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from shared_utils import findFirst
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
from skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.loot_box import LootBox
_TIME_DELAY_CONSTANT = 1.0

class LootBoxNotificationHelper(Notifiable):
    __itemsCache = dependency.descriptor(IItemsCache)
    __nyController = dependency.descriptor(INewYearController)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self):
        super(LootBoxNotificationHelper, self).__init__()
        self.__delayedNotifications = {}

    def onLobbyInited(self):
        self.addNotificator(PeriodicNotifier(self.__timeTillNextNotification, self.__notify))
        self.startNotification()

    def prepareNotifications(self, tokens):
        for tokenID, data in tokens.iteritems():
            lootBox = self.__itemsCache.items.tokens.getLootBoxByTokenID(tokenID)
            if lootBox is None or lootBox.getType() != NewYearLootBoxes.PREMIUM:
                continue
            count = self.__delayedNotifications.get(tokenID, 0) + data.get('count', 0)
            self.__delayedNotifications[tokenID] = count

        self.startNotification()
        return

    def onAvatarBecomePlayer(self):
        self.__clear()

    def onDisconnected(self):
        self.__delayedNotifications = {}
        self.__clear()

    def __clear(self):
        self.clearNotification()

    def __timeTillNextNotification(self):
        if not self.__nyController.isEnabled():
            return 0.0
        return _TIME_DELAY_CONSTANT if any([ value > 0 for value in self.__delayedNotifications.itervalues() ]) else 0.0

    def __notify(self):
        if not self.__nyController.isEnabled():
            return
        tokenID, value = findFirst(lambda data: data[1] > 0, sorted(self.__delayedNotifications.iteritems(), key=itemgetter(0)), ('', 0))
        if tokenID and value > 0:
            self.__pushNewLootBoxesNotification(tokenID, value)
            self.__delayedNotifications[tokenID] = max(self.__delayedNotifications[tokenID] - value, 0)

    def __pushNewLootBoxesNotification(self, tokenID, count):
        lootBox = self.__itemsCache.items.tokens.getLootBoxByTokenID(tokenID)
        if lootBox is None:
            return
        else:
            rHeader = R.strings.ny.notification.lootBox.header
            header = ''
            category = lootBox.getCategory()
            if category:
                rName = R.strings.lootboxes.tooltip.category.header.dyn(category)
                if rName.exists():
                    header = backport.text(rHeader.big(), name=backport.text(rName()))
            body = backport.text(R.strings.ny.notification.lootBox.body.default())
            self.__systemMessages.proto.serviceChannel.pushClientMessage(message=None, msgType=SCH_CLIENT_MSG_TYPE.NEW_NY_LOOT_BOXES, auxData=[{'header': header,
              'body': body,
              'category': category,
              'count': count}])
            return


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def checkAndNotifyAllDecorationReceived(itemsCache=None):
    tokens = itemsCache.items.tokens
    for tokenID in NYFriendServiceDataTokens.ALL_DECORATIONS:
        if tokens.getTokenCount(tokenID) == 0:
            return

    SystemMessages.pushMessage(backport.text(R.strings.system_messages.newYear.allObjectsCollected.body()), type=SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.LOW, messageData={'header': backport.text(R.strings.system_messages.newYear.allObjectsCollected.header())})


@dependency.replace_none_kwargs(systemMessages=ISystemMessages)
def sendNYResourceCollectingAvailableMessage(resourcesCount, systemMessages=None):
    systemMessages.proto.serviceChannel.pushClientMessage(message=None, msgType=SCH_CLIENT_MSG_TYPE.NY_RESOURCE_COLLECTING_AVAILABLE, auxData=resourcesCount)
    return


@dependency.replace_none_kwargs(systemMessages=ISystemMessages)
def sendNYFriendResourceCollectingAvailableMessage(friendsNames, resourcesCount, friendSpaIDs, systemMessages=None):
    systemMessages.proto.serviceChannel.pushClientMessage(message=None, msgType=SCH_CLIENT_MSG_TYPE.NY_FRIEND_RESOURCE_COLLECTING_AVAILABLE, auxData={'resourcesCount': resourcesCount,
     'friendsNames': friendsNames,
     'friendSpaIDs': friendSpaIDs})
    return
