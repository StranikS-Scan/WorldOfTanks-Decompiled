# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ny_requester.py
import logging
import typing
import BigWorld
from adisp import adisp_async
from gui.shared.utils.requesters.abstract import AbstractSyncDataRequester
from helpers import dependency
from items.components.ny_constants import CurrentNYConstants, INVALID_TOY_ID
from new_year.friend_service_controller import FriendHangarDataKeys
from new_year.ny_constants import SyncDataKeys
from new_year.ny_toy_info import NewYearCurrentToyInfo
from skeletons.new_year import IFriendServiceController
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from typing import Optional
_logger = logging.getLogger(__name__)

class _NewYearToy(NewYearCurrentToyInfo):
    __slots__ = ('__totalCount', '__slotId', '__unseenCount', '__unseenInCollection', '__slotsCount')

    def __init__(self, toyId, slotId, totalCount, unseenFlag, slotsCount):
        super(_NewYearToy, self).__init__(toyId)
        self.__totalCount = totalCount
        self.__slotId = slotId
        self.__slotsCount = slotsCount
        self.__unseenCount = unseenFlag >> 1
        self.__unseenInCollection = not bool(unseenFlag % 2)

    def getCount(self):
        return self.__totalCount

    def getSlotID(self):
        return self.__slotId

    def getUnseenCount(self):
        return self.__unseenCount

    def isNewInCollection(self):
        return self.__unseenInCollection

    def __cmp__(self, other):
        if other.getRank() != self.getRank():
            return other.getRank() - self.getRank()
        if self.__unseenCount and not other.getUnseenCount():
            return -1
        return 1 if not self.__unseenCount and other.getUnseenCount() else self.getID() - other.getID()


class NewYearRequester(AbstractSyncDataRequester):
    _itemsCache = dependency.descriptor(IItemsCache)
    dataKey = CurrentNYConstants.PDATA_KEY

    def getToys(self):
        return self.getCacheValue(SyncDataKeys.INVENTORY_TOYS, {})

    def getChosenXPBonus(self):
        return self.getCacheValue(SyncDataKeys.XP_BONUS_CHOICE)

    def getSlotsData(self):
        return self.getCacheValue(SyncDataKeys.SLOTS, [])

    def getAtmPoints(self):
        return self.getCacheValue(SyncDataKeys.POINTS, 0)

    def getMaxLevel(self):
        return self.getCacheValue(SyncDataKeys.LEVEL, 0)

    def getToyCollection(self):
        return self.getCacheValue(SyncDataKeys.TOY_COLLECTION)

    def getCollectionDistributions(self):
        return self.getCacheValue(SyncDataKeys.COLLECTION_DISTRIBUTIONS, {})

    def getVehicleBonusChoices(self):
        return self.getCacheValue(SyncDataKeys.VEHICLE_BONUS_CHOICES, -1)

    def getSelectedDiscounts(self):
        return self.getCacheValue(SyncDataKeys.SELECTED_DISCOUNTS, set())

    def getObjectsLevels(self):
        return self.getCacheValue(SyncDataKeys.OBJECTS_LEVELS, set())

    def getHangarNameMask(self):
        return self.getCacheValue(SyncDataKeys.HANGAR_NAME_MASK)

    def getResourceCollecting(self):
        return self.getCacheValue(SyncDataKeys.RESOURCE_COLLECTING, (None, None, None))

    def getPiggyBankActiveItemIndex(self):
        return self.getCacheValue(SyncDataKeys.PIGGY_BANK_ACTIVE_ITEM_INDEX, 0)

    def getPrevNYLevel(self):
        return self.getCacheValue(SyncDataKeys.PREV_NY_LEVEL, 0)

    @adisp_async
    def _requestCache(self, callback):
        BigWorld.player().festivities.getCache(lambda resID, value: self._response(resID, value, callback))

    def _preprocessValidData(self, data):
        nyData = data.get(self.dataKey, {})
        result = dict(nyData)
        if SyncDataKeys.INVENTORY_TOYS in nyData:
            inventoryToys = {}
            for slotId, toys in nyData[SyncDataKeys.INVENTORY_TOYS].iteritems():
                inventoryToys[slotId] = {}
                for toyId, (totalCount, unseenCount, slotsCount) in toys.iteritems():
                    inventoryToys[slotId][toyId] = _NewYearToy(toyId, slotId, totalCount, unseenCount, slotsCount)

            result[SyncDataKeys.INVENTORY_TOYS] = inventoryToys
        return result

    def isTokenReceived(self, token):
        return self._itemsCache.items.tokens.isTokenAvailable(token)

    def getTokenCount(self, token):
        return self._itemsCache.items.tokens.getTokenCount(token)


class FriendNewYearRequester(NewYearRequester):
    __friendService = dependency.descriptor(IFriendServiceController)

    @property
    def __friendHangarState(self):
        return self.__friendService.getFriendState()

    def getToys(self):
        return {slotId:{toyId: _NewYearToy(toyId, slotId, 1, 0, 0)} for slotId, toyId in enumerate(self.getSlotsData()) if toyId != INVALID_TOY_ID}

    def getChosenXPBonus(self):
        raise SoftException("unexpected call of getChosenXPBonus in friend's hangar.")

    def getSlotsData(self):
        return self.__friendHangarState[FriendHangarDataKeys.TOY_SLOTS]

    def getAtmPoints(self):
        return self.__friendHangarState[FriendHangarDataKeys.ATM_POINTS]

    def getMaxLevel(self):
        return self.__friendHangarState[FriendHangarDataKeys.ATM_LEVEL]

    def getToyCollection(self):
        raise SoftException("unexpected call of getToyCollection in friend's hangar.")

    def getCollectionDistributions(self):
        raise SoftException("unexpected call of getCollectionDistributions in friend's hangar.")

    def getVehicleBonusChoices(self):
        raise SoftException("unexpected call of getVehicleBonusChoices in friend's hangar.")

    def getSelectedDiscounts(self):
        raise SoftException("unexpected call of getSelectedDiscounts in friend's hangar.")

    def getObjectsLevels(self):
        return self.__friendHangarState[FriendHangarDataKeys.CUSTOMIZATION_OBJECTS]

    def getHangarNameMask(self):
        return self.__friendService.getFriendState()[FriendHangarDataKeys.HANGAR_NAME]

    def getResourceCollecting(self):
        raise SoftException("unexpected call of getResourceCollecting in friend's hangar.")

    def isTokenReceived(self, token):
        return token in self.__friendService.getFriendTokens()

    def getTokenCount(self, token):
        return self.__friendService.getFriendTokens().get(token, 0)
