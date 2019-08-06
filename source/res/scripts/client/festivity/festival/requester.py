# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/festival/requester.py
import typing
from festivity.base import BaseFestivityRequester
from festivity.festival.constants import FestSyncDataKeys, FEST_DATA_SYNC_KEY
from gui.shared.utils.requesters import RequestCriteria
from gui.shared.utils.requesters.ItemsRequester import PredicateCondition
from items.components.festival_constants import FEST_ITEM_TYPE, BOT_PLAYER_CARD

class FestCriteria(object):
    INVENTORY = RequestCriteria(PredicateCondition(lambda item: item.isInInventory()))
    BASIS = RequestCriteria(PredicateCondition(lambda item: item.getType() == FEST_ITEM_TYPE.BASIS))
    INSCRIPTION = RequestCriteria(PredicateCondition(lambda item: item.getType() == FEST_ITEM_TYPE.TITLE))
    EMBLEM = RequestCriteria(PredicateCondition(lambda item: item.getType() == FEST_ITEM_TYPE.EMBLEM))
    RANK = RequestCriteria(PredicateCondition(lambda item: item.getType() == FEST_ITEM_TYPE.RANK))
    UNSEEN = RequestCriteria(PredicateCondition(lambda item: not item.isSeen()))
    TYPE = staticmethod(lambda typeName: RequestCriteria(PredicateCondition(lambda item: item.getType() == typeName)))
    QUALITY = staticmethod(lambda quality: RequestCriteria(PredicateCondition(lambda item: item.getQuality() == quality)))


class FestivalRequester(BaseFestivityRequester):
    dataKey = FEST_DATA_SYNC_KEY

    def getItemsBytes(self):
        return self.getCacheValue(FestSyncDataKeys.ITEMS, bytearray())

    def getSeenItemsBytes(self):
        return self.getCacheValue(FestSyncDataKeys.SEEN_ITEMS, bytearray())

    def getTickets(self):
        return self.getCacheValue(FestSyncDataKeys.TICKETS, 0)

    def getPlayerCard(self):
        return self.getCacheValue(FestSyncDataKeys.PLAYER_CARD, BOT_PLAYER_CARD)

    def getPurchases(self):
        return self.getCacheValue(FestSyncDataKeys.PURCHASES, {})
